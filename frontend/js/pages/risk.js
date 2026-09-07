/**
 * Risk Scoring Page Controller
 * Handles applicant inputs, preset archetype loading, real-time LightGBM inference,
 * gauge visualization, SHAP factor attribution bars, and AI explanation
 */

let riskPresets = [];

async function initRiskPage() {
  try {
    riskPresets = await api.getRiskPresets();
    const presetSelect = document.getElementById('risk-preset-select');
    if (presetSelect && presetSelect.options.length <= 1) {
      riskPresets.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        presetSelect.appendChild(opt);
      });

      // Default load first preset
      if (riskPresets.length > 0) {
        presetSelect.value = riskPresets[0].id;
        loadRiskPreset(riskPresets[0].id);
      }
    }
  } catch (err) {
    console.error('Failed to load risk presets:', err);
  }
}

function loadRiskPreset(presetId) {
  const p = riskPresets.find(x => x.id === presetId);
  if (!p) return;

  const d = p.data;
  document.getElementById('input-income').value = d.AMT_INCOME_TOTAL;
  document.getElementById('input-credit').value = d.AMT_CREDIT;
  document.getElementById('input-annuity').value = d.AMT_ANNUITY;
  document.getElementById('input-goods-price').value = d.AMT_GOODS_PRICE;
  document.getElementById('input-contract-type').value = d.NAME_CONTRACT_TYPE;
  document.getElementById('input-gender').value = d.CODE_GENDER;
  document.getElementById('input-income-type').value = d.NAME_INCOME_TYPE;
  document.getElementById('input-education').value = d.NAME_EDUCATION_TYPE;
  document.getElementById('input-occupation').value = d.OCCUPATION_TYPE;

  // Sliders
  document.getElementById('input-age').value = d.AGE;
  document.getElementById('val-age').textContent = `${d.AGE} yrs`;

  document.getElementById('input-employed').value = d.YEARS_EMPLOYED;
  document.getElementById('val-employed').textContent = `${d.YEARS_EMPLOYED} yrs`;

  document.getElementById('input-ext2').value = d.EXT_SOURCE_2;
  document.getElementById('val-ext2').textContent = d.EXT_SOURCE_2.toFixed(2);

  document.getElementById('input-ext3').value = d.EXT_SOURCE_3;
  document.getElementById('val-ext3').textContent = d.EXT_SOURCE_3.toFixed(2);

  document.getElementById('input-active-loans').value = d.BUREAU_ACTIVE_LOANS;

  document.getElementById('input-refused-rate').value = d.PREV_APP_REFUSED_RATE;
  document.getElementById('val-refused-rate').textContent = `${Math.round(d.PREV_APP_REFUSED_RATE * 100)}%`;

  const statusEl = document.getElementById('risk-lookup-status');
  if (statusEl) {
    statusEl.innerHTML = `Loaded archetype: <b>${escapeHtml(p.name)}</b>`;
    statusEl.style.color = 'var(--ink-dim)';
  }
}

async function lookupAndLoadApplicant(skId) {
  if (!skId) return;
  const statusEl = document.getElementById('risk-lookup-status');
  if (statusEl) {
    statusEl.textContent = `Querying SQLite database for applicant SK_ID_CURR ${skId}...`;
    statusEl.style.color = 'var(--ink-dim)';
  }

  try {
    const res = await api.lookupApplicant(skId);
    if (!res || !res.data) {
      if (statusEl) {
        statusEl.textContent = `Applicant ID ${skId} not found in database.`;
        statusEl.style.color = '#b85c3e';
      }
      return;
    }

    const d = res.data;
    document.getElementById('input-income').value = d.AMT_INCOME_TOTAL;
    document.getElementById('input-credit').value = d.AMT_CREDIT;
    document.getElementById('input-annuity').value = d.AMT_ANNUITY;
    document.getElementById('input-goods-price').value = d.AMT_GOODS_PRICE;
    document.getElementById('input-contract-type').value = d.NAME_CONTRACT_TYPE;
    document.getElementById('input-gender').value = d.CODE_GENDER;
    document.getElementById('input-income-type').value = d.NAME_INCOME_TYPE;
    document.getElementById('input-education').value = d.NAME_EDUCATION_TYPE;
    document.getElementById('input-occupation').value = d.OCCUPATION_TYPE;

    document.getElementById('input-age').value = d.AGE;
    document.getElementById('val-age').textContent = `${d.AGE} yrs`;

    document.getElementById('input-employed').value = d.YEARS_EMPLOYED;
    document.getElementById('val-employed').textContent = `${d.YEARS_EMPLOYED} yrs`;

    document.getElementById('input-ext2').value = d.EXT_SOURCE_2;
    document.getElementById('val-ext2').textContent = d.EXT_SOURCE_2.toFixed(2);

    document.getElementById('input-ext3').value = d.EXT_SOURCE_3;
    document.getElementById('val-ext3').textContent = d.EXT_SOURCE_3.toFixed(2);

    document.getElementById('input-active-loans').value = d.BUREAU_ACTIVE_LOANS;
    document.getElementById('input-refused-rate').value = d.PREV_APP_REFUSED_RATE;
    document.getElementById('val-refused-rate').textContent = `${Math.round(d.PREV_APP_REFUSED_RATE * 100)}%`;

    if (statusEl) {
      const isDef = res.actual_target === 1;
      statusEl.innerHTML = `Loaded applicant <b>#${skId}</b> from SQLite &middot; <span style="display:inline-block; padding:2px 8px; border-radius:2px; font-weight:700; font-size:11px; background:${isDef ? '#fee2e2; color:#b91c1c;' : '#dcfce7; color:#15803d;'}">Historical Ground Truth: ${res.actual_outcome}</span>`;
    }
  } catch (err) {
    if (statusEl) {
      statusEl.textContent = `Error: ${err.message}`;
      statusEl.style.color = '#b85c3e';
    }
  }
}
window.lookupAndLoadApplicant = lookupAndLoadApplicant;

async function handleRiskEvaluation(e) {
  if (e) e.preventDefault();

  const evalBtn = document.getElementById('btn-evaluate-risk');
  const resultsContainer = document.getElementById('risk-results-container');
  const errorAlert = document.getElementById('risk-error-alert');

  errorAlert.style.display = 'none';
  evalBtn.disabled = true;
  evalBtn.innerHTML = '<span class="spinner"></span> Evaluating Risk & SHAP...';

  const payload = {
    AMT_INCOME_TOTAL: parseFloat(document.getElementById('input-income').value) || 150000,
    AMT_CREDIT: parseFloat(document.getElementById('input-credit').value) || 500000,
    AMT_ANNUITY: parseFloat(document.getElementById('input-annuity').value) || 25000,
    AMT_GOODS_PRICE: parseFloat(document.getElementById('input-goods-price').value) || 500000,
    NAME_CONTRACT_TYPE: document.getElementById('input-contract-type').value,
    CODE_GENDER: document.getElementById('input-gender').value,
    NAME_INCOME_TYPE: document.getElementById('input-income-type').value,
    NAME_EDUCATION_TYPE: document.getElementById('input-education').value,
    OCCUPATION_TYPE: document.getElementById('input-occupation').value,
    AGE: parseFloat(document.getElementById('input-age').value),
    YEARS_EMPLOYED: parseFloat(document.getElementById('input-employed').value),
    EXT_SOURCE_2: parseFloat(document.getElementById('input-ext2').value),
    EXT_SOURCE_3: parseFloat(document.getElementById('input-ext3').value),
    BUREAU_ACTIVE_LOANS: parseFloat(document.getElementById('input-active-loans').value),
    PREV_APP_REFUSED_RATE: parseFloat(document.getElementById('input-refused-rate').value)
  };

  try {
    const res = await api.evaluateRisk(payload);
    const riskBand = String(res.risk_band || '').toUpperCase();

    // 1. Populate Verdict Scorecard
    const probValEl = document.getElementById('res-prob-val');
    if (probValEl) probValEl.textContent = `${res.default_probability_pct}%`;
    
    const creditScoreEl = document.getElementById('res-credit-score');
    if (creditScoreEl) creditScoreEl.textContent = `${res.credit_score_proxy} / 850`;

    const decisionEl = document.getElementById('res-decision');
    if (decisionEl) decisionEl.textContent = res.decision;

    const policyEl = document.getElementById('res-policy-action');
    if (policyEl) policyEl.textContent = res.policy_recommendation;

    const debtRatioEl = document.getElementById('res-debt-ratio');
    if (debtRatioEl) debtRatioEl.textContent = `${res.credit_income_ratio}×`;

    const payRateEl = document.getElementById('res-payment-rate');
    if (payRateEl) payRateEl.textContent = `${res.payment_rate_pct}%`;

    // 2. Risk Badge & Decision Styling
    const badgeEl = document.getElementById('res-risk-badge');
    if (badgeEl) {
      badgeEl.className = 'risk-flag' + (riskBand === 'LOW' ? ' low' : (riskBand === 'MEDIUM' ? ' medium' : ''));
      badgeEl.textContent = `${riskBand} RISK`;
    }

    const decisionRow = document.getElementById('res-decision-row');
    if (decisionRow) {
      decisionRow.className = 'row decision' + (res.decision === 'APPROVED' ? ' approved' : '');
    }

    // 3. Render SVG Circular Gauge
    const gaugeCircle = document.getElementById('risk-gauge-circle');
    if (gaugeCircle) {
      const circum = 339.3;
      const offset = circum * (1 - (Math.min(100, Math.max(0, res.default_probability_pct)) / 100));
      gaugeCircle.style.strokeDashoffset = offset;
      if (riskBand === 'HIGH') {
        gaugeCircle.style.stroke = '#C1543F';
      } else if (riskBand === 'MEDIUM') {
        gaugeCircle.style.stroke = '#D99A3C';
      } else {
        gaugeCircle.style.stroke = '#5FA83D';
      }
    }

    // 4. Render SHAP Risk Factors (Diverging horizontal bars matching mockup)
    renderShapFactors(res.risk_reducing_factors, res.risk_increasing_factors);

    // 5. Populate AI Explanation
    const expTextEl = document.getElementById('res-explanation-text') || document.getElementById('res-ai-narrative');
    if (expTextEl) expTextEl.textContent = res.ai_explanation;

    // 6. Populate Live Model Confidence Signals (bottom-right panel)
    const ext2Val = parseFloat(document.getElementById('input-ext2').value);
    const creditVal = parseFloat(document.getElementById('input-credit').value);
    const incomeVal = parseFloat(document.getElementById('input-income').value);
    const refusedVal = parseFloat(document.getElementById('input-refused-rate').value);

    const sigExt2 = document.getElementById('res-sig-ext2');
    if (sigExt2) {
      const ext2Status = ext2Val < 0.25 ? '⚠ CRITICAL (<0.25)' : ext2Val < 0.40 ? '↓ BELOW SAFE (<0.40)' : '✓ WITHIN RANGE';
      const ext2Color = ext2Val < 0.25 ? '#C1543F' : ext2Val < 0.40 ? '#D99A3C' : '#3C7A26';
      sigExt2.textContent = `${ext2Val.toFixed(2)} — ${ext2Status}`;
      sigExt2.style.color = ext2Color;
    }

    const sigLeverage = document.getElementById('res-sig-leverage');
    if (sigLeverage && incomeVal > 0) {
      const leverage = (creditVal / incomeVal).toFixed(2);
      const levStatus = leverage > 6 ? '⚠ SEVERE (>6.0×)' : leverage > 4 ? '↑ ELEVATED (>4.0×)' : '✓ ACCEPTABLE';
      const levColor = leverage > 6 ? '#C1543F' : leverage > 4 ? '#D99A3C' : '#3C7A26';
      sigLeverage.textContent = `${leverage}× income — ${levStatus}`;
      sigLeverage.style.color = levColor;
    }

    const sigRefusal = document.getElementById('res-sig-refusal');
    if (sigRefusal) {
      const refPct = Math.round(refusedVal * 100);
      const refStatus = refusedVal >= 0.40 ? '⚠ HIGH RISK FLAG' : refusedVal >= 0.20 ? '↑ MONITOR' : '✓ CLEAN HISTORY';
      const refColor = refusedVal >= 0.40 ? '#C1543F' : refusedVal >= 0.20 ? '#D99A3C' : '#3C7A26';
      sigRefusal.textContent = `${refPct}% refusal rate — ${refStatus}`;
      sigRefusal.style.color = refColor;
    }

    if (resultsContainer) {
      resultsContainer.style.display = 'block';
    }

    // Smoothly scroll down to prediction section
    setTimeout(() => {
      const predSection = document.getElementById('risk-results-container');
      if (predSection) {
        predSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 80);

  } catch (err) {
    console.error('Risk evaluation failed:', err);
    if (errorAlert) {
      errorAlert.textContent = `Unable to generate risk assessment: ${err.message}`;
      errorAlert.style.display = 'block';
    }
  } finally {
    evalBtn.disabled = false;
    evalBtn.textContent = 'Evaluate Credit Risk & View Prediction ↓';
  }
}

function renderShapFactors(reducing, increasing) {
  const reducingContainer = document.getElementById('res-factors-reducing') || document.getElementById('shap-reducing-container');
  const increasingContainer = document.getElementById('res-factors-increasing') || document.getElementById('shap-increasing-container');

  // Max impact for relative scaling
  const allImpacts = [...reducing, ...increasing].map(d => Math.abs(d.shap_impact));
  const maxImpact = Math.max(...allImpacts, 0.05);

  if (reducingContainer) {
    if (reducing.length === 0) {
      reducingContainer.innerHTML = '<div style="color:var(--ink-dim); font-size:11px;">No significant risk-reducing factors.</div>';
    } else {
      reducingContainer.innerHTML = reducing.slice(0, 4).map(d => {
        const pct = Math.min(100, Math.round((Math.abs(d.shap_impact) / maxImpact) * 100));
        const label = d.feature.replace(/_/g, ' ').toLowerCase();
        return `
          <div class="shap-row g">
            <div class="lbl"><span>${label}</span><span>${d.shap_impact.toFixed(2)}</span></div>
            <div class="bar"><i style="width: ${pct}%;"></i></div>
          </div>
        `;
      }).join('');
    }
  }

  if (increasingContainer) {
    if (increasing.length === 0) {
      increasingContainer.innerHTML = '<div style="color:var(--ink-dim); font-size:11px;">No significant risk-increasing factors.</div>';
    } else {
      increasingContainer.innerHTML = increasing.slice(0, 4).map(d => {
        const pct = Math.min(100, Math.round((Math.abs(d.shap_impact) / maxImpact) * 100));
        const label = d.feature.replace(/_/g, ' ').toLowerCase();
        return `
          <div class="shap-row r">
            <div class="lbl"><span>${label}</span><span>+${d.shap_impact.toFixed(2)}</span></div>
            <div class="bar"><i style="width: ${pct}%;"></i></div>
          </div>
        `;
      }).join('');
    }
  }
}
