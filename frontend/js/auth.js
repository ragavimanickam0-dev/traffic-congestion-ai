function isAuthenticated() {
  return !!localStorage.getItem('traffic_token');
}

function getCurrentUser() {
  const userStr = localStorage.getItem('traffic_user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
}

function requireAuth() {
  if (!isAuthenticated()) {
    const currentPath = window.location.pathname;
    window.location.href = `login.html?redirect=${encodeURIComponent(currentPath)}`;
  }
}

function handleLogout() {
  localStorage.removeItem('traffic_token');
  localStorage.removeItem('traffic_user');
  window.location.href = 'login.html';
}

document.addEventListener('DOMContentLoaded', () => {
  const user = getCurrentUser();
  const userNameElements = document.querySelectorAll('.auth-user-name');
  const userEmailElements = document.querySelectorAll('.auth-user-email');
  const logoutButtons = document.querySelectorAll('.btn-logout');
  const authNavElements = document.querySelectorAll('.nav-auth-state');

  if (user) {
    userNameElements.forEach(el => el.textContent = user.name || 'User');
    userEmailElements.forEach(el => el.textContent = user.email || '');
    authNavElements.forEach(el => {
      el.innerHTML = `
        <div class="dropdown">
          <button class="btn btn-sm btn-outline-secondary dropdown-toggle d-flex align-items-center gap-2" data-bs-toggle="dropdown">
            <i class="bi bi-person-circle"></i>
            <span>${user.name || 'Account'}</span>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li><a class="dropdown-item" href="dashboard.html"><i class="bi bi-speedometer2 me-2"></i>Dashboard</a></li>
            <li><a class="dropdown-item" href="predictions.html"><i class="bi bi-graph-up me-2"></i>Predictions</a></li>
            <li><a class="dropdown-item" href="route-planner.html"><i class="bi bi-signpost-split me-2"></i>Routes</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item text-danger btn-logout" onclick="handleLogout()"><i class="bi bi-box-arrow-right me-2"></i>Sign Out</button></li>
          </ul>
        </div>
      `;
    });
  } else {
    authNavElements.forEach(el => {
      el.innerHTML = `
        <a href="login.html" class="btn btn-sm btn-outline-secondary me-2">Sign In</a>
        <a href="register.html" class="btn btn-sm btn-primary">Get Started</a>
      `;
    });
  }

  logoutButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      handleLogout();
    });
  });
});
