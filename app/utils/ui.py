"""UI utilities, theme management, SVG iconography, and styling helpers for NeoStats Platform."""

import streamlit as st
from pathlib import Path
from typing import Dict, Any

APP_DIR = Path(__file__).resolve().parent.parent
FAVICON_PATH = APP_DIR / "assets" / "favicon.png"
CSS_PATH = APP_DIR / "styles" / "theme.css"

# Modern SVG Vector Icons (Zero emojis)
SVG_ICONS = {
    "shield": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>""",
    "zap": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>""",
    "rules": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>""",
    "message": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>""",
    "alert": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>""",
    "database": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>""",
    "moon": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>""",
    "sun": """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>""",
}

def get_svg_icon(name: str, size: int = 18, color: str = "currentColor") -> str:
    """Return inline SVG icon markup by name."""
    template = SVG_ICONS.get(name, SVG_ICONS["shield"])
    return template.format(size=size, color=color)

def init_theme_state() -> str:
    """Initialize theme session state with 'dark' as default."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    return st.session_state["theme"]

def get_current_theme() -> str:
    """Get current active theme ('dark' or 'light')."""
    return st.session_state.get("theme", "dark")

def inject_theme_css():
    """Read theme.css and inject direct CSS variable overrides based on active theme."""
    theme = get_current_theme()
    css_content = ""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()

    if theme == "light":
        theme_override = f"""
        <style>
        {css_content}

        /* Light Mode Stripe/Linear Theme */
        .stApp {{
          background-color: #f8fafc !important;
          color: #0f172a !important;
        }}
        section[data-testid="stSidebar"] {{
          background-color: #ffffff !important;
          border-right: 1px solid #e2e8f0 !important;
        }}
        header[data-testid="stHeader"] {{
          background-color: transparent !important;
        }}
        .hero-banner {{
          background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%) !important;
          border: 1px solid #bfdbfe !important;
          box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04) !important;
        }}
        .hero-title {{
          color: #0f172a !important;
          -webkit-text-fill-color: #0f172a !important;
        }}
        .hero-subtitle {{
          color: #475569 !important;
        }}
        .glass-card, .stat-box {{
          background: #ffffff !important;
          border: 1px solid #e2e8f0 !important;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        }}
        .glass-card:hover, .stat-box:hover {{
          border-color: #3b82f6 !important;
          box-shadow: 0 8px 24px rgba(59, 130, 246, 0.10) !important;
        }}
        .stat-val {{
          color: #0f172a !important;
        }}
        .stat-label {{
          color: #64748b !important;
        }}
        .stMarkdown, p, span, label, h1, h2, h3, h4, h5, h6 {{
          color: #0f172a !important;
        }}
        div[data-testid="stMetricValue"] {{
          color: #0f172a !important;
        }}
        div[data-testid="stMetricLabel"] {{
          color: #64748b !important;
        }}
        div[data-baseweb="input"], div[data-baseweb="select"] {{
          background-color: #ffffff !important;
          border: 1px solid #cbd5e1 !important;
        }}
        div[data-baseweb="input"] input {{
          color: #0f172a !important;
        }}
        div[data-baseweb="tab-list"] {{
          border-bottom: 1px solid #e2e8f0 !important;
        }}
        button[data-baseweb="tab"] {{
          color: #64748b !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
          color: #2563eb !important;
          border-bottom: 2px solid #2563eb !important;
        }}
        .badge-low {{
          background: #ecfdf5 !important;
          color: #059669 !important;
          border: 1px solid #a7f3d0 !important;
        }}
        .badge-medium {{
          background: #fffbeb !important;
          color: #d97706 !important;
          border: 1px solid #fde68a !important;
        }}
        .badge-high {{
          background: #fff1f2 !important;
          color: #e11d48 !important;
          border: 1px solid #fecdd3 !important;
        }}
        </style>
        """
    else:
        theme_override = f"""
        <style>
        {css_content}

        /* Dark Mode Slate/Navy Theme */
        .stApp {{
          background-color: #090d16 !important;
          color: #f8fafc !important;
        }}
        section[data-testid="stSidebar"] {{
          background-color: #0d121f !important;
          border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }}
        </style>
        """

    st.markdown(theme_override, unsafe_allow_html=True)

def render_theme_toggle():
    """Render a clean, high-design Dark/Light mode switcher in sidebar with clear segmented buttons."""
    current = get_current_theme()
    
    st.sidebar.markdown(
        """
        <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 6px;">
            Theme Mode
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    col_d, col_l = st.sidebar.columns(2)
    with col_d:
        dark_active = (current == "dark")
        if st.button("Dark", key="btn_dark_theme", use_container_width=True, type="primary" if dark_active else "secondary"):
            if current != "dark":
                st.session_state["theme"] = "dark"
                st.rerun()

    with col_l:
        light_active = (current == "light")
        if st.button("Light", key="btn_light_theme", use_container_width=True, type="primary" if light_active else "secondary"):
            if current != "light":
                st.session_state["theme"] = "light"
                st.rerun()

def render_sidebar_header():
    """Render consistent brand header in sidebar."""
    render_theme_toggle()
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns([1, 4])
    with col1:
        if FAVICON_PATH.exists():
            st.image(str(FAVICON_PATH), width=42)
    with col2:
        st.markdown("""
        <div style="line-height: 1.15; padding-top: 2px;">
            <div style="font-size: 1.15rem; font-weight: 800; letter-spacing: 0.04em;">NEOSTATS</div>
            <div style="font-size: 0.75rem; font-weight: 500; color: #3b82f6;">Risk Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid var(--border-glass);'>", unsafe_allow_html=True)

def render_sidebar_footer():
    """Render clean sidebar footer without emojis."""
    st.sidebar.markdown("<hr style='margin: 20px 0 10px 0; border: none; border-top: 1px solid var(--border-glass);'>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.5;">
        <span style="font-weight: 600;">NeoStats Engine</span><br>
        LightGBM GBDT • SHAP XAI • Groq Qwen
    </div>
    """, unsafe_allow_html=True)

def setup_page(page_title: str):
    """Convenience bootstrap for all pages."""
    init_theme_state()
    inject_theme_css()
    render_sidebar_header()

def get_plotly_template() -> Dict[str, Any]:
    """Return optimized layout parameters for Plotly graphs based on theme."""
    theme = get_current_theme()
    if theme == "light":
        return {
            "template": "plotly_white",
            "paper_bgcolor": "rgba(255, 255, 255, 0.0)",
            "plot_bgcolor": "rgba(255, 255, 255, 0.0)",
            "font": {"family": "Inter, sans-serif", "color": "#0f172a"},
            "xaxis": {
                "gridcolor": "#e2e8f0",
                "linecolor": "#cbd5e1",
                "tickfont": {"color": "#475569"}
            },
            "yaxis": {
                "gridcolor": "#e2e8f0",
                "linecolor": "#cbd5e1",
                "tickfont": {"color": "#475569"}
            }
        }
    else:
        return {
            "template": "plotly_dark",
            "paper_bgcolor": "rgba(10, 14, 26, 0.0)",
            "plot_bgcolor": "rgba(10, 14, 26, 0.0)",
            "font": {"family": "Inter, sans-serif", "color": "#f8fafc"},
            "xaxis": {
                "gridcolor": "rgba(255, 255, 255, 0.07)",
                "linecolor": "rgba(255, 255, 255, 0.15)",
                "tickfont": {"color": "#94a3b8"}
            },
            "yaxis": {
                "gridcolor": "rgba(255, 255, 255, 0.07)",
                "linecolor": "rgba(255, 255, 255, 0.15)",
                "tickfont": {"color": "#94a3b8"}
            }
        }
