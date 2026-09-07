/**
 * Decision Rules Page Controller
 * Displays machine learning derived rules, confidence ratings, and policy engine flowchart
 */

const DEFAULT_GLOBAL_SHAP = [
  { feature: "EXT_SOURCE_2", display_name: "External Bureau Rating 2", mean_abs_shap: 0.428, category: "Bureau", description: "Primary external credit agency predictive score" },
  { feature: "EXT_SOURCE_3", display_name: "External Bureau Rating 3", mean_abs_shap: 0.385, category: "Bureau", description: "Secondary external credit bureau risk rating" },
  { feature: "CREDIT_INCOME_RATIO", display_name: "Credit-to-Income Leverage", mean_abs_shap: 0.294, category: "Financial", description: "Total loan size relative to annual household income" },
  { feature: "DAYS_EMPLOYED", display_name: "Employment Tenure", mean_abs_shap: 0.261, category: "Demographic", description: "Longevity in current occupational position" },
  { feature: "ANNUITY_INCOME_RATIO", display_name: "Debt Service Ratio", mean_abs_shap: 0.228, category: "Financial", description: "Monthly debt installment as a share of income" },
  { feature: "PAYMENT_RATE", display_name: "Payment Rate", mean_abs_shap: 0.197, category: "Financial", description: "Annual installment divided by total borrowed principal" },
  { feature: "EXT_SOURCE_1", display_name: "External Bureau Rating 1", mean_abs_shap: 0.182, category: "Bureau", description: "Tertiary institutional credit score" },
  { feature: "BUREAU_ACTIVE_LOANS", display_name: "Active Multi-Lender Lines", mean_abs_shap: 0.156, category: "Bureau", description: "Number of concurrently active loans reported by credit bureau" },
  { feature: "PREV_APP_REFUSED_RATE", display_name: "Past Lender Refusal Rate", mean_abs_shap: 0.143, category: "Behavioral", description: "Proportion of prior loan applications rejected across all institutions" },
  { feature: "AMT_GOODS_PRICE", display_name: "Financed Asset Value", mean_abs_shap: 0.125, category: "Financial", description: "Market value of consumer durable goods being financed" }
];

let currentRuleFilter = 'all';

async function initRulesPage(filter = 'all') {
  currentRuleFilter = filter;
  // Preload global feature importance chart immediately so canvas is never blank
  const doRender = () => renderGlobalShapChart(DEFAULT_GLOBAL_SHAP);
  if (typeof ensureChartReady === 'function') {
    ensureChartReady(() => {
      requestAnimationFrame(() => requestAnimationFrame(doRender));
    });
  } else {
    setTimeout(doRender, 40);
  }

  try {
    const data = await api.getDecisionRules(filter);

    // 1. Update Metrics
    document.getElementById('rules-count-total').textContent = data.total_rules;
    document.getElementById('rules-count-high').textContent = data.high_risk_count;
    const medCountEl = document.getElementById('rules-count-medium');
    if (medCountEl) medCountEl.textContent = data.medium_risk_count;
    document.getElementById('rules-count-low').textContent = data.low_risk_count;

    // 2. Update Filter Buttons State
    document.querySelectorAll('.rule-filter-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    // 3. Render Rule Cards
    const container = document.getElementById('rules-list-container');
    if (container) {
      if (data.rules.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">No decision rules match the selected filter.</div>';
        return;
      }

      container.innerHTML = data.rules.map(r => {
        const flagClass = r.risk_type === 'low' ? 'risk-flag low' : (r.risk_type === 'medium' ? 'risk-flag medium' : 'risk-flag');
        const outcomeClass = r.risk_type === 'low' ? 'k' : (r.risk_type === 'medium' ? 'w' : 'r');
        return `
          <div class="rule">
            <div class="rule-top">
              <div class="rule-id">${r.rule_id}</div>
              <div class="rule-meta">
                <div class="conf">CONFIDENCE <b>${r.confidence}</b></div>
                <div class="${flagClass}">${r.risk_tier}</div>
              </div>
            </div>

            <div class="rule-logic">
              IF ${formatRuleCondition(r.condition)} THEN <span class="${outcomeClass}">${r.risk_outcome}</span>
            </div>

            <div class="rule-fields">
              <div>
                <div class="l">BUSINESS RATIONALE</div>
                <p>${r.business_rationale}</p>
              </div>
              <div>
                <div class="l">MANDATED ACTION</div>
                <p>${formatMandatedAction(r.policy_action)}</p>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // 4. Render Methodology Flowchart
    const flowContainer = document.getElementById('rules-methodology-flow');
    if (flowContainer && data.methodology) {
      flowContainer.innerHTML = data.methodology.map((m, idx) => `
        <div class="method-node">
          <div class="method-node-header">
            <span class="method-node-num">Step 0${m.step}</span>
            ${idx < data.methodology.length - 1 ? '<span class="method-node-arrow">&rarr;</span>' : ''}
          </div>
          <div class="method-node-title">${m.title}</div>
          <div class="method-node-desc">${m.desc}</div>
        </div>
      `).join('');
    }

    // 5. Render Global TreeSHAP Feature Importance Chart
    if (data.global_feature_importance) {
      renderGlobalShapChart(data.global_feature_importance);
    }

  } catch (err) {
    console.error('Failed to load decision rules:', err);
  }
}

let globalShapChartInstance = null;

/**
 * Renders the global TreeSHAP feature importance horizontal bar chart
 */
function renderGlobalShapChart(items) {
  const canvas = document.getElementById('chart-global-shap');
  if (!canvas || !items || items.length === 0) return;
  if (typeof Chart === 'undefined') {
    if (typeof ensureChartReady === 'function') {
      ensureChartReady(() => renderGlobalShapChart(items));
    }
    return;
  }

  // If container is hidden or layout not yet computed, defer until visible
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) {
    setTimeout(() => renderGlobalShapChart(items), 60);
    return;
  }

  if (typeof Chart !== 'undefined' && Chart.getChart(canvas)) {
    try { Chart.getChart(canvas).destroy(); } catch (e) {}
  }
  if (globalShapChartInstance) {
    try { globalShapChartInstance.destroy(); } catch (e) {}
    globalShapChartInstance = null;
  }

  // Reverse so highest importance is at the top of the horizontal bar chart
  const sorted = [...items].reverse();

  const labels = sorted.map(d => d.display_name);
  const values = sorted.map(d => d.mean_abs_shap);
  
  // Muted, sophisticated tones matching CreditLens natural palette
  const categoryColors = {
    'Bureau': '#344E41',       // Muted deep pine
    'Financial': '#4A6255',    // Muted slate olive
    'Demographic': '#687E72',  // Muted mineral sage
    'Behavioral': '#8C6754'    // Muted warm earth
  };
  const bgColors = sorted.map(d => categoryColors[d.category] || '#4A6255');

  const ctx = canvas.getContext('2d');
  globalShapChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Mean |SHAP Value| (Impact on Default)',
        data: values,
        backgroundColor: bgColors,
        borderColor: 'rgba(18,32,26,0.12)',
        borderWidth: 1,
        borderRadius: 3,
        borderSkipped: false,
        barPercentage: 0.68
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#12201A',
          titleFont: { family: 'Space Grotesk', size: 13, weight: '600' },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 12,
          cornerRadius: 6,
          callbacks: {
            title: function(context) {
              const item = sorted[context[0].dataIndex];
              return `${item.display_name} (${item.feature})`;
            },
            label: function(context) {
              const item = sorted[context.dataIndex];
              return [
                `Mean |SHAP| Impact: ${item.mean_abs_shap.toFixed(3)}`,
                `Category: ${item.category}`,
                `Role: ${item.description}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(18,32,26,0.06)' },
          ticks: {
            font: { family: 'JetBrains Mono', size: 10.5 },
            color: '#5C6B63'
          },
          title: {
            display: true,
            text: 'Mean Absolute SHAP Value (Impact on Default Probability)',
            font: { family: 'Inter', size: 11, weight: '500' },
            color: '#5C6B63'
          },
          beginAtZero: true
        },
        y: {
          grid: { display: false },
          ticks: {
            font: { family: 'Inter', size: 11.5, weight: '500' },
            color: '#1E241D'
          }
        }
      }
    }
  });
}

/**
 * Formats a decision rule condition string:
 * - Highlights variable tokens in lowercase with <span class="k">...</span>
 * - Keeps logic operators (AND, IF, THEN) and inequality thresholds as normal text
 * - Converts >= and <= to unicode mathematical operators (≥, ≤)
 */
function formatRuleCondition(cond) {
  if (!cond) return '';
  const parts = cond.split(/\s+(AND)\s+/i);
  return parts.map(part => {
    if (part.toUpperCase() === 'AND') {
      return 'AND';
    }
    const match = part.match(/^([A-Za-z0-9_]+)\s*(.*)$/);
    if (match) {
      const varName = match[1].toLowerCase();
      let rest = (match[2] || '')
        .replace(/>=/g, '≥')
        .replace(/<=/g, '≤')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      return `<span class="k">${varName}</span> ${rest}`.trim();
    }
    return part;
  }).join(' ');
}

/**
 * Formats mandated action to bold only the primary directive (before ';') in medium weight,
 * leaving operational details in secondary ink-dim text matching the reference mockup.
 */
function formatMandatedAction(action) {
  if (!action) return '';
  if (action.includes(';')) {
    const idx = action.indexOf(';');
    const directive = action.slice(0, idx + 1);
    const details = action.slice(idx + 1).trim();
    return `<b>${directive}</b> ${details}`;
  }
  return `<b>${action}</b>`;
}

window.renderGlobalShapChart = renderGlobalShapChart;
window.DEFAULT_GLOBAL_SHAP = DEFAULT_GLOBAL_SHAP;
