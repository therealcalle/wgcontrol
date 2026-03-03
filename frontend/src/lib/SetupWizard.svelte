<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { get, post } from '../stores/api.js';
  import { error as showError, success as showSuccess } from '../stores/toast.js';

  const dispatch = createEventDispatcher();

  let step = 1; // 1=bridge, 2=users, 3=assign lights
  let loading = false;

  // Step 1: Bridge
  let bridges = [];
  let selectedBridgeIp = '';
  let manualIp = '';
  let pairingStatus = ''; // '', 'waiting', 'success', 'error'
  let pairingMessage = '';

  // Step 2: Users
  let user1Name = '';
  let user1Pin = '';
  let user2Name = '';
  let user2Pin = '';

  // Step 3: Light assignment
  let allLights = [];
  let assignments = {}; // lightId -> 'user1' | 'user2' | 'shared' | ''

  onMount(async () => {
    await discoverBridges();
  });

  async function discoverBridges() {
    loading = true;
    try {
      const result = await get('/api/bridge/discover');
      bridges = result.bridges || [];
      if (bridges.length > 0) {
        selectedBridgeIp = bridges[0].internalipaddress;
      }
    } catch (e) {
      // Discovery failed, user can enter manually
    } finally {
      loading = false;
    }
  }

  async function pairBridge() {
    const ip = manualIp || selectedBridgeIp;
    if (!ip) {
      showError('Please enter a bridge IP address');
      return;
    }

    pairingStatus = 'waiting';
    pairingMessage = 'Press the button on your Hue Bridge, then wait...';

    // Try pairing every 2 seconds for 30 seconds
    let attempts = 0;
    const maxAttempts = 15;

    const tryPair = async () => {
      try {
        const result = await post('/api/bridge/pair', { ip });
        pairingStatus = 'success';
        pairingMessage = 'Bridge paired successfully!';
        showSuccess('Bridge connected!');
        setTimeout(() => { step = 2; }, 1000);
      } catch (e) {
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(tryPair, 2000);
        } else {
          pairingStatus = 'error';
          pairingMessage = 'Pairing timed out. Make sure you pressed the bridge button.';
        }
      }
    };

    tryPair();
  }

  async function saveUsers() {
    if (!user1Name || !user1Pin || !user2Name || !user2Pin) {
      showError('Please fill in all fields');
      return;
    }

    loading = true;
    try {
      await post('/api/config/users', {
        users: [
          { name: user1Name, pin: user1Pin, light_ids: [] },
          { name: user2Name, pin: user2Pin, light_ids: [] },
        ],
      });

      // Fetch lights for assignment
      allLights = await get('/api/lights/all');
      // Initialize assignments
      assignments = {};
      for (const light of allLights) {
        assignments[light.id] = '';
      }

      step = 3;
    } catch (e) {
      showError('Failed to save users: ' + e.message);
    } finally {
      loading = false;
    }
  }

  function cycleAssignment(lightId) {
    const order = ['', 'user1', 'user2', 'shared'];
    const current = assignments[lightId] || '';
    const idx = order.indexOf(current);
    assignments[lightId] = order[(idx + 1) % order.length];
  }

  function getAssignmentLabel(value) {
    if (value === 'user1') return user1Name;
    if (value === 'user2') return user2Name;
    if (value === 'shared') return 'Shared';
    return 'Unassigned';
  }

  function getAssignmentClass(value) {
    if (value === 'user1') return 'assign-user1';
    if (value === 'user2') return 'assign-user2';
    if (value === 'shared') return 'assign-shared';
    return 'assign-none';
  }

  async function finishSetup() {
    loading = true;
    try {
      const user_lights = {};
      user_lights[user1Name] = [];
      user_lights[user2Name] = [];
      const shared = [];

      for (const [lightId, assignment] of Object.entries(assignments)) {
        if (assignment === 'user1') user_lights[user1Name].push(lightId);
        else if (assignment === 'user2') user_lights[user2Name].push(lightId);
        else if (assignment === 'shared') shared.push(lightId);
      }

      await post('/api/config/assign', { user_lights, shared });

      // Start the event stream listener
      await post('/api/bridge/start-events', {});

      showSuccess('Setup complete!');
      dispatch('complete', { users: [user1Name, user2Name] });
    } catch (e) {
      showError('Failed to save: ' + e.message);
    } finally {
      loading = false;
    }
  }
</script>

<div class="wizard">
  <div class="wizard-header">
    <div class="logo">💡</div>
    <h1>wgControl Setup</h1>
    <div class="steps">
      <span class="step" class:active={step >= 1} class:done={step > 1}>1. Bridge</span>
      <span class="step-line" class:active={step > 1}></span>
      <span class="step" class:active={step >= 2} class:done={step > 2}>2. Users</span>
      <span class="step-line" class:active={step > 2}></span>
      <span class="step" class:active={step >= 3}>3. Lights</span>
    </div>
  </div>

  <div class="wizard-content card">
    {#if step === 1}
      <div class="wizard-step fade-in">
        <h2>Connect to Hue Bridge</h2>
        <p class="step-desc">
          We'll find your Hue Bridge on the network. Make sure it's powered on.
        </p>

        {#if bridges.length > 0}
          <div class="bridge-list">
            {#each bridges as bridge}
              <button
                class="bridge-item"
                class:selected={selectedBridgeIp === bridge.internalipaddress}
                on:click={() => { selectedBridgeIp = bridge.internalipaddress; manualIp = ''; }}
              >
                <span class="bridge-icon">🌉</span>
                <span>{bridge.internalipaddress}</span>
                {#if bridge.id}
                  <span class="bridge-id">{bridge.id.slice(0, 8)}</span>
                {/if}
              </button>
            {/each}
          </div>
        {:else if !loading}
          <p class="no-bridges">No bridges found automatically.</p>
        {/if}

        <div class="manual-ip">
          <label>Or enter IP manually:</label>
          <input
            type="text"
            class="input"
            placeholder="192.168.1.x"
            bind:value={manualIp}
          />
        </div>

        {#if pairingStatus}
          <div class="pairing-status {pairingStatus}">
            {#if pairingStatus === 'waiting'}
              <span class="loading-pulse">🔗</span>
            {:else if pairingStatus === 'success'}
              <span>✅</span>
            {:else}
              <span>❌</span>
            {/if}
            <span>{pairingMessage}</span>
          </div>
        {/if}

        <button
          class="btn btn-primary"
          on:click={pairBridge}
          disabled={pairingStatus === 'waiting' || (!selectedBridgeIp && !manualIp)}
        >
          {pairingStatus === 'waiting' ? 'Waiting for bridge...' : 'Pair Bridge'}
        </button>
      </div>

    {:else if step === 2}
      <div class="wizard-step fade-in">
        <h2>Create Users</h2>
        <p class="step-desc">Set up the two user profiles with a name and PIN.</p>

        <div class="user-setup">
          <div class="user-form">
            <h3>User 1</h3>
            <input class="input" placeholder="Name" bind:value={user1Name} />
            <input class="input" type="password" placeholder="PIN" maxlength="8" bind:value={user1Pin} />
          </div>
          <div class="user-form">
            <h3>User 2</h3>
            <input class="input" placeholder="Name" bind:value={user2Name} />
            <input class="input" type="password" placeholder="PIN" maxlength="8" bind:value={user2Pin} />
          </div>
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" on:click={() => step = 1}>Back</button>
          <button class="btn btn-primary" on:click={saveUsers} disabled={loading}>
            {loading ? 'Saving...' : 'Next'}
          </button>
        </div>
      </div>

    {:else if step === 3}
      <div class="wizard-step fade-in">
        <h2>Assign Lights</h2>
        <p class="step-desc">
          Click each light to cycle between: <strong>{user1Name}</strong>,
          <strong>{user2Name}</strong>, <strong>Shared</strong>, or unassigned.
        </p>

        <div class="light-assignment-list">
          {#each allLights as light}
            <button
              class="light-assign-item {getAssignmentClass(assignments[light.id])}"
              on:click={() => cycleAssignment(light.id)}
            >
              <span class="light-name">{light.name}</span>
              <span class="light-badge">{getAssignmentLabel(assignments[light.id])}</span>
            </button>
          {/each}
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" on:click={() => step = 2}>Back</button>
          <button class="btn btn-primary" on:click={finishSetup} disabled={loading}>
            {loading ? 'Finishing...' : 'Finish Setup'}
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .wizard {
    max-width: 600px;
    margin: 0 auto;
    padding: 24px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .wizard-header {
    text-align: center;
    margin-bottom: 24px;
  }

  .logo {
    font-size: 48px;
    margin-bottom: 4px;
  }

  h1 {
    font-size: 24px;
    margin-bottom: 20px;
  }

  .steps {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-muted);
  }

  .step.active {
    color: var(--accent);
    font-weight: 600;
  }

  .step.done {
    color: var(--success);
  }

  .step-line {
    width: 40px;
    height: 2px;
    background: var(--bg-input);
    border-radius: 1px;
  }

  .step-line.active {
    background: var(--accent);
  }

  .wizard-content {
    padding: 32px;
  }

  .wizard-step {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  h2 {
    font-size: 20px;
  }

  .step-desc {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.5;
  }

  .bridge-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .bridge-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--bg-input);
    border: 2px solid transparent;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    cursor: pointer;
    transition: all var(--transition);
  }

  .bridge-item:hover {
    background: var(--bg-card-hover);
  }

  .bridge-item.selected {
    border-color: var(--accent);
    background: var(--accent-dim);
  }

  .bridge-icon {
    font-size: 20px;
  }

  .bridge-id {
    color: var(--text-muted);
    font-size: 12px;
    margin-left: auto;
  }

  .no-bridges {
    color: var(--text-muted);
    font-size: 14px;
    font-style: italic;
  }

  .manual-ip {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .manual-ip label {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .pairing-status {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    font-size: 14px;
  }

  .pairing-status.waiting {
    background: var(--accent-dim);
    color: var(--accent);
  }

  .pairing-status.success {
    background: rgba(102, 187, 106, 0.15);
    color: var(--success);
  }

  .pairing-status.error {
    background: rgba(239, 83, 80, 0.15);
    color: var(--danger);
  }

  .user-setup {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .user-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .user-form h3 {
    font-size: 14px;
    color: var(--text-secondary);
  }

  .step-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
  }

  .light-assignment-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 300px;
    overflow-y: auto;
  }

  .light-assign-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-input);
    border: 2px solid transparent;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    cursor: pointer;
    transition: all var(--transition);
  }

  .light-assign-item:hover {
    background: var(--bg-card-hover);
  }

  .light-badge {
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
    background: var(--bg-card);
  }

  .assign-user1 {
    border-color: #4fc3f7;
  }
  .assign-user1 .light-badge {
    background: rgba(79, 195, 247, 0.2);
    color: #4fc3f7;
  }

  .assign-user2 {
    border-color: #ba68c8;
  }
  .assign-user2 .light-badge {
    background: rgba(186, 104, 200, 0.2);
    color: #ba68c8;
  }

  .assign-shared {
    border-color: var(--accent);
  }
  .assign-shared .light-badge {
    background: var(--accent-dim);
    color: var(--accent);
  }

  .assign-none .light-badge {
    color: var(--text-muted);
  }

  @media (max-width: 500px) {
    .user-setup {
      grid-template-columns: 1fr;
    }
  }
</style>
