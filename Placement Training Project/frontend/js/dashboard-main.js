/**
 * PP.PRICING — Dashboard Controller
 * NO GSAP opacity animations — cards are always visible.
 * Backend data is used only to UPDATE values, never to block rendering.
 */

const API = 'http://localhost:8000/api/v1';

/* ─── Pure demo data (always shown first) ─── */
const DEMO = {
  currentPrice:     1200,
  recommendedPrice: 1350,
  priceChangePct:   12.5,
  confidence:       94,
  revenueImpact:    21500,
  baseDemand:       1324,
  costPerUnit:      840,
  elasticity:       1.6,
  competitors: [
    { name:'Amazon',           price:1280, diff:6.7,  dir:'up'   },
    { name:'Flipkart',         price:1320, diff:10.0, dir:'up'   },
    { name:'Meesho',           price:1180, diff:-1.7, dir:'down' },
    { name:'Reliance Digital', price:1300, diff:8.3,  dir:'up'   }
  ],
  features: [
    { name:'Demand',           value:45, cls:'cyan'    },
    { name:'Competitor Price', value:25, cls:'purple'  },
    { name:'Inventory',        value:15, cls:'magenta' },
    { name:'Promotion',        value:10, cls:'amber'   },
    { name:'Others',           value:5,  cls:'muted'   }
  ],
  insights: [
    { type:'info',    icon:'fa-bolt',                 sender:'AI Predictor',     text:'Demand surge expected at 7 PM based on local traffic forecasting.',        time:'2 mins ago'  },
    { type:'urgent',  icon:'fa-triangle-exclamation', sender:'AI Monitor',       text:'Inventory running low. Exhaustion predicted in 14 hours.',                 time:'5 mins ago'  },
    { type:'alert',   icon:'fa-store',                sender:'Competitor Watch', text:'Flipkart dropped category prices by 8% — review recommended.',             time:'12 mins ago' },
    { type:'success', icon:'fa-coins',                sender:'Revenue Strategy', text:'Revenue opportunity: upward price elasticity holds for next 4 hours.',     time:'20 mins ago' }
  ],
  timeline: [
    { title:'Price Optimised',   desc:'AI optimised pricing to ₹1,350 (+12.5% increase).',         time:'10:30 AM', style:'active'  },
    { title:'Demand Spike',      desc:'Real-time traffic spiked by 28% on matched inventory.',      time:'10:15 AM', style:'warning' },
    { title:'Inventory Alert',   desc:'Available inventory dipped below safety margin (45 units).',  time:'09:45 AM', style:'error'   },
    { title:'Competitor Action', desc:'Reliance Digital reduced pricing on equivalents by 3.5%.',    time:'09:20 AM', style:'active'  }
  ],
  kpis: [
    { label:'Revenue',     val:'₹2,45,230', trend:'+12.5%', dir:'up',   icon:'fa-indian-rupee-sign', spark:[210,225,220,235,230,240,245],       color:'#00f2fe' },
    { label:'Demand',      val:'78%',        trend:'+8.0%',  dir:'up',   icon:'fa-fire-flame-curve',  spark:[60,65,63,72,70,75,78],              color:'#ff007f' },
    { label:'Orders',      val:'1,324',      trend:'+15.2%', dir:'up',   icon:'fa-cart-shopping',     spark:[1100,1150,1130,1220,1200,1280,1324], color:'#7f00ff' },
    { label:'Conv. Rate',  val:'3.42%',      trend:'+4.8%',  dir:'up',   icon:'fa-bullseye',          spark:[2.9,3.1,3.0,3.25,3.2,3.35,3.42],   color:'#4facfe' },
    { label:'Inventory',   val:'91%',        trend:'-2.0%',  dir:'down', icon:'fa-warehouse',         spark:[98,96,95,94,93,92,91],              color:'#ff9f0a' }
  ]
};

/* ─── Helpers ─── */
function inr(n) {
  return Math.round(Math.abs(n)).toLocaleString('en-IN');
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function animateCount(id, target, prefix, suffix, decimals) {
  const el = document.getElementById(id);
  if (!el) return;
  const safe = isFinite(target) ? Math.abs(target) : 0;
  const t0   = performance.now();
  const dur  = 1200;
  const tick = (now) => {
    const p   = Math.min((now - t0) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const cur  = ease * safe;
    el.textContent = (prefix || '') +
      (decimals ? cur.toFixed(decimals) : Math.round(cur).toLocaleString('en-IN')) +
      (suffix || '');
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

async function apiPost(path, body) {
  const r = await fetch(API + path, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

/* ═══════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {

  /* 1 ── Render EVERYTHING from demo data immediately ── */
  renderStats(DEMO);
  renderRecommendation(DEMO);
  renderCompetitors(DEMO.competitors);
  initSimulator(DEMO);
  renderHeatmap();
  renderFeatures(DEMO.features);
  renderInsights(DEMO.insights);
  renderTimeline(DEMO.timeline);
  renderKPIs(DEMO.kpis);
  startClock();
  animateBars();

  /* 2 ── Fetch live data in background, update silently ── */
  try {
    const livePayload = {
      current_price:    DEMO.currentPrice,
      competitor_price: DEMO.competitors[0].price,
      demand:           200,
      inventory:        50,
      conversion_rate:  0.12,
      promotion:        1,
      discount_percent: 0,
      demand_index:     0.75
    };
    const res = await apiPost('/pricing/predict', livePayload);

    // Only update if values are sensible (recommended > 0)
    if (res.recommended_price && res.recommended_price > 0) {
      const live = {
        ...DEMO,
        recommendedPrice: res.recommended_price,
        confidence:       res.confidence_score    ?? DEMO.confidence,
        revenueImpact:    Math.abs(res.revenue_impact ?? DEMO.revenueImpact),
        priceChangePct:   res.price_change_percent ?? DEMO.priceChangePct
      };
      renderStats(live);
      renderRecommendation(live);
      console.log('✅ Live pricing applied:', res.recommended_price);
    }
  } catch (e) {
    console.warn('⚠️ Using demo pricing data:', e.message);
  }

  try {
    const cr = await apiPost('/competitor/analyze', {
      product_id:        'prod-001',
      your_current_price: DEMO.currentPrice,
      competitor_prices:  { Amazon:1280, Flipkart:1320, Meesho:1180, 'Reliance Digital':1300 }
    });
    if (cr.competitor_breakdown) {
      const comps = Object.entries(cr.competitor_breakdown).map(([name, info]) => {
        const diff = ((info.price - DEMO.currentPrice) / DEMO.currentPrice) * 100;
        return { name, price: info.price, diff: parseFloat(diff.toFixed(1)), dir: diff >= 0 ? 'up' : 'down' };
      });
      renderCompetitors(comps);
      console.log('✅ Live competitor data applied');
    }
  } catch (e) {
    console.warn('⚠️ Using demo competitor data:', e.message);
  }
});

/* ─────────────────────────────────────── */
function renderStats(d) {
  animateCount('s-current',     d.currentPrice,     '₹', '',  0);
  animateCount('s-recommended', d.recommendedPrice, '₹', '',  0);
  animateCount('s-revenue',     d.revenueImpact,    '₹', '',  0);
  animateCount('s-confidence',  d.confidence,       '',  '%', 0);

  const diffEl = document.getElementById('s-diff');
  if (diffEl) {
    const pct  = parseFloat(d.priceChangePct);
    const sign = pct >= 0 ? '+' : '';
    diffEl.textContent = sign + pct.toFixed(1) + '%';
    diffEl.className   = pct >= 0 ? 'trend-up' : 'trend-down';
  }
}

function renderRecommendation(d) {
  animateCount('rec-current',     d.currentPrice,     '₹', '', 0);
  animateCount('rec-recommended', d.recommendedPrice, '₹', '', 0);
  animateCount('rec-conf',        d.confidence,       '',  '%', 0);

  const pct   = parseFloat(d.priceChangePct);
  const sign  = pct >= 0 ? '+' : '';
  const badge = document.getElementById('rec-badge');
  if (badge) badge.textContent = sign + Math.abs(pct).toFixed(1) + '%';
  const inc = document.getElementById('rec-inc');
  if (inc) inc.textContent = sign + Math.abs(pct).toFixed(1) + '%';
}

function renderCompetitors(comps) {
  const grid = document.getElementById('comp-grid');
  if (!grid) return;
  grid.innerHTML = comps.map(c => `
    <div class="comp-card ${c.dir}">
      <div class="comp-brand">
        <span class="comp-name">${c.name}</span>
        <span class="glow-dot ${c.dir}"></span>
      </div>
      <div class="comp-price">₹${inr(c.price)}</div>
      <div class="comp-diff ${c.dir}">
        <i class="fa-solid fa-arrow-trend-${c.dir === 'up' ? 'up' : 'down'}"></i>
        <span>${c.diff >= 0 ? '+' : ''}${c.diff.toFixed(1)}%</span>
      </div>
    </div>`).join('');
}

function initSimulator(d) {
  const slider  = document.getElementById('sim-slider');
  if (!slider) return;

  const calc = (val) => {
    const pct    = parseFloat(val);
    setText('slider-readout', (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%');
    const demand  = Math.max(0, Math.round(d.baseDemand * (1 - d.elasticity * pct / 100)));
    const price   = d.currentPrice * (1 + pct / 100);
    const revenue = demand * price;
    const profit  = demand * (price - d.costPerUnit) - d.baseDemand * (d.currentPrice - d.costPerUnit);

    setText('sim-revenue', '₹' + Math.round(revenue).toLocaleString('en-IN'));
    setText('sim-demand',  demand.toLocaleString('en-IN'));

    const profEl = document.getElementById('sim-profit');
    if (profEl) {
      profEl.textContent = (profit >= 0 ? '+' : '-') + '₹' + inr(profit);
      profEl.style.color = profit >= 0 ? 'var(--success-neon)' : 'var(--accent-magenta)';
    }
  };

  // Remove duplicate listeners by cloning
  const fresh = slider.cloneNode(true);
  slider.parentNode.replaceChild(fresh, slider);
  fresh.addEventListener('input', e => calc(e.target.value));
  calc(fresh.value);
}

function renderHeatmap() {
  const root = document.getElementById('heatmap-root');
  if (!root || root.children.length > 0) return;
  const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  const hdr = document.createElement('div');
  hdr.className = 'heatmap-header-row';
  [0,4,8,12,16,20].forEach(h => {
    const s = document.createElement('span');
    s.className = 'heatmap-hour-lbl';
    s.style.flex = '4';
    s.textContent = h + ':00';
    hdr.appendChild(s);
  });
  root.appendChild(hdr);

  days.forEach(day => {
    const row = document.createElement('div');
    row.className = 'heatmap-row';
    const lbl = document.createElement('span');
    lbl.className = 'heatmap-day-lbl';
    lbl.textContent = day;
    row.appendChild(lbl);
    const cells = document.createElement('div');
    cells.className = 'heatmap-cells';
    for (let h = 0; h < 24; h++) {
      const c = document.createElement('div');
      c.className = 'h-cell';
      let lvl = 0;
      if      (h >= 18 && h <= 22) lvl = Math.random() > 0.3 ? (Math.random() > 0.5 ? 4 : 3) : 2;
      else if (h >= 12 && h <= 14) lvl = Math.random() > 0.4 ? 3 : 2;
      else if (h >= 8  && h <= 17) lvl = Math.random() > 0.5 ? 2 : 1;
      else if (h <= 5)             lvl = Math.random() > 0.8 ? 1 : 0;
      else                         lvl = 1;
      c.classList.add('l' + lvl);
      c.title = day + ' ' + h + ':00 — Demand: ' + (lvl * 25) + '%';
      cells.appendChild(c);
    }
    row.appendChild(cells);
    root.appendChild(row);
  });

  const leg = document.createElement('div');
  leg.className = 'heatmap-legend';
  leg.innerHTML = '<span>Less</span>' +
    '<div class="leg-swatch h-cell l0"></div>' +
    '<div class="leg-swatch h-cell l1"></div>' +
    '<div class="leg-swatch h-cell l2"></div>' +
    '<div class="leg-swatch h-cell l3"></div>' +
    '<div class="leg-swatch h-cell l4"></div>' +
    '<span>Peak</span>';
  root.appendChild(leg);
}

function renderFeatures(features) {
  const list = document.getElementById('feat-list');
  if (!list) return;
  list.innerHTML = features.map(f => `
    <div class="feat-item">
      <div class="feat-info">
        <span class="feat-name">${f.name}</span>
        <span class="feat-pct">${f.value}%</span>
      </div>
      <div class="feat-bar-bg">
        <div class="feat-bar ${f.cls}" data-w="${f.value}"></div>
      </div>
    </div>`).join('');
}

function renderInsights(insights) {
  const list = document.getElementById('insights-list');
  if (!list) return;
  list.innerHTML = insights.map(i => `
    <div class="insight-card ${i.type}">
      <div class="insight-avatar"><i class="fa-solid ${i.icon}"></i></div>
      <div class="insight-body">
        <div class="insight-sender">${i.sender}</div>
        <div class="insight-text">${i.text}</div>
        <div class="insight-time">${i.time}</div>
      </div>
    </div>`).join('');
}

function renderTimeline(events) {
  const root = document.getElementById('timeline-root');
  if (!root) return;
  root.innerHTML = events.map(e => `
    <div class="t-item ${e.style}">
      <div class="t-marker"><span class="t-dot"></span></div>
      <div class="t-head">
        <span class="t-title">${e.title}</span>
        <span class="t-time">${e.time}</span>
      </div>
      <div class="t-desc">${e.desc}</div>
    </div>`).join('');
}

function renderKPIs(kpis) {
  const row = document.getElementById('kpi-row');
  if (!row || row.children.length > 0) return;
  kpis.forEach((k, i) => {
    const card = document.createElement('div');
    card.className = 'kpi-card';
    const icon = k.dir === 'up' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
    card.innerHTML = `
      <div class="kpi-top">
        <div class="kpi-info">
          <span class="kpi-label">${k.label}</span>
          <span class="kpi-val">${k.val}</span>
        </div>
        <div class="kpi-icon"><i class="fa-solid ${k.icon}"></i></div>
      </div>
      <div class="kpi-spark"><canvas id="ks-${i}"></canvas></div>
      <div class="kpi-foot">
        <span class="kpi-trend ${k.dir}"><i class="fa-solid ${icon}"></i> ${k.trend}</span>
        <span>vs last cycle</span>
      </div>`;
    row.appendChild(card);
    requestAnimationFrame(() => drawSparkline('ks-' + i, k.spark, k.color));
  });
}

function drawSparkline(id, data, color) {
  const canvas = document.getElementById(id);
  if (!canvas || !window.Chart) return;
  const ctx  = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, 42);
  grad.addColorStop(0, color + '30');
  grad.addColorStop(1, 'transparent');
  new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{ data, borderColor: color, borderWidth: 1.8, fill: true,
        backgroundColor: grad, tension: 0.45, pointRadius: 0,
        pointHoverRadius: 3, pointBackgroundColor: color }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales:  { x: { display: false }, y: { display: false } }
    }
  });
}

function startClock() {
  const el = document.getElementById('ts-refresh');
  if (!el) return;
  const tick = () => {
    el.textContent = new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', second:'2-digit' });
  };
  tick();
  setInterval(tick, 1000);
}

function animateBars() {
  setTimeout(() => {
    document.querySelectorAll('.feat-bar[data-w]').forEach(b => {
      b.style.width = b.dataset.w + '%';
    });
  }, 400);
}
