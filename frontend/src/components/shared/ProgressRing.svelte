<script lang="ts">
  let {
    value = 0,
    size = 96,
    stroke = 8,
    track = 'rgba(255,255,255,0.25)',
  }: {
    value?: number;
    size?: number;
    stroke?: number;
    track?: string;
  } = $props();

  // 每个实例唯一 gradient id，避免多环冲突
  const uid = $state(crypto.randomUUID?.() ?? `ring-${Math.random().toString(36).slice(2)}`);
  const r = $derived((size - stroke) / 2);
  const c = $derived(2 * Math.PI * r);
  const clamped = $derived(Math.min(Math.max(value, 0), 100));
  const offset = $derived(c * (1 - clamped / 100));
</script>

<svg
  width={size}
  height={size}
  role="img"
  aria-label={`进度 ${clamped}%`}
>
  <defs>
    <linearGradient id={uid} x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a78bfa" />
      <stop offset="100%" stop-color="#ffffff" />
    </linearGradient>
  </defs>
  <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={track} stroke-width={stroke} />
  <circle
    cx={size / 2}
    cy={size / 2}
    r={r}
    fill="none"
    stroke={`url(#${uid})`}
    stroke-width={stroke}
    stroke-linecap="round"
    stroke-dasharray={c}
    stroke-dashoffset={offset}
    transform={`rotate(-90 ${size / 2} ${size / 2})`}
  />
  <text
    x="50%"
    y="50%"
    dy="0.35em"
    text-anchor="middle"
    fill="#fff"
    font-size={size * 0.22}
    font-weight="700"
  >{clamped}%</text>
</svg>
