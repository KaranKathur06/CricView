"""
📅 Year Explorer — Season-by-season breakdown
"""

import streamlit as st
import pandas as pd
import numpy as np
from components.styles import inject_global_css
from components.kpi_card import kpi_card, kpi_row, section_header, insight_card
from src.data_loader import (
    load_matches, load_deliveries, load_yearly_stats, get_all_teams,
)
from src.batting_analysis import top_run_scorers
from src.bowling_analysis import top_wicket_takers
from src import charts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="CricView · Year Explorer", page_icon="📅", layout="wide")
inject_global_css()

# ── Load Data ────────────────────────────────────────────────
matches_df = load_matches()
deliveries_df = load_deliveries()
yearly_df = load_yearly_stats()

# ── Header ───────────────────────────────────────────────────
st.markdown("# 📅 Year Explorer")
st.caption("Season-by-season cricket intelligence — drill into any year")

# ── Year Selection ───────────────────────────────────────────
years = sorted(matches_df["year"].dropna().unique().astype(int), reverse=True)

col_year, col_team = st.columns([1, 2])
with col_year:
    selected_year = st.selectbox(
        "📅 Select Year",
        options=years,
        index=0,
        key="year_select",
    )
with col_team:
    all_teams = get_all_teams(matches_df)
    selected_team = st.selectbox(
        "🏏 Filter by Team (Optional)",
        options=["All"] + all_teams,
        key="year_team_filter",
    )

st.markdown("---")

# ── Filter data for selected year ────────────────────────────
year_matches = matches_df[matches_df["year"] == selected_year]
year_match_ids = year_matches["match_id"].tolist()
year_deliveries = deliveries_df[deliveries_df["match_id"].isin(year_match_ids)]

if selected_team != "All":
    team_year_matches = year_matches[
        (year_matches["team1"] == selected_team) | (year_matches["team2"] == selected_team)
    ]
    team_match_ids = team_year_matches["match_id"].tolist()
    team_year_deliveries = year_deliveries[year_deliveries["match_id"].isin(team_match_ids)]
else:
    team_year_matches = year_matches
    team_year_deliveries = year_deliveries

# ── Year Header ──────────────────────────────────────────────
team_label = f" — {selected_team}" if selected_team != "All" else ""
st.markdown(f"## 📅 {selected_year}{team_label}")

# ── KPIs for the year ────────────────────────────────────────
total_matches = len(team_year_matches)
total_runs = int(team_year_deliveries["runs_total"].sum())
total_fours = int(team_year_deliveries["is_four"].sum())
total_sixes = int(team_year_deliveries["is_six"].sum())
total_wickets = int(team_year_deliveries["is_wicket"].sum())
total_balls = len(team_year_deliveries)
avg_rr = round(total_runs / max(total_balls / 6, 1), 2)

kpi_row([
    {"label": "Matches", "value": total_matches, "icon": "🏏"},
    {"label": "Total Runs", "value": total_runs, "icon": "🏃"},
    {"label": "Fours", "value": total_fours, "icon": "4️⃣"},
    {"label": "Sixes", "value": total_sixes, "icon": "6️⃣"},
    {"label": "Wickets", "value": total_wickets, "icon": "🎯"},
    {"label": "Avg Run Rate", "value": avg_rr, "icon": "⚡"},
], columns=6)

if total_matches == 0:
    st.warning(f"No matches found for {selected_year}{team_label}.")
    st.stop()

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────
tab_overview, tab_players, tab_teams, tab_matches = st.tabs([
    "📊 Overview", "👤 Top Performers", "🏟️ Team Standings", "📋 Match Results"
])

# ━━━━━━━━━━━━━━━━ OVERVIEW TAB ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_overview:
    if selected_team != "All":
        # Team-specific stats for the year
        wins = len(team_year_matches[team_year_matches["winner"] == selected_team])
        valid = team_year_matches[team_year_matches["winner"] != "No Result"]
        losses = len(valid) - wins
        win_pct = round(wins / max(len(valid), 1) * 100, 2)

        section_header("🏆", f"{selected_team}'s {selected_year} Record")

        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("Wins", wins, "🟢")
        with col2:
            kpi_card("Losses", losses, "🔴")
        with col3:
            kpi_card("Win Rate", f"{win_pct}%", "🏆")

        st.markdown("---")

        # Opponent-wise breakdown
        section_header("⚔️", "Performance vs Opponents")

        opp_data = []
        for _, row in team_year_matches.iterrows():
            opp = row["team2"] if row["team1"] == selected_team else row["team1"]
            won = 1 if row["winner"] == selected_team else 0
            opp_data.append({"opponent": opp, "won": won, "played": 1})

        if opp_data:
            opp_df = pd.DataFrame(opp_data).groupby("opponent").agg(
                played=("played", "sum"),
                won=("won", "sum"),
            ).reset_index()
            opp_df["lost"] = opp_df["played"] - opp_df["won"]
            opp_df = opp_df.sort_values("played", ascending=False)

            fig = charts.grouped_bar_chart(
                opp_df, x="opponent",
                y_cols=["won", "lost"],
                names=["Won", "Lost"],
                title=f"Results vs Each Opponent in {selected_year}",
                colors=["#00d4aa", "#ef4444"],
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        # Global overview for the year
        section_header("📊", f"{selected_year} Season Summary")

        # Win distribution by type
        decided = year_matches[year_matches["winner"] != "No Result"]
        chasing_wins = len(decided[decided["win_type"] == "wickets"])
        defending_wins = len(decided[decided["win_type"] == "runs"])

        col1, col2 = st.columns(2)
        with col1:
            win_dist = pd.DataFrame({
                "Type": ["Chasing Won", "Defending Won"],
                "Count": [chasing_wins, defending_wins],
            })
            fig = charts.pie_chart(win_dist, "Count", "Type", f"Win Distribution — {selected_year}")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Innings scores distribution
            innings_totals = team_year_deliveries.groupby(["match_id", "innings"])["runs_total"].sum().reset_index()
            fig = charts.bar_chart(
                innings_totals, x="runs_total", y=None,
                title=f"Score Distribution — {selected_year}",
            )
            # Use histogram instead
            import plotly.express as px
            fig = px.histogram(
                innings_totals, x="runs_total",
                title=f"Score Distribution — {selected_year}",
                nbins=20,
                color_discrete_sequence=["#00d4aa"],
            )
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="'Inter', sans-serif",
                xaxis_title="Runs",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━ TOP PERFORMERS TAB ━━━━━━━━━━━━━━━━━━━━━━
with tab_players:
    col1, col2 = st.columns(2)

    with col1:
        section_header("🏏", f"Top Batters — {selected_year}")
        year_top_batters = team_year_deliveries.groupby("batter").agg(
            runs=("runs_batter", "sum"),
            balls=("runs_batter", "count"),
            fours=("is_four", "sum"),
            sixes=("is_six", "sum"),
        ).reset_index()
        year_top_batters["sr"] = (year_top_batters["runs"] / year_top_batters["balls"] * 100).round(2)
        year_top_batters = year_top_batters.sort_values("runs", ascending=False).head(15)
        year_top_batters = year_top_batters.rename(columns={"batter": "player"})

        if not year_top_batters.empty:
            fig = charts.horizontal_bar_chart(
                year_top_batters.sort_values("runs").tail(10),
                x="runs", y="player",
                title=f"Top Scorers — {selected_year}",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)

            display = year_top_batters[["player", "runs", "balls", "sr", "fours", "sixes"]].copy()
            display.columns = ["Player", "Runs", "Balls", "SR", "4s", "6s"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    with col2:
        section_header("🎯", f"Top Bowlers — {selected_year}")
        year_top_bowlers = team_year_deliveries.groupby("bowler").agg(
            balls=("runs_total", "count"),
            runs_conceded=("runs_total", "sum"),
            wickets=("is_wicket", "sum"),
        ).reset_index()
        year_top_bowlers["economy"] = (year_top_bowlers["runs_conceded"] / (year_top_bowlers["balls"] / 6)).round(2)
        year_top_bowlers = year_top_bowlers[year_top_bowlers["balls"] >= 12]
        year_top_bowlers = year_top_bowlers.sort_values("wickets", ascending=False).head(15)
        year_top_bowlers = year_top_bowlers.rename(columns={"bowler": "player"})

        if not year_top_bowlers.empty:
            fig = charts.horizontal_bar_chart(
                year_top_bowlers.sort_values("wickets").tail(10),
                x="wickets", y="player",
                title=f"Top Wicket Takers — {selected_year}",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)

            display = year_top_bowlers[["player", "wickets", "runs_conceded", "economy"]].copy()
            display.columns = ["Player", "Wickets", "Runs", "Economy"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    # Most Player of Match awards this year
    st.markdown("---")
    section_header("⭐", f"Player of Match Awards — {selected_year}")

    pom = team_year_matches["player_of_match"].value_counts().head(10).reset_index()
    pom.columns = ["Player", "Awards"]

    if not pom.empty:
        fig = charts.horizontal_bar_chart(
            pom.sort_values("Awards"),
            x="Awards", y="Player",
            title=f"Most Player of Match — {selected_year}",
        )
        st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━ TEAM STANDINGS TAB ━━━━━━━━━━━━━━━━━━━━━━━
with tab_teams:
    section_header("🏟️", f"Team Standings — {selected_year}")

    # Calculate win % for each team in this year
    team_data = []
    for team in get_all_teams(year_matches):
        team_m = year_matches[
            (year_matches["team1"] == team) | (year_matches["team2"] == team)
        ]
        valid = team_m[team_m["winner"] != "No Result"]
        played = len(team_m)
        wins = len(team_m[team_m["winner"] == team])
        if played >= 2:
            team_data.append({
                "Team": team,
                "Played": played,
                "Won": wins,
                "Lost": len(valid) - wins,
                "Win %": round(wins / max(len(valid), 1) * 100, 2),
            })

    if team_data:
        standings = pd.DataFrame(team_data).sort_values("Win %", ascending=False)

        fig = charts.horizontal_bar_chart(
            standings.sort_values("Win %"),
            x="Win %", y="Team",
            title=f"Team Win Rates — {selected_year}",
            height=max(350, len(standings) * 30),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(standings, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━ MATCH RESULTS TAB ━━━━━━━━━━━━━━━━━━━━━━━
with tab_matches:
    section_header("📋", f"Match Results — {selected_year}")

    display_matches = team_year_matches[[
        "match_date", "venue", "city",
        "team1", "team2", "winner",
        "win_type", "win_margin", "player_of_match",
    ]].copy()

    display_matches.columns = [
        "Date", "Venue", "City",
        "Team 1", "Team 2", "Winner",
        "Win By", "Margin", "Player of Match",
    ]
    display_matches = display_matches.sort_values("Date", ascending=False)

    st.dataframe(
        display_matches,
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    # Venue distribution this year
    st.markdown("---")
    section_header("🌍", f"Venues Used — {selected_year}")

    venue_counts = team_year_matches["venue"].value_counts().head(15).reset_index()
    venue_counts.columns = ["Venue", "Matches"]

    fig = charts.horizontal_bar_chart(
        venue_counts.sort_values("Matches"),
        x="Matches", y="Venue",
        title=f"Top Venues — {selected_year}",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
