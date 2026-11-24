let routeMapManager = null;
let originCoords = { lat: 12.9772, lon: 77.5708, label: 'Majestic Transit Center' };
let destCoords = { lat: 12.8452, lon: 77.6602, label: 'Electronic City Phase 1' };

document.addEventListener('DOMContentLoaded', () => {
  routeMapManager = new TrafficMapManager('routeMap', {
    center: [12.9112, 77.6155],
    zoom: 12
  });

  setupRouteControls();
  calculateAndRenderRoutes();
});

function setupRouteControls() {
  const form = document.getElementById('routeForm');
  const originInput = document.getElementById('originInput');
  const destInput = document.getElementById('destInput');
  const originSuggestions = document.getElementById('originSuggestions');
  const destSuggestions = document.getElementById('destSuggestions');
  const btnSwap = document.getElementById('btnSwapRoute');
  const btnOriginGps = document.getElementById('btnOriginGps');

  function setupAutocomplete(input, suggestionsBox, onSelect) {
    let timer = null;
    input.addEventListener('input', (e) => {
      clearTimeout(timer);
      const q = e.target.value.trim();
      if (q.length < 3) {
        suggestionsBox.style.display = 'none';
        return;
      }
      timer = setTimeout(async () => {
        try {
          const results = await locationAPI.search(q);
          suggestionsBox.innerHTML = '';
          if (results && results.length > 0) {
            results.forEach(item => {
              const div = document.createElement('div');
              div.className = 'autocomplete-item';
              div.innerHTML = `<i class="bi bi-geo-alt text-primary"></i> <span>${item.display_name}</span>`;
              div.addEventListener('click', () => {
                input.value = item.display_name;
                suggestionsBox.style.display = 'none';
                onSelect(parseFloat(item.lat), parseFloat(item.lon), item.display_name);
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
  }

  setupAutocomplete(originInput, originSuggestions, (lat, lon, label) => {
    originCoords = { lat, lon, label };
  });

  setupAutocomplete(destInput, destSuggestions, (lat, lon, label) => {
    destCoords = { lat, lon, label };
  });

  document.addEventListener('click', (e) => {
    if (!originInput.contains(e.target) && !originSuggestions.contains(e.target)) {
      originSuggestions.style.display = 'none';
    }
    if (!destInput.contains(e.target) && !destSuggestions.contains(e.target)) {
      destSuggestions.style.display = 'none';
    }
  });

  btnSwap.addEventListener('click', () => {
    const tempCoords = { ...originCoords };
    originCoords = { ...destCoords };
    destCoords = tempCoords;

    const tempVal = originInput.value;
    originInput.value = destInput.value;
    destInput.value = tempVal;

    calculateAndRenderRoutes();
  });

  btnOriginGps.addEventListener('click', () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      return;
    }
    btnOriginGps.innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span>';
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        btnOriginGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        originCoords.lat = pos.coords.latitude;
        originCoords.lon = pos.coords.longitude;
        try {
          const rev = await locationAPI.reverseGeocode(originCoords.lat, originCoords.lon);
          originCoords.label = rev.display_name;
        } catch (e) {
          originCoords.label = 'Current GPS Position';
        }
        originInput.value = originCoords.label;
        calculateAndRenderRoutes();
      },
      (err) => {
        btnOriginGps.innerHTML = '<i class="bi bi-crosshair text-primary"></i>';
        alert(`Location failed: ${err.message}`);
      }
    );
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    calculateAndRenderRoutes();
  });
}

async function calculateAndRenderRoutes() {
  const btn = document.getElementById('btnCalculateRoute');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Comparing routes...';

  try {
    const data = await routeAPI.compareRoutes(
      originCoords.lat,
      originCoords.lon,
      destCoords.lat,
      destCoords.lon
    );

    renderRouteDetails(data);
  } catch (err) {
    console.warn('Route compare fallback:', err);
    renderSimulatedRouteFallback();
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-compass me-1"></i> Compare Available Routes';
  }
}

function renderRouteDetails(data) {
  routeMapManager.clearLayers();

  const startIcon = L.divIcon({
    html: '<div style="background:#16a34a; width:16px; height:16px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 4px rgba(0,0,0,0.4);"></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });
  const endIcon = L.divIcon({
    html: '<div style="background:#dc2626; width:16px; height:16px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 4px rgba(0,0,0,0.4);"></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });

  L.marker([originCoords.lat, originCoords.lon], { icon: startIcon })
    .bindPopup(`<strong>Origin:</strong> ${originCoords.label}`)
    .addTo(routeMapManager.markersLayer);

  L.marker([destCoords.lat, destCoords.lon], { icon: endIcon })
    .bindPopup(`<strong>Destination:</strong> ${destCoords.label}`)
    .addTo(routeMapManager.markersLayer);

  if (data.primary_route && data.primary_route.geometry) {
    routeMapManager.drawRoute(data.primary_route.geometry, {
      color: '#2563eb',
      weight: 5,
      opacity: 0.9,
      fitBounds: true
    });
  }

  if (data.alternative_route && data.alternative_route.geometry) {
    routeMapManager.drawRoute(data.alternative_route.geometry, {
      color: '#64748b',
      weight: 4,
      opacity: 0.7,
      dashArray: '6, 6',
      fitBounds: false
    });
  }

  document.getElementById('routeComparisonSection').classList.remove('d-none');

  if (data.primary_route) {
    document.getElementById('route1Duration').textContent = `${Math.round(data.primary_route.duration_minutes)} mins`;
    document.getElementById('route1Distance').textContent = `${data.primary_route.distance_km.toFixed(1)} km`;
    document.getElementById('route1Summary').textContent = data.primary_route.summary || 'Primary Expressway Corridor';
    
    const badge = document.getElementById('route1CongBadge');
    badge.className = data.primary_route.congestion_level === 'LOW' ? 'badge badge-traffic-low'
      : data.primary_route.congestion_level === 'MODERATE' ? 'badge badge-traffic-mod'
      : 'badge badge-traffic-high';
    badge.textContent = `${data.primary_route.congestion_level} Traffic`;
  }

  if (data.alternative_route) {
    document.getElementById('route2Duration').textContent = `${Math.round(data.alternative_route.duration_minutes)} mins`;
    document.getElementById('route2Distance').textContent = `${data.alternative_route.distance_km.toFixed(1)} km`;
    document.getElementById('route2Summary').textContent = data.alternative_route.summary || 'Secondary Arterial Bypass';

    const badge2 = document.getElementById('route2CongBadge');
    badge2.className = data.alternative_route.congestion_level === 'LOW' ? 'badge badge-traffic-low'
      : data.alternative_route.congestion_level === 'MODERATE' ? 'badge badge-traffic-mod'
      : 'badge badge-traffic-high';
    badge2.textContent = `${data.alternative_route.congestion_level} Traffic`;
  }

  if (data.departure_guidance) {
    document.getElementById('routeDepartureGuidance').textContent = data.departure_guidance;
  }
}

function renderSimulatedRouteFallback() {
  const lat1 = originCoords.lat, lon1 = originCoords.lon;
  const lat2 = destCoords.lat, lon2 = destCoords.lon;

  const primaryCoords = [
    [lat1, lon1],
    [lat1 + (lat2 - lat1) * 0.3 + 0.01, lon1 + (lon2 - lon1) * 0.25],
    [lat1 + (lat2 - lat1) * 0.7 - 0.01, lon1 + (lon2 - lon1) * 0.75],
    [lat2, lon2]
  ];

  const altCoords = [
    [lat1, lon1],
    [lat1 + (lat2 - lat1) * 0.4 - 0.02, lon1 + (lon2 - lon1) * 0.4],
    [lat1 + (lat2 - lat1) * 0.8 - 0.015, lon1 + (lon2 - lon1) * 0.85],
    [lat2, lon2]
  ];

  renderRouteDetails({
    primary_route: {
      duration_minutes: 36,
      distance_km: 21.2,
      congestion_level: 'MODERATE',
      summary: 'Main Corridor with standard congestion',
      geometry: primaryCoords
    },
    alternative_route: {
      duration_minutes: 48,
      distance_km: 24.5,
      congestion_level: 'HIGH',
      summary: 'Arterial bypass experiencing bottlenecks',
      geometry: altCoords
    },
    departure_guidance: 'Departing within the next 20 minutes saves approximately 14 minutes compared to peak rush window.'
  });
}
