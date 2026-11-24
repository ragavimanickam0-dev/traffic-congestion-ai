class TrafficMapManager {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.defaultCenter = options.center || [12.9716, 77.5946];
    this.defaultZoom = options.zoom || 13;
    this.map = null;
    this.markersLayer = null;
    this.routesLayer = null;
    this.trafficLayer = null;
    this.userLocationMarker = null;

    this.initMap();
  }

  initMap() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    this.map = L.map(this.containerId, {
      zoomControl: true,
      attributionControl: true
    }).setView(this.defaultCenter, this.defaultZoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
    this.routesLayer = L.layerGroup().addTo(this.map);
    this.trafficLayer = L.layerGroup().addTo(this.map);
  }

  setView(lat, lon, zoom = 14) {
    if (this.map) {
      this.map.setView([lat, lon], zoom);
    }
  }

  clearLayers() {
    if (this.markersLayer) this.markersLayer.clearLayers();
    if (this.routesLayer) this.routesLayer.clearLayers();
    if (this.trafficLayer) this.trafficLayer.clearLayers();
  }

  setUserLocation(lat, lon, label = 'Your Current Location') {
    if (this.userLocationMarker) {
      this.userLocationMarker.remove();
    }

    const customIcon = L.divIcon({
      className: 'user-gps-marker',
      html: `
        <div style="background-color: #2563eb; width: 16px; height: 16px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 0 4px rgba(37,99,235,0.3);"></div>
      `,
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });

    this.userLocationMarker = L.marker([lat, lon], { icon: customIcon })
      .bindPopup(`<strong>${label}</strong><br><small>Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}</small>`)
      .addTo(this.map);

    this.map.setView([lat, lon], 14);
  }

  addCongestionNode(lat, lon, level = 'LOW', name = 'Road Segment', speed = 40) {
    let color = '#16a34a';
    if (level === 'MODERATE') color = '#d97706';
    if (level === 'HIGH') color = '#dc2626';

    const circle = L.circleMarker([lat, lon], {
      radius: 12,
      fillColor: color,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8
    });

    circle.bindPopup(`
      <div style="font-family: sans-serif; padding: 2px;">
        <strong style="color: #0f172a; font-size: 0.95rem;">${name}</strong>
        <div style="margin-top: 4px; display: flex; align-items: center; gap: 6px;">
          <span style="font-size: 0.8rem; font-weight: bold; color: ${color};">${level} CONGESTION</span>
          <span style="font-size: 0.8rem; color: #64748b;">| ~${speed} km/h</span>
        </div>
      </div>
    `);

    circle.addTo(this.trafficLayer);
    return circle;
  }

  drawRoute(coordinates, options = {}) {
    const color = options.color || '#2563eb';
    const weight = options.weight || 5;
    const opacity = options.opacity || 0.85;
    const dashArray = options.dashArray || null;

    const polyline = L.polyline(coordinates, {
      color,
      weight,
      opacity,
      dashArray
    }).addTo(this.routesLayer);

    if (options.fitBounds !== false) {
      this.map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
    }

    return polyline;
  }

  addIncidentMarker(lat, lon, report) {
    const iconClass = report.report_type === 'Accident' ? 'bi-exclamation-octagon text-danger'
      : report.report_type === 'Road Closure' ? 'bi-slash-circle text-danger'
      : report.report_type === 'Waterlogging' ? 'bi-water text-primary'
      : report.report_type === 'Construction' ? 'bi-cone-striped text-warning'
      : 'bi-exclamation-triangle text-warning';

    const incidentIcon = L.divIcon({
      className: 'incident-map-pin',
      html: `
        <div style="background: #ffffff; border: 2px solid #e2e8f0; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
          <i class="bi ${iconClass}" style="font-size: 1.1rem;"></i>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const marker = L.marker([lat, lon], { icon: incidentIcon }).addTo(this.markersLayer);
    marker.bindPopup(`
      <div style="min-width: 180px;">
        <span class="badge bg-secondary mb-1">${report.report_type}</span>
        <h6 class="mb-1 fw-bold">${report.road_name || 'Reported Incident'}</h6>
        <p class="mb-1 text-muted small">${report.description || 'No description provided'}</p>
        <div class="d-flex justify-content-between align-items-center text-muted" style="font-size: 0.75rem;">
          <span>Severity: ${report.severity || 'Moderate'}</span>
          <span>${report.votes || 0} confirmations</span>
        </div>
      </div>
    `);

    return marker;
  }
}
