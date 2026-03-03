<script>
  import { createEventDispatcher } from 'svelte';
  import { put, post, del } from '../stores/api.js';
  import { lights } from '../stores/lights.js';
  import { success as showSuccess, error as showError } from '../stores/toast.js';

  export let scenes = [];
  export let availableLights = [];

  const dispatch = createEventDispatcher();

  let showCreate = false;
  let newSceneName = '';
  let selectedLightIds = [];
  let saving = false;

  function toggleLightForScene(id) {
    if (selectedLightIds.includes(id)) {
      selectedLightIds = selectedLightIds.filter((l) => l !== id);
    } else {
      selectedLightIds = [...selectedLightIds, id];
    }
  }

  async function createScene() {
    if (!newSceneName.trim()) {
      showError('Please enter a scene name');
      return;
    }
    if (selectedLightIds.length === 0) {
      showError('Select at least one light');
      return;
    }

    saving = true;
    try {
      await post('/api/scenes', {
        name: newSceneName.trim(),
        light_ids: selectedLightIds,
      });
      showSuccess(`Scene "${newSceneName}" created!`);
      newSceneName = '';
      selectedLightIds = [];
      showCreate = false;
      dispatch('refresh');
    } catch (e) {
      showError('Failed to create scene: ' + e.message);
    } finally {
      saving = false;
    }
  }

  async function applyScene(scene) {
    try {
      await post(`/api/scenes/${scene.id}/apply`, {});
      showSuccess(`Applied "${scene.name}"`);
    } catch (e) {
      showError('Failed to apply scene');
    }
  }

  async function deleteScene(scene) {
    try {
      await del(`/api/scenes/${scene.id}`);
      showSuccess(`Deleted "${scene.name}"`);
      dispatch('refresh');
    } catch (e) {
      showError('Failed to delete scene');
    }
  }
</script>

<div class="scene-manager">
  {#if scenes.length > 0}
    <div class="scene-list">
      {#each scenes as scene}
        <div class="scene-item card">
          <div class="scene-info">
            <span class="scene-name">{scene.name}</span>
            <span class="scene-lights-count">
              {Object.keys(scene.lights || {}).length} lights
            </span>
          </div>
          <div class="scene-actions">
            <button class="btn btn-primary btn-sm" on:click={() => applyScene(scene)}>
              ▶ Apply
            </button>
            <button class="btn btn-danger btn-sm" on:click={() => deleteScene(scene)}>
              ✕
            </button>
          </div>
        </div>
      {/each}
    </div>
  {:else if !showCreate}
    <p class="empty-text">No scenes yet. Create one from your current light setup!</p>
  {/if}

  {#if showCreate}
    <div class="scene-create card fade-in">
      <h3>Create Scene</h3>
      <p class="create-desc">Save the current state of selected lights.</p>

      <input
        class="input"
        placeholder="Scene name (e.g. Movie Night)"
        bind:value={newSceneName}
      />

      <div class="create-lights">
        {#each availableLights as light}
          <button
            class="create-light-item"
            class:selected={selectedLightIds.includes(light.id)}
            on:click={() => toggleLightForScene(light.id)}
          >
            {light.custom_name || light.name}
          </button>
        {/each}
      </div>

      <div class="create-actions">
        <button class="btn btn-secondary btn-sm" on:click={() => showCreate = false}>
          Cancel
        </button>
        <button class="btn btn-primary btn-sm" on:click={createScene} disabled={saving}>
          {saving ? 'Saving...' : 'Save Scene'}
        </button>
      </div>
    </div>
  {/if}

  {#if !showCreate}
    <button class="btn btn-secondary" on:click={() => showCreate = true}>
      + New Scene
    </button>
  {/if}
</div>

<style>
  .scene-manager {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .scene-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .scene-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
  }

  .scene-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .scene-name {
    font-weight: 600;
    font-size: 14px;
  }

  .scene-lights-count {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .scene-actions {
    display: flex;
    gap: 6px;
  }

  .empty-text {
    color: var(--text-muted);
    font-size: 14px;
    padding: 12px 0;
  }

  .scene-create {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .scene-create h3 {
    font-size: 16px;
  }

  .create-desc {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .create-lights {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .create-light-item {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    background: var(--bg-input);
    color: var(--text-primary);
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition);
  }

  .create-light-item:hover {
    background: var(--bg-card-hover);
  }

  .create-light-item.selected {
    border-color: var(--accent);
    background: var(--accent-dim);
  }

  .create-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
