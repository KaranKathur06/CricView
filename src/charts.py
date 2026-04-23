"""
CricView Chart Factory
======================
Reusable Plotly chart builders with consistent dark theme styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import CHART_COLORS, CHART_CONFIG, COLORS, BG


def _apply_theme(fig, height=None):
    """Apply consistent CricView theme to any figure."""
    fig.update_layout(
        template="plotly_dark",
        font_family=CHART_CONFIG["font_family"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=50, b=30),
        height=height or CHART_CONFIG["height"],
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#8b92a5"),
        ),
        xaxis=dict(gridcolor="rgba(48,54,90,0.3)", zerolinecolor="rgba(48,54,90,0.3)"),
        yaxis=dict(gridcolor="rgba(48,54,90,0.3)", zerolinecolor="rgba(48,54,90,0.3)"),
    )
    return fig


def bar_chart(df, x, y, title, color=None, orientation="v", height=None, text=None, barmode=None):
    """Create a themed bar chart."""
    fig = px.bar(
        df, x=x, y=y, title=title, color=color, text=text,
        orientation=orientation,
        color_discrete_sequence=CHART_COLORS,
        barmode=barmode,
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside" if text else None,
    )
    return _apply_theme(fig, height)


def line_chart(df, x, y, title, color=None, markers=True, height=None):
    """Create a themed line chart."""
    fig = px.line(
        df, x=x, y=y, title=title, color=color,
        markers=markers,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(line_width=2.5)
    return _apply_theme(fig, height)


def area_chart(df, x, y, title, color=None, height=None):
    """Create a themed area chart."""
    fig = px.area(
        df, x=x, y=y, title=title, color=color,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(line_width=2)
    return _apply_theme(fig, height)


def pie_chart(df, values, names, title, hole=0.45, height=None):
    """Create a themed donut chart."""
    fig = px.pie(
        df, values=values, names=names, title=title,
        hole=hole,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=12,
    )
    return _apply_theme(fig, height)


def scatter_chart(df, x, y, title, color=None, size=None, hover_name=None, height=None):
    """Create a themed scatter plot."""
    fig = px.scatter(
        df, x=x, y=y, title=title, color=color, size=size,
        hover_name=hover_name,
        color_discrete_sequence=CHART_COLORS,
    )
    return _apply_theme(fig, height)


def heatmap_chart(df, x, y, z, title, height=None):
    """Create a themed heatmap."""
    fig = px.density_heatmap(
        df, x=x, y=y, z=z, title=title,
        color_continuous_scale=["#0a0e1a", "#00d4aa"],
    )
    return _apply_theme(fig, height)


def radar_chart(categories, values_a, values_b, name_a, name_b, title="", height=450):
    """Create a radar/spider chart for player/team comparison."""
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_a + [values_a[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name_a,
        line_color=COLORS["primary"],
        fillcolor="rgba(0,212,170,0.15)",
        line_width=2.5,
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_b + [values_b[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name_b,
        line_color=COLORS["secondary"],
        fillcolor="rgba(59,130,246,0.15)",
        line_width=2.5,
    ))

    fig.update_layout(
        title=title,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                gridcolor="rgba(48,54,90,0.4)",
                linecolor="rgba(48,54,90,0.2)",
            ),
            angularaxis=dict(
                gridcolor="rgba(48,54,90,0.4)",
                linecolor="rgba(48,54,90,0.2)",
            ),
        ),
    )
    return _apply_theme(fig, height)


def horizontal_bar_chart(df, x, y, title, color_col=None, height=None):
    """Create a horizontal bar chart (great for rankings)."""
    if color_col:
        fig = px.bar(df, x=x, y=y, title=title, orientation="h", color=color_col,
                     color_discrete_sequence=CHART_COLORS)
    else:
        fig = px.bar(df, x=x, y=y, title=title, orientation="h",
                     color_discrete_sequence=[COLORS["primary"]])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _apply_theme(fig, height)


def grouped_bar_chart(df, x, y_cols, names, title, colors=None, height=None):
    """Create a grouped bar chart with multiple series."""
    fig = go.Figure()
    use_colors = colors or CHART_COLORS

    for i, (y_col, name) in enumerate(zip(y_cols, names)):
        fig.add_trace(go.Bar(
            x=df[x], y=df[y_col], name=name,
            marker_color=use_colors[i % len(use_colors)],
            marker_line_width=0,
        ))

    fig.update_layout(title=title, barmode="group")
    return _apply_theme(fig, height)


def worm_chart(deliveries_df, match_id, team1, team2, height=400):
    """Ball-by-ball run progression (worm) chart for a match."""
    match_data = deliveries_df[deliveries_df["match_id"] == match_id]
    fig = go.Figure()

    for team, color in [(team1, COLORS["primary"]), (team2, COLORS["secondary"])]:
        team_data = match_data[match_data["batting_team"] == team].copy()
        if len(team_data) == 0:
            continue
        team_data = team_data.sort_values(["over_num", "ball_num"])
        team_data["cumulative_runs"] = team_data["runs_total"].cumsum()
        team_data["ball_number"] = range(1, len(team_data) + 1)

        fig.add_trace(go.Scatter(
            x=team_data["ball_number"],
            y=team_data["cumulative_runs"],
            mode="lines",
            name=team,
            line=dict(color=color, width=3),
        ))

    fig.update_layout(
        title="Match Worm",
        xaxis_title="Balls",
        yaxis_title="Runs",
    )
    return _apply_theme(fig, height)


def sparkline(values, color=None, height=60, width=150):
    """Create a tiny sparkline chart for inline use."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values,
        mode="lines",
        line=dict(color=color or COLORS["primary"], width=2),
        fill="tozeroy",
        fillcolor=f"rgba(0,212,170,0.1)",
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        width=width,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig
