<script lang="ts">
  let { tone = 'neutral', children }: { tone?: string; children?: import('svelte').Snippet } = $props();
</script>

<span class="badge {tone}">
  {@render children?.()}
</span>

<style>
  .neutral { background: #eef0f6; color: var(--c-text-2); }
  .primary { background: var(--c-primary-soft); color: var(--c-primary); }
  .accent  { background: #d1fae5; color: #047857; }
  .warn    { background: #fef3c7; color: #b45309; }
  .danger  { background: #fee2e2; color: #b91c1c; }
  .dark    { background: rgba(0, 0, 0, 0.35); color: #fff; backdrop-filter: blur(4px); }
</style>
