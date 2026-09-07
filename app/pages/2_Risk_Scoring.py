"""Page 2: Real-time Loan Applicant Risk Scoring and SHAP Explainability."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.predict import RiskPredictor
from src.xai.explainer import CreditRiskExplainer
from app.utils.ui import (
    setup_page,
    get_current_theme,
    get_plotly_template,
    get_svg_icon,
    render_sidebar_footer,
    FAVICON_PATH
)

st.set_page_config(
    page_title="Risk Scoring & SHAP | CreditLens", 
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else None, 
    layout="wide"
)

# Apply global theme (Dark default / Light selectable) and render sidebar
setup_page("Risk Scoring & SHAP")
render_sidebar_footer()

st.title("Real-Time Applicant Risk Scoring & Explainable AI")
st.markdown("Automated loan underwriting with calibrated default probabilities and individual **SHAP feature attributions**.")

# Preset profiles for quick testing
presets = {
    "Prime Low Risk (Software Executive)": {
        "AMT_INCOME_TOTAL": 320000.0,
        "AMT_CREDIT": 600000.0,
        "AMT_ANNUITY": 24000.0,
        "AMT_GOODS_PRICE": 600000.0,
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": "M",
        "NAME_INCOME_TYPE": "Commercial associate",
        "NAME_EDUCATION_TYPE": "Higher education",
        "OCCUPATION_TYPE": "Managers",
        "AGE": 38,
        "YEARS_EMPLOYED": 9.5,
        "EXT_SOURCE_2": 0.72,
        "EXT_SOURCE_3": 0.68,
        "BUREAU_ACTIVE_LOANS": 1.0,
        "PREV_APP_REFUSED_RATE": 0.0
    },
    "Borderline Risk (Mid-Career Sales Representative)": {
        "AMT_INCOME_TOTAL": 140000.0,
        "AMT_CREDIT": 450000.0,
        "AMT_ANNUITY": 28000.0,
        "AMT_GOODS_PRICE": 420000.0,
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": "F",
        "NAME_INCOME_TYPE": "Working",
        "NAME_EDUCATION_TYPE": "Secondary / secondary special",
        "OCCUPATION_TYPE": "Sales staff",
        "AGE": 29,
        "YEARS_EMPLOYED": 2.1,
        "EXT_SOURCE_2": 0.44,
        "EXT_SOURCE_3": 0.38,
        "BUREAU_ACTIVE_LOANS": 3.0,
        "PREV_APP_REFUSED_RATE": 0.25
    },
    "High Risk Defaulter (Overleveraged Driver)": {
        "AMT_INCOME_TOTAL": 90000.0,
        "AMT_CREDIT": 650000.0,
        "AMT_ANNUITY": 35000.0,
        "AMT_GOODS_PRICE": 580000.0,
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": "M",
        "NAME_INCOME_TYPE": "Working",
        "NAME_EDUCATION_TYPE": "Secondary / secondary special",
        "OCCUPATION_TYPE": "Drivers",
        "AGE": 24,
        "YEARS_EMPLOYED": 0.7,
        "EXT_SOURCE_2": 0.18,
        "EXT_SOURCE_3": 0.15,
        "BUREAU_ACTIVE_LOANS": 5.0,
        "PREV_APP_REFUSED_RATE": 0.60
    }
}

selected_preset = st.selectbox("Load Pre-Configured Applicant Archetype:", ["Custom Applicant"] + list(presets.keys()))
p = presets.get(selected_preset, presets["Prime Low Risk (Software Executive)"])

# Input Form
with st.form("applicant_form"):
    st.markdown("### Applicant Financial & Demographic Attributes")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Financial Capacity**")
        income = st.number_input("Annual Income ($)", min_value=10000.0, max_value=2000000.0, value=float(p["AMT_INCOME_TOTAL"]), step=10000.0)
        credit = st.number_input("Requested Credit ($)", min_value=20000.0, max_value=4000000.0, value=float(p["AMT_CREDIT"]), step=25000.0)
        annuity = st.number_input("Annual Annuity Installment ($)", min_value=1000.0, max_value=500000.0, value=float(p["AMT_ANNUITY"]), step=5000.0)
        goods_price = st.number_input("Goods Price ($)", min_value=10000.0, max_value=4000000.0, value=float(p["AMT_GOODS_PRICE"]), step=25000.0)

    with c2:
        st.markdown("**Employment & Demographics**")
        contract_type = st.selectbox("Contract Type", ["Cash loans", "Revolving loans"], index=0 if p["NAME_CONTRACT_TYPE"]=="Cash loans" else 1)
        gender = st.selectbox("Gender", ["M", "F"], index=0 if p["CODE_GENDER"]=="M" else 1)
        income_type = st.selectbox(
            "Income Type", 
            ["Working", "Commercial associate", "State servant", "Pensioner"],
            index=["Working", "Commercial associate", "State servant", "Pensioner"].index(p["NAME_INCOME_TYPE"]) if p["NAME_INCOME_TYPE"] in ["Working", "Commercial associate", "State servant", "Pensioner"] else 0
        )
        education = st.selectbox(
            "Education Level", 
            ["Higher education", "Secondary / secondary special", "Incomplete higher", "Lower secondary"],
            index=0 if p["NAME_EDUCATION_TYPE"]=="Higher education" else 1
        )
        occupation = st.selectbox(
            "Occupation Type", 
            ["Managers", "Core staff", "Accountants", "High skill tech staff", "Sales staff", "Laborers", "Drivers", "Security staff", "Cooking staff"],
            index=["Managers", "Core staff", "Accountants", "High skill tech staff", "Sales staff", "Laborers", "Drivers", "Security staff", "Cooking staff"].index(p["OCCUPATION_TYPE"]) if p["OCCUPATION_TYPE"] in ["Managers", "Core staff", "Accountants", "High skill tech staff", "Sales staff", "Laborers", "Drivers", "Security staff", "Cooking staff"] else 0
        )

    with c3:
        st.markdown("**Credit Bureau & Track Record**")
        age = st.slider("Applicant Age (Years)", min_value=18, max_value=75, value=int(p["AGE"]))
        years_employed = st.slider("Tenure at Current Job (Years)", min_value=0.0, max_value=40.0, value=float(p["YEARS_EMPLOYED"]), step=0.5)
        ext_source_2 = st.slider("Bureau Rating (EXT_SOURCE_2)", min_value=0.01, max_value=0.99, value=float(p["EXT_SOURCE_2"]), step=0.01)
        ext_source_3 = st.slider("Internal Score (EXT_SOURCE_3)", min_value=0.01, max_value=0.99, value=float(p["EXT_SOURCE_3"]), step=0.01)
        active_loans = st.number_input("Active Credit Bureau Accounts", min_value=0, max_value=20, value=int(p["BUREAU_ACTIVE_LOANS"]))
        refused_rate = st.slider("Past Loan Rejection Rate (0 to 1.0)", min_value=0.0, max_value=1.0, value=float(p["PREV_APP_REFUSED_RATE"]), step=0.05)

    submitted = st.form_submit_button("Evaluate Credit Risk & Generate SHAP Explanation", use_container_width=True)

if submitted or "last_prediction" in st.session_state:
    applicant_payload = {
        "AMT_INCOME_TOTAL": income,
        "AMT_CREDIT": credit,
        "AMT_ANNUITY": annuity,
        "AMT_GOODS_PRICE": goods_price,
        "NAME_CONTRACT_TYPE": contract_type,
        "CODE_GENDER": gender,
        "FLAG_OWN_CAR": "Y" if years_employed > 3 else "N",
        "FLAG_OWN_REALTY": "Y",
        "CNT_CHILDREN": 0,
        "NAME_INCOME_TYPE": income_type,
        "NAME_EDUCATION_TYPE": education,
        "NAME_FAMILY_STATUS": "Married",
        "NAME_HOUSING_TYPE": "House / apartment",
        "REGION_POPULATION_RELATIVE": 0.02,
        "DAYS_BIRTH": -int(age * 365),
        "DAYS_EMPLOYED": -int(years_employed * 365),
        "DAYS_REGISTRATION": -2500,
        "DAYS_ID_PUBLISH": -1500,
        "OWN_CAR_AGE": 4.0,
        "OCCUPATION_TYPE": occupation,
        "CNT_FAM_MEMBERS": 2.0,
        "REGION_RATING_CLIENT": 2,
        "REGION_RATING_CLIENT_W_CITY": 2,
        "ORGANIZATION_TYPE": "Business Entity Type 3",
        "EXT_SOURCE_1": (ext_source_2 + ext_source_3) / 2.0,
        "EXT_SOURCE_2": ext_source_2,
        "EXT_SOURCE_3": ext_source_3,
        "BUREAU_ACTIVE_LOANS": float(active_loans),
        "PREV_APP_REFUSED_RATE": float(refused_rate)
    }

    try:
        predictor = RiskPredictor()
        prediction = predictor.predict_single(applicant_payload)
        st.session_state["last_prediction"] = prediction

        prob = prediction["default_probability"]
        band = prediction["risk_band"]
        score = prediction["credit_score_proxy"]
        proc_features = pd.Series(prediction["processed_features"])

        st.markdown("<hr style='margin: 28px 0; border: none; border-top: 1px solid var(--border-glass);'>", unsafe_allow_html=True)
        st.subheader("Underwriting Decision & Risk Classification")

        # Visual Scoreboard
        col_gauge, col_decision = st.columns([2, 3])

        current_theme = get_current_theme()
        text_color = "#f8fafc" if current_theme == "dark" else "#0f172a"
        border_color = "#334155" if current_theme == "dark" else "#cbd5e1"

        with col_gauge:
            # Plotly Gauge Chart with dynamic theme sync
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Default Probability", 'font': {'size': 18, 'color': text_color}},
                number={'suffix': "%", 'font': {'size': 32, 'color': text_color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                    'bar': {'color': "#ef4444" if band=="High" else ("#f59e0b" if band=="Medium" else "#10b981")},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': border_color,
                    'steps': [
                        {'range': [0, 20], 'color': "rgba(16, 185, 129, 0.20)"},
                        {'range': [20, 50], 'color': "rgba(245, 158, 11, 0.20)"},
                        {'range': [50, 100], 'color': "rgba(239, 68, 68, 0.20)"}
                    ],
                    'threshold': {
                        'line': {'color': text_color, 'width': 3},
                        'thickness': 0.8,
                        'value': prob * 100
                    }
                }
            ))
            fig_gauge.update_layout(
                template="plotly_dark" if current_theme == "dark" else "plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=280, 
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_decision:
            badge_class = "badge-low" if band=="Low" else ("badge-medium" if band=="Medium" else "badge-high")
            
            if band == "Low":
                policy_action = '<span class="badge-low">Approved</span> Fast-track automated approval with standard prime pricing tier.'
            elif band == "Medium":
                policy_action = '<span class="badge-medium">Conditional Review</span> Require secondary proof of income and maximum 3-year term.'
            else:
                policy_action = '<span class="badge-high">Declined</span> Escalate to Special Assets Committee due to elevated default probability.'

            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <h3 style="margin: 0; font-size: 1.3rem;">Risk Classification</h3>
                    <span class="{badge_class}">{band.upper()} RISK</span>
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; margin: 12px 0 6px 0; color: var(--text-primary);">
                    Estimated Credit Score: {score} / 850
                </div>
                <p style="color: var(--text-secondary); line-height: 1.6; margin: 10px 0;">
                    <b>Policy Recommendation:</b><br>{policy_action}
                </p>
                <div style="font-size: 0.82rem; color: var(--text-muted); border-top: 1px solid var(--border-glass); padding-top: 10px; margin-top: 10px;">
                    Debt-to-Income: <b>{credit/income:.2f}x</b> &nbsp;|&nbsp; Payment-to-Credit Rate: <b>{annuity/credit*100:.1f}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ----------------- SHAP EXPLANATION SECTION -----------------
        st.markdown("### Explainable AI: SHAP Feature Attribution")
        st.markdown("Identifies exactly which financial and demographic factors pushed this applicant's risk up or down.")

        explainer = CreditRiskExplainer()

        col_shap, col_drivers = st.columns([3, 2])
        with col_shap:
            st.markdown("#### Local SHAP Waterfall Plot")
            fig_waterfall = explainer.explain_local_waterfall(proc_features)
            st.pyplot(fig_waterfall)

        with col_drivers:
            st.markdown("#### Top Risk Driving Features")
            drivers = explainer.get_local_top_drivers(proc_features, top_k=6)
            df_drivers = pd.DataFrame(drivers)
            st.dataframe(
                df_drivers,
                column_config={
                    "feature": "Feature Name",
                    "value": "Applicant Value",
                    "shap_impact": st.column_config.NumberColumn("SHAP Impact (+/-)", format="%.4f"),
                    "direction": "Effect on Default Risk"
                },
                hide_index=True,
                use_container_width=True
            )
            st.caption("Positive SHAP values elevate default probability; negative values reduce it.")

    except Exception as e:
        st.error(f"Error executing risk assessment pipeline: {str(e)}")
        st.info("Ensure the LightGBM model has finished training in the background.")
