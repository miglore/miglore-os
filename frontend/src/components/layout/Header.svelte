<script lang="ts">
  const NAV = [
    { href: '#/', label: '首页' },
    { href: '#/learning', label: '学习' },
    { href: '#/lab', label: 'Lab' },
    { href: '#/career', label: '求职' },
    { href: '#/projects', label: '项目' },
    { href: '#/tasks', label: '任务' },
    { href: '#/journal', label: '日志' },
    { href: '#/blog', label: 'Blog' },
  ];

  let route = $state(window.location.hash || '#/');

  $effect(() => {
    const onHash = () => {
      route = window.location.hash || '#/';
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  });

  // route 是 $state，模板调用时自动追踪依赖，无需 $derived
  const active = (href: string) =>
    route === href || (href === '#/' && (route === '' || route === '#'));
</script>

<header class="header">
  <div class="header-inner">
    <a class="logo" href="#/">
      <span class="logo-mark">M</span>
      <span class="logo-text">Miglore OS</span>
    </a>

    <nav class="nav">
      {#each NAV as item (item.href)}
        <a
          class="nav-link"
          class:is-active={active(item.href)}
          href={item.href}
        >{item.label}</a>
      {/each}
    </nav>

    <div class="header-right">
      <div class="search" aria-label="搜索（开发中）">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" />
        </svg>
        <span>搜索模块</span>
      </div>
      <div class="avatar" title="miglore">m</div>
    </div>
  </div>
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(244, 245, 250, 0.82);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--c-border);
  }
  .header-inner {
    max-width: var(--page-max);
    margin: 0 auto;
    height: var(--header-h);
    padding: 0 var(--sp-5);
    display: flex;
    align-items: center;
    gap: var(--sp-6);
  }
  .logo {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: -0.02em;
  }
  .logo-mark {
    width: 30px;
    height: 30px;
    border-radius: 9px;
    background: var(--grad-brand);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    box-shadow: var(--shadow-sm);
  }
  .nav {
    display: flex;
    gap: var(--sp-1);
    flex: 1;
  }
  .nav-link {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: var(--fs-small);
    font-weight: 500;
    color: var(--c-text-2);
    transition: background var(--t-fast), color var(--t-fast);
  }
  .nav-link:hover { color: var(--c-text); background: var(--c-surface); }
  .nav-link.is-active { color: var(--c-primary); background: var(--c-primary-soft); font-weight: 600; }
  .header-right { display: flex; align-items: center; gap: var(--sp-4); }
  .search {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 999px;
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    color: var(--c-text-3);
    font-size: var(--fs-micro);
  }
  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--grad-brand);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: var(--fs-small);
    cursor: pointer;
  }

  /* 移动端：搜索隐藏，导航可横向滚动 */
  @media (max-width: 900px) {
    .header-inner { gap: var(--sp-3); }
    .search { display: none; }
    .nav { overflow-x: auto; scrollbar-width: none; }
    .nav::-webkit-scrollbar { display: none; }
    .logo-text { display: none; }
  }
</style>
