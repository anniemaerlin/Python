/**
 * PP.PRICING — Global API helper
 * Exposes window.API_BASE and window.api for all pages.
 */

window.API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';

window.api = {
  /**
   * POST JSON to a backend endpoint.
   * @param {string} path  — e.g. '/pricing/predict'
   * @param {object} body  — request payload
   * @returns {Promise<any>}
   */
  async postJSON(path, body) {
    const res = await fetch(`${window.API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `API error ${res.status}`);
    }
    return res.json();
  },

  /**
   * GET request.
   * @param {string} path
   * @returns {Promise<any>}
   */
  async getJSON(path) {
    const res = await fetch(`${window.API_BASE}${path}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  },

  /**
   * Check backend health.
   * @returns {Promise<boolean>}
   */
  async isOnline() {
    try {
      const res = await fetch(`${window.API_BASE}/pricing/health`, { method: 'GET' });
      return res.ok;
    } catch {
      return false;
    }
  }
};
