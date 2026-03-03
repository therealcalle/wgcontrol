<script>
  import { post, put, del } from '../stores/api.js';
  import { currentUser } from '../stores/user.js';
  import { success as showSuccess, error as showError } from '../stores/toast.js';

  export let allLights = [];
  export let config = null;

  let groups = [];
  let editingGroup = null;
  let showCreate = false;
  let groupName = '';
  let selectedLightIds = [];

  $: groups = config?.groups || [];
  $: userNames = (config?.users || []).map((u) => u.name);

  function startCreate() {
    showCreate = true;
    editingGroup = null;
    groupName = '';
    selectedLightIds = [];
  }

  function startEdit(group) {
    editingGroup = group;
    showCreate = false;
    groupName = group.name;
    selectedLightIds = [...group.light_ids];
  }

  function toggleLight(id) {
    if (selectedLightIds.includes(id)) {
      selectedLightIds = selectedLightIds.filter((l) => l !== id);
    } else {
      selectedLightIds = [...selectedLightIds, id];
    }
  }

  function cancel() {
    showCreate = false;
    editingGroup = null;
    groupName = '';
    selectedLightIds = [];
  }

  async function saveGroup() {
    if (!groupName.trim()) {
      showError('Please enter a group name');
      return;
    }

    try {
      if (editingGroup) {
        await put(`/api/config/groups/${editingGroup.id}`, {
          name: groupName.trim(),
          light_ids: selectedLightIds,
          users: editingGroup.users,
        });
        showSuccess('Group updated!');
      } else {
        await post('/api/config/groups', {
          name: groupName.trim(),
          light_ids: selectedLightIds,
          users: [$currentUser.name],
        });
        showSuccess('Group created!');
      }
      cancel();
      // Reload config
      config = await (await fetch('/api/config')).json();
    } catch (e) {
      showError('Failed to save group');
    }
  }

  async function deleteGroup(group) {
    try {
      await del(`/api/config/groups/${group.id}`);
      showSuccess(`Deleted "${group.name}"`);
      config = await (await fetch('/api/config')).json();
    } catch (e) {
      showError('Failed to delete group');
    }
  }

  function getLightName(id) {
    const light = allLights.find((l) => l.id === id);
    return light?.custom_name || light?.name || id.slice(0, 8);
  }
</script>

<div class="group-editor">
  {#if !showCreate && !editingGroup}
    <div class="group-list">
      {#each groups as group}
        <div class="group-item card">
          <div class="group-info">
            <span class="group-name">{group.name}</span>
            <span class="group-lights-text">
              {group.light_ids.map(getLightName).join(', ')}
            </span>
          </div>
          <div class="group-actions">
            <button class="btn btn-secondary btn-sm" on:click={() => startEdit(group)}>
              Edit
            </button>
            <button class="btn btn-danger btn-sm" on:click={() => deleteGroup(group)}>
              ✕
            </button>
          </div>
        </div>
      {/each}

      {#if groups.length === 0}
        <p class="empty-text">No groups yet.</p>
      {/if}

      <button class="btn btn-secondary" on:click={startCreate}>
        + New Group
      </button>
    </div>

  {:else}
    <div class="group-form card fade-in">
      <h3>{editingGroup ? 'Edit Group' : 'Create Group'}</h3>

      <input
        class="input"
        placeholder="Group name"
        bind:value={groupName}
      />

      <p class="form-label">Select lights:</p>
      <div class="light-select">
        {#each allLights as light}
          <button
            class="light-chip"
            class:selected={selectedLightIds.includes(light.id)}
            on:click={() => toggleLight(light.id)}
          >
            {light.custom_name || light.name}
          </button>
        {/each}
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary btn-sm" on:click={cancel}>Cancel</button>
        <button class="btn btn-primary btn-sm" on:click={saveGroup}>
          {editingGroup ? 'Update' : 'Create'}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .group-editor {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .group-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .group-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
  }

  .group-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
    min-width: 0;
  }

  .group-name {
    font-weight: 600;
    font-size: 14px;
  }

  .group-lights-text {
    font-size: 12px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .group-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
    margin-left: 12px;
  }

  .group-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .group-form h3 {
    font-size: 16px;
  }

  .form-label {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .light-select {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .light-chip {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    background: var(--bg-input);
    color: var(--text-primary);
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition);
  }

  .light-chip:hover {
    background: var(--bg-card-hover);
  }

  .light-chip.selected {
    border-color: var(--accent);
    background: var(--accent-dim);
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  .empty-text {
    color: var(--text-muted);
    font-size: 14px;
    padding: 8px 0;
  }
</style>
