"""
📈 Overall Analysis — Historical Trends & Intelligence
"""

import pages._path_setup  # noqa: F401 — must be first
import streamlit as st
import pandas as pd
import numpy as np
from components.styles import inject_global_css
from components.kpi_card import section_header, kpi_row, insight_card, kpi_card
from src.data_loader import (
    load_matches, load_deliveries, load_yearly_stats,
    load_player_batting, load_player_bowling,
)
from src.batting_analysis import top_run_scorers, top_partnerships
from src.bowling_analysis import top_wicket_takers, best_economy_bowlers, death_bowling_specialists
from src.team_analysis import toss_analysis
from src import charts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Overall Analysis", page_icon="📈", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
matches_df = load_matches()
deliveries_df = load_deliveries()
yearly_df = load_yearly_stats()
batting_df = load_player_batting()
bowling_df = load_player_bowling()

# ── Header ───────────────────────────────────────────────────
st.markdown("# 📈 Overall Analysis")
st.caption("Historical trends, records, and deep intelligence across all T20 Internationals")

# ── Trend Analysis Tabs ──────────────────────────────────────
tab_trends, tab_batting, tab_bowling, tab_records = st.tabs([
    "📈 Trends", "🏏 Batting Records", "🎯 Bowling Records", "🏆 All-Time Records"
])

# ━━━━━━━━━━━━━━━━ TRENDS TAB ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_trends:
    section_header("📈", "Scoring Evolution")

    # Avg runs per match over time
    yearly_df["avg_score_per_innings"] = (yearly_df["total_runs"] / (yearly_df["matches"] * 2)).round(1)

    col1, col2 = st.columns(2)

    with col1:
        fig = charts.line_chart(
            yearly_df, x="year", y="avg_score_per_innings",
            title="📈 Average Score Per Innings",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = charts.line_chart(
            yearly_df, x="year", y="avg_run_rate",
            title="⚡ Average Run Rate Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Boundary trends
    section_header("💥", "Boundary Evolution")

    yearly_df["sixes_per_match"] = (yearly_df["total_sixes"] / yearly_df["matches"]).round(2)
    yearly_df["fours_per_match"] = (yearly_df["total_fours"] / yearly_df["matches"]).round(2)

    col1, col2 = st.columns(2)
    with col1:
        fig = charts.grouped_bar_chart(
            yearly_df, x="year",
            y_cols=["fours_per_match", "sixes_per_match"],
            names=["Fours/Match", "Sixes/Match"],
            title="Boundaries Per Match",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        yearly_df["boundary_ratio"] = (yearly_df["total_sixes"] / yearly_df["total_fours"].replace(0, 1)).round(3)
        fig = charts.area_chart(
            yearly_df, x="year", y="boundary_ratio",
            title="Six-to-Four Ratio (Higher = More Aggressive)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Toss analysis
    section_header("🪙", "Toss Intelligence")
    toss_data = toss_analysis(matches_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Toss Winner = Match Winner", f"{toss_data['toss_win_match_win_pct']}%", "🪙")
    with col2:
        kpi_card("Bat First Win %", f"{toss_data['bat_first_win_pct']}%", "🏏")
    with col3:
        kpi_card("Field First Win %", f"{toss_data['field_first_win_pct']}%", "🎯")

    # Toss preferences over years
    toss_yearly = matches_df.groupby("year").apply(
        lambda g: pd.Series({
            "bat_pct": round(len(g[g["toss_decision"] == "bat"]) / max(len(g), 1) * 100, 1),
            "field_pct": round(len(g[g["toss_decision"] == "field"]) / max(len(g), 1) * 100, 1),
        })
    ).reset_index()

    fig = charts.grouped_bar_chart(
        toss_yearly, x="year",
        y_cols=["bat_pct", "field_pct"],
        names=["Chose to Bat %", "Chose to Field %"],
        title="🪙 Toss Decision Preference Over Years",
    )
    st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━ BATTING RECORDS ━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_batting:
    section_header("🏏", "Top Run Scorers — All Time")

    top_batters = top_run_scorers(deliveries_df, n=20)
    if not top_batters.empty:
        display_bat = top_batters[["player", "runs", "balls", "strike_rate", "batting_avg", "fours", "sixes"]].copy()
        display_bat.columns = ["Player", "Runs", "Balls", "SR", "Avg", "4s", "6s"]

        fig = charts.horizontal_bar_chart(
            top_batters.head(15).sort_values("runs"),
            x="runs", y="player",
            title="🏏 Top 15 Run Scorers",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(display_bat, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Highest strike rates (min qualification)
    section_header("⚡", "Highest Strike Rates (Min 200 balls)")
    sr_leaders = batting_df[batting_df["balls_faced"] >= 200].nlargest(15, "strike_rate")

    if not sr_leaders.empty:
        fig = charts.horizontal_bar_chart(
            sr_leaders.sort_values("strike_rate"),
            x="strike_rate", y="player",
            title="⚡ Highest Strike Rates",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top partnerships
    section_header("🤝", "Top Batting Partnerships")
    partnerships = top_partnerships(deliveries_df, n=15)
    if not partnerships.empty:
        st.dataframe(partnerships, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━ BOWLING RECORDS ━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_bowling:
    section_header("🎯", "Top Wicket Takers — All Time")

    top_bowlers = top_wicket_takers(deliveries_df, n=20)
    if not top_bowlers.empty:
        fig = charts.horizontal_bar_chart(
            top_bowlers.head(15).sort_values("wickets"),
            x="wickets", y="player",
            title="🎯 Top 15 Wicket Takers",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

        display_bowl = top_bowlers[["player", "matches", "wickets", "economy", "bowling_avg", "bowling_sr", "dot_pct"]].copy()
        display_bowl.columns = ["Player", "Matches", "Wickets", "Econ", "Avg", "SR", "Dot%"]
        st.dataframe(display_bowl, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Best economy (min qualification)
    section_header("💰", "Best Economy Rates (Min 10 overs)")
    eco_leaders = best_economy_bowlers(deliveries_df, n=15, min_overs=10)
    if not eco_leaders.empty:
        fig = charts.horizontal_bar_chart(
            eco_leaders.sort_values("economy", ascending=False),
            x="economy", y="player",
            title="💰 Best Economy Rates",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Death bowling specialists
    section_header("💀", "Death Overs Specialists (Overs 16-20)")
    death_bowlers = death_bowling_specialists(deliveries_df, n=15, min_balls=50)
    if not death_bowlers.empty:
        st.dataframe(
            death_bowlers[["player", "balls", "runs", "wickets", "economy", "dot_pct"]],
            use_container_width=True,
            hide_index=True,
        )

# ━━━━━━━━━━━━━━━━ ALL-TIME RECORDS ━━━━━━━━━━━━━━━━━━━━━━━━
with tab_records:
    section_header("🏆", "All-Time T20I Records")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏏 Batting Records")

        # Most Player of Match
        pom_counts = matches_df["player_of_match"].value_counts().head(10).reset_index()
        pom_counts.columns = ["Player", "Awards"]
        fig = charts.horizontal_bar_chart(
            pom_counts.sort_values("Awards"),
            x="Awards", y="Player",
            title="⭐ Most Player of Match Awards",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🏟️ Match Distribution")

        # Wins by type
        win_types = matches_df[matches_df["winner"] != "No Result"]["win_type"].value_counts().reset_index()
        win_types.columns = ["Type", "Count"]
        fig = charts.pie_chart(
            win_types, values="Count", names="Type",
            title="Win Distribution by Type",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Biggest margins
    st.markdown("---")
    section_header("📊", "Biggest Victory Margins")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### By Runs")
        biggest_run_wins = matches_df[matches_df["win_type"] == "runs"].nlargest(10, "win_margin")
        display = biggest_run_wins[["match_date", "team1", "team2", "winner", "win_margin", "venue"]].copy()
        display.columns = ["Date", "Team 1", "Team 2", "Winner", "Margin", "Venue"]
        st.dataframe(display, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("##### By Wickets")
        biggest_wkt_wins = matches_df[matches_df["win_type"] == "wickets"].nlargest(10, "win_margin")
        display = biggest_wkt_wins[["match_date", "team1", "team2", "winner", "win_margin", "venue"]].copy()
        display.columns = ["Date", "Team 1", "Team 2", "Winner", "Margin", "Venue"]
        st.dataframe(display, use_container_width=True, hide_index=True)
