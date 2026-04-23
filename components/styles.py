"""
CricView Global CSS Injection
==============================
Premium dark-theme styling applied to the entire Streamlit app.
"""

import streamlit as st


def inject_global_css():
    """Inject premium CSS styling for the entire app."""
    st.markdown("""
    <style>
        /* ── Import Google Font ─────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        /* ── Global Resets ──────────────────────────────── */
        * { font-family: 'Inter', 'Segoe UI', sans-serif !important; }

        .stApp {
            background: linear-gradient(180deg, #0a0e1a 0%, #0d1321 50%, #111827 100%);
        }

        /* ── Hide Streamlit Branding ───────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] {
            background: rgba(10, 14, 26, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(48, 54, 90, 0.3);
        }

        /* ── Sidebar Styling ───────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #0d1321 100%);
            border-right: 1px solid rgba(48, 54, 90, 0.4);
        }

        section[data-testid="stSidebar"] .stRadio > div {
            gap: 2px;
        }

        section[data-testid="stSidebar"] .stRadio > div > label {
            padding: 10px 16px;
            border-radius: 8px;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }

        section[data-testid="stSidebar"] .stRadio > div > label:hover {
            background: rgba(0, 212, 170, 0.08);
            border-color: rgba(0, 212, 170, 0.2);
        }

        /* ── Typography ────────────────────────────────── */
        h1 {
            color: #e0e6ed !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #e0e6ed 0%, #00d4aa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h2 {
            color: #c8cfd8 !important;
            font-weight: 700 !important;
            font-size: 1.5rem !important;
            letter-spacing: -0.01em;
        }

        h3 {
            color: #8b92a5 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── Metric Cards ──────────────────────────────── */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 18px 22px;
            border-radius: 14px;
            border: 1px solid rgba(48, 54, 90, 0.5);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.3s ease;
        }

        div[data-testid="stMetric"]:hover {
            border-color: rgba(0, 212, 170, 0.4);
            box-shadow: 0 8px 30px rgba(0, 212, 170, 0.1);
            transform: translateY(-2px);
        }

        div[data-testid="stMetric"] label {
            color: #8b92a5 !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #e0e6ed !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }

        div[data-testid="stMetricDelta"] > div {
            font-weight: 600 !important;
        }

        /* ── Dataframe / Table Styling ─────────────────── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }

        div[data-testid="stDataFrame"] > div {
            border-radius: 12px;
            border: 1px solid rgba(48, 54, 90, 0.4);
        }

        /* ── Selectbox / Multiselect ───────────────────── */
        div[data-baseweb="select"] {
            border-radius: 10px !important;
        }

        div[data-baseweb="select"] > div {
            background: #1a1a2e !important;
            border-color: rgba(48, 54, 90, 0.6) !important;
            border-radius: 10px !important;
        }

        div[data-baseweb="select"] > div:hover {
            border-color: rgba(0, 212, 170, 0.5) !important;
        }

        /* ── Tabs ──────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(17, 24, 39, 0.6);
            border-radius: 12px;
            padding: 4px;
            border: 1px solid rgba(48, 54, 90, 0.3);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 0.85rem;
            color: #8b92a5;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%) !important;
            color: #00d4aa !important;
            border: 1px solid rgba(0, 212, 170, 0.3) !important;
        }

        /* ── Plotly Charts Container ───────────────────── */
        div[data-testid="stPlotlyChart"] {
            background: linear-gradient(135deg, #13182a 0%, #161d30 100%);
            border-radius: 14px;
            border: 1px solid rgba(48, 54, 90, 0.35);
            padding: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        /* ── Expander ──────────────────────────────────── */
        details {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(48, 54, 90, 0.4) !important;
        }

        /* ── Dividers ──────────────────────────────────── */
        hr {
            border-color: rgba(48, 54, 90, 0.3) !important;
        }

        /* ── Scrollbar ─────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0e1a;
        }
        ::-webkit-scrollbar-thumb {
            background: #30365a;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00d4aa;
        }

        /* ── Animations ────────────────────────────────── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .element-container {
            animation: fadeInUp 0.4s ease-out;
        }

        /* ── Custom KPI Card ───────────────────────────── */
        .cricview-kpi {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 22px 24px;
            border-radius: 14px;
            border: 1px solid rgba(48, 54, 90, 0.5);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.3s ease;
            min-height: 120px;
        }

        .cricview-kpi:hover {
            border-color: rgba(0, 212, 170, 0.4);
            box-shadow: 0 8px 30px rgba(0, 212, 170, 0.1);
            transform: translateY(-3px);
        }

        .cricview-kpi .kpi-icon {
            font-size: 1.5rem;
            margin-bottom: 4px;
        }

        .cricview-kpi .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #8b92a5;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 6px;
        }

        .cricview-kpi .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            color: #e0e6ed;
            line-height: 1;
            margin-bottom: 4px;
        }

        .cricview-kpi .kpi-delta {
            font-size: 0.8rem;
            font-weight: 600;
        }

        .cricview-kpi .kpi-delta.positive { color: #00d4aa; }
        .cricview-kpi .kpi-delta.negative { color: #ef4444; }

        /* ── Section Headers ───────────────────────────── */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(48, 54, 90, 0.3);
        }

        .section-header .icon { font-size: 1.4rem; }

        .section-header .title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #c8cfd8;
            letter-spacing: -0.01em;
        }

        /* ── Insight Card ──────────────────────────────── */
        .insight-card {
            background: linear-gradient(135deg, rgba(0, 212, 170, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
            border: 1px solid rgba(0, 212, 170, 0.2);
            border-radius: 12px;
            padding: 16px 20px;
            margin: 8px 0;
        }

        .insight-card .insight-icon { font-size: 1.2rem; }

        .insight-card .insight-text {
            color: #c8cfd8;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        /* ── Stat Row ──────────────────────────────────── */
        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(48, 54, 90, 0.2);
        }

        .stat-row .stat-label {
            color: #8b92a5;
            font-size: 0.85rem;
        }

        .stat-row .stat-value {
            color: #e0e6ed;
            font-weight: 700;
            font-size: 0.95rem;
        }
    </style>
    """, unsafe_allow_html=True)
