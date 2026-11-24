const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000/api'
  : '/api';

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('traffic_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
      localStorage.removeItem('traffic_token');
      localStorage.removeItem('traffic_user');
      window.location.href = 'login.html?session_expired=1';
      return null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data && data.detail 
        ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
        : `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

const authAPI = {
  login: (email, password) => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  }),
  register: (name, email, password) => apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password })
  }),
  getMe: () => apiRequest('/auth/me'),
  logout: () => apiRequest('/auth/logout', { method: 'POST' })
};

const locationAPI = {
  search: (query) => apiRequest(`/locations/search?q=${encodeURIComponent(query)}`),
  reverseGeocode: (lat, lon) => apiRequest(`/locations/reverse?lat=${lat}&lon=${lon}`),
  getSaved: () => apiRequest('/saved-locations'),
  saveLocation: (data) => apiRequest('/saved-locations', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  deleteSaved: (id) => apiRequest(`/saved-locations/${id}`, {
    method: 'DELETE'
  })
};

const weatherAPI = {
  getWeather: (lat, lon) => apiRequest(`/weather?lat=${lat}&lon=${lon}`)
};

const trafficAPI = {
  getTraffic: (lat, lon, zoom = 14) => apiRequest(`/traffic?lat=${lat}&lon=${lon}&zoom=${zoom}`)
};

const predictionAPI = {
  predict: (params) => apiRequest('/predictions', {
    method: 'POST',
    body: JSON.stringify(params)
  }),
  getHistory: (limit = 10) => apiRequest(`/predictions/history?limit=${limit}`)
};

const routeAPI = {
  compareRoutes: (originLat, originLon, destLat, destLon) => apiRequest('/routes/compare', {
    method: 'POST',
    body: JSON.stringify({
      origin_lat: originLat,
      origin_lon: originLon,
      dest_lat: destLat,
      dest_lon: destLon
    })
  })
};

const reportAPI = {
  getReports: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return apiRequest(`/reports${q ? '?' + q : ''}`);
  },
  submitReport: (data) => apiRequest('/reports', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  voteReport: (id) => apiRequest(`/reports/${id}/vote`, {
    method: 'POST'
  })
};

const analyticsAPI = {
  getTrafficTrends: (location = 'All') => apiRequest(`/analytics/traffic?location=${encodeURIComponent(location)}`),
  getModelMetrics: () => apiRequest('/analytics/model-metrics')
};
