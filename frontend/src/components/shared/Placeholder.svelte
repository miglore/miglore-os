<script lang="ts">
  let { title, desc }: { title: string; desc?: string } = $props();
</script>

<section class="placeholder">
  <div class="glyph">{title.slice(0, 1)}</div>
  <h1>{title}</h1>
  {#if desc}<p>{desc}</p>{/if}
  <span class="badge warn">V1 开发中</span>
</section>

<style>
  .placeholder {
    text-align: center;
    padding: var(--sp-8) var(--sp-5);
    min-height: 50vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--sp-4);
  }
  .glyph {
    width: 72px;
    height: 72px;
    border-radius: 20px;
    background: var(--grad-brand);
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
  }
  h1 { font-size: var(--fs-title); letter-spacing: -0.03em; }
  p { color: var(--c-text-2); max-width: 420px; }
</style>
