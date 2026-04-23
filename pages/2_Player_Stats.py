"""
🏏 Player Stats — Individual Player Deep-Dive
"""

import pages._path_setup  # noqa: F401 — must be first
import streamlit as st
import pandas as pd
from components.styles import inject_global_css
from components.kpi_card import kpi_card, kpi_row, section_header, stat_table
from src.data_loader import (
    load_matches, load_deliveries, load_player_batting,
    load_player_bowling, get_all_players,
)
from src.batting_analysis import (
    player_career_summary, player_phase_splits,
    player_vs_teams, player_innings_list, player_yearly_runs,
)
from src.bowling_analysis import bowler_career_summary, bowler_phase_splits, bowler_vs_teams
from src import charts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Player Stats", page_icon="🏏", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
matches_df = load_matches()
deliveries_df = load_deliveries()
batting_df = load_player_batting()

# ── Header ───────────────────────────────────────────────────
st.markdown("# 🏏 Player Stats")
st.caption("Deep-dive into any player's T20I career")

# ── Player Search ────────────────────────────────────────────
all_players = get_all_players(deliveries_df)

selected_player = st.selectbox(
    "🔍 Search Player",
    options=all_players,
    index=all_players.index("V Kohli") if "V Kohli" in all_players else 0,
    key="player_search",
)

if selected_player:
    st.markdown("---")

    # ── Career Summary KPIs ──────────────────────────────────
    career = player_career_summary(deliveries_df, matches_df, selected_player)

    st.markdown(f"## {selected_player}")

    # ── Batting & Bowling Tabs ───────────────────────────────
    tab_bat, tab_bowl, tab_matchup, tab_innings = st.tabs([
        "🏏 Batting", "🎯 Bowling", "⚔️ Matchups", "📋 Innings Log"
    ])

    # ━━━━━━━━━━━━━━━━━━ BATTING TAB ━━━━━━━━━━━━━━━━━━━━━━━━
    with tab_bat:
        section_header("🏏", "Batting Career Summary")

        kpi_row([
            {"label": "Matches", "value": career["bat_matches"], "icon": "🏏"},
            {"label": "Runs", "value": career["total_runs"], "icon": "🏃"},
            {"label": "Highest Score", "value": career["highest_score"], "icon": "🔥"},
            {"label": "Strike Rate", "value": career["strike_rate"], "icon": "⚡"},
            {"label": "Average", "value": career["batting_avg"], "icon": "📊"},
            {"label": "50s / 100s", "value": f"{career['fifties']} / {career['hundreds']}", "icon": "⭐"},
        ], columns=6)

        st.markdown("<br/>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("Fours", career["fours"], "4️⃣")
        with col2:
            kpi_card("Sixes", career["sixes"], "6️⃣")
        with col3:
            kpi_card("Boundary %", career["boundary_pct"], "💥")

        st.markdown("---")

        # ── Phase-wise Batting ───────────────────────────────
        section_header("📊", "Phase-wise Batting Split")
        phase_df = player_phase_splits(deliveries_df, selected_player)

        if not phase_df.empty:
            col_phase_chart, col_phase_table = st.columns([3, 2])

            with col_phase_chart:
                fig = charts.bar_chart(
                    phase_df, x="phase", y="sr",
                    title=f"Strike Rate by Phase",
                    text="sr",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_phase_table:
                st.dataframe(
                    phase_df[["phase", "balls", "runs", "fours", "sixes", "sr", "dot_pct"]],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("Not enough data for phase analysis.")

        # ── Yearly Performance ───────────────────────────────
        section_header("📅", "Year-by-Year Performance")
        yearly = player_yearly_runs(deliveries_df, matches_df, selected_player)

        if not yearly.empty:
            fig = charts.bar_chart(
                yearly, x="year", y="runs",
                title=f"Runs Scored Per Year",
                text="runs",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ━━━━━━━━━━━━━━━━━━ BOWLING TAB ━━━━━━━━━━━━━━━━━━━━━━━━
    with tab_bowl:
        bowl_career = bowler_career_summary(deliveries_df, selected_player)

        if bowl_career and bowl_career["balls_bowled"] > 0:
            section_header("🎯", "Bowling Career Summary")

            kpi_row([
                {"label": "Matches (Bowled)", "value": bowl_career["matches"], "icon": "🏏"},
                {"label": "Wickets", "value": bowl_career["wickets"], "icon": "🎯"},
                {"label": "Economy", "value": bowl_career["economy"], "icon": "💰"},
                {"label": "Bowling Avg", "value": bowl_career["bowling_avg"], "icon": "📊"},
                {"label": "Best Figures", "value": bowl_career["best_figures"], "icon": "🔥"},
                {"label": "Dot Ball %", "value": bowl_career["dot_pct"], "icon": "⭕"},
            ], columns=6)

            st.markdown("---")

            # Bowling phase splits
            section_header("📊", "Bowling Phase Split")
            bowl_phase = bowler_phase_splits(deliveries_df, selected_player)

            if not bowl_phase.empty:
                col1, col2 = st.columns([3, 2])
                with col1:
                    fig = charts.bar_chart(
                        bowl_phase, x="phase", y="economy",
                        title="Economy Rate by Phase",
                        text="economy",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.dataframe(
                        bowl_phase[["phase", "overs", "runs", "wickets", "economy", "dot_pct"]],
                        use_container_width=True,
                        hide_index=True,
                    )
        else:
            st.info(f"📭 {selected_player} has no significant bowling data.")

    # ━━━━━━━━━━━━━━━━━━ MATCHUPS TAB ━━━━━━━━━━━━━━━━━━━━━━━
    with tab_matchup:
        section_header("⚔️", "Performance vs Teams")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🏏 Batting vs Opponents")
            bat_vs = player_vs_teams(deliveries_df, selected_player)
            if not bat_vs.empty:
                fig = charts.horizontal_bar_chart(
                    bat_vs.head(10), x="runs", y="opponent",
                    title="Runs Scored Against Each Team",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No batting matchup data available.")

        with col2:
            st.markdown("#### 🎯 Bowling vs Opponents")
            bowl_vs = bowler_vs_teams(deliveries_df, selected_player)
            if not bowl_vs.empty:
                fig = charts.horizontal_bar_chart(
                    bowl_vs.head(10), x="wickets", y="opponent",
                    title="Wickets Taken Against Each Team",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No bowling matchup data available.")

    # ━━━━━━━━━━━━━━━━━━ INNINGS LOG ━━━━━━━━━━━━━━━━━━━━━━━━
    with tab_innings:
        section_header("📋", f"Recent Innings — {selected_player}")

        innings = player_innings_list(deliveries_df, matches_df, selected_player, n=30)
        if not innings.empty:
            display_df = innings[["match_date", "runs", "balls", "fours", "sixes", "sr", "venue"]].copy()
            display_df["match_date"] = display_df["match_date"].dt.strftime("%Y-%m-%d")
            display_df.columns = ["Date", "Runs", "Balls", "4s", "6s", "SR", "Venue"]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=600,
            )

            # Scores trend
            fig = charts.bar_chart(
                innings.head(20).sort_values("match_date"),
                x="match_date", y="runs",
                title="Last 20 Innings Performance",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No innings data available.")
