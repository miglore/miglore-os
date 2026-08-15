<script lang="ts">
  import Badge from '../shared/Badge.svelte';
  import type { Project } from '../../lib/types';

  let { projects }: { projects: Project[] } = $props();

  const statusTone = (s: Project['status']) =>
    s === 'active' ? 'accent' : s === 'done' ? 'primary' : 'neutral';
  const statusLabel = (s: Project['status']) =>
    ({ active: '进行中', paused: '暂停', done: '已完成', planning: '规划中', archived: '已归档' })[s];
</script>

<section class="featured">
  <div class="section-head">
    <h2 class="section-title">Featured Projects</h2>
    <a class="section-link" href="#/projects">全部项目 →</a>
  </div>
  <div class="proj-grid">
    {#each projects as p (p.id)}
      <a class="proj-card" href="#/projects">
        <div class="proj-top">
          <Badge tone={statusTone(p.status)}>{statusLabel(p.status)}</Badge>
          <span class="proj-stack">{p.tech_stack}</span>
        </div>
        <h3 class="proj-name">{p.name}</h3>
        <p class="proj-desc">{p.description}</p>
        <div class="proj-progress">
          <div class="proj-bar"><div class="proj-fill" style={`width: ${p.progress}%`}></div></div>
          <span class="proj-pct">{p.progress}%</span>
        </div>
      </a>
    {/each}
  </div>
</section>

<style>
  .featured { margin-bottom: var(--sp-7); }
  .proj-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--sp-4);
  }
  .proj-card {
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: var(--sp-5);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    transition: transform var(--t-fast), box-shadow var(--t-med);
  }
  .proj-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
  .proj-top { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-2); }
  .proj-stack { font-size: var(--fs-micro); color: var(--c-text-3); }
  .proj-name { font-size: var(--fs-h3); font-weight: 700; letter-spacing: -0.01em; }
  .proj-desc {
    font-size: var(--fs-small);
    color: var(--c-text-2);
    line-height: 1.55;
    min-height: 2.4em;
  }
  .proj-progress { display: flex; align-items: center; gap: var(--sp-3); margin-top: auto; }
  .proj-bar { flex: 1; height: 6px; border-radius: 999px; background: var(--c-bg); overflow: hidden; }
  .proj-fill { height: 100%; border-radius: 999px; background: var(--grad-brand); }
  .proj-pct { font-size: var(--fs-micro); font-weight: 700; color: var(--c-text-2); }
</style>
