<script lang="ts">
  import TaskItem from '../shared/TaskItem.svelte';
  import type { Task } from '../../lib/api';

  let {
    tasks,
    onToggle,
  }: {
    tasks: Task[];
    onToggle?: (task: Task, done: boolean) => void;
  } = $props();

  const sorted = $derived(
    [...tasks].sort(
      (a, b) => b.priority - a.priority || (a.due_date ?? '').localeCompare(b.due_date ?? '')
    )
  );
</script>

<section class="today">
  <div class="section-head">
    <h2 class="section-title">Today's Tasks</h2>
    <a class="section-link" href="#/tasks">全部任务 →</a>
  </div>

  <div class="task-list">
    {#if sorted.length === 0}
      <div class="today-empty">今天已清空 🎉 可以休息或规划明天</div>
    {:else}
      {#each sorted as t (t.id)}
        <TaskItem task={t} onToggle={onToggle} />
      {/each}
    {/if}
    <button class="add-task">+ 添加任务</button>
  </div>
</section>

<style>
  .today { flex: 1; min-width: 0; }
  .task-list { display: flex; flex-direction: column; gap: var(--sp-3); }
  .today-empty {
    padding: var(--sp-5);
    text-align: center;
    color: var(--c-text-2);
    background: var(--c-surface);
    border: 1px dashed var(--c-border);
    border-radius: var(--r-lg);
  }
  .add-task {
    padding: var(--sp-3);
    border-radius: var(--r-md);
    border: 1px dashed var(--c-border);
    color: var(--c-primary);
    font-weight: 600;
    font-size: var(--fs-small);
    transition: background var(--t-fast);
  }
  .add-task:hover { background: var(--c-primary-soft); }
</style>
