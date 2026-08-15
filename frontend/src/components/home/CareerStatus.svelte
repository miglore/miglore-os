<script lang="ts">
  let {
    stats,
  }: {
    stats: { label: string; value: number }[] | Record<string, never>;
  } = $props();

  const hasStats = $derived(Array.isArray(stats) && stats.length > 0);
  const list = $derived(Array.isArray(stats) ? (stats as { label: string; value: number }[]) : []);
</script>

<section class="career">
  <div class="section-head">
    <h2 class="section-title">Career Status</h2>
    <a class="section-link" href="#/career">求职 →</a>
  </div>

  {#if !hasStats}
    <div class="career-panel career-empty">
      <p class="career-empty-title">求职模块开发中</p>
      <p class="career-empty-sub">投递方向 · 投递记录 · 面试记录（V1.1 支持）</p>
    </div>
  {:else}
    <div class="career-panel">
      <div class="career-dir">
        <span class="dir-dot"></span>
        <div>
          <p class="dir-name">DevOps / 运维开发</p>
          <p class="dir-sub">投递方向 · 进行中</p>
        </div>
      </div>
      <div class="career-stats">
        {#each list as s (s.label)}
          <div class="stat">
            <span class="stat-value">{s.value}</span>
            <span class="stat-label">{s.label}</span>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</section>

<style>
  .career { margin-bottom: var(--sp-6); }
  .career-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-5);
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: var(--sp-5) var(--sp-6);
    box-shadow: var(--shadow-sm);
    flex-wrap: wrap;
  }
  .career-dir { display: flex; align-items: center; gap: var(--sp-3); }
  .dir-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--c-accent);
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
  }
  .dir-name { font-weight: 700; font-size: 1.05rem; }
  .dir-sub { font-size: var(--fs-micro); color: var(--c-text-3); }
  .career-stats { display: flex; gap: var(--sp-6); }
  .stat { text-align: center; min-width: 64px; }
  .stat-value { display: block; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: var(--c-text); }
  .stat-label { font-size: var(--fs-micro); color: var(--c-text-3); }

  @media (max-width: 768px) {
    .career-panel { flex-direction: column; align-items: flex-start; }
    .career-stats { width: 100%; justify-content: space-between; }
  }
</style>
