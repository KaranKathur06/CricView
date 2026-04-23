"""
CricView KPI Card Component
============================
Production-grade KPI cards with icons, deltas, and trend indicators.
"""

import streamlit as st


def kpi_card(label: str, value, icon: str = "📊", delta=None, delta_suffix: str = "%", prefix: str = ""):
    """
    Render a premium KPI card with optional trend delta.

    Args:
        label: KPI title (e.g., "Total Matches")
        value: KPI value (auto-formatted with commas)
        icon: Emoji icon
        delta: Optional change value (positive = green, negative = red)
        delta_suffix: Suffix for delta value
        prefix: Prefix for value (e.g., "$" or "₹")
    """
    # Format value
    if isinstance(value, (int, float)):
        if value >= 1_000_000:
            display_val = f"{prefix}{value / 1_000_000:.1f}M"
        elif value >= 10_000:
            display_val = f"{prefix}{value:,.0f}"
        elif isinstance(value, float) and value != int(value):
            display_val = f"{prefix}{value:,.2f}"
        else:
            display_val = f"{prefix}{int(value):,}"
    else:
        display_val = str(value)

    # Delta HTML
    delta_html = ""
    if delta is not None:
        color = "#00d4aa" if delta >= 0 else "#ef4444"
        arrow = "▲" if delta >= 0 else "▼"
        css_class = "positive" if delta >= 0 else "negative"
        delta_html = f'<div class="kpi-delta {css_class}">{arrow} {abs(delta):.1f}{delta_suffix}</div>'

    st.markdown(f"""
    <div class="cricview-kpi">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{display_val}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def kpi_row(kpis: list, columns: int = None):
    """
    Render a row of KPI cards.

    Args:
        kpis: List of dicts with keys: label, value, icon, delta (optional)
        columns: Number of columns (auto-detected if None)
    """
    n = columns or len(kpis)
    cols = st.columns(n)

    for i, kp in enumerate(kpis):
        with cols[i % n]:
            kpi_card(
                label=kp.get("label", ""),
                value=kp.get("value", 0),
                icon=kp.get("icon", "📊"),
                delta=kp.get("delta"),
                delta_suffix=kp.get("delta_suffix", "%"),
                prefix=kp.get("prefix", ""),
            )


def section_header(icon: str, title: str):
    """Render a styled section header."""
    st.markdown(f"""
    <div class="section-header">
        <span class="icon">{icon}</span>
        <span class="title">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def insight_card(icon: str, text: str):
    """Render an insight/tip card."""
    st.markdown(f"""
    <div class="insight-card">
        <span class="insight-icon">{icon}</span>
        <span class="insight-text">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def stat_table(stats: dict):
    """
    Render a key-value stat table.

    Args:
        stats: Dict of {label: value}
    """
    rows = ""
    for label, value in stats.items():
        if isinstance(value, float):
            val_str = f"{value:,.2f}"
        elif isinstance(value, int):
            val_str = f"{value:,}"
        else:
            val_str = str(value)
        rows += f"""
        <div class="stat-row">
            <span class="stat-label">{label}</span>
            <span class="stat-value">{val_str}</span>
        </div>
        """

    st.markdown(f'<div style="padding: 10px 0;">{rows}</div>', unsafe_allow_html=True)
