/**
 * PP.PRICING — Competitor Analysis Page
 * Connects to /api/v1/competitor/analyze and /api/v1/competitor/pricing-strategy
 */

const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
let compBarChart = null;

async function callAPI(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function showError(msg) {
  const el = document.getElementById('comp-error');
  el.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
  el.style.display = 'flex';
  setTimeout(() => el.style.display = 'none', 6000);
}

function getCompetitorPrices() {
  const rows = document.querySelectorAll('.comp-input-row');
  const prices = {};
  rows.forEach(row => {
    const inputs = row.querySelectorAll('input');
    const name = inputs[0]?.value?.trim();
    const price = parseFloat(inputs[1]?.value);
    if (name && !isNaN(price)) prices[name] = price;
  });
  return prices;
}

function renderCompCards(yourPrice, competitorPrices) {
  const grid = document.getElementById('comp-cards-grid');
  const entries = Object.entries(competitorPrices);
  grid.innerHTML = entries.map(([name, price]) => {
    const diff    = ((price - yourPrice) / yourPrice * 100);
    const dir     = diff >= 0 ? 'up' : 'down';
    const diffStr = `${diff >= 0 ? '+' : ''}${diff.toFixed(1)}%`;
    return `
      <div class="comp-card ${dir}">
        <div class="comp-brand">
          <span class="comp-name">${name}</span>
          <span class="glow-dot ${dir}"></span>
        </div>
        <div class="comp-price">₹${price.toLocaleString('en-IN')}</div>
        <div class="comp-diff ${dir}">
          <i class="fa-solid fa-arrow-trend-${dir === 'up' ? 'up' : 'down'}"></i>
          <span>${diffStr}</span>
        </div>
      </div>`;
  }).join('');
  document.getElementById('comp-count-badge').textContent = `${entries.length} Competitors`;
}

function renderBarChart(yourPrice, competitorPrices) {
  const ctx = document.getElementById('compChart').getContext('2d');
  if (compBarChart) compBarChart.destroy();

  const names  = ['Your Price', ...Object.keys(competitorPrices)];
  const prices = [yourPrice, ...Object.values(competitorPrices)];
  const colors = prices.map((p, i) => i === 0 ? 'rgba(0,242,254,0.8)' : p > yourPrice ? 'rgba(57,255,20,0.7)' : 'rgba(255,0,127,0.7)');
  const borders= prices.map((p, i) => i === 0 ? '#00f2fe' : p > yourPrice ? '#39ff14' : '#ff007f');

  compBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: names,
      datasets: [{
        label: 'Price (₹)',
        data: prices,
        backgroundColor: colors,
        borderColor: borders,
        borderWidth: 1.5,
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(10,15,28,0.95)',
          borderColor: 'rgba(0,242,254,0.3)',
          borderWidth: 1,
          titleColor: '#00f2fe',
          bodyColor: '#f0f2f8',
          callbacks: { label: (ctx) => ` ₹${ctx.raw.toLocaleString('en-IN')}` }
        }
      },
      scales: {
        x: {
          ticks: { color: '#8b92a9', font: { family: 'Inter' } },
          grid: { color: 'rgba(255,255,255,0.04)' }
        },
        y: {
          ticks: { color: '#8b92a9', font: { family: 'Space Grotesk' }, callback: (v) => '₹' + v.toLocaleString('en-IN') },
          grid: { color: 'rgba(255,255,255,0.04)' },
          beginAtZero: false
        }
      }
    }
  });
}

function renderSummary(res) {
  const block = document.getElementById('comp-summary-block');
  block.classList.add('visible');

  const pos   = res.price_position || '—';
  const posEl = document.getElementById('position-badge');
  posEl.textContent = pos.toUpperCase();
  posEl.style.display = 'inline-flex';
  if (pos.toLowerCase() === 'below')    { posEl.className = 'badge badge-success'; }
  else if (pos.toLowerCase() === 'above') { posEl.className = 'badge badge-magenta'; }
  else                                    { posEl.className = 'badge badge-cyan'; }

  block.innerHTML = `
    <div class="result-row"><span class="label">Avg Competitor Price</span><span class="value">₹${res.average_competitor_price?.toLocaleString('en-IN') ?? '—'}</span></div>
    <div class="result-row"><span class="label">Your Price Position</span><span class="value ${pos === 'below' ? 'green' : pos === 'above' ? 'magenta' : 'cyan'}">${pos.toUpperCase()}</span></div>
    <div class="result-row"><span class="label">Price Difference</span><span class="value">${res.price_difference_percent != null ? res.price_difference_percent.toFixed(1) + '%' : '—'}</span></div>
    <div class="result-row"><span class="label">Recommended Action</span><span class="value cyan">${res.recommended_action || '—'}</span></div>
    <div class="result-row"><span class="label">Market Share Potential</span><span class="value green">${res.market_share_potential != null ? res.market_share_potential.toFixed(1) + '%' : '—'}</span></div>
  `;
}

function renderStrategy(res) {
  const content = document.getElementById('strategy-content');
  content.innerHTML = `
    <div class="result-block visible">
      <div class="result-row"><span class="label">Strategy</span><span class="value cyan">${res.strategy || '—'}</span></div>
      <div class="result-row"><span class="label">Suggested Price</span><span class="value green">${res.suggested_price ? '₹' + res.suggested_price.toLocaleString('en-IN') : '—'}</span></div>
    </div>
    ${res.rationale ? `<p style="margin-top:1rem;font-size:0.87rem;color:var(--text-secondary);line-height:1.55;">${res.rationale}</p>` : ''}
  `;
}

async function runAnalysis() {
  const btn = document.getElementById('analyze-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analyzing…';

  const yourPrice = parseFloat(document.getElementById('your_price').value);
  const productId = document.getElementById('prod_id').value || 'PROD-001';
  const compPrices = getCompetitorPrices();

  if (Object.keys(compPrices).length === 0) {
    showError('Add at least one competitor price.');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-chart-bar"></i> Analyze';
    return;
  }

  renderCompCards(yourPrice, compPrices);
  renderBarChart(yourPrice, compPrices);

  const payload = { product_id: productId, your_current_price: yourPrice, competitor_prices: compPrices };

  try {
    const res = await callAPI('/competitor/analyze', payload);
    renderSummary(res);
  } catch (err) {
    // Demo fallback
    const avgPrice = Object.values(compPrices).reduce((a, b) => a + b, 0) / Object.values(compPrices).length;
    const diff = ((yourPrice - avgPrice) / avgPrice * 100).toFixed(1);
    const pos  = yourPrice > avgPrice ? 'above' : yourPrice < avgPrice ? 'below' : 'at';
    renderSummary({
      average_competitor_price: avgPrice,
      price_position: pos,
      price_difference_percent: parseFloat(Math.abs(diff)),
      recommended_action: pos === 'above' ? 'Consider slight reduction to capture market share' : 'Maintain or increase price — you are below market',
      market_share_potential: pos === 'below' ? 65 : 42
    });
    showError(`Backend offline — showing estimated analysis. Error: ${err.message}`);
  }

  try {
    const stratRes = await callAPI('/competitor/pricing-strategy', payload);
    renderStrategy(stratRes);
  } catch {
    renderStrategy({
      strategy: 'Competitive Matching',
      suggested_price: Math.round(Object.values(compPrices).reduce((a,b)=>a+b,0) / Object.values(compPrices).length * 0.97),
      rationale: 'Price slightly below market average to maximize volume while maintaining healthy margins.'
    });
  }

  btn.disabled = false;
  btn.innerHTML = '<i class="fa-solid fa-chart-bar"></i> Analyze';
}

document.addEventListener('DOMContentLoaded', () => {
  // Add competitor row button
  document.getElementById('add-comp-btn').addEventListener('click', () => {
    const container = document.getElementById('competitor-inputs');
    const row = document.createElement('div');
    row.className = 'comp-input-row';
    row.style.cssText = 'display:flex;gap:0.5rem;margin-bottom:0.6rem;';
    row.innerHTML = `
      <input type="text" placeholder="Competitor name" style="flex:1;background:rgba(255,255,255,0.04);border:1px solid var(--border-glass);border-radius:8px;color:var(--text-main);padding:0.55rem 0.75rem;font-size:0.85rem;outline:none;">
      <input type="number" placeholder="Price" style="width:90px;background:rgba(255,255,255,0.04);border:1px solid var(--border-glass);border-radius:8px;color:var(--text-main);padding:0.55rem 0.75rem;font-size:0.85rem;outline:none;font-family:var(--font-mono);">
      <button onclick="this.parentElement.remove()" style="background:rgba(255,59,92,0.1);border:1px solid rgba(255,59,92,0.3);border-radius:8px;color:#ff3b5c;padding:0 0.6rem;cursor:pointer;font-size:1rem;">×</button>
    `;
    container.appendChild(row);
  });

  document.getElementById('analyze-btn').addEventListener('click', runAnalysis);

  // Auto-run with demo data on load
  setTimeout(() => {
    const yourPrice = 1200;
    const compPrices = { Amazon: 1280, Flipkart: 1320, Meesho: 1180, 'Reliance Digital': 1300 };
    renderCompCards(yourPrice, compPrices);
    renderBarChart(yourPrice, compPrices);
  }, 100);
});
