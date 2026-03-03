<script>
  import { put } from '../stores/api.js';
  import { lights } from '../stores/lights.js';
  import { error as showError } from '../stores/toast.js';

  export let groups = [];

  async function toggleGroup(group, turnOn) {
    try {
      const promises = group.light_ids.map((id) =>
        put(`/api/lights/${id}`, { on: turnOn })
      );
      await Promise.all(promises);
    } catch (e) {
      showError('Failed to control group');
    }
  }

  function isGroupOn(group, lightMap) {
    return group.light_ids.some((id) => lightMap[id]?.on);
  }

  $: lightMap = $lights;
</script>

<div class="groups">
  {#each groups as group}
    <div class="group-card card">
      <div class="group-info">
        <span class="group-name">{group.name}</span>
        <span class="group-count">{group.light_ids.length} lights</span>
      </div>
      <div class="group-actions">
        <button
          class="btn btn-sm"
          class:btn-primary={!isGroupOn(group, lightMap)}
          class:btn-secondary={isGroupOn(group, lightMap)}
          on:click={() => toggleGroup(group, true)}
        >
          On
        </button>
        <button
          class="btn btn-sm btn-secondary"
          on:click={() => toggleGroup(group, false)}
        >
          Off
        </button>
      </div>
    </div>
  {/each}

  {#if groups.length === 0}
    <p class="empty-text">No groups configured. Add them in Settings.</p>
  {/if}
</div>

<style>
  .groups {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .group-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
  }

  .group-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .group-name {
    font-weight: 600;
    font-size: 14px;
  }

  .group-count {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .group-actions {
    display: flex;
    gap: 6px;
  }

  .empty-text {
    color: var(--text-muted);
    font-size: 14px;
    padding: 12px 0;
  }
</style>
