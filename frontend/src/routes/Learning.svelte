<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type LearningData, type Task } from '../lib/api';
  import ProgressRing from '../components/shared/ProgressRing.svelte';
  import Badge from '../components/shared/Badge.svelte';

    let data = $state<LearningData | null>(null);
    let error = $state('');
    let busy = $state(false);

    // 完成学习弹窗
    let editingTask = $state<Task | null>(null);
    let draft = $state('');
    let saving = $state(false);

    onMount(load);

    async function load() {
      try {
        data = await api.get<{ data: LearningData }>('/api/learning').then((r) => r.data);
        error = '';
      } catch (e) {
        error = e instanceof Error ? e.message : String(e);
      }
    }

    function openComplete(task: Task) {
      if (busy || task.status === 'done') return;
      editingTask = task;
      draft = '';
    }

    // 保存学习记录 → 落库 + 任务完成 + 生成 Markdown
    async function saveLog() {
      if (!editingTask || saving) return;
      saving = true;
      try {
        await api.post('/api/study-logs', {
          task_id: editingTask.id,
          content: draft.trim(),
        });
        editingTask = null;
        await load();
      } catch (e) {
        error = e instanceof Error ? e.message : String(e);
      } finally {
        saving = false;
      }
    }

    // 跳过 → 任务仍完成（无学习记录）
    async function skipComplete() {
      if (!editingTask || saving) return;
      saving = true;
      try {
        await api.patch(`/api/tasks/${editingTask.id}`, { status: 'done' });
        editingTask = null;
        await load();
      } catch (e) {
        error = e instanceof Error ? e.message : String(e);
      } finally {
        saving = false;
      }
    }

  const byStatus = $derived({
    doing: (data?.tasks ?? []).filter((t) => t.status === 'in_progress'),
    todo: (data?.tasks ?? []).filter((t) => t.status === 'todo'),
    done: (data?.tasks ?? []).filter((t) => t.status === 'done'),
  });

  const taskTone = (s: Task['status']) =>
    s === 'done' ? 'accent' : s === 'in_progress' ? 'primary' : 'neutral';
  const taskLabel = (s: Task['status']) =>
    ({ done: '已完成', in_progress: '进行中', todo: '待开始', cancelled: '已取消' })[s];
</script>

<div class="page">
  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}</div>
  {:else if !data}
    <div class="loading">
      <div class="skeleton" style="height:220px; border-radius:28px;"></div>
      <div class="skeleton" style="height:140px;"></div>
      <div class="skeleton" style="height:200px;"></div>
    </div>
  {:else}
    <!-- 1. Learning Hero -->
    {#if data.current}
      <section class="learn-hero">
        <div class="lh-copy">
          <p class="lh-kicker">当前学习路线</p>
          <h1 class="lh-title">{data.current.title}</h1>
          <p class="lh-stage">
            <span class="lh-stage-badge">{data.current.stage}</span>
          </p>
          <p class="lh-stats">
            已完成 <strong>{data.current.stats.done}</strong> / {data.current.stats.total} 个任务
          </p>
        </div>
        <div class="lh-ring">
          <ProgressRing value={data.current.progress} size={132} stroke={10} />
          <div class="ring-caption">路线进度</div>
        </div>
      </section>
    {/if}

    <!-- 2. 总体进度 -->
    <section class="overall">
      <div class="section-head">
        <h2 class="section-title">总体进度</h2>
        <span class="overall-pct">{data.progress.percent}%</span>
      </div>
      <div class="overall-bar">
        <div class="overall-fill" style={`width: ${data.progress.percent}%`}></div>
      </div>
      <p class="overall-sub">
        {data.progress.done} / {data.progress.total} 任务完成 · Linux → DevOps 共 8 阶段
      </p>
    </section>

    <!-- 3. 当前学习任务 -->
    {#if byStatus.doing.length > 0}
      <section class="current-block">
        <div class="section-head">
          <h2 class="section-title">当前学习任务</h2>
        </div>
        <div class="current-shelf shelf-scroll">
          {#each byStatus.doing as t (t.id)}
            <article class="current-card">
              <div class="cc-top">
                <Badge tone="primary">进行中</Badge>
                <span class="cc-skill">{t.skill_name ?? ''}</span>
              </div>
              <h3 class="cc-title">{t.title}</h3>
              <p class="cc-desc">{t.description ?? ''}</p>
              <button
                class="cc-btn"
                disabled={busy}
                onclick={() => openComplete(t)}
              >✓ 标记完成</button>
            </article>
          {/each}
        </div>
      </section>
    {/if}

    <!-- 4. Task List (Doing / Todo / Done) -->
    <section class="task-list-block">
      <div class="section-head">
        <h2 class="section-title">Task List</h2>
        <span class="task-count">共 {data.tasks.length} 个任务</span>
      </div>

      {#each ['doing', 'todo', 'done'] as group (group)}
        {#if byStatus[group as 'doing' | 'todo' | 'done'].length > 0}
          <h3 class="group-title">
            {{ doing: '进行中', todo: '待开始', done: '已完成' }[group]}
            <span class="group-count">{byStatus[group as 'doing' | 'todo' | 'done'].length}</span>
          </h3>
          <div class="task-list">
            {#each byStatus[group as 'doing' | 'todo' | 'done'] as t (t.id)}
              <div class="task-row" class:task-done={t.status === 'done'}>
                <button
                  class="task-check"
                  class:checked={t.status === 'done'}
                  disabled={busy}
                  onclick={() => openComplete(t)}
                  aria-label={`完成 ${t.title}`}
                >{t.status === 'done' ? '✓' : ''}</button>
                <div class="task-body">
                  <p class="task-title">{t.title}</p>
                  <p class="task-meta">
                    {t.skill_name ?? ''}
                    {#if t.due_date}· 截止 {t.due_date}{/if}
                  </p>
                </div>
                <Badge tone={taskTone(t.status)}>{taskLabel(t.status)}</Badge>
              </div>
            {/each}
          </div>
        {/if}
      {/each}
    </section>
  {/if}
</div>

{#if editingTask}
  <div class="modal-backdrop" role="dialog" aria-modal="true" aria-label="完成学习">
    <div class="modal">
      <h2 class="modal-title">完成学习</h2>
      <p class="modal-task">{editingTask.title}</p>
      <label class="modal-label" for="study-content">今天学到了什么？</label>
      <textarea
        id="study-content"
        class="modal-editor"
        bind:value={draft}
        placeholder="用 Markdown 记录今天的学习内容，保存后会自动生成博客草稿…"
        rows={7}
      ></textarea>
      <div class="modal-actions">
        <button class="btn-ghost" onclick={skipComplete} disabled={saving}>跳过</button>
        <button class="btn-save" onclick={saveLog} disabled={saving || !draft.trim()}>
          {saving ? '保存中…' : '保存学习记录'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .loading {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
    padding: var(--sp-6) 0;
  }
  .load-error {
    margin: var(--sp-6) 0;
    padding: var(--sp-4) var(--sp-5);
    background: #fee2e2;
    color: #b91c1c;
    border-radius: var(--r-md);
    font-weight: 600;
  }

  /* Hero */
  .learn-hero {
    margin: var(--sp-6) 0 var(--sp-7);
    padding: var(--sp-7);
    border-radius: 28px;
    background: var(--grad-hero);
    color: #fff;
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-6);
    position: relative;
    overflow: hidden;
  }
  .learn-hero::after {
    content: '';
    position: absolute;
    right: -80px;
    top: -80px;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.18), transparent 70%);
  }
  .lh-kicker {
    font-size: var(--fs-small);
    opacity: 0.75;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: var(--sp-2);
  }
  .lh-title {
    font-size: var(--fs-title);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: var(--sp-3);
  }
  .lh-stage-badge {
    display: inline-block;
    font-size: var(--fs-small);
    background: rgba(255, 255, 255, 0.16);
    padding: 4px 14px;
    border-radius: 999px;
    margin-bottom: var(--sp-4);
  }
  .lh-stats { font-size: var(--fs-small); opacity: 0.85; }
  .lh-stats strong { font-size: 1.1rem; }
  .lh-ring { text-align: center; flex-shrink: 0; position: relative; z-index: 1; }
  .ring-caption { margin-top: var(--sp-2); font-size: var(--fs-micro); opacity: 0.75; }

  /* 总体进度 */
  .overall { margin-bottom: var(--sp-7); }
  .overall-pct { font-size: var(--fs-h3); font-weight: 800; color: var(--c-primary); }
  .overall-bar {
    height: 12px;
    border-radius: 999px;
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    overflow: hidden;
  }
  .overall-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--grad-brand);
    transition: width 0.5s ease;
  }
  .overall-sub { margin-top: var(--sp-2); font-size: var(--fs-small); color: var(--c-text-2); }

  /* 当前任务 shelf */
  .current-block { margin-bottom: var(--sp-7); }
  .current-shelf {
    display: flex;
    gap: var(--sp-4);
    overflow-x: auto;
    padding-bottom: var(--sp-3);
  }
  .current-card {
    flex: 0 0 300px;
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: var(--sp-5);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }
  .cc-top { display: flex; align-items: center; justify-content: space-between; }
  .cc-skill { font-size: var(--fs-micro); color: var(--c-text-3); }
  .cc-title { font-size: var(--fs-h3); font-weight: 700; }
  .cc-desc { font-size: var(--fs-small); color: var(--c-text-2); }
  .cc-btn {
    margin-top: auto;
    padding: 8px 16px;
    border-radius: 999px;
    background: var(--grad-brand);
    color: #fff;
    font-weight: 600;
    font-size: var(--fs-small);
    transition: transform var(--t-fast);
  }
  .cc-btn:hover:not(:disabled) { transform: translateY(-1px); }
  .cc-btn:disabled { opacity: 0.6; cursor: not-allowed; }

  /* Task List */
  .task-list-block { margin-bottom: var(--sp-7); }
  .task-count { font-size: var(--fs-small); color: var(--c-text-3); }
  .group-title {
    font-size: var(--fs-h3);
    font-weight: 700;
    margin: var(--sp-5) 0 var(--sp-3);
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }
  .group-count {
    font-size: var(--fs-micro);
    color: var(--c-text-3);
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: 999px;
    padding: 0 8px;
  }
  .task-list { display: flex; flex-direction: column; gap: var(--sp-3); }
  .task-row {
    display: flex;
    align-items: center;
    gap: var(--sp-4);
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-md);
    padding: var(--sp-3) var(--sp-4);
    transition: background var(--t-fast);
  }
  .task-row:hover { background: var(--c-surface-2); }
  .task-check {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid var(--c-border);
    background: var(--c-surface);
    color: transparent;
    font-size: var(--fs-micro);
    font-weight: 700;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--t-fast);
  }
  .task-check:hover:not(:disabled) { border-color: var(--c-primary); }
  .task-check.checked {
    background: var(--grad-brand);
    border-color: transparent;
    color: #fff;
  }
  .task-check:disabled { opacity: 0.6; cursor: not-allowed; }
  .task-body { flex: 1; min-width: 0; }
  .task-title { font-weight: 600; }
  .task-done .task-title { text-decoration: line-through; color: var(--c-text-3); }
  .task-meta { font-size: var(--fs-micro); color: var(--c-text-3); margin-top: 2px; }

  @media (max-width: 768px) {
    .learn-hero { flex-direction: column; align-items: flex-start; padding: var(--sp-6); }
    .lh-ring { align-self: center; }
  }

  /* 完成学习 Modal */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 100;
    background: rgba(15, 17, 23, 0.45);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--sp-5);
  }
  .modal {
    width: min(560px, 100%);
    background: var(--c-surface);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-lg);
    padding: var(--sp-6);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }
  .modal-title { font-size: var(--fs-h2); font-weight: 800; letter-spacing: -0.02em; }
  .modal-task {
    font-size: var(--fs-body);
    color: var(--c-primary);
    font-weight: 700;
    background: var(--c-primary-soft);
    align-self: flex-start;
    padding: 4px 14px;
    border-radius: 999px;
  }
  .modal-label { font-size: var(--fs-small); font-weight: 600; color: var(--c-text-2); }
  .modal-editor {
    width: 100%;
    border: 1px solid var(--c-border);
    border-radius: var(--r-md);
    padding: var(--sp-3) var(--sp-4);
    font-size: var(--fs-body);
    line-height: 1.6;
    resize: vertical;
    background: var(--c-surface-2);
    color: var(--c-text);
    outline: none;
  }
  .modal-editor:focus { border-color: var(--c-primary); }
  .modal-actions { display: flex; justify-content: flex-end; gap: var(--sp-3); margin-top: var(--sp-2); }
  .btn-ghost {
    padding: 10px 22px;
    border-radius: 999px;
    border: 1px solid var(--c-border);
    color: var(--c-text-2);
    font-weight: 600;
    font-size: var(--fs-body);
    transition: background var(--t-fast);
  }
  .btn-ghost:hover:not(:disabled) { background: var(--c-surface-2); }
  .btn-save {
    padding: 10px 24px;
    border-radius: 999px;
    background: var(--grad-brand);
    color: #fff;
    font-weight: 600;
    font-size: var(--fs-body);
    box-shadow: var(--shadow-md);
    transition: transform var(--t-fast), opacity var(--t-fast);
  }
  .btn-save:hover:not(:disabled) { transform: translateY(-1px); }
  .btn-save:disabled, .btn-ghost:disabled { opacity: 0.55; cursor: not-allowed; }
</style>
