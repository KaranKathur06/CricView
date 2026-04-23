"""
🏏 CricView — Cricket Intelligence Platform
=============================================
Entry point for the Streamlit multi-page application.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for all deployment platforms
PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from components.styles import inject_global_css

# ── Page Configuration ───────────────────────────────────────
st.set_page_config(
    page_title="CricView — Cricket Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Global CSS ────────────────────────────────────────
inject_global_css()

# ── Sidebar Branding ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="font-size: 3rem; margin-bottom: 4px;">🏏</div>
        <div style="font-size: 1.5rem; font-weight: 800; 
                    background: linear-gradient(135deg, #00d4aa 0%, #3b82f6 100%);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    background-clip: text; letter-spacing: -0.02em;">
            CricView
        </div>
        <div style="font-size: 0.7rem; color: #5a6178; text-transform: uppercase;
                    letter-spacing: 0.15em; margin-top: 2px;">
            Cricket Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="padding: 0 8px;">
        <div style="font-size: 0.7rem; color: #5a6178; text-transform: uppercase;
                    letter-spacing: 0.12em; margin-bottom: 8px; font-weight: 600;">
            Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Main Content (Landing) ───────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 80px 20px;">
    <div style="font-size: 5rem; margin-bottom: 16px;">🏏</div>
    <h1 style="font-size: 3rem !important; margin-bottom: 8px;
               background: linear-gradient(135deg, #e0e6ed 0%, #00d4aa 50%, #3b82f6 100%) !important;
               -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
               background-clip: text !important;">
        CricView
    </h1>
    <p style="font-size: 1.2rem; color: #8b92a5; max-width: 600px; margin: 0 auto 30px auto;">
        T20 International Cricket Intelligence Platform<br/>
        <span style="color: #5a6178;">2005 — 2024 · ~2,800 Matches · 500K+ Deliveries</span>
    </p>
    <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; margin-top: 40px;">
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; color: #00d4aa; font-weight: 800;">6</div>
            <div style="font-size: 0.75rem; color: #5a6178; text-transform: uppercase;">Dashboard Pages</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; color: #3b82f6; font-weight: 800;">1,400+</div>
            <div style="font-size: 0.75rem; color: #5a6178; text-transform: uppercase;">Players Tracked</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; color: #f59e0b; font-weight: 800;">28+</div>
            <div style="font-size: 0.75rem; color: #5a6178; text-transform: uppercase;">Teams</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; color: #8b5cf6; font-weight: 800;">19</div>
            <div style="font-size: 0.75rem; color: #5a6178; text-transform: uppercase;">Years of Data</div>
        </div>
    </div>
    <p style="color: #3d4560; font-size: 0.85rem; margin-top: 50px;">
        👈 Select a page from the sidebar to begin exploring
    </p>
</div>
""", unsafe_allow_html=True)
