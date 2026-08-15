<script lang="ts">
  import type { Task } from '../../lib/api';

  let {
    task,
    onToggle,
  }: {
    task: Task;
    onToggle?: (task: Task, done: boolean) => void;
  } = $props();
  // 本地勾选状态：初始取任务状态；仅当 task.status 变化时同步（用户手动勾选不被覆盖）
  let done = $state(false);
  $effect(() => {
    done = task.status === 'done';
  });

  function handleChange() {
    const next = !done;
    done = next; // 乐观更新，父组件负责调用后端 PATCH
    onToggle?.(task, next);
  }

  const prioLabel = $derived(task.priority === 3 ? '高' : task.priority === 2 ? '中' : '低');
  const prioClass = $derived(
    task.priority === 3 ? 'p-high' : task.priority === 2 ? 'p-mid' : 'p-low'
  );
  const meta = $derived(task.track_name ?? '');
</script>

<label class="task-item" class:done>
  <input type="checkbox" checked={done} onchange={handleChange} />
  <span class="task-title">{task.title}</span>
  {#if meta}<span class="task-meta">{meta}</span>{/if}
  <span class="badge {prioClass}">{prioLabel}</span>
</label>

<style>
  .task-item {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-3) var(--sp-4);
    border-radius: var(--r-md);
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    cursor: pointer;
    transition: background var(--t-fast);
  }
  .task-item:hover { background: var(--c-surface-2); }
  .task-item input { width: 18px; height: 18px; accent-color: var(--c-primary); cursor: pointer; }
  .task-title { flex: 1; font-weight: 500; }
  .task-meta { font-size: var(--fs-micro); color: var(--c-text-3); background: var(--c-bg); padding: 2px 8px; border-radius: 999px; }
  .done .task-title { text-decoration: line-through; color: var(--c-text-3); }
  .p-high { background: #fee2e2; color: #b91c1c; }
  .p-mid  { background: #fef3c7; color: #b45309; }
  .p-low  { background: #eef0f6; color: var(--c-text-2); }
</style>
