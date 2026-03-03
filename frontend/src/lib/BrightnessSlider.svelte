<script>
  import { createEventDispatcher } from 'svelte';

  export let value = 100;

  const dispatch = createEventDispatcher();

  function handleInput(e) {
    const v = parseFloat(e.target.value);
    dispatch('change', v);
  }
</script>

<div class="brightness-control">
  <div class="brightness-header">
    <span class="brightness-label">☀️ Brightness</span>
    <span class="brightness-value">{Math.round(value)}%</span>
  </div>
  <input
    type="range"
    min="1"
    max="100"
    step="1"
    value={value}
    on:input={handleInput}
    class="brightness-slider"
    style="background: linear-gradient(to right, #333 0%, var(--accent) {value}%, var(--bg-input) {value}%);"
  />
</div>

<style>
  .brightness-control {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .brightness-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brightness-label {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .brightness-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    min-width: 40px;
    text-align: right;
  }

  .brightness-slider {
    height: 8px;
    border-radius: 4px;
  }
</style>
