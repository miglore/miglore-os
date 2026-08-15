<script lang="ts">
  import type { StudyLog } from '../../lib/types';

  let { logs }: { logs: StudyLog[] } = $props();

  const rel = (d: string) => {
    const diff = Math.floor(
      (new Date().setHours(0, 0, 0, 0) - new Date(d).setHours(0, 0, 0, 0)) / 86400000
    );
    if (diff === 0) return '今天';
    if (diff === 1) return '昨天';
    return `${diff} 天前`;
  };
</script>

<section class="recent">
  <div class="section-head">
    <h2 class="section-title">Recent Activity</h2>
    <a class="section-link" href="#/journal">查看日志 →</a>
  </div>

  <ol class="timeline">
    {#each logs as l (l.id)}
      <li class="tl-item">
        <span class="tl-dot"></span>
        <div class="tl-body">
          <div class="tl-meta">
            <span class="tl-when">{rel(l.log_date)}</span>
            {#if l.duration_min}<span class="tl-dur">⏱ {l.duration_min}min</span>{/if}
          </div>
          <p class="tl-content">{l.content}</p>
        </div>
      </li>
    {/each}
  </ol>
</section>

<style>
  .recent { flex: 1; min-width: 0; }
  .timeline {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }
  .tl-item {
    display: flex;
    gap: var(--sp-3);
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-md);
    padding: var(--sp-3) var(--sp-4);
  }
  .tl-dot {
    flex-shrink: 0;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--grad-brand);
    margin-top: 7px;
  }
  .tl-meta { display: flex; gap: var(--sp-3); align-items: center; }
  .tl-when { font-size: var(--fs-micro); font-weight: 700; color: var(--c-primary); }
  .tl-dur { font-size: var(--fs-micro); color: var(--c-text-3); }
  .tl-content {
    font-size: var(--fs-small);
    color: var(--c-text-2);
    line-height: 1.55;
    margin-top: 2px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
