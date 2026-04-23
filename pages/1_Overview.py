"""
📊 Overview — Global KPIs, Trends, and Insights
"""

import streamlit as st
import pandas as pd
from components.styles import inject_global_css
from components.kpi_card import kpi_card, kpi_row, section_header, insight_card
from src.data_loader import (
    load_matches, load_deliveries, load_team_stats,
    load_yearly_stats, load_venue_stats, get_all_teams,
)
from src.team_analysis import toss_analysis
from src import charts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Overview", page_icon="📊", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
with st.spinner("Loading cricket intelligence..."):
    matches_df = load_matches()
    deliveries_df = load_deliveries()
    team_stats_df = load_team_stats()
    yearly_df = load_yearly_stats()
    venue_stats_df = load_venue_stats()

# ── Header ───────────────────────────────────────────────────
st.markdown("# 📊 Overview")
st.caption(f"T20 International Cricket · {int(matches_df['year'].min())}–{int(matches_df['year'].max())} · {len(matches_df):,} Matches")

# ── Primary KPIs ─────────────────────────────────────────────
total_matches = len(matches_df)
teams = get_all_teams(matches_df)
total_teams = len(teams)
total_players = len(set(deliveries_df["batter"].unique()) | set(deliveries_df["bowler"].unique()))
total_runs = int(deliveries_df["runs_total"].sum())
total_fours = int(deliveries_df["is_four"].sum())
total_sixes = int(deliveries_df["is_six"].sum())
total_wickets = int(deliveries_df["is_wicket"].sum())
total_balls = len(deliveries_df)

# Calculate year-over-year deltas
if len(yearly_df) >= 2:
    latest = yearly_df.iloc[-1]
    prev = yearly_df.iloc[-2]
    match_delta = ((latest["matches"] - prev["matches"]) / max(prev["matches"], 1) * 100)
    six_delta = ((latest["total_sixes"] - prev["total_sixes"]) / max(prev["total_sixes"], 1) * 100)
    rr_delta = latest["avg_run_rate"] - prev["avg_run_rate"]
else:
    match_delta = six_delta = rr_delta = None

kpi_row([
    {"label": "Total Matches", "value": total_matches, "icon": "🏏", "delta": match_delta},
    {"label": "Teams", "value": total_teams, "icon": "🏟️"},
    {"label": "Players", "value": total_players, "icon": "👤"},
    {"label": "Total Runs", "value": total_runs, "icon": "🏃"},
    {"label": "Fours Hit", "value": total_fours, "icon": "4️⃣"},
    {"label": "Sixes Hit", "value": total_sixes, "icon": "6️⃣", "delta": six_delta},
], columns=6)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 2: Secondary KPIs ───────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total Wickets", total_wickets, "🎯")
with col2:
    kpi_card("Total Deliveries", total_balls, "⚾")
with col3:
    avg_score = round(total_runs / max(total_matches * 2, 1), 1)  # per innings
    kpi_card("Avg Score/Innings", avg_score, "📊")
with col4:
    avg_rr = round(total_runs / max(total_balls / 6, 1), 2)
    kpi_card("Overall Run Rate", avg_rr, "⚡", delta=rr_delta, delta_suffix="")

st.markdown("---")

# ── Charts Row 1: Scoring Trends + Team Win Rates ───────────
section_header("📈", "Scoring Trends & Team Performance")

col_chart1, col_chart2 = st.columns([3, 2])

with col_chart1:
    fig = charts.line_chart(
        yearly_df, x="year", y="avg_run_rate",
        title="📈 Average Run Rate by Year",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_chart2:
    top_teams = team_stats_df.head(12).sort_values("win_pct")
    fig = charts.horizontal_bar_chart(
        top_teams, x="win_pct", y="team",
        title="🏆 Team Win Rates (%)",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2: Boundaries + Toss Analysis ────────────────
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    fig = charts.grouped_bar_chart(
        yearly_df, x="year",
        y_cols=["total_fours", "total_sixes"],
        names=["Fours", "Sixes"],
        title="🏏 Boundary Evolution Over Years",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_chart4:
    toss_data = toss_analysis(matches_df)
    toss_df = pd.DataFrame({
        "Decision": ["Bat First", "Field First"],
        "Times Chosen": [toss_data["bat_first_chosen"], toss_data["field_first_chosen"]],
        "Win %": [toss_data["bat_first_win_pct"], toss_data["field_first_win_pct"]],
    })
    fig = charts.bar_chart(
        toss_df, x="Decision", y="Win %",
        title="🪙 Toss Decision Win Rate",
        text="Win %",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Charts Row 3: Yearly Match Count + Insights ─────────────
section_header("💡", "Key Insights")

col_insight1, col_insight2 = st.columns([3, 2])

with col_insight1:
    fig = charts.area_chart(
        yearly_df, x="year", y="matches",
        title="📅 T20I Matches Per Year",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_insight2:
    # Generate dynamic insights from data
    top_scorer = deliveries_df.groupby("batter")["runs_batter"].sum().idxmax()
    top_scorer_runs = int(deliveries_df.groupby("batter")["runs_batter"].sum().max())

    top_wicket_taker = deliveries_df.groupby("bowler")["is_wicket"].sum().idxmax()
    top_wickets = int(deliveries_df.groupby("bowler")["is_wicket"].sum().max())

    most_pom = matches_df["player_of_match"].value_counts().idxmax()
    pom_count = int(matches_df["player_of_match"].value_counts().max())

    chasing_wins = len(matches_df[matches_df["win_type"] == "wickets"])
    defending_wins = len(matches_df[matches_df["win_type"] == "runs"])
    chase_pct = round(chasing_wins / max(chasing_wins + defending_wins, 1) * 100, 1)

    insight_card("🏏", f"**Top Run Scorer:** {top_scorer} with {top_scorer_runs:,} runs across all T20Is")
    insight_card("🎯", f"**Leading Wicket-Taker:** {top_wicket_taker} with {top_wickets} wickets")
    insight_card("⭐", f"**Most Player of Match Awards:** {most_pom} ({pom_count} times)")
    insight_card("📊", f"**Chasing teams win {chase_pct}%** of decided matches")

    if len(yearly_df) >= 2:
        first_rr = yearly_df.iloc[0]["avg_run_rate"]
        last_rr = yearly_df.iloc[-1]["avg_run_rate"]
        rr_change = round((last_rr - first_rr) / first_rr * 100, 1)
        insight_card("⚡", f"**Run rate has {'increased' if rr_change > 0 else 'decreased'} by {abs(rr_change)}%** from {int(yearly_df.iloc[0]['year'])} to {int(yearly_df.iloc[-1]['year'])}")

st.markdown("---")

# ── Top Venues ───────────────────────────────────────────────
section_header("🏟️", "Venue Intelligence")

top_venues = venue_stats_df.head(15)
fig = charts.bar_chart(
    top_venues.sort_values("matches_hosted", ascending=True).tail(15),
    x="matches_hosted", y="venue",
    title="🏟️ Top Venues by Matches Hosted",
    orientation="h",
    height=500,
)
st.plotly_chart(fig, use_container_width=True)
