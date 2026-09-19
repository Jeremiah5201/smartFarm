const apiBase = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the HTTP status message when the server returns non-JSON content.
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  health: () => request("/api/health"),
  farms: () => request("/api/farms"),
  latest: (farmId) => request(`/api/farms/${farmId}/latest`),
  readings: (farmId, limit = 12) => request(`/api/farms/${farmId}/readings?limit=${limit}`),
  irrigationHistory: (farmId, limit = 8) => request(`/api/irrigation/${farmId}/history?limit=${limit}`),
  override: (farmId, command) => request(`/api/irrigation/${farmId}/override`, {
    method: "POST",
    body: JSON.stringify(command),
  }),
};