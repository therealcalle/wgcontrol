<script>
  import { put } from '../stores/api.js';
  import { lights, updateLightLocal } from '../stores/lights.js';
  import { error as showError, success as showSuccess } from '../stores/toast.js';
  import ColorPicker from './ColorPicker.svelte';
  import BrightnessSlider from './BrightnessSlider.svelte';

  export let light; // initial/base data (capabilities, gamut, etc.)

  let expanded = false;
  let debounceTimer = null;
  let renaming = false;
  let renameValue = '';

  // Subscribe to the lights store directly for reactive state
  $: storedState = $lights[light.id] || {};
  $: mergedLight = { ...light, ...storedState };
  $: isOn = mergedLight.on;
  $: brightness = mergedLight.brightness || 0;
  $: hasColor = (mergedLight.capabilities || light.capabilities || []).includes('color');
  $: hasColorTemp = (mergedLight.capabilities || light.capabilities || []).includes('color_temperature');
  $: hasDimming = (mergedLight.capabilities || light.capabilities || []).includes('dimming');
  $: colorXy = mergedLight.color_xy || { x: 0.3127, y: 0.3290 };
  $: displayName = mergedLight.custom_name || mergedLight.name || light.name;

  // Compute preview color for the card indicator
  $: previewColor = getPreviewColor(mergedLight);

  function getPreviewColor(l) {
    if (!l.on) return '#555';
    if (l.color_xy) {
      // Quick CIE xy approximation to RGB for preview
      const x = l.color_xy.x, y = l.color_xy.y;
      const bri = (l.brightness || 100) / 100;
      const z = 1 - x - y;
      const Y = bri;
      if (y === 0) return '#000';
      const X = (Y / y) * x;
      const Z2 = (Y / y) * z;
      let r = X * 1.656492 - Y * 0.354851 - Z2 * 0.255038;
      let g = -X * 0.707196 + Y * 1.655397 + Z2 * 0.036152;
      let b = X * 0.051713 - Y * 0.121364 + Z2 * 1.011530;
      const mx = Math.max(r, g, b, 1);
      r /= mx; g /= mx; b /= mx;
      r = Math.max(0, Math.min(1, r <= 0.0031308 ? 12.92 * r : 1.055 * Math.pow(r, 1/2.4) - 0.055));
      g = Math.max(0, Math.min(1, g <= 0.0031308 ? 12.92 * g : 1.055 * Math.pow(g, 1/2.4) - 0.055));
      b = Math.max(0, Math.min(1, b <= 0.0031308 ? 12.92 * b : 1.055 * Math.pow(b, 1/2.4) - 0.055));
      return `rgb(${Math.round(r*255)}, ${Math.round(g*255)}, ${Math.round(b*255)})`;
    }
    // White/dimming only
    const bri = (l.brightness || 100) / 100;
    const v = Math.round(180 + bri * 75);
    return `rgb(${v}, ${v}, ${Math.round(v * 0.95)})`;
  }

  async function togglePower() {
    const newState = !isOn;
    updateLightLocal(light.id, { on: newState });
    try {
      await put(`/api/lights/${light.id}`, { on: newState });
    } catch (e) {
      showError('Failed to toggle light');
      updateLightLocal(light.id, { on: !newState });
    }
  }

  function handleBrightnessChange(event) {
    const value = event.detail;
    updateLightLocal(light.id, { brightness: value });
    debouncedUpdate({ brightness: value });
  }

  function handleColorChange(event) {
    const { x, y } = event.detail;
    updateLightLocal(light.id, { color_xy: { x, y } });
    debouncedUpdate({ color_xy: [x, y] });
  }

  function debouncedUpdate(state) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      try {
        await put(`/api/lights/${light.id}`, state);
      } catch (e) {
        showError('Failed to update light');
      }
    }, 150);
  }

  function toggleExpand() {
    expanded = !expanded;
  }

  function startRename() {
    renameValue = displayName;
    renaming = true;
  }

  async function saveRename() {
    const newName = renameValue.trim();
    if (!newName) {
      renaming = false;
      return;
    }
    try {
      await put(`/api/config/custom-name/${light.id}`, { name: newName });
      updateLightLocal(light.id, { custom_name: newName });
      showSuccess('Renamed to "' + newName + '"');
    } catch (e) {
      showError('Failed to rename');
    }
    renaming = false;
  }

  function cancelRename() {
    renaming = false;
  }

  function handleRenameKeydown(e) {
    if (e.key === 'Enter') saveRename();
    if (e.key === 'Escape') cancelRename();
  }
</script>

<div class="lamp-card card" class:off={!isOn}>
  <div class="lamp-header" on:click={toggleExpand} on:keydown={() => {}} role="button" tabindex="0">
    <div class="lamp-color-dot" style="background: {previewColor}"></div>
    <div class="lamp-info">
      {#if renaming}
        <!-- svelte-ignore a11y-autofocus -->
        <input
          class="rename-input"
          bind:value={renameValue}
          on:keydown={handleRenameKeydown}
          on:blur={saveRename}
          on:click|stopPropagation={() => {}}
          autofocus
        />
      {:else}
        <span class="lamp-name">{displayName}</span>
      {/if}
      {#if hasDimming && isOn && !renaming}
        <span class="lamp-brightness">{Math.round(brightness)}%</span>
      {/if}
    </div>
    <div
      class="toggle"
      class:on={isOn}
      on:click|stopPropagation={togglePower}
      on:keydown|stopPropagation={() => {}}
      role="switch"
      aria-checked={isOn}
      tabindex="0"
    >
      <div class="knob"></div>
    </div>
  </div>

  {#if expanded && isOn}
    <div class="lamp-controls fade-in">
      {#if !renaming}
        <button class="rename-btn" on:click|stopPropagation={startRename}>
          ✏️ Rename
        </button>
      {/if}

      {#if hasDimming}
        <BrightnessSlider value={brightness} on:change={handleBrightnessChange} />
      {/if}

      {#if hasColor}
        <ColorPicker
          x={colorXy.x}
          y={colorXy.y}
          gamut={light.gamut}
          on:change={handleColorChange}
        />
      {/if}
    </div>
  {/if}
</div>

<style>
  .lamp-card {
    transition: all var(--transition);
    overflow: hidden;
  }

  .lamp-card.off {
    opacity: 0.7;
  }

  .lamp-header {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    user-select: none;
  }

  .lamp-color-dot {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(255, 255, 255, 0.1);
    transition: background var(--transition);
  }

  .lamp-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .lamp-name {
    font-size: 15px;
    font-weight: 600;
  }

  .lamp-brightness {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .lamp-controls {
    padding-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .rename-btn {
    align-self: flex-start;
    background: none;
    color: var(--text-secondary);
    font-size: 12px;
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    transition: all var(--transition);
  }

  .rename-btn:hover {
    background: var(--bg-input);
    color: var(--text-primary);
  }

  .rename-input {
    background: var(--bg-input);
    border: 1px solid var(--accent);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 600;
    font-family: inherit;
    padding: 2px 8px;
    width: 100%;
    outline: none;
  }
</style>
