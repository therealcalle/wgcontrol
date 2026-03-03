<script>
  import { toasts } from '../stores/toast.js';
</script>

{#if $toasts.length > 0}
  <div class="toast-container">
    {#each $toasts as toast (toast.id)}
      <div class="toast toast-{toast.type} fade-in">
        <span class="toast-icon">
          {#if toast.type === 'success'}✅
          {:else if toast.type === 'error'}❌
          {:else if toast.type === 'warning'}⚠️
          {:else}ℹ️
          {/if}
        </span>
        <span class="toast-message">{toast.message}</span>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 360px;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(8px);
  }

  .toast-success {
    background: rgba(102, 187, 106, 0.9);
    color: #1a1a1a;
  }

  .toast-error {
    background: rgba(239, 83, 80, 0.9);
    color: white;
  }

  .toast-warning {
    background: rgba(255, 167, 38, 0.9);
    color: #1a1a1a;
  }

  .toast-info {
    background: rgba(66, 165, 245, 0.9);
    color: white;
  }

  .toast-icon {
    font-size: 16px;
    flex-shrink: 0;
  }

  @media (max-width: 500px) {
    .toast-container {
      left: 16px;
      right: 16px;
      max-width: none;
    }
  }
</style>
