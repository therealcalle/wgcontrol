<script>
  import { onMount } from 'svelte';
  import { currentUser } from './stores/user.js';
  import { connectSSE, disconnectSSE } from './stores/lights.js';
  import { get } from './stores/api.js';
  import SetupWizard from './lib/SetupWizard.svelte';
  import LoginPage from './lib/LoginPage.svelte';
  import Dashboard from './lib/Dashboard.svelte';
  import Toast from './lib/Toast.svelte';

  let page = 'loading';
  let bridgeUsers = [];

  onMount(async () => {
    try {
      const status = await get('/api/bridge/status');
      if (!status.configured || !status.has_users) {
        page = 'setup';
      } else {
        bridgeUsers = status.users;
        page = 'login';
      }
    } catch {
      page = 'setup';
    }
  });

  function handleSetupComplete(event) {
    bridgeUsers = event.detail?.users || [];
    page = 'login';
  }

  function handleLogin() {
    connectSSE();
    page = 'dashboard';
  }

  function handleLogout() {
    disconnectSSE();
    currentUser.set(null);
    page = 'login';
  }

  function handleGoToSetup() {
    page = 'setup';
  }
</script>

{#if page === 'loading'}
  <div class="loading-screen">
    <div class="loading-icon loading-pulse">💡</div>
    <p>Loading wgControl...</p>
  </div>
{:else if page === 'setup'}
  <SetupWizard on:complete={handleSetupComplete} />
{:else if page === 'login'}
  <LoginPage users={bridgeUsers} on:login={handleLogin} on:setup={handleGoToSetup} />
{:else if page === 'dashboard'}
  <Dashboard on:logout={handleLogout} />
{/if}

<Toast />

<style>
  .loading-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 16px;
  }

  .loading-icon {
    font-size: 48px;
  }

  .loading-screen p {
    color: var(--text-secondary);
    font-size: 16px;
  }
</style>
