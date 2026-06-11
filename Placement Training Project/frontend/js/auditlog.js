/**
 * PP.PRICING — Audit Log Page
 * Tries Firebase/backend audit endpoint; falls back to local session log.
 */

const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';

// Session-level log (also shared between pages via sessionStorage)
const STORAGE_KEY = 'pp_audit_log';

const ACTION_COLORS = {
  'Pricing Predict':   '#00f2fe',
  'Forecast Update':   '#7f00ff',
  'Competitor Scan':   '#ff007f',
  'Customer Segment':  '#4facfe',
  'System':            '#39ff14'
};

const ACTION_ICONS = {
  'Pricing Predict':   'fa-bolt',
  'Forecast Update':   'fa-chart-area',
  'Competitor Scan':   'fa-store',
  'Customer Segment':  'fa-users',
  'System':            'fa-shield-halved'
};

// Pre-seeded demo data
const DEMO_LOGS = [
  { ts:'2026-06-10 10:30', action:'Pricing Predict', price:'₹1,350', confidence:'94%', reason:'Demand high, competitor prices above baseline', status:'success' },
  { ts:'2026-06-10 10:15', action:'Competitor Scan', price:'—', confidence:'—', reason:'Market scan triggered by demand spike alert', status:'success' },
  { ts:'2026-06-10 09:55', action:'Forecast Update', price:'—', confidence:'87%', reason:'Weekly seasonality pattern applied — 30d ahead', status:'success' },
  { ts:'2026-06-10 09:45', action:'Customer Segment', price:'—', confidence:'—', reason:'VIP customer classified — loyalty score 0.92', status:'success' },
  { ts:'2026-06-09 16:30', action:'Pricing Predict', price:'₹1,280', confidence:'91%', reason:'Competitor Meesho dropped price by 3%, adjusted accordingly', status:'success' },
  { ts:'2026-06-09 14:20', action:'Competitor Scan', price:'—', confidence:'—', reason:'Scheduled daily market intelligence scan', status:'success' },
  { ts:'2026-06-09 12:05', action:'Forecast Update', price:'—', confidence:'89%', reason:'Monthly seasonality re-calculation with 20 data points', status:'success' },
  { ts:'2026-06-08 18:10', action:'Pricing Predict', price:'₹1,200', confidence:'78%', reason:'Low demand period — baseline price maintained', status:'warning' },
  { ts:'2026-06-08 09:00', action:'System', price:'—', confidence:'—', reason:'AI Engine restarted — models reloaded successfully', status:'success' },
  { ts:'2026-06-07 16:02', action:'Customer Segment', price:'—', confidence:'—', reason:'Budget_Conscious segment — 15% discount recommended', status:'success' }
];

function getStoredLogs() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function getAllLogs() {
  const session = getStoredLogs();
  return [...session, ...DEMO_LOGS];
}

// Public helper — other pages call this to log events
window.ppAuditLog = function(action, price, confidence, reason, status = 'success') {
  const entry = {
    ts:         new Date().toLocaleString('en-IN'),
    action,
    price:      price || '—',
    confidence: confidence || '—',
    reason:     reason || '—',
    status
  };
  try {
    const logs = getStoredLogs();
    logs.unshift(entry);
    if (logs.length > 50) logs.pop();
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(logs));
  } catch { /* storage full or unavailable */ }
};

function statusBadge(s) {
  if (s === 'success') return `<span class="badge badge-success" style="font-size:0.7rem;padding:0.25rem 0.55rem;">✓ OK</span>`;
  if (s === 'warning') return `<span class="badge badge-amber" style="font-size:0.7rem;padding:0.25rem 0.55rem;">⚠ Warn</span>`;
  if (s === 'error')   return `<span class="badge badge-danger" style="font-size:0.7rem;padding:0.25rem 0.55rem;">✕ Error</span>`;
  return `<span class="badge" style="font-size:0.7rem;padding:0.25rem 0.55rem;">${s}</span>`;
}

function renderTable(logs) {
  const tbody = document.getElementById('audit-body');
  const empty = document.getElementById('audit-empty');
  const countEl = document.getElementById('audit-count');

  if (logs.length === 0) {
    tbody.innerHTML = '';
    empty.style.display = 'block';
    countEl.textContent = '0 records';
    return;
  }
  empty.style.display = 'none';
  countEl.textContent = `${logs.length} record${logs.length !== 1 ? 's' : ''}`;

  tbody.innerHTML = logs.map(r => {
    const color = ACTION_COLORS[r.action] || '#8b92a9';
    const icon  = ACTION_ICONS[r.action]  || 'fa-circle';
    return `
      <tr>
        <td style="color:var(--text-secondary);white-space:nowrap;">${r.ts}</td>
        <td>
          <span style="display:flex;align-items:center;gap:0.4rem;color:${color};">
            <i class="fa-solid ${icon}" style="font-size:0.8rem;"></i> ${r.action}
          </span>
        </td>
        <td>${r.price}</td>
        <td>${r.confidence}</td>
        <td style="color:var(--text-secondary);max-width:280px;">${r.reason}</td>
        <td>${statusBadge(r.status)}</td>
      </tr>`;
  }).join('');
}

function updateCounts(logs) {
  document.getElementById('cnt-pricing').textContent    = logs.filter(l => l.action === 'Pricing Predict').length;
  document.getElementById('cnt-forecast').textContent   = logs.filter(l => l.action === 'Forecast Update').length;
  document.getElementById('cnt-competitor').textContent = logs.filter(l => l.action === 'Competitor Scan').length;
  document.getElementById('cnt-customer').textContent   = logs.filter(l => l.action === 'Customer Segment').length;
}

function applyFilters() {
  const search  = document.getElementById('audit-search').value.toLowerCase();
  const filter  = document.getElementById('audit-filter').value;
  let logs = getAllLogs();

  if (filter !== 'all') {
    const map = { pricing:'Pricing Predict', forecast:'Forecast Update', competitor:'Competitor Scan', customer:'Customer Segment' };
    logs = logs.filter(l => l.action === map[filter]);
  }
  if (search) {
    logs = logs.filter(l =>
      l.action.toLowerCase().includes(search) ||
      l.reason.toLowerCase().includes(search) ||
      l.price.toLowerCase().includes(search)
    );
  }
  renderTable(logs);
}

async function tryLoadFromBackend() {
  try {
    const res = await fetch(`${API_BASE}/pricing/health`);
    if (res.ok) {
      document.getElementById('refresh-btn').innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Refresh';
    }
  } catch { /* backend offline */ }
}

document.addEventListener('DOMContentLoaded', () => {
  const allLogs = getAllLogs();
  updateCounts(allLogs);
  renderTable(allLogs);
  tryLoadFromBackend();

  document.getElementById('audit-search').addEventListener('input', applyFilters);
  document.getElementById('audit-filter').addEventListener('change', applyFilters);
  document.getElementById('refresh-btn').addEventListener('click', () => {
    const btn = document.getElementById('refresh-btn');
    btn.innerHTML = '<span class="spinner"></span>';
    btn.disabled = true;
    setTimeout(() => {
      const logs = getAllLogs();
      updateCounts(logs);
      renderTable(logs);
      applyFilters();
      btn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Refresh';
      btn.disabled = false;
    }, 600);
  });
});
