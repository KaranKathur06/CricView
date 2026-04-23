"""
CricView Design System — Color Palette & Chart Defaults
"""

# ── Primary Palette ──────────────────────────────────────────
COLORS = {
    "primary":      "#00d4aa",   # Emerald accent
    "primary_dark": "#00a88a",
    "secondary":    "#3b82f6",   # Blue
    "warning":      "#f59e0b",   # Amber
    "danger":       "#ef4444",   # Red
    "purple":       "#8b5cf6",
    "cyan":         "#06b6d4",
    "pink":         "#ec4899",
    "lime":         "#84cc16",
    "orange":       "#f97316",
}

# ── Background Palette ───────────────────────────────────────
BG = {
    "page":         "#0a0e1a",
    "card":         "#111827",
    "card_hover":   "#1a2035",
    "surface":      "#1e293b",
    "border":       "#30365a",
    "border_light": "#3d4560",
}

# ── Text Palette ─────────────────────────────────────────────
TEXT = {
    "primary":   "#e0e6ed",
    "secondary": "#8b92a5",
    "muted":     "#5a6178",
    "accent":    "#00d4aa",
}

# ── Chart Color Sequence ─────────────────────────────────────
CHART_COLORS = [
    "#00d4aa", "#3b82f6", "#f59e0b", "#ef4444",
    "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
    "#f97316", "#14b8a6", "#a855f7", "#eab308",
]

# ── Plotly Chart Template Config ─────────────────────────────
CHART_CONFIG = {
    "template": "plotly_dark",
    "color_discrete_sequence": CHART_COLORS,
    "font_family": "'Inter', 'Segoe UI', sans-serif",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=30, r=30, t=50, b=30),
    "height": 420,
}

# ── Gradient Definitions ─────────────────────────────────────
GRADIENTS = {
    "primary":  "linear-gradient(135deg, #00d4aa 0%, #00a88a 100%)",
    "blue":     "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    "purple":   "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)",
    "card":     "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
    "card_alt": "linear-gradient(135deg, #111827 0%, #1e293b 100%)",
    "hero":     "linear-gradient(135deg, #0a0e1a 0%, #1a1a2e 50%, #16213e 100%)",
}
