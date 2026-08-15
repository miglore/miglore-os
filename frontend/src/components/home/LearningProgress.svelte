<script lang="ts">
  import Shelf from '../shared/Shelf.svelte';
  import type { Skill } from '../../lib/api';

  let { skills }: { skills: Skill[] } = $props();
</script>

<Shelf title="Learning Progress" link="技能清单" linkHref="#/learning">
  {#if skills.length === 0}
    <div class="empty-note">暂无技能数据</div>
  {/if}
  {#each skills as s (s.id)}
    <div class="skill-card">
      <div class="skill-head">
        <span class="skill-name">{s.name}</span>
        <span class="skill-score">{s.level}/{s.target_level}</span>
      </div>
      <div class="skill-bar">
        <div class="skill-fill" style={`width: ${(s.level / s.target_level) * 100}%`}></div>
      </div>
      <span class="skill-status">
        {s.status === 'learning' ? '学习中' : s.status === 'learned' ? '已掌握' : '暂缓'}
      </span>
    </div>
  {/each}
</Shelf>

<style>
  .skill-card {
    width: 200px;
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: var(--sp-5);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }
  .skill-head { display: flex; align-items: baseline; justify-content: space-between; }
  .skill-name { font-weight: 700; font-size: var(--fs-h3); }
  .skill-score { font-size: var(--fs-micro); color: var(--c-primary); font-weight: 700; }
  .skill-bar {
    height: 8px;
    border-radius: 999px;
    background: var(--c-bg);
    overflow: hidden;
  }
  .skill-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--grad-brand);
    transition: width var(--t-med);
  }
  .skill-status { font-size: var(--fs-micro); color: var(--c-text-3); }
</style>
