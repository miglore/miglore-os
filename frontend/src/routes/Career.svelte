<script lang="ts">
  import { onMount } from 'svelte';
  import {
    api,
    type CareerData,
    type JDAnalyzeResult,
    type JobApplication,
    type Interview,
  } from '../lib/api';
  import Badge from '../components/shared/Badge.svelte';

  let data = $state<CareerData | null>(null);
  let error = $state('');
  let loading = $state(true);

  // JD Analyzer 状态
  let jdTitle = $state('');
  let jdText = $state('');
  let jdResult = $state<JDAnalyzeResult | null>(null);
  let analyzing = $state(false);
  let jdError = $state('');

  onMount(load);

  async function load() {
    loading = true;
    try {
      data = await api.get<{ data: CareerData }>('/api/career').then((r) => r.data);
      error = '';
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    } finally {
      loading = false;
    }
  }

  async function runAnalyze() {
    if (analyzing || !jdText.trim()) return;
    analyzing = true;
    jdError = '';
    jdResult = null;
    try {
      jdResult = await api.post<{ data: JDAnalyzeResult }>('/api/jd-analyze', {
        title: jdTitle,
        jd_text: jdText,
      }).then((r) => r.data);
    } catch (e) {
      jdError = e instanceof Error ? e.message : String(e);
    } finally {
      analyzing = false;
    }
  }

  const appStatusTone = (s: string) =>
    ({ interviewing: 'primary', offer: 'accent', rejected: 'danger', applied: 'neutral' })[s] ??
    'neutral';
  const appStatusLabel = (s: string) =>
    ({ draft: '草稿', applied: '已投递', interviewing: '面试中', offer: 'Offer', rejected: '已拒绝', withdrawn: '已撤回' })[s] ?? s;
  const ivwResultTone = (r: string) =>
    ({ passed: 'accent', failed: 'danger', offered: 'accent', pending: 'warn' })[r] ?? 'neutral';
  const ivwResultLabel = (r: string) =>
    ({ pending: '待定', passed: '通过', failed: '未过', offered: 'Offer' })[r] ?? r;
  const dirStatusTone = (s: string) => (s === 'active' ? 'accent' : 'neutral');
  const dirStatusLabel = (s: string) => ({ active: '进行中', paused: '暂停', closed: '已关闭' })[s] ?? s;
</script>

<div class="page">
  {#if error}
    <div class="load-error">⚠️ 加载失败：{error}</div>
  {:else if loading}
    <div class="loading">
      <div class="skeleton" style="height:200px; border-radius:28px;"></div>
      <div class="skeleton" style="height:120px;"></div>
      <div class="skeleton" style="height:200px;"></div>
    </div>
  {:else if data}
    <!-- Hero: 职业转型 -->
    <section class="career-hero">
      <div class="ch-copy">
        <p class="ch-kicker">Career · 求职</p>
        <h1 class="ch-title">职业转型</h1>
        <p class="ch-sub">
          {data.directions[0]?.target_role ?? 'DevOps 工程师'} · 从门店 IT 运维走向云原生
        </p>
      </div>
      <div class="ch-badge">
        <Badge tone="dark">{data.stats.pending_interviews} 个待面试</Badge>
      </div>
    </section>

    <!-- Target Directions -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Target Directions</h2>
      </div>
      {#if data.directions.length === 0}
        <div class="empty-note">暂无投递方向，去添加第一个方向吧（V1.1 支持编辑）</div>
      {:else}
        <div class="dir-grid">
          {#each data.directions as d (d.id)}
            <div class="dir-card">
              <div class="dir-head">
                <h3 class="dir-name">{d.name}</h3>
                <Badge tone={dirStatusTone(d.status)}>{dirStatusLabel(d.status)}</Badge>
              </div>
              {#if d.description}<p class="dir-desc">{d.description}</p>{/if}
              <p class="dir-meta">{d.application_count} 次投递 · 目标 {d.target_role ?? '—'}</p>
            </div>
          {/each}
        </div>
      {/if}
    </section>

    <!-- Application Statistics -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Application Statistics</h2>
      </div>
      <div class="stat-grid">
        <div class="stat-card"><span class="stat-num">{data.stats.total}</span><span class="stat-lbl">投递</span></div>
        <div class="stat-card accent"><span class="stat-num">{data.stats.interviewing}</span><span class="stat-lbl">面试中</span></div>
        <div class="stat-card good"><span class="stat-num">{data.stats.offers}</span><span class="stat-lbl">Offer</span></div>
        <div class="stat-card bad"><span class="stat-num">{data.stats.rejected}</span><span class="stat-lbl">拒绝</span></div>
      </div>
    </section>

    <!-- Applications -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Applications</h2>
      </div>
      {#if data.recent_applications.length === 0}
        <div class="empty-note">还没有投递记录</div>
      {:else}
        <div class="app-list">
          {#each data.recent_applications as a (a.id)}
            <div class="app-row">
              <div class="app-main">
                <p class="app-company">{a.company}</p>
                <p class="app-position">{a.position}</p>
              </div>
              <div class="app-meta">
                {#if a.city}<span class="app-chip">{a.city}</span>{/if}
                {#if a.salary}<span class="app-chip money">{a.salary}</span>{/if}
                <Badge tone={appStatusTone(a.status)}>{appStatusLabel(a.status)}</Badge>
              </div>
              <p class="app-date">{a.applied_at ?? ''}</p>
            </div>
          {/each}
        </div>
      {/if}
    </section>

    <!-- Interviews -->
    <section class="block">
      <div class="section-head">
        <h2 class="section-title">Interviews</h2>
      </div>
      {#if data.recent_interviews.length === 0}
        <div class="empty-note">还没有面试记录</div>
      {:else}
        <div class="ivw-list">
          {#each data.recent_interviews as i (i.id)}
            <div class="ivw-row">
              <div class="ivw-main">
                <p class="ivw-company">{i.company} · {i.round}</p>
                <p class="ivw-position">{i.position}</p>
                {#if i.review}<p class="ivw-review">{i.review}</p>{/if}
              </div>
              <div class="ivw-meta">
                <span class="app-chip">{i.scheduled_at?.slice(0, 16) ?? ''}</span>
                <Badge tone={ivwResultTone(i.result)}>{ivwResultLabel(i.result)}</Badge>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </section>

    <!-- JD Analyzer -->
    <section class="block jd-block">
      <div class="section-head">
        <h2 class="section-title">JD 分析</h2>
        <span class="jd-tag">Rule-based JD Analyzer · 非 AI</span>
      </div>
      <div class="jd-panel">
        <input
          class="jd-input"
          bind:value={jdTitle}
          placeholder="岗位名称（可选），如：初级 DevOps 工程师"
        />
        <textarea
          class="jd-textarea"
          bind:value={jdText}
          rows={5}
          placeholder="粘贴 JD 文本，分析技能匹配度…"
        ></textarea>
        <div class="jd-actions">
          <button class="btn-primary" onclick={runAnalyze} disabled={analyzing || !jdText.trim()}>
            {analyzing ? '分析中…' : '开始分析'}
          </button>
        </div>

        {#if jdError}
          <p class="jd-error">⚠️ {jdError}</p>
        {/if}

        {#if jdResult}
          <div class="jd-result">
            <div class="jd-score">
              <span class="jd-score-num">{jdResult.score}%</span>
              <span class="jd-score-lbl">JD Match Score</span>
            </div>
            <div class="jd-groups">
              <div class="jd-group">
                <p class="jd-group-title">✅ MATCH</p>
                {#if jdResult.matched.length === 0}<p class="jd-group-empty">无</p>{/if}
                <div class="jd-tags">
                  {#each jdResult.matched as s (s)}<span class="jd-tag-good">{s}</span>{/each}
                </div>
              </div>
              <div class="jd-group">
                <p class="jd-group-title">🔄 PARTIAL <small>已学未完成</small></p>
                {#if jdResult.partial.length === 0}<p class="jd-group-empty">无</p>{/if}
                <div class="jd-tags">
                  {#each jdResult.partial as s (s)}<span class="jd-tag-warn">{s}</span>{/each}
                </div>
              </div>
              <div class="jd-group">
                <p class="jd-group-title">❌ MISSING</p>
                {#if jdResult.missing.length === 0}<p class="jd-group-empty">无</p>{/if}
                <div class="jd-tags">
                  {#each jdResult.missing as s (s)}<span class="jd-tag-bad">{s}</span>{/each}
                </div>
              </div>
              <p class="jd-foot">共 {jdResult.total_required} 个技能要求 · 引擎：{jdResult.engine}</p>
            </div>
          </div>
        {/if}
      </div>
    </section>
  {/if}
</div>

<style>
  .loading { display: flex; flex-direction: column; gap: var(--sp-5); padding: var(--sp-6) 0; }
  .load-error { margin: var(--sp-6) 0; padding: var(--sp-4) var(--sp-5); background: #fee2e2; color: #b91c1c; border-radius: var(--r-md); font-weight: 600; }
  .block { margin-bottom: var(--sp-7); }
  .empty-note { padding: var(--sp-5); border: 1px dashed var(--c-border); border-radius: var(--r-lg); color: var(--c-text-2); text-align: center; }

  /* Hero */
  .career-hero {
    margin: var(--sp-6) 0 var(--sp-7);
    padding: var(--sp-7);
    border-radius: 28px;
    background: var(--grad-hero);
    color: #fff;
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-5);
    position: relative;
    overflow: hidden;
  }
  .career-hero::after {
    content: '';
    position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%);
  }
  .ch-kicker { font-size: var(--fs-small); opacity: 0.75; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: var(--sp-2); }
  .ch-title { font-size: var(--fs-title); font-weight: 800; letter-spacing: -0.03em; margin-bottom: var(--sp-2); }
  .ch-sub { font-size: var(--fs-body); opacity: 0.85; }
  .ch-badge { position: relative; z-index: 1; }

  /* Directions */
  .dir-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--sp-4); }
  .dir-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-5); box-shadow: var(--shadow-sm); }
  .dir-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--sp-2); }
  .dir-name { font-size: var(--fs-h3); font-weight: 700; }
  .dir-desc { font-size: var(--fs-small); color: var(--c-text-2); margin-bottom: var(--sp-2); }
  .dir-meta { font-size: var(--fs-micro); color: var(--c-text-3); }

  /* Stats */
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--sp-4); }
  .stat-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-5); text-align: center; box-shadow: var(--shadow-sm); }
  .stat-card.accent { border-color: var(--c-primary); }
  .stat-card.good { border-color: #d1fae5; }
  .stat-card.bad { border-color: #fee2e2; }
  .stat-num { display: block; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; }
  .stat-card.accent .stat-num { color: var(--c-primary); }
  .stat-card.good .stat-num { color: #047857; }
  .stat-card.bad .stat-num { color: #b91c1c; }
  .stat-lbl { font-size: var(--fs-small); color: var(--c-text-2); }

  /* Applications */
  .app-list, .ivw-list { display: flex; flex-direction: column; gap: var(--sp-3); }
  .app-row, .ivw-row {
    display: flex; align-items: center; gap: var(--sp-4);
    background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-md);
    padding: var(--sp-4) var(--sp-5); box-shadow: var(--shadow-sm);
  }
  .app-main, .ivw-main { flex: 1; min-width: 0; }
  .app-company { font-weight: 700; }
  .app-position { font-size: var(--fs-small); color: var(--c-text-2); }
  .app-meta { display: flex; align-items: center; gap: var(--sp-2); flex-wrap: wrap; }
  .app-chip { font-size: var(--fs-micro); color: var(--c-text-2); background: var(--c-bg); padding: 2px 10px; border-radius: 999px; }
  .app-chip.money { color: var(--c-primary); font-weight: 600; }
  .app-date { font-size: var(--fs-micro); color: var(--c-text-3); white-space: nowrap; }
  .ivw-company { font-weight: 700; }
  .ivw-position { font-size: var(--fs-small); color: var(--c-text-2); }
  .ivw-review { font-size: var(--fs-micro); color: var(--c-text-3); margin-top: 2px; }
  .ivw-meta { display: flex; align-items: center; gap: var(--sp-2); }

  /* JD Analyzer */
  .jd-block { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: var(--sp-6); box-shadow: var(--shadow-sm); }
  .jd-tag { font-size: var(--fs-micro); color: var(--c-text-3); background: var(--c-bg); padding: 3px 10px; border-radius: 999px; }
  .jd-panel { display: flex; flex-direction: column; gap: var(--sp-3); }
  .jd-input, .jd-textarea {
    width: 100%; border: 1px solid var(--c-border); border-radius: var(--r-md);
    padding: var(--sp-3) var(--sp-4); font-size: var(--fs-body); background: var(--c-surface-2); color: var(--c-text); outline: none;
  }
  .jd-input:focus, .jd-textarea:focus { border-color: var(--c-primary); }
  .jd-textarea { resize: vertical; line-height: 1.6; }
  .jd-actions { display: flex; justify-content: flex-end; }
  .jd-error { color: #b91c1c; font-size: var(--fs-small); font-weight: 600; }
  .jd-result {
    margin-top: var(--sp-4); padding-top: var(--sp-5); border-top: 1px solid var(--c-border);
    display: flex; gap: var(--sp-6); flex-wrap: wrap;
  }
  .jd-score { text-align: center; min-width: 140px; }
  .jd-score-num { display: block; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.03em; color: var(--c-primary); }
  .jd-score-lbl { font-size: var(--fs-micro); color: var(--c-text-3); }
  .jd-groups { flex: 1; display: flex; flex-direction: column; gap: var(--sp-3); }
  .jd-group-title { font-size: var(--fs-small); font-weight: 700; margin-bottom: var(--sp-2); }
  .jd-group-title small { font-weight: 400; color: var(--c-text-3); }
  .jd-group-empty { font-size: var(--fs-micro); color: var(--c-text-3); }
  .jd-tags { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
  .jd-tag-good { background: #d1fae5; color: #047857; }
  .jd-tag-warn { background: #fef3c7; color: #b45309; }
  .jd-tag-bad { background: #fee2e2; color: #b91c1c; }
  .jd-tag-good, .jd-tag-warn, .jd-tag-bad { padding: 3px 12px; border-radius: 999px; font-size: var(--fs-micro); font-weight: 600; }
  .jd-foot { font-size: var(--fs-micro); color: var(--c-text-3); }

  @media (max-width: 768px) {
    .career-hero { flex-direction: column; align-items: flex-start; padding: var(--sp-6); }
    .app-row, .ivw-row { flex-wrap: wrap; }
    .app-date { width: 100%; }
  }
</style>
