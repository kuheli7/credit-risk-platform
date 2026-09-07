/**
 * Overview Page Controller
 * Fetches real model performance metrics, portfolio overview, and strategic insights
 */

async function initOverviewPage() {
  const container = document.getElementById('page-overview');
  if (!container) return;

  try {
    const data = await api.getOverview();
    const m = data.metrics;

    // 1. Populate KPI Row
    const kpiRoc = document.getElementById('kpi-roc');
    if (kpiRoc) kpiRoc.textContent = m.model_performance.roc_auc_str;
    const kpiPr = document.getElementById('kpi-pr');
    if (kpiPr) kpiPr.textContent = m.model_performance.pr_auc_str;
    const kpiFeatures = document.getElementById('kpi-features');
    if (kpiFeatures) kpiFeatures.textContent = m.features.total_engineered;
    const kpiEngine = document.getElementById('kpi-engine');
    if (kpiEngine) kpiEngine.textContent = m.engine.llm_provider + ' LLM';

    // 2. Render Strategic Business Insight Cards (all 6)
    const insightsGrid = document.getElementById('overview-insights-grid');
    if (insightsGrid && data.key_insights && data.key_insights.length > 0) {
      const accentColors = ['#2B6B48', '#38A169', '#2B6B48', '#4A7C59', '#2B6B48', '#38A169'];
      insightsGrid.innerHTML = data.key_insights.map((ins, idx) => `
        <div style="
          background: #FFFFFF;
          border: 1px solid var(--line);
          border-top: 3px solid ${accentColors[idx % accentColors.length]};
          padding: 20px 22px 18px;
          display: flex;
          flex-direction: column;
          gap: 0;
        ">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <span style="
              font-family: 'JetBrains Mono', monospace;
              font-size: 10px;
              font-weight: 600;
              letter-spacing: 0.08em;
              color: var(--green-dark);
              background: var(--green-tint);
              padding: 3px 8px;
              border-radius: 2px;
            ">INSIGHT ${ins.number.toString().padStart(2, '0')}</span>
            <span style="
              font-family: 'Space Grotesk', sans-serif;
              font-size: 22px;
              font-weight: 700;
              color: var(--green-dark);
              line-height: 1;
            ">${ins.metric.value}</span>
          </div>

          <h4 style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: var(--navy);
            margin: 0 0 10px 0;
            line-height: 1.4;
          ">${ins.title}</h4>

          <p style="
            font-size: 12.5px;
            color: var(--ink-dim);
            line-height: 1.6;
            margin: 0 0 14px 0;
            flex: 1;
          ">${ins.summary}</p>

          ${ins.policy ? `
            <div style="
              background: var(--green-tint);
              border-left: 3px solid var(--green);
              padding: 9px 12px;
              margin-top: auto;
            ">
              <div style="font-family:'JetBrains Mono',monospace; font-size:9.5px; color:var(--green-dark); font-weight:700; letter-spacing:0.08em; margin-bottom:4px;">POLICY ACTION</div>
              <p style="margin:0; font-size:12px; color:var(--navy); line-height:1.5;">${ins.policy}</p>
            </div>
          ` : `
            <div style="font-family:'JetBrains Mono',monospace; font-size:10.5px; color:var(--ink-dim); border-top:1px solid var(--line); padding-top:8px; margin-top:auto;">
              KEY SIGNAL: <span style="color:var(--navy); font-weight:600;">${ins.metric.label}</span>
            </div>
          `}
        </div>
      `).join('');
    }

  } catch (err) {
    console.error('Failed to initialize overview page:', err);
    const insightsGrid = document.getElementById('overview-insights-grid');
    if (insightsGrid) {
      insightsGrid.innerHTML = `
        <div style="grid-column:1/-1; padding:20px; color:var(--ink-dim); font-family:'JetBrains Mono',monospace; font-size:12px;">
          Could not load strategic insights. Ensure the backend server is running.
        </div>`;
    }
  }
}
