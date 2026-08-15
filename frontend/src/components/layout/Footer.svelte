<footer class="footer">
  <div class="footer-inner">
    <span class="brand">Miglore OS</span>
    <nav>
      <a href="#/learning">学习</a>
      <a href="#/career">求职</a>
      <a href="#/projects">项目</a>
      <a href="#/journal">日志</a>
    </nav>
    <span class="copy">© 2026 Miglore · 个人成长操作系统</span>
  </div>
</footer>

<style>
  .footer {
    border-top: 1px solid var(--c-border);
    margin-top: var(--sp-8);
    background: var(--c-surface);
  }
  .footer-inner {
    max-width: var(--page-max);
    margin: 0 auto;
    padding: var(--sp-6) var(--sp-5);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-4);
    flex-wrap: wrap;
    font-size: var(--fs-small);
  }
  .brand { font-weight: 700; }
  .footer nav { display: flex; gap: var(--sp-4); }
  .footer nav a { color: var(--c-text-2); transition: color var(--t-fast); }
  .footer nav a:hover { color: var(--c-primary); }
  .copy { color: var(--c-text-3); }
</style>
