/**
 * Decision Rules Page Controller
 * Displays machine learning derived rules, confidence ratings, and policy engine flowchart
 */

let currentRuleFilter = 'all';

async function initRulesPage(filter = 'all') {
  currentRuleFilter = filter;
  try {
    const data = await api.getDecisionRules(filter);

    // 1. Update Metrics
    document.getElementById('rules-count-total').textContent = data.total_rules;
    document.getElementById('rules-count-high').textContent = data.high_risk_count;
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
              IF ${formatRuleCondition(r.condition)} THEN <span class="${r.risk_type === 'low' ? 'k' : 'r'}">${r.risk_outcome}</span>
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

  } catch (err) {
    console.error('Failed to load decision rules:', err);
  }
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
