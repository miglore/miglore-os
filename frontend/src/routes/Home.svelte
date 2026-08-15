<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type DashboardData, type Task } from '../lib/api';
  import Hero from '../components/home/Hero.svelte';
  import ContinueLearning from '../components/home/ContinueLearning.svelte';
  import LearningProgress from '../components/home/LearningProgress.svelte';
  import FeaturedProjects from '../components/home/FeaturedProjects.svelte';
  import TodayTasks from '../components/home/TodayTasks.svelte';
  import RecentActivity from '../components/home/RecentActivity.svelte';
  import CareerStatus from '../components/home/CareerStatus.svelte';

  let d = $state<DashboardData | null>(null);
  let error = $state('');
  let toggling = $state(false);

  onMount(load);

  async function load() {
    try {
      d = await api.get<{ data: DashboardData }>('/api/dashboard').then((r) => r.data);
      error = '';
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    }
  }

  // 任务勾选 → 后端 PATCH → 重新拉取 dashboard 保持全局一致
  async function handleTaskToggle(task: Task, done: boolean) {
    if (toggling) return;
    toggling = true;
    try {
      await api.patch(`/api/tasks/${task.id}`, { status: done ? 'done' : 'todo' });
      await load();
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
      await load(); // 回滚
    } finally {
      toggling = false;
    }
  }
</script>

<div class="page">
  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}</div>
  {:else if !d}
    <div class="loading">
      <div class="skeleton" style="height:260px; border-radius:28px;"></div>
      <div class="skeleton" style="height:120px;"></div>
      <div class="skeleton" style="height:180px;"></div>
    </div>
  {:else}
    {#if d.hero}
      <Hero hero={d.hero} />
    {/if}

    <ContinueLearning tasks={d.continue_learning} />
    <LearningProgress skills={d.learning_progress} />

    <FeaturedProjects projects={d.featured_projects} />

    <div class="two-col">
      <TodayTasks tasks={d.today_tasks} onToggle={handleTaskToggle} />
      <RecentActivity logs={d.recent_activity} />
    </div>

    <CareerStatus stats={d.career_status} />
  {/if}
</div>

<style>
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--sp-5);
    margin-bottom: var(--sp-7);
    align-items: start;
  }
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
  @media (max-width: 900px) {
    .two-col { grid-template-columns: 1fr; }
  }
</style>
