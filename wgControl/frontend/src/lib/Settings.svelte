<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { get, post, put, del } from '../stores/api.js';
  import { currentUser } from '../stores/user.js';
  import { success as showSuccess, error as showError } from '../stores/toast.js';
  import LightAssignment from './LightAssignment.svelte';
  import GroupEditor from './GroupEditor.svelte';

  export let config = null;

  const dispatch = createEventDispatcher();

  let activeTab = 'lights';
  let allLights = [];
  let newPin = '';
  let pinSaving = false;

  onMount(async () => {
    try {
      allLights = await get('/api/lights/all');
    } catch (e) {
      showError('Failed to load lights');
    }
  });

  async function changePin() {
    if (!newPin || newPin.length < 1) {
      showError('Please enter a new PIN');
      return;
    }
    pinSaving = true;
    try {
      await put(`/api/config/users/${$currentUser.name}/pin?pin=${encodeURIComponent(newPin)}`, {});
      showSuccess('PIN updated!');
      newPin = '';
    } catch (e) {
      showError('Failed to update PIN');
    } finally {
      pinSaving = false;
    }
  }

  function close() {
    dispatch('close');
  }
</script>

<div class="settings-page">
  <div class="settings-header">
    <button class="back-btn" on:click={close}>← Back</button>
    <h1>Settings</h1>
  </div>

  <div class="settings-tabs">
    <button
      class="tab" class:active={activeTab === 'lights'}
      on:click={() => activeTab = 'lights'}
    >Lights</button>
    <button
      class="tab" class:active={activeTab === 'groups'}
      on:click={() => activeTab = 'groups'}
    >Groups</button>
    <button
      class="tab" class:active={activeTab === 'account'}
      on:click={() => activeTab = 'account'}
    >Account</button>
    <button
      class="tab" class:active={activeTab === 'bridge'}
      on:click={() => activeTab = 'bridge'}
    >Bridge</button>
  </div>

  <div class="settings-content">
    {#if activeTab === 'lights'}
      <LightAssignment
        {allLights}
        {config}
        on:saved={() => showSuccess('Light assignments saved!')}
      />

    {:else if activeTab === 'groups'}
      <GroupEditor
        {allLights}
        {config}
      />

    {:else if activeTab === 'account'}
      <div class="settings-section card">
        <h2>Change PIN</h2>
        <p class="desc">Update your login PIN.</p>
        <div class="pin-change">
          <input
            class="input"
            type="password"
            placeholder="New PIN"
            maxlength="8"
            bind:value={newPin}
          />
          <button class="btn btn-primary btn-sm" on:click={changePin} disabled={pinSaving}>
            {pinSaving ? 'Saving...' : 'Update PIN'}
          </button>
        </div>
      </div>

      <div class="settings-section card">
        <h2>Logout</h2>
        <p class="desc">Return to the login screen.</p>
        <button class="btn btn-danger" on:click={() => dispatch('logout')}>
          Logout
        </button>
      </div>

    {:else if activeTab === 'bridge'}
      <div class="settings-section card">
        <h2>Bridge Info</h2>
        {#if config}
          <div class="info-row">
            <span class="info-label">IP Address</span>
            <span class="info-value">{config.bridge?.ip || 'Not configured'}</span>
          </div>
          <div class="info-row">
            <span class="info-label">API Key</span>
            <span class="info-value mono">
              {config.bridge?.api_key ? config.bridge.api_key.slice(0, 12) + '...' : 'N/A'}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Total Lights</span>
            <span class="info-value">{allLights.length}</span>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .settings-page {
    min-height: 100vh;
    background: var(--bg-primary);
  }

  .settings-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
  }

  .back-btn {
    background: none;
    color: var(--text-secondary);
    font-size: 14px;
    padding: 4px 8px;
  }

  .back-btn:hover {
    color: var(--text-primary);
  }

  h1 {
    font-size: 20px;
  }

  .settings-tabs {
    display: flex;
    padding: 0 20px;
    background: var(--bg-secondary);
    gap: 0;
    overflow-x: auto;
  }

  .tab {
    padding: 12px 20px;
    background: none;
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    transition: all var(--transition);
    white-space: nowrap;
  }

  .tab:hover {
    color: var(--text-primary);
  }

  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }

  .settings-content {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .settings-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .settings-section h2 {
    font-size: 16px;
  }

  .desc {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .pin-change {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .pin-change .input {
    max-width: 200px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }

  .info-label {
    font-size: 14px;
    color: var(--text-secondary);
  }

  .info-value {
    font-size: 14px;
    font-weight: 500;
  }

  .mono {
    font-family: monospace;
    font-size: 12px;
  }
</style>
