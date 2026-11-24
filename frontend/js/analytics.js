document.addEventListener('DOMContentLoaded', async () => {
  renderDistributionChart();
  renderDiurnalChart();
  renderWeeklyChart();
  await loadModelEvaluationMetrics();
});

function renderDistributionChart() {
  const ctx = document.getElementById('distributionChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Low Congestion', 'Moderate Congestion', 'High Congestion'],
      datasets: [{
        data: [35, 42, 23],
        backgroundColor: ['#16a34a', '#d97706', '#dc2626'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { size: 11 }, color: '#475569', boxWidth: 12 }
        }
      },
      cutout: '65%'
    }
  });
}

function renderDiurnalChart() {
  const ctx = document.getElementById('diurnalChart');
  if (!ctx) return;

  const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const avgSpeed = [
    54, 56, 58, 57, 52, 42, 30, 18, 16, 26, 34, 38,
    36, 35, 33, 28, 20, 14, 16, 24, 35, 42, 48, 52
  ];

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [{
        label: 'Average Velocity (km/h)',
        data: avgSpeed,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.08)',
        fill: true,
        borderWidth: 2.5,
        tension: 0.35,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => ` Speed: ${ctx.parsed.y} km/h` } }
      },
      scales: {
        y: {
          min: 0,
          max: 70,
          ticks: { callback: (v) => `${v} km/h`, color: '#64748b' },
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

function renderWeeklyChart() {
  const ctx = document.getElementById('weeklyChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Congestion Index Score',
        data: [78, 82, 85, 84, 91, 54, 42],
        backgroundColor: [
          '#d97706', '#d97706', '#dc2626', '#dc2626', '#dc2626', '#16a34a', '#16a34a'
        ],
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => ` Peak Index: ${ctx.parsed.y}/100` } }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { color: '#64748b' },
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

async function loadModelEvaluationMetrics() {
  try {
    const data = await analyticsAPI.getModelMetrics();
    if (data) {
      if (data.accuracy) document.getElementById('metricAccuracy').textContent = `${(data.accuracy * 100).toFixed(1)}%`;
      if (data.f1_macro) document.getElementById('metricF1').textContent = data.f1_macro.toFixed(3);
      if (data.total_samples) document.getElementById('metricRecords').textContent = data.total_samples.toLocaleString();
    }
  } catch (err) {
    console.warn('Metrics endpoint notice:', err);
  }
}
