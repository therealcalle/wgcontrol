<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { drawColorWheel, xyToHsv, hsvToXy, clipToGamut } from '../utils/color.js';

  export let x = 0.3127;
  export let y = 0.3290;
  export let gamut = null;

  const dispatch = createEventDispatcher();
  const SIZE = 200;

  let canvas;
  let dragging = false;
  let markerX = SIZE / 2;
  let markerY = SIZE / 2;

  onMount(() => {
    drawColorWheel(canvas, SIZE);
    updateMarkerFromXy(x, y);
  });

  // React to external color changes
  $: if (canvas) updateMarkerFromXy(x, y);

  function updateMarkerFromXy(cx, cy) {
    const hsv = xyToHsv(cx, cy, 1.0);
    const radius = SIZE / 2 - 2;
    const centerX = SIZE / 2;
    const centerY = SIZE / 2;
    const angle = (hsv.h * Math.PI) / 180;
    const dist = hsv.s * radius;
    markerX = centerX + dist * Math.cos(angle);
    markerY = centerY + dist * Math.sin(angle);
  }

  function getColorFromPosition(px, py) {
    const cx = SIZE / 2;
    const cy = SIZE / 2;
    const radius = SIZE / 2 - 2;
    const dx = px - cx;
    const dy = py - cy;
    let dist = Math.sqrt(dx * dx + dy * dy);

    // Clamp to circle
    if (dist > radius) dist = radius;

    const angle = Math.atan2(dy, dx);
    const hue = ((angle * 180) / Math.PI + 360) % 360;
    const saturation = dist / radius;

    // Convert to CIE xy
    let xy = hsvToXy(hue, saturation, 1);

    // Clip to gamut if available
    if (gamut) {
      xy = clipToGamut(xy.x, xy.y, gamut);
    }

    return xy;
  }

  function handlePointerDown(e) {
    dragging = true;
    handlePointerMove(e);
    e.target.setPointerCapture(e.pointerId);
  }

  function handlePointerMove(e) {
    if (!dragging) return;
    const rect = canvas.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;

    const xy = getColorFromPosition(px, py);
    markerX = px;
    markerY = py;

    // Clamp marker to circle
    const cx = SIZE / 2;
    const cy = SIZE / 2;
    const radius = SIZE / 2 - 2;
    const dx = markerX - cx;
    const dy = markerY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > radius) {
      markerX = cx + (dx / dist) * radius;
      markerY = cy + (dy / dist) * radius;
    }

    dispatch('change', xy);
  }

  function handlePointerUp() {
    dragging = false;
  }
</script>

<div class="color-picker">
  <span class="picker-label">🎨 Color</span>
  <div class="wheel-container" style="width: {SIZE}px; height: {SIZE}px;">
    <canvas
      bind:this={canvas}
      width={SIZE}
      height={SIZE}
      on:pointerdown={handlePointerDown}
      on:pointermove={handlePointerMove}
      on:pointerup={handlePointerUp}
      on:pointerleave={handlePointerUp}
    />
    <div
      class="marker"
      style="left: {markerX}px; top: {markerY}px;"
    ></div>
  </div>
</div>

<style>
  .color-picker {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .picker-label {
    font-size: 13px;
    color: var(--text-secondary);
    align-self: flex-start;
  }

  .wheel-container {
    position: relative;
    cursor: crosshair;
    touch-action: none;
  }

  canvas {
    border-radius: 50%;
    display: block;
  }

  .marker {
    position: absolute;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.5), inset 0 0 2px rgba(0, 0, 0, 0.3);
    transform: translate(-50%, -50%);
    pointer-events: none;
    transition: left 0.05s, top 0.05s;
  }
</style>
