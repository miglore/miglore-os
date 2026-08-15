<script lang="ts">
  import ProgressRing from '../shared/ProgressRing.svelte';
  import Badge from '../shared/Badge.svelte';
  import type { DashboardData } from '../../lib/types';

  let { hero }: { hero: NonNullable<DashboardData['hero']> } = $props();
</script>

<section class="hero">
  <div class="hero-top">
    <span class="hero-date">{hero.date} · {hero.weekday}</span>
    <Badge tone="dark">🔥 连续学习 {hero.streak_days} 天</Badge>
  </div>

  <div class="hero-main">
    <div class="hero-copy">
      <p class="hero-kicker">职业目标</p>
      <h1 class="hero-title">{hero.career_goal}</h1>
      <p class="hero-track">
        <span class="track-name">{hero.active_track.title}</span>
        <span class="track-stage">{hero.active_track.stage}</span>
      </p>
      <a class="btn-primary" href="#/learning">继续学习 →</a>
    </div>

    <div class="hero-ring">
      <ProgressRing value={hero.active_track.progress} size={132} stroke={10} />
      <div class="ring-caption">当前路线进度</div>
    </div>
  </div>
</section>

<style>
  .hero {
    margin: var(--sp-6) 0 var(--sp-7);
    padding: var(--sp-7);
    border-radius: 28px;
    background: var(--grad-hero);
    color: #fff;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
  }
  .hero::after {
    content: '';
    position: absolute;
    right: -80px;
    top: -80px;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.18), transparent 70%);
  }
  .hero-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--sp-6);
  }
  .hero-date { font-size: var(--fs-small); opacity: 0.85; font-weight: 500; }
  .hero-main {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-6);
    position: relative;
    z-index: 1;
  }
  .hero-kicker {
    font-size: var(--fs-small);
    opacity: 0.75;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: var(--sp-2);
  }
  .hero-title {
    font-size: var(--fs-title);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: var(--sp-4);
  }
  .hero-track { display: flex; align-items: center; gap: var(--sp-3); margin-bottom: var(--sp-6); }
  .track-name { font-weight: 600; font-size: 1.05rem; }
  .track-stage { font-size: var(--fs-small); opacity: 0.8; background: rgba(255,255,255,0.16); padding: 3px 12px; border-radius: 999px; }
  .hero-ring { text-align: center; flex-shrink: 0; }
  .ring-caption { margin-top: var(--sp-2); font-size: var(--fs-micro); opacity: 0.75; }

  @media (max-width: 768px) {
    .hero { padding: var(--sp-6); }
    .hero-main { flex-direction: column; align-items: flex-start; }
    .hero-ring { align-self: center; }
  }
</style>
