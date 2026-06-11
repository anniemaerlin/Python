/**
 * PP.PRICING — Dynamic Pricing Page
 * Connects to /api/v1/pricing/predict and /api/v1/pricing/predict-with-explanation
 */

const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
let predictionCount = 0;

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

function getFormData() {
  return {
    current_price:    parseFloat(document.getElementById('current_price').value),
    competitor_price: parseFloat(document.getElementById('competitor_price').value),
    demand:           parseInt(document.getElementById('demand').value, 10),
    inventory:        parseInt(document.getElementById('inventory').value, 10),
    conversion_rate:  parseFloat(document.getElementById('conversion_rate').value),
    promotion:        parseInt(document.getElementById('promotion').value, 10),
    discount_percent: parseFloat(document.getElementById('discount_percent').value),
    demand_index:     parseFloat(document.getElementById('demand_index').value)
  };
}

function showError(msg) {
  const box = document.getElementById('error-box');
  box.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
  box.style.display = 'flex';
  setTimeout(() => { box.style.display = 'none'; }, 6000);
}

function clearError() {
  document.getElementById('error-box').style.display = 'none';
}

function showResult(data) {
  const cp    = parseFloat(document.getElementById('current_price').value);
  const rp    = data.recommended_price;
  const diff  = ((rp - cp) / cp * 100).toFixed(1);
  const sign  = diff >= 0 ? '+' : '';

  document.getElementById('r-price').textContent      = `₹${rp.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
  document.getElementById('r-change').textContent     = `${sign}${diff}%`;
  document.getElementById('r-confidence').textContent = `${data.confidence_score?.toFixed(1) ?? '—'}%`;
  document.getElementById('r-revenue').textContent    = data.revenue_impact
    ? `₹${data.revenue_impact.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    : '—';
  document.getElementById('r-model').textContent      = data.model_used || '—';

  const modelBadge = document.getElementById('model-badge');
  modelBadge.textContent = data.model_used || '—';
  modelBadge.style.display = 'inline-flex';

  document.getElementById('loading-state').style.display = 'none';
  document.getElementById('result-block').classList.add('visible');

  // Color the change
  const changeEl = document.getElementById('r-change');
  changeEl.className = `value ${parseFloat(diff) >= 0 ? 'green' : 'magenta'}`;

  predictionCount++;
  const cntEl = document.getElementById('predict-count');
  if (cntEl) cntEl.textContent = `Predictions: ${predictionCount}`;
}

function showExplanation(data) {
  const block = document.getElementById('explain-block');
  block.style.display = 'block';

  document.getElementById('r-explanation').textContent = data.explanation || '';

  const factorsEl = document.getElementById('r-factors');
  if (data.top_factors && Array.isArray(data.top_factors)) {
    factorsEl.innerHTML = data.top_factors.map(f => `
      <div style="display:flex;align-items:center;gap:0.6rem;padding:0.45rem 0.75rem;background:rgba(255,255,255,0.02);border:1px solid var(--border-glass);border-radius:8px;font-size:0.83rem;">
        <i class="fa-solid fa-circle-dot" style="color:var(--primary-cyan);font-size:0.6rem;"></i>
        <span style="color:var(--text-main);">${f}</span>
      </div>`).join('');
  }
}

function setLoading(btn, loading) {
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Predicting…';
  } else {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Predict Optimal Price';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('pricing-form');
  const explainBtn = document.getElementById('explain-btn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();
    const btn = document.getElementById('predict-btn');
    setLoading(btn, true);
    document.getElementById('explain-block').style.display = 'none';

    const model   = document.getElementById('model-select').value;
    const payload = getFormData();

    try {
      const data = await callAPI(`/pricing/predict?model=${model}`, payload);
      showResult(data);
    } catch (err) {
      // Graceful fallback: show estimated result
      const cp = payload.current_price;
      const est = {
        recommended_price: parseFloat((cp * 1.125).toFixed(2)),
        confidence_score:  87.5,
        revenue_impact:    cp * 150,
        model_used:        model === 'xgboost' ? 'XGBoost (demo)' : 'Random Forest (demo)',
        price_change_percent: 12.5
      };
      showResult(est);
      showError(`Backend offline — showing estimated result. Error: ${err.message}`);
    } finally {
      setLoading(btn, false);
    }
  });

  explainBtn.addEventListener('click', async () => {
    clearError();
    const payload = getFormData();
    const model   = document.getElementById('model-select').value;

    explainBtn.disabled = true;
    explainBtn.innerHTML = '<span class="spinner"></span> Analyzing…';

    try {
      const data = await callAPI(`/pricing/predict-with-explanation?model=${model}`, payload);
      showResult(data);
      showExplanation(data);
    } catch (err) {
      showError(`Explanation unavailable: ${err.message}`);
    } finally {
      explainBtn.disabled = false;
      explainBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass-chart"></i> Explain Prediction';
    }
  });
});
