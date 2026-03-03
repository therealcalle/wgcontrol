<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { currentUser } from '../stores/user.js';
  import { lights, setAllLights, connectSSE } from '../stores/lights.js';
  import { get } from '../stores/api.js';
  import { error as showError } from '../stores/toast.js';
  import Navbar from './Navbar.svelte';
  import LampCard from './LampCard.svelte';
  import GroupControl from './GroupControl.svelte';
  import SceneManager from './SceneManager.svelte';
  import Settings from './Settings.svelte';

  const dispatch = createEventDispatcher();

  let showSettings = false;
  let userLights = [];
  let sharedLights = [];
  let groups = [];
  let scenes = [];
  let config = null;
  let loading = true;

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    loading = true;
    try {
      const [lightData, configData, sceneData, groupData] = await Promise.all([
        get(`/api/lights/user/${$currentUser.name}`),
        get('/api/config'),
        get(`/api/scenes?user=${$currentUser.name}`),
        get('/api/config/groups'),
      ]);

      userLights = lightData.user_lights;
      sharedLights = lightData.shared_lights;
      config = configData;
      scenes = sceneData;
      groups = groupData.filter(
        (g) => g.users.length === 0 || g.users.includes($currentUser.name)
      );

      // Populate the lights store
      setAllLights([...userLights, ...sharedLights]);
    } catch (e) {
      showError('Failed to load lights: ' + e.message);
    } finally {
      loading = false;
    }
  }

  // Keep component light lists in sync with the store
  $: lightMap = $lights;

  function getUpdatedLight(light) {
    const stored = lightMap[light.id];
    if (!stored) return light;
    return { ...light, ...stored };
  }

  function handleLogout() {
    dispatch('logout');
  }

  function toggleSettings() {
    showSettings = !showSettings;
  }

  async function handleSettingsClosed() {
    showSettings = false;
    await loadData(); // Reload in case config changed
  }
</script>

{#if showSettings}
  <Settings
    {config}
    on:close={handleSettingsClosed}
    on:logout={handleLogout}
  />
{:else}
  <div class="dashboard">
    <Navbar
      on:logout={handleLogout}
      on:settings={toggleSettings}
    />

    {#if loading}
      <div class="loading-container">
        <p class="loading-pulse">Loading lights...</p>
      </div>
    {:else}
      <div class="dashboard-content">
        <!-- User's lights -->
        {#if userLights.length > 0}
          <section>
            <h2 class="section-title">My Lights</h2>
            <div class="lights-grid">
              {#each userLights as light (light.id)}
                <LampCard light={getUpdatedLight(light)} />
              {/each}
            </div>
          </section>
        {/if}

        <!-- Shared lights -->
        {#if sharedLights.length > 0}
          <section>
            <h2 class="section-title">Shared Lights</h2>
            <div class="lights-grid">
              {#each sharedLights as light (light.id)}
                <LampCard light={getUpdatedLight(light)} />
              {/each}
            </div>
          </section>
        {/if}

        <!-- Groups -->
        {#if groups.length > 0}
          <section>
            <h2 class="section-title">Groups</h2>
            <GroupControl {groups} />
          </section>
        {/if}

        <!-- Scenes -->
        <section>
          <h2 class="section-title">Scenes</h2>
          <SceneManager
            {scenes}
            availableLights={[...userLights, ...sharedLights]}
            on:refresh={loadData}
          />
        </section>
      </div>
    {/if}
  </div>
{/if}

<style>
  .dashboard {
    min-height: 100vh;
    background: var(--bg-primary);
  }

  .dashboard-content {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 28px;
    padding-bottom: 60px;
  }

  section {
    display: flex;
    flex-direction: column;
  }

  .lights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
  }

  .loading-container {
    display: flex;
    justify-content: center;
    padding: 80px 20px;
    color: var(--text-secondary);
    font-size: 16px;
  }

  @media (max-width: 640px) {
    .lights-grid {
      grid-template-columns: 1fr;
    }

    .dashboard-content {
      padding: 16px;
    }
  }
</style>
