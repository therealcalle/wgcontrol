<script>
  import { createEventDispatcher } from 'svelte';
  import { currentUser } from '../stores/user.js';
  import { connected } from '../stores/lights.js';

  const dispatch = createEventDispatcher();
</script>

<nav class="navbar">
  <div class="nav-left">
    <span class="nav-logo">💡</span>
    <span class="nav-title">wgControl</span>
    <span class="connection-dot" class:connected={$connected} title={$connected ? 'Connected' : 'Disconnected'}></span>
  </div>

  <div class="nav-right">
    {#if $currentUser}
      <span class="nav-user">{$currentUser.name}</span>
    {/if}
    <button class="btn-icon" on:click={() => dispatch('settings')} title="Settings">
      ⚙️
    </button>
    <button class="btn-icon" on:click={() => dispatch('logout')} title="Logout">
      🚪
    </button>
  </div>
</nav>

<style>
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .nav-logo {
    font-size: 24px;
  }

  .nav-title {
    font-size: 18px;
    font-weight: 700;
  }

  .connection-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--danger);
    transition: background var(--transition);
  }

  .connection-dot.connected {
    background: var(--success);
  }

  .nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .nav-user {
    font-size: 14px;
    color: var(--text-secondary);
    margin-right: 4px;
  }
</style>
