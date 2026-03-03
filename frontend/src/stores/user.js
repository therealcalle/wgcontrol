import { writable, derived } from 'svelte/store';

/**
 * Stores the current user object: { name, light_ids }
 * null when not logged in.
 */
export const currentUser = writable(null);

/**
 * Derived store: just the username.
 */
export const username = derived(currentUser, ($u) => ($u ? $u.name : null));
