<script>
  import { createEventDispatcher } from 'svelte';
  import { currentUser } from '../stores/user.js';
  import { post } from '../stores/api.js';
  import { error as showError } from '../stores/toast.js';

  export let users = [];

  const dispatch = createEventDispatcher();

  let selectedUser = null;
  let pin = '';
  let pinError = '';
  let loading = false;

  function selectUser(name) {
    selectedUser = name;
    pin = '';
    pinError = '';
  }

  function goBack() {
    selectedUser = null;
    pin = '';
    pinError = '';
  }

  async function handleLogin() {
    if (!pin) {
      pinError = 'Please enter your PIN';
      return;
    }

    loading = true;
    pinError = '';

    try {
      const result = await post('/api/auth/login', {
        user: selectedUser,
        pin: pin,
      });
      currentUser.set(result.user);
      dispatch('login');
    } catch (e) {
      pinError = e.message || 'Incorrect PIN';
      pin = '';
    } finally {
      loading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') handleLogin();
    if (e.key === 'Escape') goBack();
  }
</script>

<div class="login-page">
  <div class="login-header">
    <div class="logo">💡</div>
    <h1>wgControl</h1>
    <p>Select your profile</p>
  </div>

  {#if !selectedUser}
    <div class="user-cards">
      {#each users as name}
        <button class="user-card card" on:click={() => selectUser(name)}>
          <div class="user-avatar">
            {name.charAt(0).toUpperCase()}
          </div>
          <span class="user-name">{name}</span>
        </button>
      {/each}
    </div>

    <button class="setup-link" on:click={() => dispatch('setup')}>
      ⚙️ Setup
    </button>
  {:else}
    <div class="pin-entry fade-in">
      <button class="back-btn" on:click={goBack}>← Back</button>

      <div class="user-avatar large">
        {selectedUser.charAt(0).toUpperCase()}
      </div>
      <h2>{selectedUser}</h2>

      <div class="pin-field">
        <input
          type="password"
          class="input pin-input"
          placeholder="Enter PIN"
          maxlength="8"
          bind:value={pin}
          on:keydown={handleKeydown}
          autofocus
        />
        {#if pinError}
          <p class="pin-error">{pinError}</p>
        {/if}
      </div>

      <button
        class="btn btn-primary login-btn"
        on:click={handleLogin}
        disabled={loading}
      >
        {loading ? 'Logging in...' : 'Enter'}
      </button>
    </div>
  {/if}
</div>

<style>
  .login-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 24px;
  }

  .login-header {
    text-align: center;
    margin-bottom: 40px;
  }

  .logo {
    font-size: 56px;
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .login-header p {
    color: var(--text-secondary);
    font-size: 15px;
  }

  .user-cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .user-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 32px 40px;
    cursor: pointer;
    transition: all var(--transition);
    background: var(--bg-card);
    color: var(--text-primary);
  }

  .user-card:hover {
    background: var(--bg-card-hover);
    transform: translateY(-4px);
    box-shadow: var(--shadow);
  }

  .user-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: var(--accent-dim);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 700;
  }

  .user-avatar.large {
    width: 80px;
    height: 80px;
    font-size: 36px;
    margin-bottom: 8px;
  }

  .user-name {
    font-size: 16px;
    font-weight: 600;
  }

  .pin-entry {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    width: 100%;
    max-width: 320px;
  }

  .back-btn {
    align-self: flex-start;
    background: none;
    color: var(--text-secondary);
    font-size: 14px;
    padding: 4px 0;
  }

  .back-btn:hover {
    color: var(--text-primary);
  }

  h2 {
    font-size: 22px;
    margin-bottom: 8px;
  }

  .pin-field {
    width: 100%;
  }

  .pin-input {
    text-align: center;
    font-size: 20px;
    letter-spacing: 8px;
    padding: 14px;
  }

  .pin-error {
    color: var(--danger);
    font-size: 13px;
    margin-top: 8px;
    text-align: center;
  }

  .login-btn {
    width: 100%;
    padding: 14px;
    font-size: 16px;
    margin-top: 8px;
  }

  .setup-link {
    margin-top: 32px;
    background: none;
    color: var(--text-muted);
    font-size: 13px;
  }

  .setup-link:hover {
    color: var(--text-secondary);
  }
</style>
