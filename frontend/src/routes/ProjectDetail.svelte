<script lang="ts">
  import { onMount } from 'svelte';
  import {
    api,
    type ProjectDetailData,
    type Evidence,
    type Milestone,
  } from '../lib/api';
  import Badge from '../components/shared/Badge.svelte';

  let { projectId }: { projectId: number } = $props();

  let data = $state<ProjectDetailData | null>(null);
  let error = $state('');
  let loading = $state(true);

  onMount(load);

  async function load() {
    loading = true;
    error = '';
    try {
      data = await api.get<{ data: ProjectDetailData }>(`/api/projects/${projectId}`).then((r) => r.data);
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    } finally {
      loading = false;
    }
  }

  const chips = $derived(
    (data?.project.tech_stack ?? '').split('·').map((t) => t.trim()).filter(Boolean)
  );

  const catLabel = (c: string) =>
    ({ architecture: '架构', linux: 'Linux', docker: 'Docker', network: '网络', ci_cd: 'CI/CD', monitoring: '监控', database: '数据库', security: '安全', troubleshooting: '故障排查' })[c] ?? c;
  const msTone = (s: Milestone['status']) => ({ done: 'accent', current: 'primary', todo: 'neutral' })[s];
  const msLabel = (s: Milestone['status']) => ({ done: '完成', current: '进行中', todo: '待开始' })[s] ?? s;
  const statusLabel = (s: string) =>
    ({ active: '进行中', done: '已完成', paused: '暂停', planning: '规划中', archived: '已归档' })[s] ?? s;
</script>

<div class="page">
  <a class="back" href="#/projects">← 返回项目</a>

  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}（项目不存在或已被删除）</div>
  {:else if loading}
    <div class="loading">
      <div class="skeleton" style="height:200px; border-radius:28px;"></div>
      <div class="skeleton" style="height:160px;"></div>
      <div class="skeleton" style="height:240px;"></div>
    </div>
  {:else if data}
    <!-- 1. Overview -->
    <section class="pd-hero">
      <div class="pd-copy">
        <p class="pd-kicker">Project Detail</p>
        <h1 class="pd-title">{data.project.name}</h1>
        <p class="pd-desc">{data.project.description ?? ''}</p>
        <div class="pd-chips">
          {#each chips as c (c)}
            <span class="pd-chip">{c}</span>
          {/each}
        </div>
      </div>
      <div class="pd-progress">
        <span class="pd-pct">{data.project.progress}%</span>
        <div class="pd-bar"><div class="pd-fill" style={`width: ${data.project.progress}%`}></div></div>
        <Badge tone="dark">{statusLabel(data.project.status)}</Badge>
      </div>
    </section>

    <!-- 2. Milestones -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Milestones</h2>
      </div>
      {#if data.milestones.length === 0}
        <div class="empty-note">暂无里程碑</div>
      {:else}
        <div class="ms-list">
          {#each data.milestones as m (m.id)}
            <div class="ms-row" class:ms-current={m.status === 'current'}>
              <span class="ms-dot" class:ms-dot-current={m.status === 'current'}></span>
              <span class="ms-title">{m.title}</span>
              <Badge tone={msTone(m.status)}>{msLabel(m.status)}</Badge>
              {#if m.achieved_at}<span class="ms-date">{m.achieved_at}</span>{/if}
            </div>
          {/each}
        </div>
      {/if}
    </section>

    <!-- 3. Technical Evidence -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Technical Evidence</h2>
        <span class="count">{data.evidence.length} 条</span>
      </div>
      {#if data.evidence.length === 0}
        <div class="empty-note">暂无技术证据</div>
      {:else}
        <div class="ev-list">
          {#each data.evidence as e (e.id)}
            <details class="ev-card">
              <summary class="ev-head">
                <span class="ev-title">{e.title}</span>
                <Badge tone="primary">{catLabel(e.category)}</Badge>
                <span class="ev-toggle">▾</span>
              </summary>
              <div class="ev-body">
                  {#if e.description}<p class="ev-desc"><strong>做了什么：</strong>{e.description}</p>{/if}
                  {#if e.technical_detail}<p class="ev-tech"><strong>技术细节：</strong>{e.technical_detail}</p>{/if}
                  {#if e.result}<p class="ev-result"><strong>结果：</strong>{e.result}</p>{/if}

                  {#if (e.interviews ?? []).length > 0}
                    <div class="ivw-box">
                      <p class="ivw-box-title">Interview Evidence</p>
                      {#each (e.interviews ?? []) as iv (iv.id)}
                        <div class="ivw-item">
                          <p class="ivw-q">Q：{iv.question}</p>
                          <p class="ivw-a">A：{iv.answer}</p>
                          {#if iv.skill_name}<span class="ivw-skill">#{iv.skill_name}</span>{/if}
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
            </details>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</div>

<style>
  .back { display: inline-block; margin: var(--sp-5) 0 var(--sp-2); font-size: var(--fs-small); color: var(--c-primary); font-weight: 600; }
  .loading { display: flex; flex-direction: column; gap: var(--sp-5); padding: var(--sp-4) 0; }
  .load-error { margin: var(--sp-6) 0; padding: var(--sp-4) var(--sp-5); background: #fee2e2; color: #b91c1c; border-radius: var(--r-md); font-weight: 600; }
  .block { margin-bottom: var(--sp-7); }
  .empty-note { padding: var(--sp-5); border: 1px dashed var(--c-border); border-radius: var(--r-lg); color: var(--c-text-2); text-align: center; }
  .count { font-size: var(--fs-small); color: var(--c-text-3); }

  .pd-hero {
    margin: var(--sp-4) 0 var(--sp-7); padding: var(--sp-7);
    border-radius: 28px; background: var(--grad-hero); color: #fff; box-shadow: var(--shadow-lg);
    display: flex; align-items: center; justify-content: space-between; gap: var(--sp-6); position: relative; overflow: hidden;
  }
  .pd-hero::after { content: ''; position: absolute; right: -60px; top: -60px; width: 260px; height: 260px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%); }
  .pd-kicker { font-size: var(--fs-small); opacity: 0.75; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: var(--sp-2); }
  .pd-title { font-size: var(--fs-title); font-weight: 800; letter-spacing: -0.03em; margin-bottom: var(--sp-2); }
  .pd-desc { font-size: var(--fs-body); opacity: 0.85; max-width: 560px; margin-bottom: var(--sp-4); }
  .pd-chips { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
  .pd-chip { background: rgba(255,255,255,0.16); padding: 3px 12px; border-radius: 999px; font-size: var(--fs-micro); }
  .pd-progress { text-align: center; flex-shrink: 0; width: 170px; position: relative; z-index: 1; }
  .pd-pct { display: block; font-size: 1.8rem; font-weight: 800; margin-bottom: var(--sp-2); }
  .pd-bar { height: 8px; border-radius: 999px; background: rgba(255,255,255,0.25); overflow: hidden; margin-bottom: var(--sp-3); }
  .pd-fill { height: 100%; background: #fff; border-radius: 999px; }

  .ms-list { display: flex; flex-direction: column; gap: var(--sp-3); }
  .ms-row { display: flex; align-items: center; gap: var(--sp-3); background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
  .ms-row.ms-current { border-color: var(--c-primary); }
  .ms-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--c-accent); }
  .ms-dot.ms-dot-current { background: var(--c-primary); box-shadow: 0 0 0 4px var(--c-primary-soft); }
  .ms-title { flex: 1; font-weight: 600; }
  .ms-date { font-size: var(--fs-micro); color: var(--c-text-3); }

  .ev-list { display: flex; flex-direction: column; gap: var(--sp-3); }
  .ev-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-md); overflow: hidden; }
  .ev-head { width: 100%; display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5); cursor: pointer; list-style: none; text-align: left; }
  .ev-head::-webkit-details-marker { display: none; }
  .ev-head:hover { background: var(--c-surface-2); }
  .ev-title { flex: 1; font-weight: 700; font-size: var(--fs-body); }
  .ev-toggle { color: var(--c-text-3); transition: transform var(--t-fast); }
  details[open] .ev-toggle { transform: rotate(180deg); }
  .ev-body { padding: 0 var(--sp-5) var(--sp-5); display: flex; flex-direction: column; gap: var(--sp-3); }
  .ev-desc, .ev-tech, .ev-result { font-size: var(--fs-small); color: var(--c-text-2); line-height: 1.6; }
  .ev-tech { color: var(--c-text); background: var(--c-surface-2); border-radius: var(--r-sm); padding: var(--sp-3); }
  .ev-result { color: #047857; }
  .ivw-box { border-top: 1px dashed var(--c-border); padding-top: var(--sp-3); }
  .ivw-box-title { font-size: var(--fs-micro); font-weight: 700; color: var(--c-primary); margin-bottom: var(--sp-2); }
  .ivw-item { background: var(--c-surface-2); border-radius: var(--r-sm); padding: var(--sp-3); margin-bottom: var(--sp-2); }
  .ivw-q { font-weight: 600; font-size: var(--fs-small); margin-bottom: 4px; }
  .ivw-a { font-size: var(--fs-small); color: var(--c-text-2); line-height: 1.6; }
  .ivw-skill { display: inline-block; margin-top: var(--sp-2); font-size: var(--fs-micro); color: var(--c-primary); background: var(--c-primary-soft); padding: 2px 10px; border-radius: 999px; }

  @media (max-width: 768px) {
    .pd-hero { flex-direction: column; align-items: flex-start; padding: var(--sp-6); }
    .pd-progress { width: 100%; }
  }
</style>
