<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Task, type LabExecResult, type LabVerifyResult } from '../lib/api';
  import Badge from '../components/shared/Badge.svelte';

  let tasks = $state<Task[]>([]);
  let loading = $state(true);
  let error = $state('');

  // 终端状态
  let lines = $state<{ kind: 'cmd' | 'out' | 'err' | 'sys'; text: string }[]>([]);
  let input = $state('');
  let busy = $state(false);
  let cmdHistory = $state<string[]>([]);
  let histIdx = $state(-1);
  let verifying = $state<number | null>(null);
  let verifyMsg = $state<{ taskId: number; ok: boolean; text: string } | null>(null);
  let termEl = $state<HTMLDivElement | null>(null);

  const QUICK_CMDS = [
    'pwd', 'ls -lah /', 'mkdir -p /tmp/miglab', 'touch /tmp/miglab/hello.txt',
    'echo hello > /tmp/miglab/hello.txt', 'cat /tmp/miglab/hello.txt',
    'cp /tmp/miglab/hello.txt /tmp/miglab/copy.txt', 'mv /tmp/miglab/copy.txt /tmp/miglab/moved.txt',
    'grep hello /tmp/miglab/hello.txt', 'find /tmp/miglab -name "*.txt"',
  ];

  onMount(loadTasks);
  $effect(() => {
    if (termEl) termEl.scrollTop = termEl.scrollHeight;
  });

  async function loadTasks() {
    loading = true;
    error = '';
    try {
      const r = await api.get<{ data: { tasks: Task[] } }>('/api/tasks?type=learning&track_id=2');
      tasks = r.data.tasks;
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    } finally {
      loading = false;
    }
  }

  const statusLabel = (s: string) =>
    ({ todo: '待开始', in_progress: '进行中', done: '已完成', cancelled: '已取消' })[s] ?? s;
  const statusTone = (s: string) =>
    ({ todo: 'neutral', in_progress: 'primary', done: 'accent' })[s] ?? 'neutral';
  const doneCount = $derived(tasks.filter((t) => t.status === 'done').length);

  // ---- 终端 ----
  function push(kind: 'cmd' | 'out' | 'err' | 'sys', text: string) {
    lines = [...lines, { kind, text }];
  }

  async function runCmd(cmd?: string) {
    const c = (cmd ?? input).trim();
    if (!c || busy) return;
    input = '';
    cmdHistory = [...cmdHistory, c];
    histIdx = -1;
    push('cmd', `$ ${c}`);
    busy = true;
    try {
      const r = await api.post<{ data: LabExecResult }>('/api/lab/exec', { cmd: c });
      const d = r.data;
      if (d.stdout) push('out', d.stdout.replace(/\n$/, ''));
      if (d.stderr) push('err', d.stderr.replace(/\n$/, ''));
      if (d.exit_code !== 0 && !d.stderr) push('err', `(exit code ${d.exit_code})`);
    } catch (e) {
      push('err', e instanceof Error ? e.message : String(e));
    } finally {
      busy = false;
    }
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Enter') runCmd();
    else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (cmdHistory.length === 0) return;
      histIdx = histIdx === -1 ? cmdHistory.length - 1 : Math.max(0, histIdx - 1);
      input = cmdHistory[histIdx];
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (histIdx === -1) return;
      histIdx = Math.min(cmdHistory.length - 1, histIdx + 1);
      input = histIdx === cmdHistory.length - 1 ? '' : cmdHistory[histIdx];
    }
  }

  async function resetLab() {
    push('sys', '↻ 正在重置实验环境…');
    try {
      await api.post<{ data: { ok: boolean; message: string } }>('/api/lab/reset', {});
      push('sys', '✓ 环境已重置（/tmp/miglab 已清空，从 05 mkdir 重新开始）');
    } catch (e) {
      push('err', e instanceof Error ? e.message : String(e));
    }
  }

  // ---- 验证 ----
  async function verify(t: Task) {
    verifying = t.id;
    verifyMsg = null;
    try {
      const r = await api.post<{ data: LabVerifyResult }>('/api/lab/verify', { task_id: t.id });
      const d = r.data;
      if (d.passed) {
        verifyMsg = { taskId: t.id, ok: true, text: `✓ 验证通过！已记录学习日志：${d.study_log?.title ?? ''}` };
        await loadTasks();
      } else {
        verifyMsg = { taskId: t.id, ok: false, text: `✗ 未通过：${d.output ?? ''}` };
      }
    } catch (e) {
      verifyMsg = { taskId: t.id, ok: false, text: e instanceof Error ? e.message : String(e) };
    } finally {
      verifying = null;
    }
  }
</script>

<div class="page">
  <section class="lab-hero">
    <p class="lh-kicker">Linux Lab · 隔离实验环境</p>
    <h1 class="lh-title">Linux Engineer Roadmap V2</h1>
    <p class="lh-sub">
      L0 Linux 基础操作 · 浏览器内直接实操（docker 隔离容器，与生产完全隔离，可一键 Reset）
    </p>
    <div class="lh-meta">
      <span>任务进度 <strong>{doneCount}/15</strong></span>
      <button class="reset-btn" onclick={resetLab}>↻ Reset 实验环境</button>
    </div>
  </section>

  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}</div>
  {:else if loading}
    <div class="loading">
      <div class="skeleton" style="height:180px; border-radius:28px;"></div>
      <div class="skeleton" style="height:300px;"></div>
    </div>
  {:else}
    <div class="lab-grid">
      <!-- 左侧: 任务列表 -->
      <section class="task-panel">
        <div class="section-head">
          <h2 class="section-title">L0 · Linux 基础操作</h2>
          <span class="count">{doneCount}/15</span>
        </div>
        {#if tasks.length === 0}
          <div class="empty-note">暂无实验任务</div>
        {:else}
          <div class="task-list">
            {#each tasks as t (t.id)}
              <div class="task-card" class:done-card={t.status === 'done'}>
                <div class="tc-top">
                  <span class="tc-title">{t.title}</span>
                  <Badge tone={statusTone(t.status)}>{statusLabel(t.status)}</Badge>
                </div>
                <p class="tc-desc">{t.description}</p>
                {#if t.status !== 'done'}
                  <button class="verify-btn" onclick={() => verify(t)} disabled={verifying === t.id}>
                    {verifying === t.id ? '验证中…' : '验证实验结果'}
                  </button>
                {/if}
                {#if verifyMsg?.taskId === t.id}
                  <p class="verify-msg" class:ok={verifyMsg.ok} class:fail={!verifyMsg.ok}>{verifyMsg.text}</p>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </section>

      <!-- 右侧: 终端 -->
      <section class="term-panel">
        <div class="section-head">
          <h2 class="section-title">Terminal</h2>
          <span class="term-hint">仅执行一次命令（vim/top 等全屏程序暂不支持）</span>
        </div>
        <div class="term" bind:this={termEl}>
          {#if lines.length === 0}
            <p class="term-placeholder">试试：mkdir -p /tmp/miglab，然后开始 01-15 实验</p>
          {:else}
            {#each lines as l, i (i)}
              <p class:term-cmd={l.kind === 'cmd'} class:term-err={l.kind === 'err'} class:term-sys={l.kind === 'sys'}>{l.text}</p>
            {/each}
          {/if}
          <div class="term-input-line">
            <span class="term-prompt">$</span>
            <input
              class="term-input"
              bind:value={input}
              onkeydown={onKey}
              placeholder="输入 Linux 命令…"
              autocomplete="off"
              spellcheck="false"
            />
            <button class="send-btn" onclick={() => runCmd()} disabled={busy}>发送</button>
          </div>
        </div>
        <div class="quick-cmds">
          {#each QUICK_CMDS as c (c)}
            <button class="chip" onclick={() => runCmd(c)} disabled={busy}>{c}</button>
          {/each}
        </div>
      </section>
    </div>
  {/if}
</div>

<style>
  .loading { display: flex; flex-direction: column; gap: var(--sp-5); padding: var(--sp-6) 0; }
  .load-error { margin: var(--sp-6) 0; padding: var(--sp-4) var(--sp-5); background: #fee2e2; color: #b91c1c; border-radius: var(--r-md); font-weight: 600; }
  .empty-note { padding: var(--sp-5); border: 1px dashed var(--c-border); border-radius: var(--r-lg); color: var(--c-text-2); text-align: center; }
  .count { font-size: var(--fs-small); color: var(--c-text-3); }

  .lab-hero {
    margin: var(--sp-6) 0 var(--sp-7); padding: var(--sp-7);
    border-radius: 28px; background: linear-gradient(135deg, #1e1b4b 0%, #312e81 55%, #4c1d95 100%);
    color: #fff; box-shadow: var(--shadow-lg); position: relative; overflow: hidden;
  }
  .lab-hero::after { content: ''; position: absolute; right: -60px; top: -60px; width: 260px; height: 260px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.15), transparent 70%); }
  .lh-kicker { font-size: var(--fs-small); opacity: 0.75; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: var(--sp-2); }
  .lh-title { font-size: var(--fs-title); font-weight: 800; letter-spacing: -0.03em; margin-bottom: var(--sp-2); }
  .lh-sub { font-size: var(--fs-body); opacity: 0.85; max-width: 620px; margin-bottom: var(--sp-5); }
  .lh-meta { display: flex; align-items: center; gap: var(--sp-4); flex-wrap: wrap; position: relative; z-index: 1; }
  .reset-btn { background: rgba(255,255,255,0.16); color: #fff; border: 1px solid rgba(255,255,255,0.35); border-radius: 999px; padding: 6px 16px; font-size: var(--fs-small); font-weight: 600; cursor: pointer; }
  .reset-btn:hover { background: rgba(255,255,255,0.26); }

  .lab-grid { display: grid; grid-template-columns: 420px 1fr; gap: var(--sp-6); align-items: start; }

  .task-panel, .term-panel { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-5); box-shadow: var(--shadow-sm); }
  .task-list { display: flex; flex-direction: column; gap: var(--sp-3); max-height: 640px; overflow-y: auto; padding-right: 4px; }
  .task-card { border: 1px solid var(--c-border); border-radius: var(--r-md); padding: var(--sp-4); }
  .task-card.done-card { background: var(--c-surface-2); opacity: 0.75; }
  .tc-top { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3); margin-bottom: var(--sp-2); }
  .tc-title { font-weight: 700; font-size: var(--fs-body); }
  .tc-desc { font-size: var(--fs-micro); color: var(--c-text-2); line-height: 1.6; margin-bottom: var(--sp-3); }
  .verify-btn { width: 100%; background: var(--grad-brand); color: #fff; border: none; border-radius: var(--r-sm); padding: 8px; font-size: var(--fs-small); font-weight: 600; cursor: pointer; }
  .verify-btn:disabled { opacity: 0.6; cursor: wait; }
  .verify-msg { margin-top: var(--sp-2); font-size: var(--fs-micro); line-height: 1.5; }
  .verify-msg.ok { color: #047857; }
  .verify-msg.fail { color: #b91c1c; }

  .term { background: #0f172a; border-radius: var(--r-md); padding: var(--sp-4); min-height: 460px; max-height: 560px; overflow-y: auto; font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; line-height: 1.7; }
  .term-placeholder { color: #64748b; }
  .term :global(p) { margin: 0; white-space: pre-wrap; word-break: break-all; color: #e2e8f0; }
  .term-cmd { color: #a5b4fc !important; font-weight: 600; }
  .term-err { color: #f87171 !important; }
  .term-sys { color: #34d399 !important; font-style: italic; }
  .term-input-line { display: flex; align-items: center; gap: var(--sp-2); margin-top: var(--sp-3); }
  .term-prompt { color: #34d399; font-weight: 700; }
  .term-input { flex: 1; background: #1e293b; border: 1px solid #334155; color: #e2e8f0; border-radius: var(--r-sm); padding: 8px 12px; font-family: inherit; font-size: 13px; outline: none; }
  .term-input:focus { border-color: #6366f1; }
  .send-btn { background: #6366f1; color: #fff; border: none; border-radius: var(--r-sm); padding: 8px 14px; font-weight: 600; font-size: var(--fs-small); cursor: pointer; }
  .send-btn:disabled { opacity: 0.6; }

  .quick-cmds { display: flex; flex-wrap: wrap; gap: var(--sp-2); margin-top: var(--sp-3); }
  .chip { background: var(--c-surface-2); border: 1px solid var(--c-border); border-radius: 999px; padding: 4px 12px; font-size: var(--fs-micro); color: var(--c-text-2); cursor: pointer; }
  .chip:hover { color: var(--c-primary); border-color: var(--c-primary); }

  @media (max-width: 980px) {
    .lab-grid { grid-template-columns: 1fr; }
  }
</style>
