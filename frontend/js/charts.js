/**
 * Chart.js Helpers for NeoStats Enterprise Analytics
 * Dark navy canvas styling, transparent backgrounds, smooth animations
 */

const chartRegistry = {};

function destroyChart(canvasId) {
  if (chartRegistry[canvasId]) {
    chartRegistry[canvasId].destroy();
    delete chartRegistry[canvasId];
  }
}

const COMMON_CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  color: '#5C6B63',
  font: {
    family: "'JetBrains Mono', monospace",
    size: 10.5
  },
  plugins: {
    legend: {
      labels: {
        color: '#1E241D',
        boxWidth: 10,
        font: { family: "'JetBrains Mono', monospace", size: 10.5 }
      }
    },
    tooltip: {
      backgroundColor: '#1E241D',
      titleColor: '#F4F6F3',
      bodyColor: '#E6ECE3',
      borderColor: 'rgba(95, 168, 61, 0.3)',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 6,
      displayColors: false
    }
  }
};

function renderBarChart(canvasId, labels, data, colors, labelName = 'Default Rate (%)') {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: labelName,
        data: data,
        backgroundColor: colors,
        borderRadius: 4,
        maxBarThickness: 42
      }]
    },
    options: {
      ...COMMON_CHART_DEFAULTS,
      scales: {
        x: {
          grid: { color: 'rgba(18, 32, 26, 0.07)' },
          ticks: { color: '#5C6B63', font: { family: "'JetBrains Mono', monospace", size: 10 } }
        },
        y: {
          grid: { color: 'rgba(18, 32, 26, 0.07)' },
          ticks: { color: '#5C6B63', font: { family: "'JetBrains Mono', monospace", size: 10 } }
        }
      }
    }
  });
}

function renderHorizontalBarChart(canvasId, labels, data, colors, labelName = 'Default Rate (%)') {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: labelName,
        data: data,
        backgroundColor: colors,
        borderRadius: 4,
        maxBarThickness: 20
      }]
    },
    options: {
      ...COMMON_CHART_DEFAULTS,
      indexAxis: 'y',
      scales: {
        x: {
          grid: { color: 'rgba(18, 32, 26, 0.07)' },
          ticks: { color: '#5C6B63', font: { family: "'JetBrains Mono', monospace", size: 10 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#1E241D', font: { family: "'Space Grotesk', sans-serif", size: 11, weight: '500' } }
        }
      }
    }
  });
}

function renderLineChart(canvasId, labels, data, borderColor = '#3C7A26', labelName = 'Default Rate (%)') {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: labelName,
        data: data,
        borderColor: borderColor,
        backgroundColor: 'rgba(95, 168, 61, 0.12)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#5FA83D',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      ...COMMON_CHART_DEFAULTS,
      scales: {
        x: {
          grid: { color: 'rgba(18, 32, 26, 0.07)' },
          ticks: { color: '#5C6B63', font: { family: "'JetBrains Mono', monospace", size: 10 } }
        },
        y: {
          grid: { color: 'rgba(18, 32, 26, 0.07)' },
          ticks: { color: '#5C6B63', font: { family: "'JetBrains Mono', monospace", size: 10 } }
        }
      }
    }
  });
}

function renderDonutGauge(canvasId, probabilityPct, riskBand) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  let color = '#10b981';
  if (riskBand === 'Medium') color = '#f59e0b';
  if (riskBand === 'High') color = '#ef4444';

  const remainder = Math.max(0, 100 - probabilityPct);

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Default Probability', 'Repayment Probability'],
      datasets: [{
        data: [probabilityPct, remainder],
        backgroundColor: [color, 'rgba(255, 255, 255, 0.08)'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '76%',
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  });
}
