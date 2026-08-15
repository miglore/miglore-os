<script lang="ts">
  import Shelf from '../shared/Shelf.svelte';
  import Badge from '../shared/Badge.svelte';
  import type { Task } from '../../lib/api';

  let { tasks }: { tasks: Task[] } = $props();
</script>

<Shelf title="Continue Learning" link="查看全部" linkHref="#/learning">
  {#if tasks.length === 0}
    <div class="empty-note">暂无学习任务，去「学习」页添加吧 →</div>
  {/if}
  {#each tasks as t (t.id)}
    <article class="learn-card">
      <div class="learn-head">
        <Badge tone={t.status === 'in_progress' ? 'primary' : 'neutral'}>
          {t.status === 'in_progress' ? '进行中' : '待开始'}
        </Badge>
        <span class="learn-due">{t.due_date ?? ''}</span>
      </div>
      <h3 class="learn-title">{t.title}</h3>
      <p class="learn-track">{t.track_name ?? ''}</p>
      <a class="learn-cta" href="#/learning">
        {t.status === 'in_progress' ? '继续学习' : '开始学习'} →
      </a>
    </article>
  {/each}
</Shelf>

<style>
  .empty-note {
    width: 320px;
    padding: var(--sp-5);
    border: 1px dashed var(--c-border);
    border-radius: var(--r-lg);
    color: var(--c-text-2);
    text-align: center;
  }
  .learn-card {
    width: 260px;
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
  .learn-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
  .learn-head { display: flex; align-items: center; justify-content: space-between; }
  .learn-due { font-size: var(--fs-micro); color: var(--c-text-3); }
  .learn-title { font-size: var(--fs-h3); font-weight: 700; letter-spacing: -0.01em; line-height: 1.4; }
  .learn-track { font-size: var(--fs-micro); color: var(--c-text-2); }
  .learn-cta {
    margin-top: auto;
    font-size: var(--fs-small);
    font-weight: 600;
    color: var(--c-primary);
  }
  .learn-cta:hover { color: var(--c-primary-2); }
</style>
