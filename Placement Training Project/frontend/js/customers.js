/**
 * PP.PRICING — Customer Segments Page
 * Connects to /api/v1/customer/segment and /api/v1/customer/segments
 */

const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';

const SEGMENT_COLORS = {
  VIP:             '#00f2fe',
  Regular:         '#4facfe',
  Budget_Conscious:'#ff9f0a',
  Inactive:        '#ff3b5c',
  New:             '#7f00ff'
};

const SEGMENT_ICONS = {
  VIP:             'fa-crown',
  Regular:         'fa-user-check',
  Budget_Conscious:'fa-piggy-bank',
  Inactive:        'fa-user-clock',
  New:             'fa-user-plus'
};

const DEMO_SEGMENTS = {
  VIP:             { description:'High-value, loyal customers', recommended_discount:5,  retention_probability:0.95, price_elasticity:-0.5  },
  Regular:         { description:'Consistent purchase pattern', recommended_discount:3,  retention_probability:0.75, price_elasticity:-1.0  },
  Budget_Conscious:{ description:'Price-sensitive, respond to discounts', recommended_discount:15, retention_probability:0.6, price_elasticity:-2.0 },
  Inactive:        { description:'Low activity, need re-engagement', recommended_discount:20, retention_probability:0.4, price_elasticity:-1.5 },
  New:             { description:'New customers, acquisition phase', recommended_discount:10, retention_probability:0.5, price_elasticity:-1.8 }
};

// Distribution for demo pie chart
const DEMO_DIST = { VIP:15, Regular:35, Budget_Conscious:25, Inactive:10, New:15 };

async function callAPI(path, body = null) {
  const opts = { method: body ? 'POST' : 'GET', headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

let segChart = null;

function renderPieChart(distribution) {
  const ctx = document.getElementById('segChart').getContext('2d');
  if (segChart) segChart.destroy();

  const labels = Object.keys(distribution);
  const values = Object.values(distribution);
  const colors = labels.map(l => SEGMENT_COLORS[l] || '#4e5568');

  segChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.map(c => c + '90'),
        borderColor: colors,
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#8b92a9', font: { family: 'Inter', size: 12 }, boxWidth: 12, padding: 14 }
        },
        tooltip: {
          backgroundColor: 'rgba(10,15,28,0.95)',
          borderColor: 'rgba(0,242,254,0.3)',
          borderWidth: 1,
          titleColor: '#00f2fe',
          bodyColor: '#f0f2f8',
          callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}%` }
        }
      },
      cutout: '65%'
    }
  });
}

function renderSegmentCards(segments) {
  const container = document.getElementById('seg-cards');
  container.innerHTML = Object.entries(segments).map(([name, info]) => {
    const color = SEGMENT_COLORS[name] || '#4e5568';
    const icon  = SEGMENT_ICONS[name]  || 'fa-user';
    return `
      <div class="seg-card" style="border-left:3px solid ${color}20;border-color:${color}30;">
        <div class="seg-title" style="color:${color};">
          <i class="fa-solid ${icon}" style="margin-right:0.4rem;"></i>${name.replace('_', ' ')}
        </div>
        <div class="seg-desc">${info.description}</div>
        <div class="seg-stat">Discount: ${info.recommended_discount}% • Retention: ${(info.retention_probability * 100).toFixed(0)}%</div>
      </div>`;
  }).join('');
}

async function loadSegments() {
  try {
    const res = await callAPI('/customer/segments');
    if (res && typeof res === 'object') {
      renderSegmentCards(res);
      document.getElementById('seg-loaded-badge').style.display = 'inline-flex';
    }
  } catch {
    renderSegmentCards(DEMO_SEGMENTS);
  }
  renderPieChart(DEMO_DIST);
}

function showClsError(msg) {
  const el = document.getElementById('cls-error');
  el.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
  el.style.display = 'flex';
  setTimeout(() => el.style.display = 'none', 6000);
}

function showClassification(res) {
  const seg      = res.segment || 'Regular';
  const color    = SEGMENT_COLORS[seg] || '#4facfe';
  const badge    = document.getElementById('seg-name-badge');
  badge.textContent  = seg.replace('_', ' ');
  badge.style.display = 'inline-flex';
  badge.style.background = color + '20';
  badge.style.borderColor = color + '50';
  badge.style.color = color;

  document.getElementById('cls-placeholder').style.display = 'none';
  const block = document.getElementById('cls-result-block');
  block.classList.add('visible');
  block.innerHTML = `
    <div class="result-row"><span class="label">Customer Segment</span><span class="value" style="color:${color};">${seg.replace('_', ' ')}</span></div>
    <div class="result-row"><span class="label">Segment Description</span><span class="value">${res.segment_description || '—'}</span></div>
    <div class="result-row"><span class="label">Recommended Discount</span><span class="value green">${res.recommended_discount ?? '—'}%</span></div>
    <div class="result-row"><span class="label">Retention Probability</span><span class="value cyan">${res.retention_probability != null ? (res.retention_probability * 100).toFixed(0) + '%' : '—'}</span></div>
    <div class="result-row"><span class="label">Price Elasticity</span><span class="value">${res.price_elasticity ?? '—'}</span></div>
    <div class="result-row"><span class="label">Churn Risk</span><span class="value ${res.churn_risk === 'high' ? 'magenta' : res.churn_risk === 'medium' ? 'amber' : 'green'}">${res.churn_risk ? res.churn_risk.toUpperCase() : '—'}</span></div>
  `;

  if (res.personalized_pricing_strategy) {
    document.getElementById('cls-strategy').style.display = 'block';
    document.getElementById('cls-strategy-text').textContent = res.personalized_pricing_strategy;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSegments();

  document.getElementById('classify-btn').addEventListener('click', async () => {
    const btn = document.getElementById('classify-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Classifying…';

    const payload = {
      purchase_frequency:        parseInt(document.getElementById('pur_freq').value, 10),
      average_order_value:       parseFloat(document.getElementById('avg_order').value),
      customer_lifetime_value:   parseFloat(document.getElementById('clv').value),
      loyalty_score:             parseFloat(document.getElementById('loyalty').value),
      days_since_purchase:       parseInt(document.getElementById('days_since').value, 10)
    };

    try {
      const res = await callAPI('/customer/segment', payload);
      showClassification(res);
    } catch (err) {
      // Demo fallback based on basic rules
      const loy = payload.loyalty_score;
      const seg = loy > 0.8 ? 'VIP' : loy > 0.5 ? 'Regular' : payload.days_since_purchase > 90 ? 'Inactive' : 'Budget_Conscious';
      showClassification({
        segment: seg,
        segment_description: DEMO_SEGMENTS[seg]?.description,
        recommended_discount: DEMO_SEGMENTS[seg]?.recommended_discount,
        retention_probability: DEMO_SEGMENTS[seg]?.retention_probability,
        price_elasticity: DEMO_SEGMENTS[seg]?.price_elasticity,
        churn_risk: seg === 'Inactive' ? 'high' : seg === 'Budget_Conscious' ? 'medium' : 'low',
        personalized_pricing_strategy: `Apply a ${DEMO_SEGMENTS[seg]?.recommended_discount}% targeted discount to maximize conversion for this ${seg.replace('_',' ')} customer.`
      });
      showClsError(`Backend offline — showing estimated result. Error: ${err.message}`);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-user-magnifying-glass"></i> Classify Customer';
    }
  });
});
