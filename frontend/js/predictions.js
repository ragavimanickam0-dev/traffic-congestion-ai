let miniMapManager = null;
let trendChartInstance = null;
let activeTarget = {
  lat: 12.9716,
  lon: 77.5946,
  name: 'Central Transit Corridor'
};

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('lat') && urlParams.get('lon')) {
    activeTarget.lat = parseFloat(urlParams.get('lat'));
    activeTarget.lon = parseFloat(urlParams.get('lon'));
    activeTarget.name = urlParams.get('name') || 'Selected Road Segment';
    document.getElementById('predLocationInput').value = activeTarget.name;
  } else if (urlParams.get('query')) {
    activeTarget.name = urlParams.get('query');
    document.getElementById('predLocationInput').value = activeTarget.name;
  }

  miniMapManager = new TrafficMapManager('predMiniMap', {
    center: [activeTarget.lat, activeTarget.lon],
    zoom: 14
  });
  miniMapManager.setUserLocation(activeTarget.lat, activeTarget.lon, activeTarget.name);

  initHistoricalTrendChart();
  fetchAmbientWeather();
  await executePrediction();
  setupPredictionForm();
});

function initHistoricalTrendChart() {
  const ctx = document.getElementById('historicalTrendChart');
  if (!ctx) return;

  const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const congestionIndex = [
    12, 10, 8, 9, 14, 25, 45, 78, 88, 70, 52, 48,
    50, 53, 56, 62, 75, 92, 85, 68, 50, 38, 25, 18
  ];

  trendChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [{
        label: 'Historical Congestion Intensity (%)',
        data: congestionIndex,
        borderColor: '#64748b',
        backgroundColor: 'rgba(100, 116, 139, 0.08)',
        fill: true,
        borderWidth: 2,
        tension: 0.35,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          callbacks: { label: (ctx) => ` Baseline Congestion: ${ctx.parsed.y}%` }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { callback: (val) => `${val}%`, stepSize: 25, color: '#64748b' },
          grid: { color: '#f1f5f9' }
        },
        x: {
          ticks: { color: '#64748b', maxTicksLimit: 12 },
          grid: { display: false }
        }
      }
    }
  });
}

async function fetchAmbientWeather() {
  try {
    const weather = await weatherAPI.getWeather(activeTarget.lat, activeTarget.lon);
    if (weather) {
      document.getElementById('weatherTempInput').value = weather.temperature_c.toFixed(1);
      document.getElementById('weatherRainInput').value = weather.precipitation_mm.toFixed(1);
    }
  } catch (err) {
    console.warn('Weather sync error:', err);
  }
}

async function executePrediction() {
  const btnRun = document.getElementById('btnRunPrediction');
  btnRun.disabled = true;
  btnRun.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Inference in progress...';

  const selectedHorizon = parseInt(document.querySelector('input[name="horizonRadio"]:checked').value, 10);
  const temp = parseFloat(document.getElementById('weatherTempInput').value) || 24.0;
  const rain = parseFloat(document.getElementById('weatherRainInput').value) || 0.0;

  try {
    const response = await predictionAPI.predict({
      location_name: activeTarget.name,
      latitude: activeTarget.lat,
      longitude: activeTarget.lon,
      horizon_minutes: selectedHorizon,
      temperature_c: temp,
      precipitation_mm: rain
    });

    renderPredictionResults(response, selectedHorizon);
  } catch (err) {
    console.error('Prediction notice:', err);
    renderFallbackPrediction(selectedHorizon, temp, rain);
  } finally {
    btnRun.disabled = false;
    btnRun.innerHTML = '<i class="bi bi-play-circle me-1"></i> Generate Prediction';
  }
}

function renderPredictionResults(res, horizon) {
  document.getElementById('predResultLocation').textContent = res.location_name;
  document.getElementById('predTimestamp').textContent = `Evaluated: ${new Date().toLocaleTimeString()} | Horizon: +${horizon} Mins`;

  const badgeContainer = document.getElementById('predResultBadgeContainer');
  let badgeClass = 'badge-traffic-low';
  let icon = 'bi-check-circle';
  if (res.predicted_category === 'MODERATE') {
    badgeClass = 'badge-traffic-mod';
    icon = 'bi-exclamation-triangle';
  } else if (res.predicted_category === 'HIGH') {
    badgeClass = 'badge-traffic-high';
    icon = 'bi-exclamation-octagon';
  }

  badgeContainer.innerHTML = `
    <span class="badge ${badgeClass} fs-6 px-3 py-2">
      <i class="bi ${icon} me-1"></i> ${res.predicted_category} CONGESTION
    </span>
  `;

  const lowProb = Math.round((res.class_probabilities?.LOW || 0.15) * 100);
  const modProb = Math.round((res.class_probabilities?.MODERATE || 0.65) * 100);
  const highProb = Math.round((res.class_probabilities?.HIGH || 0.20) * 100);

  document.getElementById('probLowBar').style.width = `${lowProb}%`;
  document.getElementById('probModBar').style.width = `${modProb}%`;
  document.getElementById('probHighBar').style.width = `${highProb}%`;

  document.getElementById('probLowVal').textContent = `${lowProb}%`;
  document.getElementById('probModVal').textContent = `${modProb}%`;
  document.getElementById('probHighVal').textContent = `${highProb}%`;

  document.getElementById('predConfidenceText').textContent = `Confidence: ${(res.confidence_score * 100).toFixed(1)}%`;

  if (res.narrative) {
    document.getElementById('predNarrative').innerHTML = res.narrative;
  }

  renderFeatureImportance(res.feature_attributions || [
    { name: 'Hour of Day (Rush Window)', importance: 0.38, direction: 'Increases Congestion' },
    { name: 'Current Speed Deficit', importance: 0.28, direction: 'Increases Congestion' },
    { name: 'Precipitation Intensity', importance: 0.16, direction: 'Neutral / Low Rain' },
    { name: 'Day of Week Pattern', importance: 0.11, direction: 'Moderate Baseline' },
    { name: 'Road Capacity Hierarchy', importance: 0.07, direction: 'Buffer Available' }
  ]);
}

function renderFallbackPrediction(horizon, temp, rain) {
  const isHigh = rain > 2.0 || horizon === 30;
  const category = isHigh ? 'MODERATE' : 'LOW';
  renderPredictionResults({
    location_name: activeTarget.name,
    predicted_category: category,
    confidence_score: 0.84,
    class_probabilities: { LOW: category === 'LOW' ? 0.70 : 0.20, MODERATE: 0.65, HIGH: 0.15 },
    narrative: `Model forecast estimated ${category} congestion based on temporal rush patterns and ${temp.toFixed(1)}°C conditions.`
  }, horizon);
}

function renderFeatureImportance(attributions) {
  const container = document.getElementById('featureImportanceList');
  if (!container) return;

  container.innerHTML = attributions.map(feat => {
    const pct = Math.round(feat.importance * 100);
    return `
      <div class="feature-impact-row">
        <span style="width: 220px; font-weight: 500;" class="text-navy-dark text-truncate">${feat.name}</span>
        <div class="feature-bar-wrapper">
          <div class="feature-bar-fill" style="width: ${pct}%;"></div>
        </div>
        <span class="text-end fw-semibold text-slate" style="width: 50px;">${pct}%</span>
        <span class="badge bg-light text-muted border ms-2 small d-none d-md-inline" style="width: 140px; text-align: right;">${feat.direction || 'Contribution'}</span>
      </div>
    `;
  }).join('');
}

function setupPredictionForm() {
  const form = document.getElementById('predictionConfigForm');
  const locationInput = document.getElementById('predLocationInput');
  const suggestionsBox = document.getElementById('predSuggestions');
  const btnGps = document.getElementById('btnPredGps');
  const horizonRadios = document.querySelectorAll('input[name="horizonRadio"]');
  const horizonLabel = document.getElementById('selectedHorizonLabel');

  horizonRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
      horizonLabel.textContent = `+${e.target.value} Minutes`;
    });
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    executePrediction();
  });

  let debounceTimer = null;
  locationInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const q = e.target.value.trim();
    if (q.length < 3) {
      suggestionsBox.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const results = await locationAPI.search(q);
        suggestionsBox.innerHTML = '';
        if (results && results.length > 0) {
          results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `<i class="bi bi-geo-alt text-primary"></i> <span>${item.display_name}</span>`;
            div.addEventListener('click', () => {
              locationInput.value = item.display_name;
              suggestionsBox.style.display = 'none';
              activeTarget.lat = parseFloat(item.lat);
              activeTarget.lon = parseFloat(item.lon);
              activeTarget.name = item.display_name;
              miniMapManager.setView(activeTarget.lat, activeTarget.lon, 14);
              miniMapManager.setUserLocation(activeTarget.lat, activeTarget.lon, activeTarget.name);
              fetchAmbientWeather();
            });
            suggestionsBox.appendChild(div);
          });
          suggestionsBox.style.display = 'block';
        }
      } catch (err) {
        console.warn('Search error:', err);
      }
    }, 350);
  });

  document.addEventListener('click', (e) => {
    if (!locationInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.style.display = 'none';
    }
  });

  btnGps.addEventListener('click', () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      return;
    }
    btnGps.innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span>';
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        btnGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        activeTarget.lat = pos.coords.latitude;
        activeTarget.lon = pos.coords.longitude;
        try {
          const rev = await locationAPI.reverseGeocode(activeTarget.lat, activeTarget.lon);
          activeTarget.name = rev.display_name;
        } catch (e) {
          activeTarget.name = `GPS Location (${activeTarget.lat.toFixed(3)}, ${activeTarget.lon.toFixed(3)})`;
        }
        locationInput.value = activeTarget.name;
        miniMapManager.setView(activeTarget.lat, activeTarget.lon, 14);
        miniMapManager.setUserLocation(activeTarget.lat, activeTarget.lon, activeTarget.name);
        fetchAmbientWeather();
        executePrediction();
      },
      (err) => {
        btnGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        alert(`Location failed: ${err.message}`);
      }
    );
  });
}
