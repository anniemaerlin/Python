/**
 * PP.PRICING — Demand Forecast Page
 * Connects to /api/v1/forecast/demand and /api/v1/forecast/inventory-recommendation
 */

const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
let forecastChart = null;

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
  const el = document.getElementById('fc-error');
  el.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
  el.style.display = 'flex';
  setTimeout(() => el.style.display = 'none', 6000);
}

function renderChart(historical, forecasted, labels, lowerCI, upperCI) {
  const ctx = document.getElementById('forecastChart').getContext('2d');
  if (forecastChart) forecastChart.destroy();

  const histCount = historical.length;
  const forecastCount = forecasted.length;
  const allLabels = [
    ...labels,
    ...Array.from({ length: forecastCount }, (_, i) => `+${i + 1}d`)
  ];

  // Build padded arrays
  const histData    = [...historical, ...Array(forecastCount).fill(null)];
  const fcData      = [...Array(histCount - 1).fill(null), historical[histCount - 1], ...forecasted];
  const lowerData   = [...Array(histCount - 1).fill(null), historical[histCount - 1], ...lowerCI];
  const upperData   = [...Array(histCount - 1).fill(null), historical[histCount - 1], ...upperCI];

  forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allLabels,
      datasets: [
        {
          label: 'Historical Demand',
          data: histData,
          borderColor: '#00f2fe',
          backgroundColor: 'rgba(0,242,254,0.07)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: '#00f2fe'
        },
        {
          label: 'Forecast',
          data: fcData,
          borderColor: '#ff007f',
          borderDash: [5, 4],
          backgroundColor: 'rgba(255,0,127,0.06)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: '#ff007f'
        },
        {
          label: 'Upper CI',
          data: upperData,
          borderColor: 'rgba(127,0,255,0.4)',
          borderDash: [3, 3],
          borderWidth: 1,
          fill: false,
          pointRadius: 0,
          tension: 0.4
        },
        {
          label: 'Lower CI',
          data: lowerData,
          borderColor: 'rgba(127,0,255,0.4)',
          borderDash: [3, 3],
          borderWidth: 1,
          fill: '-1',
          backgroundColor: 'rgba(127,0,255,0.05)',
          pointRadius: 0,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#8b92a9', font: { family: 'Inter' }, boxWidth: 12, padding: 16 }
        },
        tooltip: {
          backgroundColor: 'rgba(10,15,28,0.95)',
          borderColor: 'rgba(0,242,254,0.3)',
          borderWidth: 1,
          titleColor: '#00f2fe',
          bodyColor: '#f0f2f8',
          padding: 10
        }
      },
      scales: {
        x: {
          ticks: { color: '#4e5568', maxTicksLimit: 12, font: { family: 'Space Grotesk' } },
          grid: { color: 'rgba(255,255,255,0.04)' }
        },
        y: {
          ticks: { color: '#4e5568', font: { family: 'Space Grotesk' } },
          grid: { color: 'rgba(255,255,255,0.04)' }
        }
      }
    }
  });
}

function renderInsights(res) {
  const container = document.getElementById('fc-insights');
  const trendBadge = document.getElementById('fc-trend-badge');
  const accBadge   = document.getElementById('fc-acc-badge');

  const trend = res.trend || 'medium';
  const acc   = res.prediction_accuracy != null ? res.prediction_accuracy.toFixed(1) : null;

  trendBadge.textContent = `Trend: ${trend.toUpperCase()}`;
  trendBadge.className = `badge ${trend === 'high' ? 'badge-success' : trend === 'low' ? 'badge-danger' : 'badge-cyan'}`;
  trendBadge.style.display = 'inline-flex';

  if (acc) {
    accBadge.textContent = `Accuracy: ${acc}%`;
    accBadge.className = 'badge badge-amber';
    accBadge.style.display = 'inline-flex';
  }

  const avgFc = res.forecasted_demand
    ? (res.forecasted_demand.reduce((a, b) => a + b, 0) / res.forecasted_demand.length).toFixed(0)
    : '—';

  // confidence_interval_lower/upper are arrays — show their range (min to max)
  const ciLowerArr = Array.isArray(res.confidence_interval_lower) ? res.confidence_interval_lower : [];
  const ciUpperArr = Array.isArray(res.confidence_interval_upper) ? res.confidence_interval_upper : [];
  const ciLowerStr = ciLowerArr.length ? Math.min(...ciLowerArr).toFixed(1) + ' – ' + Math.max(...ciLowerArr).toFixed(1) : '—';
  const ciUpperStr = ciUpperArr.length ? Math.min(...ciUpperArr).toFixed(1) + ' – ' + Math.max(...ciUpperArr).toFixed(1) : '—';

  container.innerHTML = `
    <div class="result-block visible">
      <div class="result-row"><span class="label">Avg Forecasted Demand</span><span class="value">${avgFc} units/day</span></div>
      <div class="result-row"><span class="label">Trend Direction</span><span class="value ${trend === 'high' ? 'green' : trend === 'low' ? 'magenta' : 'cyan'}">${trend.toUpperCase()}</span></div>
      <div class="result-row"><span class="label">Prediction Accuracy</span><span class="value">${acc ? acc + '%' : '—'}</span></div>
      <div class="result-row"><span class="label">CI Lower Range</span><span class="value">${ciLowerStr}</span></div>
      <div class="result-row"><span class="label">CI Upper Range</span><span class="value">${ciUpperStr}</span></div>
    </div>`;
}

async function runForecast() {
  const btn      = document.getElementById('forecast-btn');
  btn.disabled   = true;
  btn.innerHTML  = '<span class="spinner"></span> Running…';

  const histRaw = document.getElementById('hist_data').value;
  const historical = histRaw.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));

  if (historical.length < 3) {
    showError('Need at least 3 historical data points (comma-separated).');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-chart-area"></i> Run Forecast';
    return;
  }

  const payload = {
    product_id:       document.getElementById('product_id').value || 'PROD-001',
    historical_demand: historical,
    days_ahead:       parseInt(document.getElementById('days_ahead').value, 10) || 30
  };
  const seasonality = document.getElementById('seasonality').value;

  try {
    const res = await callAPI(`/forecast/demand?seasonality=${seasonality}`, payload);

    const labels     = historical.map((_, i) => `D${i + 1}`);
    const forecasted = res.forecasted_demand || [];

    // confidence_interval_lower/upper are arrays from backend — use them directly
    // or fall back to ±12% estimate if missing
    const lower = Array.isArray(res.confidence_interval_lower)
      ? res.confidence_interval_lower
      : forecasted.map(v => v * 0.88);
    const upper = Array.isArray(res.confidence_interval_upper)
      ? res.confidence_interval_upper
      : forecasted.map(v => v * 1.12);

    renderChart(historical, forecasted, labels, lower, upper);
    renderInsights(res);

    // Try to get inventory recommendation
    try {
      const invRes = await callAPI('/forecast/inventory-recommendation', {
        product_id: payload.product_id,
        historical_demand: historical,
        current_inventory: 150,
        lead_time_days: 7
      });
      const invCard = document.getElementById('inv-card');
      const invContent = document.getElementById('inv-content');
      invCard.style.display = 'block';
      invContent.innerHTML = `
        <div class="result-row"><span class="label">Recommended Reorder Point</span><span class="value green">${invRes.reorder_point ?? '—'} units</span></div>
        <div class="result-row"><span class="label">Recommended Order Quantity</span><span class="value cyan">${invRes.recommended_order_quantity ?? '—'} units</span></div>
        <div class="result-row"><span class="label">Days of Supply</span><span class="value">${invRes.days_of_supply ?? '—'} days</span></div>
        <div class="result-row"><span class="label">Stock Status</span><span class="value ${invRes.is_understocked ? 'magenta' : 'green'}">${invRes.is_understocked ? '⚠ Understocked' : '✓ Adequate'}</span></div>
      `;
    } catch (_) { /* inventory recommendation optional */ }

  } catch (err) {
    // Demo fallback
    const forecast30 = Array.from({ length: 30 }, (_, i) => {
      const base = historical[historical.length - 1] || 80;
      return parseFloat((base + i * 0.8 + (Math.random() - 0.5) * 5).toFixed(1));
    });
    const labels = historical.map((_, i) => `D${i + 1}`);
    renderChart(historical, forecast30.slice(0, 7), labels, forecast30.slice(0,7).map(v=>v*0.88), forecast30.slice(0,7).map(v=>v*1.12));
    renderInsights({ trend: 'medium', prediction_accuracy: 85, forecasted_demand: forecast30.slice(0,7) });
    showError(`Backend offline — showing estimated forecast. Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-chart-area"></i> Run Forecast';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Load initial demo chart
  const demoHist = [50,55,53,60,65,70,68,72,75,78,80,82,85,88,90,92,88,94,97,100];
  const demoFc   = [103,106,109,107,112,115,118];
  renderChart(
    demoHist, demoFc,
    demoHist.map((_, i) => `D${i + 1}`),
    demoFc.map(v => v * 0.88),
    demoFc.map(v => v * 1.12)
  );

  document.getElementById('forecast-btn').addEventListener('click', runForecast);
});
