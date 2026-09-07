"""NeoStats AI Credit Risk Intelligence Platform - Main Application."""

import streamlit as st
from pathlib import Path
import json
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.ui import (
    setup_page,
    get_svg_icon,
    render_sidebar_footer,
    FAVICON_PATH
)

st.set_page_config(
    page_title="NeoStats | Credit Risk Intelligence Platform",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global theme (Dark default / Light selectable) and render sidebar
setup_page("Home")

# Sidebar Module Guide
st.sidebar.markdown(
    """
    <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 8px;">
        Navigation Index
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown(f"""
<div style="font-size: 0.86rem; color: var(--text-secondary); line-height: 1.8;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
        {get_svg_icon('chart', 16, '#3b82f6')} <span><b>1. EDA & Insights</b></span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
        {get_svg_icon('zap', 16, '#f59e0b')} <span><b>2. Risk Scoring & SHAP</b></span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
        {get_svg_icon('rules', 16, '#10b981')} <span><b>3. Decision Rules</b></span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
        {get_svg_icon('message', 16, '#06b6d4')} <span><b>4. Talk-to-Data</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

render_sidebar_footer()

# Hero Banner with clean SVG shield and high-contrast typography
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">
        {get_svg_icon('shield', 34, '#3b82f6')}
        <span>AI-Powered Credit Risk Intelligence Platform</span>
    </div>
    <div class="hero-subtitle">
        Enterprise-grade credit scoring, explainable underwriting via SHAP, automated decision rule derivation, 
        and natural-language data exploration backed by generative AI.
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics Summary Cards
metrics_path = Path(__file__).resolve().parent.parent / "models" / "metrics.json"
roc_val = "0.728"
pr_val = "0.233"
feat_val = "144"

if metrics_path.exists():
    try:
        with open(metrics_path, "r") as f:
            m = json.load(f)
            roc_val = f"{m.get('test_roc_auc', 0.728):.3f}"
            pr_val = f"{m.get('test_pr_auc', 0.233):.3f}"
            feat_val = str(m.get('n_features', 144))
    except Exception:
        pass

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">Model ROC-AUC</div>
        <div class="stat-val">{roc_val}</div>
        <div class="stat-subtext">+26.2% over baseline</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">PR-AUC (Imbalance Score)</div>
        <div class="stat-val">{pr_val}</div>
        <div class="stat-subtext">Scale Pos Weight: 11.5x</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">Engineered Features</div>
        <div class="stat-val">{feat_val}</div>
        <div class="stat-subtext">3 Tables Joined</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-label">Talk-to-Data Engine</div>
        <div class="stat-val">Groq LLM</div>
        <div class="stat-subtext">NL to SQL + Insights</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Platform Navigation Cards
st.subheader("Platform Modules")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            {get_svg_icon('chart', 22, '#3b82f6')}
            <h3 style="margin: 0; font-size: 1.25rem;">1. Exploratory Data Analysis</h3>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;">
            Deep data quality assessment, feature categorization, missing value distributions, 
            and 5 strategic business findings detailing demographic, financial, and repayment patterns.
        </p>
        <span class="badge-low">5 Visual Business Insights</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            {get_svg_icon('zap', 22, '#f59e0b')}
            <h3 style="margin: 0; font-size: 1.25rem;">2. Real-Time Risk Scoring & SHAP</h3>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;">
            Instant credit default probability inference, calibrated risk tiers 
            (Low, Medium, High), credit score proxy, and local SHAP waterfall feature attributions.
        </p>
        <span class="badge-medium">Explainable AI (SHAP)</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            {get_svg_icon('rules', 22, '#10b981')}
            <h3 style="margin: 0; font-size: 1.25rem;">3. Decision Rules & Policy Formulation</h3>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;">
            Human-interpretable decision boundaries automatically derived from tree splits 
            and SHAP value distributions to bridge machine learning with corporate credit underwriting.
        </p>
        <span class="badge-low">Auditable Credit Rules</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            {get_svg_icon('message', 22, '#06b6d4')}
            <h3 style="margin: 0; font-size: 1.25rem;">4. Talk-to-Data Conversational Agent</h3>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;">
            Natural-language to SQL assistant backed by Groq LLM inference. Runs real-time analytical queries 
            against SQLite database with safety verification and executive summaries.
        </p>
        <span class="badge-high">NL-to-SQL + Verification</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 24px 0 16px 0; border: none; border-top: 1px solid var(--border-glass);'>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size: 0.9rem; color: var(--text-secondary);">
    <b>Getting Started:</b> Select any module from the sidebar navigation to interact with the platform.
</div>
""", unsafe_allow_html=True)
