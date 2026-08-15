<script lang="ts">
  import Header from './components/layout/Header.svelte';
  import Footer from './components/layout/Footer.svelte';
  import Home from './routes/Home.svelte';
  import Learning from './routes/Learning.svelte';
  import Career from './routes/Career.svelte';
  import Projects from './routes/Projects.svelte';
  import Tasks from './routes/Tasks.svelte';
  import Journal from './routes/Journal.svelte';
  import Blog from './routes/Blog.svelte';

  // 极简 hash 路由（Svelte 5 runes，无外部依赖）
  let route = $state(window.location.hash || '#/');

  $effect(() => {
    const onHash = () => {
      route = window.location.hash || '#/';
      window.scrollTo({ top: 0 });
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  });
</script>

<Header />

<main>
  {#if route === '#/' || route === ''}
    <Home />
  {:else if route.startsWith('#/learning')}
    <Learning />
  {:else if route.startsWith('#/career')}
    <Career />
  {:else if route.startsWith('#/projects')}
    <Projects />
  {:else if route.startsWith('#/tasks')}
    <Tasks />
  {:else if route.startsWith('#/journal')}
    <Journal />
  {:else if route.startsWith('#/blog')}
    <Blog />
  {:else}
    <div class="page not-found">
      <h1>页面不存在</h1>
      <a class="section-link" href="#/">返回首页 →</a>
    </div>
  {/if}
</main>

<Footer />

<style>
  main { min-height: calc(100vh - var(--header-h)); }
  .not-found {
    text-align: center;
    padding: var(--sp-8) 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--sp-4);
  }
</style>
