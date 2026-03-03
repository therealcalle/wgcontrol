import { writable } from 'svelte/store';

/**
 * Toast notification system.
 * Each toast: { id, message, type: 'info'|'success'|'error'|'warning' }
 */
export const toasts = writable([]);

let nextId = 1;

export function addToast(message, type = 'info', duration = 3500) {
  const id = nextId++;
  toasts.update((t) => [...t, { id, message, type }]);
  setTimeout(() => {
    toasts.update((t) => t.filter((toast) => toast.id !== id));
  }, duration);
}

export function success(message) {
  addToast(message, 'success');
}

export function error(message) {
  addToast(message, 'error', 5000);
}

export function warning(message) {
  addToast(message, 'warning');
}
