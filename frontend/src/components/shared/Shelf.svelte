<script lang="ts">
  let {
    title = '',
    link = '',
    linkHref = '#',
    children,
  }: {
    title?: string;
    link?: string;
    linkHref?: string;
    children?: import('svelte').Snippet;
  } = $props();
</script>

<section class="shelf-block">
  <div class="section-head">
    <h2 class="section-title">{title}</h2>
    {#if link}
      <a class="section-link" href={linkHref}>{link} →</a>
    {/if}
  </div>
  <div class="shelf-track shelf-scroll">
    {@render children?.()}
  </div>
</section>

<style>
  .shelf-block { margin-bottom: var(--sp-7); }
  .shelf-track {
    display: flex;
    gap: var(--sp-4);
    overflow-x: auto;
    padding-bottom: var(--sp-3);
    scroll-snap-type: x proximity;
  }
  .shelf-track :global(> *) {
    flex: 0 0 auto;
    scroll-snap-align: start;
  }
</style>
