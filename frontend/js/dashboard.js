let mapManager = null;
let forecastChartInstance = null;
let currentLocation = {
  lat: 12.9716,
  lon: 77.5946,
  name: 'Bangalore Central Corridor'
};

document.addEventListener('DOMContentLoaded', async () => {
  const user = getCurrentUser();
  if (user) {
    document.querySelectorAll('.auth-user-name').forEach(el => el.textContent = user.name);
    document.querySelectorAll('.auth-user-email').forEach(el => el.textContent = user.email);
  }

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('lat') && urlParams.get('lon')) {
    currentLocation.lat = parseFloat(urlParams.get('lat'));
    currentLocation.lon = parseFloat(urlParams.get('lon'));
    currentLocation.name = urlParams.get('name') || 'Selected Location';
  }

  mapManager = new TrafficMapManager('dashboardMap', {
    center: [currentLocation.lat, currentLocation.lon],
    zoom: 13
  });

  initForecastChart();
  await loadDashboardData();
  setupDashboardControls();
  setupSavedLocations();
});

function initForecastChart() {
  const ctx = document.getElementById('forecastChart');
  if (!ctx) return;

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Current', '+15 Mins', '+30 Mins', '+45 Mins', '+60 Mins'],
      datasets: [{
        label: 'Predicted Congestion Probability (%)',
        data: [35, 48, 72, 60, 45],
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#2563eb',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleFont: { size: 12, weight: '600' },
          bodyFont: { size: 12 },
          padding: 10,
          callbacks: {
            label: (ctx) => ` Congestion Index: ${ctx.parsed.y}%`
          }
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
          ticks: { color: '#64748b' },
          grid: { display: false }
        }
      }
    }
  });
}

async function loadDashboardData() {
  document.getElementById('currentLocationTitle').textContent = currentLocation.name;
  mapManager.setView(currentLocation.lat, currentLocation.lon, 13);
  mapManager.setUserLocation(currentLocation.lat, currentLocation.lon, currentLocation.name);

  const now = new Date();
  document.getElementById('freshnessTime').textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  try {
    const weather = await weatherAPI.getWeather(currentLocation.lat, currentLocation.lon);
    if (weather) {
      document.getElementById('cardWeatherTemp').textContent = `${weather.temperature_c.toFixed(1)} °C`;
      document.getElementById('cardWeatherDesc').innerHTML = `
        <i class="bi bi-droplet me-1"></i> Humidity ${weather.humidity}% | Rain: ${weather.precipitation_mm.toFixed(1)} mm
      `;
    }
  } catch (err) {
    document.getElementById('cardWeatherTemp').textContent = '24.0 °C';
  }

  try {
    const traffic = await trafficAPI.getTraffic(currentLocation.lat, currentLocation.lon);
    if (traffic) {
      const congEl = document.getElementById('cardCongestionValue');
      const badgeClass = traffic.congestion_level === 'LOW' ? 'badge-traffic-low'
        : traffic.congestion_level === 'MODERATE' ? 'badge-traffic-mod'
        : 'badge-traffic-high';

      congEl.innerHTML = `<span class="badge ${badgeClass}">${traffic.congestion_level}</span>`;
      document.getElementById('cardSpeedText').innerHTML = `
        <i class="bi bi-activity text-primary"></i> Avg speed: ${traffic.current_speed_kmh} km/h (${traffic.free_flow_speed_kmh} km/h free-flow)
      `;

      mapManager.clearLayers();
      mapManager.setUserLocation(currentLocation.lat, currentLocation.lon, currentLocation.name);

      if (traffic.segments && traffic.segments.length > 0) {
        traffic.segments.forEach(seg => {
          mapManager.addCongestionNode(seg.latitude, seg.longitude, seg.congestion_level, seg.road_name, seg.current_speed_kmh);
        });
      }
    }
  } catch (err) {
    console.warn('Traffic telemetry notice:', err);
  }

  try {
    const prediction = await predictionAPI.predict({
      location_name: currentLocation.name,
      latitude: currentLocation.lat,
      longitude: currentLocation.lon,
      horizon_minutes: 30
    });

    if (prediction) {
      const forecastEl = document.getElementById('cardForecastLevel');
      const badgeClass = prediction.predicted_category === 'LOW' ? 'badge-traffic-low'
        : prediction.predicted_category === 'MODERATE' ? 'badge-traffic-mod'
        : 'badge-traffic-high';

      forecastEl.innerHTML = `<span class="badge ${badgeClass}">${prediction.predicted_category}</span>`;
      document.getElementById('cardForecastConf').innerHTML = `
        <i class="bi bi-shield-check text-success"></i> Model Confidence: ${(prediction.confidence_score * 100).toFixed(1)}%
      `;

      if (forecastChartInstance && prediction.horizon_trend) {
        forecastChartInstance.data.datasets[0].data = prediction.horizon_trend;
        forecastChartInstance.update();
      }

      if (prediction.departure_recommendation) {
        document.getElementById('cardDepartureWindow').textContent = prediction.departure_recommendation.suggested_departure;
        document.getElementById('cardDepartureNote').textContent = prediction.departure_recommendation.rationale;
      }
    }
  } catch (err) {
    console.warn('Prediction API notice:', err);
  }

  try {
    const reports = await reportAPI.getReports({ status: 'active' });
    if (reports && reports.length > 0) {
      reports.forEach(rep => {
        mapManager.addIncidentMarker(rep.latitude, rep.longitude, rep);
      });
    }
  } catch (err) {
    console.warn('Reports overlay notice:', err);
  }

  loadHistoryTable();
}

async function loadHistoryTable() {
  const tbody = document.getElementById('historyTableBody');
  try {
    const history = await predictionAPI.getHistory(5);
    if (!history || history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-3 text-muted">No recent inquiries recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = history.map(item => {
      const badgeClass = item.predicted_category === 'LOW' ? 'badge-traffic-low'
        : item.predicted_category === 'MODERATE' ? 'badge-traffic-mod'
        : 'badge-traffic-high';

      const dt = new Date(item.created_at);
      const timeStr = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      return `
        <tr>
          <td class="ps-3 fw-semibold text-navy-dark">${item.location_name}</td>
          <td><span class="badge bg-light text-slate border">+${item.horizon_minutes}m</span></td>
          <td><span class="badge ${badgeClass}">${item.predicted_category}</span></td>
          <td>${(item.confidence_score * 100).toFixed(1)}%</td>
          <td><span class="text-muted">${item.weather_condition || 'Clear'}, ${item.temperature_c ? item.temperature_c.toFixed(1) + '°C' : '--'}</span></td>
          <td class="text-muted">${timeStr}</td>
          <td class="pe-3 text-end">
            <a href="predictions.html?lat=${item.latitude}&lon=${item.longitude}&name=${encodeURIComponent(item.location_name)}" class="btn btn-sm btn-outline-primary py-0 px-2" style="font-size: 0.75rem;">
              Re-evaluate
            </a>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-3 text-muted">Run an inquiry to view real-time log.</td></tr>`;
  }
}

function setupDashboardControls() {
  const searchInput = document.getElementById('topSearchInput');
  const suggestionsBox = document.getElementById('topSearchSuggestions');
  const btnTopGps = document.getElementById('btnTopGps');
  const btnRefresh = document.getElementById('btnRefreshData');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const appSidebar = document.getElementById('appSidebar');

  if (sidebarToggle && appSidebar) {
    sidebarToggle.addEventListener('click', () => {
      appSidebar.classList.toggle('show');
    });
  }

  btnRefresh.addEventListener('click', () => {
    btnRefresh.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Updating...';
    loadDashboardData().finally(() => {
      btnRefresh.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Refresh';
    });
  });

  let debounceTimer = null;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();
    if (query.length < 3) {
      suggestionsBox.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const results = await locationAPI.search(query);
        suggestionsBox.innerHTML = '';
        if (results && results.length > 0) {
          results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `<i class="bi bi-geo-alt text-primary"></i> <span>${item.display_name}</span>`;
            div.addEventListener('click', () => {
              searchInput.value = item.display_name;
              suggestionsBox.style.display = 'none';
              currentLocation.lat = parseFloat(item.lat);
              currentLocation.lon = parseFloat(item.lon);
              currentLocation.name = item.display_name;
              loadDashboardData();
            });
            suggestionsBox.appendChild(div);
          });
          suggestionsBox.style.display = 'block';
        } else {
          suggestionsBox.style.display = 'none';
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 350);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.style.display = 'none';
    }
  });

  btnTopGps.addEventListener('click', () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported.');
      return;
    }
    btnTopGps.innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span>';
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        btnTopGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        currentLocation.lat = pos.coords.latitude;
        currentLocation.lon = pos.coords.longitude;
        try {
          const rev = await locationAPI.reverseGeocode(currentLocation.lat, currentLocation.lon);
          currentLocation.name = (rev && rev.display_name) ? rev.display_name : 'Current GPS Position';
        } catch (e) {
          currentLocation.name = `GPS (${currentLocation.lat.toFixed(3)}, ${currentLocation.lon.toFixed(3)})`;
        }
        loadDashboardData();
      },
      (err) => {
        btnTopGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        alert(`Location detection failed: ${err.message}`);
      },
      { timeout: 10000 }
    );
  });
}

function setupSavedLocations() {
  const form = document.getElementById('saveLocationForm');
  const labelInput = document.getElementById('savedLabel');
  const categorySelect = document.getElementById('savedCategory');
  const addressInput = document.getElementById('savedAddress');
  const listContainer = document.getElementById('savedLocationsList');

  addressInput.value = currentLocation.name;

  async function renderSavedList() {
    try {
      const places = await locationAPI.getSaved();
      if (!places || places.length === 0) {
        listContainer.innerHTML = '<p class="text-center text-muted small py-2 mb-0">No saved places yet.</p>';
        return;
      }

      listContainer.innerHTML = places.map(p => `
        <div class="d-flex align-items-center justify-content-between p-2 border-bottom">
          <div class="d-flex align-items-center gap-2 overflow-hidden">
            <span class="badge bg-light text-primary border">${p.category}</span>
            <div class="text-truncate">
              <div class="fw-semibold small text-navy-dark">${p.label}</div>
              <div class="text-slate small text-truncate" style="font-size: 0.75rem;">${p.address}</div>
            </div>
          </div>
          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-sm btn-outline-primary py-0 px-2 btn-goto-place" data-lat="${p.latitude}" data-lon="${p.longitude}" data-name="${p.label}">
              Go
            </button>
            <button class="btn btn-sm btn-outline-danger py-0 px-2 btn-delete-place" data-id="${p.id}">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      `).join('');

      document.querySelectorAll('.btn-goto-place').forEach(btn => {
        btn.addEventListener('click', () => {
          currentLocation.lat = parseFloat(btn.dataset.lat);
          currentLocation.lon = parseFloat(btn.dataset.lon);
          currentLocation.name = btn.dataset.name;
          const modal = bootstrap.Modal.getInstance(document.getElementById('savedLocationsModal'));
          if (modal) modal.hide();
          loadDashboardData();
        });
      });

      document.querySelectorAll('.btn-delete-place').forEach(btn => {
        btn.addEventListener('click', async () => {
          await locationAPI.deleteSaved(btn.dataset.id);
          renderSavedList();
        });
      });
    } catch (err) {
      listContainer.innerHTML = '<p class="text-center text-muted small py-2 mb-0">Saved places available when signed in.</p>';
    }
  }

  const modalEl = document.getElementById('savedLocationsModal');
  if (modalEl) {
    modalEl.addEventListener('show.bs.modal', renderSavedList);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await locationAPI.saveLocation({
        label: labelInput.value.trim(),
        category: categorySelect.value,
        address: addressInput.value.trim(),
        latitude: currentLocation.lat,
        longitude: currentLocation.lon
      });
      labelInput.value = '';
      renderSavedList();
    } catch (err) {
      alert(err.message || 'Error saving location');
    }
  });
}
