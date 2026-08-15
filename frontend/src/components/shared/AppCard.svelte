<script lang="ts">
  let {
    href = '#',
    children,
  }: {
    href?: string;
    children?: import('svelte').Snippet;
  } = $props();
</script>

<a class="app-card" href={href}>
  {@render children?.()}
</a>

<style>
  .app-card {
    display: block;
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: var(--sp-5);
    box-shadow: var(--shadow-sm);
    transition: transform var(--t-fast), box-shadow var(--t-med);
  }
  .app-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
  }
</style>
