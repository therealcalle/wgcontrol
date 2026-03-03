<script>
  import { createEventDispatcher } from 'svelte';
  import { post, put } from '../stores/api.js';
  import { success as showSuccess, error as showError } from '../stores/toast.js';

  export let allLights = [];
  export let config = null;

  const dispatch = createEventDispatcher();

  // Build assignment map from config
  let assignments = {};

  $: {
    assignments = {};
    for (const light of allLights) {
      assignments[light.id] = 'unassigned';
    }
    if (config) {
      for (const user of config.users || []) {
        for (const id of user.light_ids || []) {
          assignments[id] = user.name;
        }
      }
      for (const id of config.shared_light_ids || []) {
        assignments[id] = 'shared';
      }
    }
  }

  $: userNames = (config?.users || []).map((u) => u.name);

  function cycleAssignment(lightId) {
    const options = [...userNames, 'shared', 'unassigned'];
    const current = assignments[lightId] || 'unassigned';
    const idx = options.indexOf(current);
    assignments[lightId] = options[(idx + 1) % options.length];
  }

  function getAssignmentColor(value) {
    if (value === 'shared') return 'var(--accent)';
    if (value === 'unassigned') return 'var(--text-muted)';
    const idx = userNames.indexOf(value);
    const colors = ['#4fc3f7', '#ba68c8', '#66bb6a', '#ff8a65'];
    return colors[idx % colors.length];
  }

  // Custom name editing
  let editingId = null;
  let editName = '';

  function startRename(light) {
    editingId = light.id;
    editName = light.custom_name || light.name;
  }

  async function saveRename(lightId) {
    try {
      await put(`/api/config/custom-name/${lightId}`, { name: editName });
      showSuccess('Name updated');
    } catch (e) {
      showError('Failed to rename');
    }
    editingId = null;
  }

  function cancelRename() {
    editingId = null;
  }

  async function saveAssignments() {
    const user_lights = {};
    for (const name of userNames) {
      user_lights[name] = [];
    }
    const shared = [];

    for (const [lightId, assignment] of Object.entries(assignments)) {
      if (assignment === 'shared') {
        shared.push(lightId);
      } else if (userNames.includes(assignment)) {
        user_lights[assignment].push(lightId);
      }
    }

    try {
      await post('/api/config/assign', { user_lights, shared });
      dispatch('saved');
    } catch (e) {
      showError('Failed to save assignments');
    }
  }
</script>

<div class="light-assignment">
  <div class="assignment-header">
    <h2>Light Assignment</h2>
    <p class="desc">Click a light to cycle its assignment. Double-click to rename.</p>
  </div>

  <div class="light-list">
    {#each allLights as light}
      <div class="light-row">
        {#if editingId === light.id}
          <div class="rename-row">
            <input
              class="input rename-input"
              bind:value={editName}
              on:keydown={(e) => { if (e.key === 'Enter') saveRename(light.id); if (e.key === 'Escape') cancelRename(); }}
              autofocus
            />
            <button class="btn btn-primary btn-sm" on:click={() => saveRename(light.id)}>✓</button>
            <button class="btn btn-secondary btn-sm" on:click={cancelRename}>✕</button>
          </div>
        {:else}
          <button
            class="light-item"
            on:click={() => cycleAssignment(light.id)}
            on:dblclick={() => startRename(light)}
          >
            <span class="light-name">{light.custom_name || light.name}</span>
            <span
              class="assignment-badge"
              style="color: {getAssignmentColor(assignments[light.id])}; border-color: {getAssignmentColor(assignments[light.id])}"
            >
              {assignments[light.id]}
            </span>
          </button>
        {/if}
      </div>
    {/each}
  </div>

  <button class="btn btn-primary" on:click={saveAssignments}>
    Save Assignments
  </button>
</div>

<style>
  .light-assignment {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .assignment-header h2 {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .desc {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .light-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 400px;
    overflow-y: auto;
  }

  .light-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    cursor: pointer;
    width: 100%;
    transition: all var(--transition);
  }

  .light-item:hover {
    background: var(--bg-card-hover);
  }

  .light-name {
    font-size: 14px;
  }

  .assignment-badge {
    font-size: 12px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    border: 1px solid;
    text-transform: capitalize;
  }

  .rename-row {
    display: flex;
    gap: 6px;
    align-items: center;
    width: 100%;
  }

  .rename-input {
    flex: 1;
  }
</style>
