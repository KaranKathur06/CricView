"""
🏟️ Team Analytics — Team-specific deep analysis
"""

import pages._path_setup  # noqa: F401 — must be first
import streamlit as st
import pandas as pd
from components.styles import inject_global_css
from components.kpi_card import kpi_card, kpi_row, section_header, insight_card
from components.filters import filter_panel
from src.data_loader import (
    load_matches, load_deliveries, load_team_stats, get_all_teams,
)
from src.team_analysis import (
    team_overview, team_top_performers, team_phase_performance,
    team_yearly_performance, toss_analysis,
)
from src import charts
from config.constants import TEAM_FLAGS

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Team Analytics", page_icon="🏟️", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
matches_df = load_matches()
deliveries_df = load_deliveries()
team_stats_df = load_team_stats()

# ── Header ───────────────────────────────────────────────────
st.markdown("# 🏟️ Team Analytics")
st.caption("Comprehensive team performance analysis with opponent and phase breakdowns")

# ── Team Selection ───────────────────────────────────────────
all_teams = get_all_teams(matches_df)

col_team, col_opp = st.columns(2)
with col_team:
    selected_team = st.selectbox(
        "🏏 Select Team",
        options=all_teams,
        index=all_teams.index("India") if "India" in all_teams else 0,
        key="team_select",
    )
with col_opp:
    # Get opponents
    team_matches = matches_df[
        (matches_df["team1"] == selected_team) | (matches_df["team2"] == selected_team)
    ]
    opponents = set()
    for _, row in team_matches.iterrows():
        opp = row["team2"] if row["team1"] == selected_team else row["team1"]
        opponents.add(opp)
    opponents = sorted(opponents)

    selected_opponent = st.selectbox(
        "⚔️ Filter by Opponent",
        options=["All"] + opponents,
        key="opponent_select",
    )

st.markdown("---")

# ── Team Flag + Name ─────────────────────────────────────────
flag = TEAM_FLAGS.get(selected_team, "🏏")
opp_str = f" vs {selected_opponent}" if selected_opponent != "All" else ""
st.markdown(f"## {flag} {selected_team}{opp_str}")

# ── Overview KPIs ────────────────────────────────────────────
overview = team_overview(matches_df, deliveries_df, selected_team, selected_opponent)

kpi_row([
    {"label": "Matches", "value": overview["total_matches"], "icon": "🏏"},
    {"label": "Wins", "value": overview["wins"], "icon": "🟢"},
    {"label": "Losses", "value": overview["losses"], "icon": "🔴"},
    {"label": "Win Rate", "value": f"{overview['win_pct']}%", "icon": "🏆"},
    {"label": "Avg Score", "value": overview["avg_score"], "icon": "📊"},
    {"label": "Highest Score", "value": overview["highest_score"], "icon": "🔥"},
], columns=6)

st.markdown("<br/>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    kpi_card("Total Fours", overview["total_fours"], "4️⃣")
with col2:
    kpi_card("Total Sixes", overview["total_sixes"], "6️⃣")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────
tab_perf, tab_players, tab_phases, tab_toss = st.tabs([
    "📈 Performance", "👤 Top Performers", "📊 Phase Analysis", "🪙 Toss Impact"
])

# ━━━━━━━━━━━━━━━━ PERFORMANCE TAB ━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_perf:
    section_header("📈", "Year-by-Year Performance")

    yearly = team_yearly_performance(matches_df, selected_team)
    if not yearly.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = charts.bar_chart(
                yearly, x="year", y="wins",
                title=f"Wins Per Year",
                text="wins",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = charts.line_chart(
                yearly, x="year", y="win_pct",
                title="Win Rate % Trend",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Win/Loss table
        st.dataframe(
            yearly[["year", "matches", "wins", "losses", "win_pct"]],
            use_container_width=True,
            hide_index=True,
        )

        # Insights
        if len(yearly) >= 2:
            best_year = yearly.loc[yearly["win_pct"].idxmax()]
            worst_year = yearly.loc[yearly[yearly["matches"] >= 3]["win_pct"].idxmin()] if len(yearly[yearly["matches"] >= 3]) > 0 else None

            insight_card("🏆", f"**Best Year:** {int(best_year['year'])} — {best_year['win_pct']}% win rate ({int(best_year['wins'])}/{int(best_year['matches'])})")
            if worst_year is not None:
                insight_card("📉", f"**Worst Year (min 3 matches):** {int(worst_year['year'])} — {worst_year['win_pct']}% win rate")

# ━━━━━━━━━━━━━━━━ TOP PERFORMERS TAB ━━━━━━━━━━━━━━━━━━━━━━
with tab_players:
    top_batters, top_bowlers = team_top_performers(deliveries_df, selected_team, selected_opponent)

    col1, col2 = st.columns(2)

    with col1:
        section_header("🏏", "Top Batters")
        if not top_batters.empty:
            fig = charts.horizontal_bar_chart(
                top_batters.sort_values("runs"),
                x="runs", y="player",
                title="Top Run Scorers",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)

            display = top_batters[["player", "runs", "balls", "sr", "fours", "sixes"]].copy()
            display.columns = ["Player", "Runs", "Balls", "SR", "4s", "6s"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    with col2:
        section_header("🎯", "Top Bowlers")
        if not top_bowlers.empty:
            fig = charts.horizontal_bar_chart(
                top_bowlers.sort_values("wickets"),
                x="wickets", y="player",
                title="Top Wicket Takers",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)

            display = top_bowlers[["player", "wickets", "runs_conceded", "economy"]].copy()
            display.columns = ["Player", "Wickets", "Runs", "Economy"]
            st.dataframe(display, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━ PHASE ANALYSIS TAB ━━━━━━━━━━━━━━━━━━━━━━
with tab_phases:
    section_header("📊", "Phase-wise Team Performance")

    phase_df = team_phase_performance(deliveries_df, selected_team, selected_opponent)

    if not phase_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = charts.bar_chart(
                phase_df, x="phase", y="run_rate",
                title="Run Rate by Phase",
                text="run_rate",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = charts.bar_chart(
                phase_df, x="phase", y="wickets_lost",
                title="Wickets Lost by Phase",
                text="wickets_lost",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            phase_df,
            use_container_width=True,
            hide_index=True,
        )

        # Phase insights
        best_phase = phase_df.loc[phase_df["run_rate"].idxmax()]
        insight_card("⚡", f"**Strongest Phase:** {best_phase['phase']} with a run rate of {best_phase['run_rate']}")
    else:
        st.info("Not enough data for phase analysis.")

# ━━━━━━━━━━━━━━━━ TOSS IMPACT TAB ━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_toss:
    section_header("🪙", "Toss Analysis")

    toss_data = toss_analysis(matches_df, selected_team)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Toss Win → Match Win", f"{toss_data['toss_win_match_win_pct']}%", "🪙")
    with col2:
        kpi_card("Bat First Win %", f"{toss_data['bat_first_win_pct']}%", "🏏")
    with col3:
        kpi_card("Field First Win %", f"{toss_data['field_first_win_pct']}%", "🎯")

    # Toss preference
    toss_pref = pd.DataFrame({
        "Decision": ["Bat First", "Field First"],
        "Times": [toss_data["bat_first_chosen"], toss_data["field_first_chosen"]],
    })

    fig = charts.pie_chart(
        toss_pref, values="Times", names="Decision",
        title=f"{selected_team} — Toss Decision Preference",
    )
    st.plotly_chart(fig, use_container_width=True)
