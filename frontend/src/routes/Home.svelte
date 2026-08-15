<script lang="ts">
  import { mockDashboard } from '../lib/mock';
  import Hero from '../components/home/Hero.svelte';
  import ContinueLearning from '../components/home/ContinueLearning.svelte';
  import LearningProgress from '../components/home/LearningProgress.svelte';
  import FeaturedProjects from '../components/home/FeaturedProjects.svelte';
  import TodayTasks from '../components/home/TodayTasks.svelte';
  import RecentActivity from '../components/home/RecentActivity.svelte';
  import CareerStatus from '../components/home/CareerStatus.svelte';

  const d = mockDashboard;
</script>

<div class="page">
  {#if d.hero}
    <Hero hero={d.hero} />
  {/if}

  <ContinueLearning tasks={d.continue_learning} />
  <LearningProgress skills={d.learning_progress} />

  <FeaturedProjects projects={d.featured_projects} />

  <div class="two-col">
    <TodayTasks tasks={d.today_tasks} />
    <RecentActivity logs={d.recent_activity} />
  </div>

  <CareerStatus stats={d.career_status} />
</div>

<style>
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--sp-5);
    margin-bottom: var(--sp-7);
    align-items: start;
  }
  @media (max-width: 900px) {
    .two-col { grid-template-columns: 1fr; }
  }
</style>
