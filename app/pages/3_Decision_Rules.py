"""Page 3: ML-Derived Decision Rules and Credit Policy Formulation."""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.xai.explainer import CreditRiskExplainer
from app.utils.ui import (
    setup_page,
    get_current_theme,
    get_svg_icon,
    render_sidebar_footer,
    FAVICON_PATH
)

st.set_page_config(
    page_title="Credit Decision Rules | CreditLens", 
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else None, 
    layout="wide"
)

# Apply global theme (Dark default / Light selectable) and render sidebar
setup_page("Credit Decision Rules")
render_sidebar_footer()

st.title("Machine Learning Decision Rules & Credit Policy")
st.markdown("Translating complex tree-based gradient boosted models into **auditable, business-readable decision logic** for compliance and credit policy committees.")

tabs = st.tabs([
    "Derived Business Decision Rules", 
    "Global Feature Importance (SHAP Beeswarm)", 
    "Regulatory & Compliance Alignment"
])

# ----------------- TAB 1: DERIVED DECISION RULES -----------------
with tabs[0]:
    st.subheader("Automated Credit Policy Rules Derived from LightGBM Splits")
    st.markdown("These rules represent critical non-linear decision boundaries identified by the model with empirical statistical confidence.")

    explainer = CreditRiskExplainer()
    rules = explainer.get_derived_decision_rules()

    filter_tier = st.radio("Filter Rules by Risk Tier:", ["All Rules", "High Risk Rules Only", "Medium Risk Rules Only", "Low Risk Rules Only"], horizontal=True)

    current_theme = get_current_theme()
    rule_code_bg = "rgba(15, 23, 42, 0.6)" if current_theme == "dark" else "rgba(241, 245, 249, 0.95)"
    rule_code_color = "#60a5fa" if current_theme == "dark" else "#2563eb"

    for r in rules:
        is_high = "HIGH" in r["risk_outcome"]
        is_med = "MEDIUM" in r["risk_outcome"]
        is_low = "LOW" in r["risk_outcome"]

        if filter_tier == "High Risk Rules Only" and not is_high:
            continue
        if filter_tier == "Medium Risk Rules Only" and not is_med:
            continue
        if filter_tier == "Low Risk Rules Only" and not is_low:
            continue

        if is_high:
            badge_class = "badge-high"
        elif is_med:
            badge_class = "badge-medium"
        else:
            badge_class = "badge-low"

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; font-size: 1.1rem;">Rule ID: <code>{r['rule_id']}</code></h4>
                <span class="{badge_class}">{r['risk_outcome']} &bull; Confidence: {r['confidence']}</span>
            </div>
            <div style="background: {rule_code_bg}; border: 1px solid var(--border-glass); border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; font-family: monospace; color: {rule_code_color}; font-weight: 500;">
                IF {r['condition']} &rarr; {r['risk_outcome']}
            </div>
            <p style="color: var(--text-primary); margin-bottom: 8px; line-height: 1.5;">
                <b>Business Rationale:</b> {r['business_rationale']}
            </p>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0;">
                <b>Mandated Underwriting Action:</b> {r['policy_action']}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 2: GLOBAL SHAP BEESWARM -----------------
with tabs[1]:
    st.subheader("Global Explanatory Attribution (Top 20 Features)")
    st.markdown("""
    The SHAP summary beeswarm plot visualizes the distribution and impact of top predictive drivers across the validation portfolio.
    Red dots indicate high feature values; blue dots indicate low feature values.
    """)

    try:
        fig_global = explainer.explain_global(max_display=18)
        st.pyplot(fig_global)
    except Exception as e:
        st.warning(f"Global SHAP calculation in progress or model artifact updating ({str(e)}).")

# ----------------- TAB 3: REGULATORY COMPLIANCE -----------------
with tabs[2]:
    st.subheader("Auditable AI & Fair Lending Compliance")
    st.markdown("""
    <div class="glass-card">
        <h4 style="margin-top: 0;">Fair Lending & Adverse Action Governance</h4>
        <p style="color: var(--text-secondary); line-height: 1.6;">
            Under the Equal Credit Opportunity Act (ECOA) and GDPR Article 22, financial institutions must provide clear, 
            non-discriminatory adverse action notices whenever an applicant is denied credit.
        </p>
        <ul style="color: var(--text-secondary); line-height: 1.7;">
            <li><b>Individualized Adverse Action Notices:</b> Using local SHAP waterfall decompositions, underwriters can extract the exact top 4 reasons for any loan refusal directly from the mathematical model.</li>
            <li><b>Disparate Impact Guardrails:</b> Model inputs strictly isolate financial capacity, external bureau reliability, and repayment track record. Sensitive demographic attributes are barred from driving rejection thresholds.</li>
            <li><b>Model Governance & Version Control:</b> All decision boundaries and threshold adjustments are versioned with reproducible random seeds and tracked cross-validation splits.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
