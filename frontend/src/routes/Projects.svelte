<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Project, type ProjectListData } from '../lib/api';
  import Badge from '../components/shared/Badge.svelte';

  let data = $state<ProjectListData | null>(null);
  let error = $state('');
  let loading = $state(true);

  onMount(load);

  async function load() {
    loading = true;
    try {
      data = await api.get<{ data: ProjectListData }>('/api/projects').then((r) => r.data);
      error = '';
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    } finally {
      loading = false;
    }
  }

  const statusTone = (s: string) =>
    ({ active: 'accent', done: 'primary', paused: 'neutral', planning: 'neutral', archived: 'neutral' })[s] ?? 'neutral';
  const statusLabel = (s: string) =>
    ({ active: '进行中', done: '已完成', paused: '暂停', planning: '规划中', archived: '已归档' })[s] ?? s;

  const featured = $derived(data?.projects.filter((p) => p.featured) ?? []);
  const grid = $derived(data?.projects ?? []);
</script>

<div class="page">
  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}</div>
  {:else if loading}
    <div class="loading">
      <div class="skeleton" style="height:200px; border-radius:28px;"></div>
      <div class="skeleton" style="height:120px;"></div>
      <div class="skeleton" style="height:240px;"></div>
    </div>
  {:else if data}
    <!-- Hero: 我的项目 -->
    <section class="proj-hero">
      <p class="ph-kicker">Projects · 项目</p>
      <h1 class="ph-title">我的项目</h1>
      <p class="ph-sub">证据驱动的项目库 — 每个项目都沉淀了可复述的技术证据与面试问答</p>
    </section>

    <!-- 统计 -->
    <section class="block">
      <div class="stat-grid">
        <div class="stat-card"><span class="stat-num">{data.stats.total}</span><span class="stat-lbl">项目数量</span></div>
        <div class="stat-card good"><span class="stat-num">{data.stats.done}</span><span class="stat-lbl">完成项目</span></div>
        <div class="stat-card accent"><span class="stat-num">{data.stats.tech_stacks}</span><span class="stat-lbl">技术栈</span></div>
        <div class="stat-card"><span class="stat-num">{data.stats.milestones}</span><span class="stat-lbl">里程碑</span></div>
      </div>
    </section>

    <!-- Featured Project -->
    {#if featured.length > 0}
      <section class="block">
        <div class="section-head">
          <h2 class="section-title">Featured Project</h2>
        </div>
        {#each featured as p (p.id)}
          <a class="featured-card" href={`#/projects/${p.id}`}>
            <div class="fc-copy">
              <Badge tone="dark">{p.name}</Badge>
              <h3 class="fc-title">{p.name}</h3>
              <p class="fc-desc">{p.description ?? ''}</p>
              <p class="fc-stack">{p.tech_stack ?? ''}</p>
              <p class="fc-evidence">{p.evidence_count} 条技术证据 · {statusLabel(p.status)}</p>
            </div>
            <div class="fc-progress">
              <span class="fc-pct">{p.progress}%</span>
              <div class="fc-bar"><div class="fc-fill" style={`width: ${p.progress}%`}></div></div>
              <span class="fc-link">查看详情 →</span>
            </div>
          </a>
        {/each}
      </section>
    {/if}

    <!-- Project Grid -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Project Grid</h2>
      </div>
      {#if grid.length === 0}
        <div class="empty-note">暂无项目</div>
      {:else}
        <div class="proj-grid">
          {#each grid as p (p.id)}
            <a class="proj-card" href={`#/projects/${p.id}`}>
              <div class="pc-top">
                <Badge tone={statusTone(p.status)}>{statusLabel(p.status)}</Badge>
                <span class="pc-ev">{p.evidence_count} 证据</span>
              </div>
              <h3 class="pc-name">{p.name}</h3>
              <p class="pc-desc">{p.description ?? ''}</p>
              <p class="pc-stack">{p.tech_stack ?? ''}</p>
              <div class="pc-progress">
                <div class="pc-bar"><div class="pc-fill" style={`width: ${p.progress}%`}></div></div>
                <span class="pc-pct">{p.progress}%</span>
              </div>
            </a>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</div>

<style>
  .loading { display: flex; flex-direction: column; gap: var(--sp-5); padding: var(--sp-6) 0; }
  .load-error { margin: var(--sp-6) 0; padding: var(--sp-4) var(--sp-5); background: #fee2e2; color: #b91c1c; border-radius: var(--r-md); font-weight: 600; }
  .block { margin-bottom: var(--sp-7); }
  .empty-note { padding: var(--sp-5); border: 1px dashed var(--c-border); border-radius: var(--r-lg); color: var(--c-text-2); text-align: center; }

  .proj-hero { margin: var(--sp-6) 0 var(--sp-7); padding: var(--sp-7); border-radius: 28px; background: var(--grad-hero); color: #fff; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; }
  .proj-hero::after { content: ''; position: absolute; right: -60px; top: -60px; width: 260px; height: 260px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%); }
  .ph-kicker { font-size: var(--fs-small); opacity: 0.75; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: var(--sp-2); }
  .ph-title { font-size: var(--fs-title); font-weight: 800; letter-spacing: -0.03em; margin-bottom: var(--sp-2); }
  .ph-sub { font-size: var(--fs-body); opacity: 0.85; }

  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--sp-4); }
  .stat-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-5); text-align: center; box-shadow: var(--shadow-sm); }
  .stat-card.accent { border-color: var(--c-primary); }
  .stat-card.good { border-color: #d1fae5; }
  .stat-num { display: block; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; }
  .stat-card.accent .stat-num { color: var(--c-primary); }
  .stat-card.good .stat-num { color: #047857; }
  .stat-lbl { font-size: var(--fs-small); color: var(--c-text-2); }

  .featured-card {
    display: flex; align-items: center; justify-content: space-between; gap: var(--sp-6);
    background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg);
    padding: var(--sp-6); box-shadow: var(--shadow-md); transition: transform var(--t-fast), box-shadow var(--t-med);
  }
  .featured-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
  .fc-copy { flex: 1; }
  .fc-title { font-size: var(--fs-h2); font-weight: 800; margin: var(--sp-2) 0; }
  .fc-desc { color: var(--c-text-2); margin-bottom: var(--sp-2); }
  .fc-stack { font-size: var(--fs-small); color: var(--c-primary); font-weight: 600; }
  .fc-evidence { font-size: var(--fs-micro); color: var(--c-text-3); margin-top: var(--sp-2); }
  .fc-progress { text-align: center; flex-shrink: 0; width: 160px; }
  .fc-pct { display: block; font-size: 1.8rem; font-weight: 800; color: var(--c-primary); }
  .fc-bar { height: 8px; border-radius: 999px; background: var(--c-bg); overflow: hidden; margin: var(--sp-2) 0; }
  .fc-fill { height: 100%; background: var(--grad-brand); border-radius: 999px; }
  .fc-link { font-size: var(--fs-small); font-weight: 600; color: var(--c-primary); }

  .proj-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--sp-4); }
  .proj-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-5); box-shadow: var(--shadow-sm); transition: transform var(--t-fast), box-shadow var(--t-med); }
  .proj-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
  .pc-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--sp-3); }
  .pc-ev { font-size: var(--fs-micro); color: var(--c-text-3); }
  .pc-name { font-size: var(--fs-h3); font-weight: 700; margin-bottom: var(--sp-2); }
  .pc-desc { font-size: var(--fs-small); color: var(--c-text-2); min-height: 2.4em; margin-bottom: var(--sp-2); }
  .pc-stack { font-size: var(--fs-micro); color: var(--c-text-3); margin-bottom: var(--sp-3); }
  .pc-progress { display: flex; align-items: center; gap: var(--sp-3); }
  .pc-bar { flex: 1; height: 6px; border-radius: 999px; background: var(--c-bg); overflow: hidden; }
  .pc-fill { height: 100%; background: var(--grad-brand); border-radius: 999px; }
  .pc-pct { font-size: var(--fs-micro); font-weight: 700; color: var(--c-text-2); }

  @media (max-width: 768px) {
    .featured-card { flex-direction: column; align-items: flex-start; }
    .fc-progress { width: 100%; }
  }
</style>
