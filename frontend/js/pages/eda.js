/**
 * EDA Page Controller
 * Handles tabs for Business Insights, Feature Categories, Data Quality, and Portfolio
 */

let edaDataLoaded = false;

async function initEDAPage() {
  if (edaDataLoaded) return;

  try {
    const [insights, categoriesData, dataQuality, portfolio] = await Promise.all([
      api.getEDAInsights(),
      api.getEDACategories(),
      api.getEDADataQuality(),
      api.getEDAPortfolio()
    ]);

    // 1. Render Tab 1: Business Insights
    const insightsContainer = document.getElementById('eda-insights-container');
    if (insightsContainer) {
      insightsContainer.innerHTML = insights.map((ins, idx) => `
        <div class="rule" style="margin-bottom: 24px;">
          <div class="rule-top">
            <div class="rule-id" style="display: flex; align-items: center; gap: 10px;">
              <span class="pill" style="font-size: 10px;">INSIGHT ${ins.number.toString().padStart(2, '0')}</span>
              <span style="font-size: 16px; font-weight: 600; color: var(--navy); font-family: 'Space Grotesk', sans-serif;">${ins.title}</span>
            </div>
          </div>

          <p style="font-size: 13.5px; color: var(--ink-dim); line-height: 1.6; margin-bottom: 20px;">
            ${ins.summary}
          </p>

          <div class="grid-2" style="align-items: center; margin-bottom: 16px; grid-template-columns: 1.2fr 0.8fr;">
            <div style="height: 220px; position: relative;">
              <canvas id="insight-chart-${idx}"></canvas>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <div style="display: flex; gap: 12px;">
                ${ins.metrics.map(m => `
                  <div class="cell" style="flex: 1; padding: 14px 16px; border: 1px solid var(--line); border-top: 3px solid var(--green); background: #FDFEFC;">
                    <div class="k" style="font-size: 9.5px; margin-bottom: 6px;">${m.label}</div>
                    <div class="v" style="font-size: 22px;">${m.value}</div>
                  </div>
                `).join('')}
              </div>
              <div class="policy" style="margin-top: 0;">
                <div class="l">UNDERWRITING POLICY ACTION</div>
                <p>${ins.policy_recommendation}</p>
              </div>
            </div>
          </div>
        </div>
      `).join('');

      // Render charts for each insight
      insights.forEach((ins, idx) => {
        const canvasId = `insight-chart-${idx}`;
        if (ins.chart.type === 'horizontalBar') {
          renderHorizontalBarChart(canvasId, ins.chart.labels, ins.chart.datasets[0].data, ins.chart.datasets[0].backgroundColor);
        } else if (ins.chart.type === 'line') {
          renderLineChart(canvasId, ins.chart.labels, ins.chart.datasets[0].data, ins.chart.datasets[0].borderColor);
        } else {
          renderBarChart(canvasId, ins.chart.labels, ins.chart.datasets[0].data, ins.chart.datasets[0].backgroundColor);
        }
      });
    }

    // 2. Render Tab 2: Feature Categories
    const categoriesContainer = document.getElementById('eda-categories-container');
    if (categoriesContainer) {
      categoriesContainer.innerHTML = categoriesData.categories.map(cat => `
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0;">${cat.name}</h4>
            <span class="badge badge-neutral">${cat.count} Features</span>
          </div>
          <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 14px;">${cat.description}</p>
          <div style="border-top: 1px solid var(--border-subtle); padding-top: 10px;">
            ${cat.key_features.map(f => `
              <div style="font-size: 0.8rem; margin-bottom: 6px; display: flex; gap: 8px;">
                <code style="color: #60a5fa; font-weight: 600; min-width: 140px;">${f.name}</code>
                <span style="color: var(--text-secondary);">${f.desc}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('');
    }

    // 3. Render Tab 3: Data Quality
    const dqMissing = document.getElementById('dq-missing-table');
    if (dqMissing) {
      dqMissing.innerHTML = dataQuality.missing_value_audit.map(item => `
        <tr>
          <td><code style="color: #60a5fa;">${item.feature}</code></td>
          <td style="font-weight: 700; color: #f59e0b;">${item.missing_pct}%</td>
          <td style="color: var(--text-secondary);">${item.strategy}</td>
        </tr>
      `).join('');
    }

    const dqAnomalies = document.getElementById('dq-anomalies-container');
    if (dqAnomalies) {
      dqAnomalies.innerHTML = dataQuality.anomalies_corrected.map(a => `
        <div style="background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px 16px; margin-bottom: 12px;">
          <div style="font-weight: 700; color: #ef4444; font-size: 0.88rem; margin-bottom: 4px;">${a.anomaly}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">Root Cause: ${a.cause}</div>
          <div style="font-size: 0.82rem; color: var(--accent-emerald);">Engineering Solution: ${a.correction}</div>
        </div>
      `).join('');
    }

    // 4. Render Tab 4: Portfolio Overview
    document.getElementById('port-total').textContent = portfolio.total_applicants_formatted;
    document.getElementById('port-default-rate').textContent = `${portfolio.default_rate_pct}%`;
    document.getElementById('port-credit').textContent = portfolio.avg_loan_credit;
    document.getElementById('port-income').textContent = portfolio.avg_annual_income;

    edaDataLoaded = true;
  } catch (err) {
    console.error('Failed to initialize EDA page:', err);
  }
}
