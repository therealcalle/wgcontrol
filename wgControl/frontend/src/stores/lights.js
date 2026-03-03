import { writable } from 'svelte/store';

/**
 * Reactive store for all light states.
 * Map of light_id -> light data object.
 */
export const lights = writable({});

/**
 * Whether the SSE connection is active.
 */
export const connected = writable(false);

let eventSource = null;
let reconnectTimeout = null;

/**
 * Connect to the backend SSE stream for real-time light updates.
 */
export function connectSSE() {
  disconnectSSE();

  eventSource = new EventSource('/api/events');

  eventSource.onopen = () => {
    connected.set(true);
  };

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'light_update') {
        lights.update((current) => {
          const existing = current[data.id] || {};
          return {
            ...current,
            [data.id]: { ...existing, ...data.state },
          };
        });
      }
    } catch (e) {
      console.warn('SSE parse error:', e);
    }
  };

  eventSource.onerror = () => {
    connected.set(false);
    eventSource.close();
    eventSource = null;
    // Reconnect after 5 seconds
    reconnectTimeout = setTimeout(() => connectSSE(), 5000);
  };
}

/**
 * Disconnect from the SSE stream.
 */
export function disconnectSSE() {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  connected.set(false);
}

/**
 * Update a single light in the store (optimistic update).
 */
export function updateLightLocal(lightId, changes) {
  lights.update((current) => {
    const existing = current[lightId] || {};
    return {
      ...current,
      [lightId]: { ...existing, ...changes },
    };
  });
}

/**
 * Set all lights at once (used when fetching initial state).
 */
export function setAllLights(lightList) {
  const map = {};
  for (const light of lightList) {
    map[light.id] = light;
  }
  lights.set(map);
}
