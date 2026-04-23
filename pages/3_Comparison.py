"""
⚔️ Comparison — Player vs Player & Team vs Team
"""

import pages._path_setup  # noqa: F401 — must be first
import streamlit as st
import pandas as pd
import numpy as np
from components.styles import inject_global_css
from components.kpi_card import section_header, kpi_row
from src.data_loader import (
    load_matches, load_deliveries, load_player_batting,
    load_team_stats, get_all_players, get_all_teams,
)
from src.batting_analysis import player_career_summary, player_phase_splits
from src.bowling_analysis import bowler_career_summary
from src.team_analysis import team_overview, head_to_head, team_phase_performance
from src import charts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Comparison", page_icon="⚔️", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
matches_df = load_matches()
deliveries_df = load_deliveries()

# ── Header ───────────────────────────────────────────────────
st.markdown("# ⚔️ Comparison Engine")
st.caption("Head-to-head analysis for players and teams")

# ── Comparison Mode ──────────────────────────────────────────
mode = st.radio(
    "Comparison Type",
    ["🏏 Player vs Player", "🏟️ Team vs Team"],
    horizontal=True,
    key="comparison_mode",
)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PLAYER vs PLAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if mode == "🏏 Player vs Player":
    all_players = get_all_players(deliveries_df)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        player_a = st.selectbox("Player A", all_players,
                                index=all_players.index("V Kohli") if "V Kohli" in all_players else 0,
                                key="comp_player_a")
    with col_sel2:
        player_b = st.selectbox("Player B", all_players,
                                index=all_players.index("RG Sharma") if "RG Sharma" in all_players else 1,
                                key="comp_player_b")

    if player_a and player_b and player_a != player_b:
        career_a = player_career_summary(deliveries_df, matches_df, player_a)
        career_b = player_career_summary(deliveries_df, matches_df, player_b)

        # ── Side-by-side KPIs ────────────────────────────────
        section_header("📊", "Career Comparison")

        stats_compare = {
            "Matches": ("bat_matches", "bat_matches"),
            "Runs": ("total_runs", "total_runs"),
            "Strike Rate": ("strike_rate", "strike_rate"),
            "Average": ("batting_avg", "batting_avg"),
            "Fours": ("fours", "fours"),
            "Sixes": ("sixes", "sixes"),
            "Highest Score": ("highest_score", "highest_score"),
            "50s": ("fifties", "fifties"),
            "100s": ("hundreds", "hundreds"),
            "Boundary %": ("boundary_pct", "boundary_pct"),
            "Wickets": ("wickets", "wickets"),
            "Economy": ("economy", "economy"),
        }

        compare_data = []
        for stat_name, (key_a, key_b) in stats_compare.items():
            val_a = career_a.get(key_a, 0)
            val_b = career_b.get(key_b, 0)
            compare_data.append({
                "Stat": stat_name,
                player_a: val_a if val_a is not None else 0,
                player_b: val_b if val_b is not None else 0,
            })

        compare_df = pd.DataFrame(compare_data)

        col1, col2, col3 = st.columns([2, 3, 2])

        with col1:
            st.markdown(f"### {player_a}")
            for _, row in compare_df.iterrows():
                val = row[player_a]
                is_better = row[player_a] >= row[player_b]
                if row["Stat"] == "Economy":
                    is_better = row[player_a] <= row[player_b] if row[player_a] > 0 else False
                color = "#00d4aa" if is_better else "#8b92a5"
                st.markdown(f'<div style="padding:6px 0;"><span style="color:{color};font-weight:700;font-size:1.1rem;">{val}</span></div>',
                            unsafe_allow_html=True)

        with col2:
            for _, row in compare_df.iterrows():
                st.markdown(f'<div style="padding:6px 0;text-align:center;color:#5a6178;font-size:0.85rem;">{row["Stat"]}</div>',
                            unsafe_allow_html=True)

        with col3:
            st.markdown(f"### {player_b}")
            for _, row in compare_df.iterrows():
                val = row[player_b]
                is_better = row[player_b] >= row[player_a]
                if row["Stat"] == "Economy":
                    is_better = row[player_b] <= row[player_a] if row[player_b] > 0 else False
                color = "#3b82f6" if is_better else "#8b92a5"
                st.markdown(f'<div style="padding:6px 0;"><span style="color:{color};font-weight:700;font-size:1.1rem;">{val}</span></div>',
                            unsafe_allow_html=True)

        st.markdown("---")

        # ── Radar Chart ──────────────────────────────────────
        section_header("🕸️", "Radar Comparison")

        # Normalize values for radar
        radar_stats = ["Strike Rate", "Average", "Boundary %", "Runs", "Sixes"]
        radar_a = []
        radar_b = []

        for stat in radar_stats:
            row = compare_df[compare_df["Stat"] == stat].iloc[0]
            max_val = max(row[player_a], row[player_b], 1)
            radar_a.append(round(row[player_a] / max_val * 100, 1))
            radar_b.append(round(row[player_b] / max_val * 100, 1))

        fig = charts.radar_chart(
            radar_stats, radar_a, radar_b,
            player_a, player_b,
            title="Batting Comparison Radar",
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Phase Comparison ─────────────────────────────────
        section_header("📊", "Phase-wise Comparison")

        col1, col2 = st.columns(2)
        phase_a = player_phase_splits(deliveries_df, player_a)
        phase_b = player_phase_splits(deliveries_df, player_b)

        with col1:
            if not phase_a.empty:
                fig = charts.bar_chart(
                    phase_a, x="phase", y="sr",
                    title=f"{player_a} — Strike Rate by Phase",
                    text="sr",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if not phase_b.empty:
                fig = charts.bar_chart(
                    phase_b, x="phase", y="sr",
                    title=f"{player_b} — Strike Rate by Phase",
                    text="sr",
                )
                st.plotly_chart(fig, use_container_width=True)

    elif player_a == player_b:
        st.warning("Please select two different players to compare.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEAM vs TEAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
else:
    all_teams = get_all_teams(matches_df)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        team_a = st.selectbox("Team A", all_teams,
                              index=all_teams.index("India") if "India" in all_teams else 0,
                              key="comp_team_a")
    with col_sel2:
        team_b = st.selectbox("Team B", all_teams,
                              index=all_teams.index("Australia") if "Australia" in all_teams else 1,
                              key="comp_team_b")

    if team_a and team_b and team_a != team_b:
        # Head-to-head record
        h2h = head_to_head(matches_df, team_a, team_b)

        section_header("🏆", "Head-to-Head Record")

        kpi_row([
            {"label": "Total Matches", "value": h2h["total"], "icon": "🏏"},
            {"label": f"{team_a} Wins", "value": h2h["team_a_wins"], "icon": "🟢"},
            {"label": f"{team_b} Wins", "value": h2h["team_b_wins"], "icon": "🔵"},
            {"label": "No Result", "value": h2h["no_result"], "icon": "⬜"},
        ], columns=4)

        st.markdown("---")

        # Overall stats comparison
        overview_a = team_overview(matches_df, deliveries_df, team_a)
        overview_b = team_overview(matches_df, deliveries_df, team_b)

        section_header("📊", "Overall Performance (All Matches)")

        compare_items = [
            ("Total Matches", "total_matches"),
            ("Wins", "wins"),
            ("Win %", "win_pct"),
            ("Avg Score", "avg_score"),
            ("Highest Score", "highest_score"),
            ("Total Fours", "total_fours"),
            ("Total Sixes", "total_sixes"),
        ]

        team_compare_data = []
        for label, key in compare_items:
            team_compare_data.append({
                "Stat": label,
                team_a: overview_a.get(key, 0),
                team_b: overview_b.get(key, 0),
            })

        st.dataframe(
            pd.DataFrame(team_compare_data),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # Phase comparison
        section_header("📊", "Phase Performance Comparison")

        col1, col2 = st.columns(2)
        phase_a = team_phase_performance(deliveries_df, team_a)
        phase_b = team_phase_performance(deliveries_df, team_b)

        with col1:
            if not phase_a.empty:
                fig = charts.bar_chart(
                    phase_a, x="phase", y="run_rate",
                    title=f"{team_a} — Run Rate by Phase",
                    text="run_rate",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if not phase_b.empty:
                fig = charts.bar_chart(
                    phase_b, x="phase", y="run_rate",
                    title=f"{team_b} — Run Rate by Phase",
                    text="run_rate",
                )
                st.plotly_chart(fig, use_container_width=True)

    elif team_a == team_b:
        st.warning("Please select two different teams to compare.")
