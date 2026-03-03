/**
 * API helper for making requests to the backend.
 */

const BASE = '';

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    const message = body.detail || `API error ${resp.status}`;
    throw new Error(message);
  }

  return resp.json();
}

export const get = (path) => request(path);
export const post = (path, body) =>
  request(path, { method: 'POST', body: JSON.stringify(body) });
export const put = (path, body) =>
  request(path, { method: 'PUT', body: JSON.stringify(body) });
export const del = (path) => request(path, { method: 'DELETE' });
