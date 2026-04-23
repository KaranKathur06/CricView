"""
CricView Filter Panel Component
=================================
Reusable multi-select filter system for all dashboard pages.
"""

import streamlit as st
import pandas as pd


def filter_panel(matches_df, deliveries_df=None, show_team=True, show_year=True,
                 show_venue=False, show_opponent=False, key_prefix=""):
    """
    Render a filter panel and return filter selections.

    Returns:
        dict with keys: team, year, venue, opponent (based on what's shown)
    """
    filters = {}

    cols = st.columns([1] * sum([show_team, show_year, show_venue, show_opponent]))
    col_idx = 0

    if show_team:
        teams = sorted(set(matches_df["team1"].unique()) | set(matches_df["team2"].unique()))
        with cols[col_idx]:
            filters["team"] = st.selectbox(
                "🏏 Team",
                options=["All"] + teams,
                key=f"{key_prefix}_team",
            )
        col_idx += 1

    if show_year:
        years = sorted(matches_df["year"].dropna().unique().astype(int), reverse=True)
        with cols[col_idx]:
            filters["year"] = st.selectbox(
                "📅 Year",
                options=["All"] + [int(y) for y in years],
                key=f"{key_prefix}_year",
            )
        col_idx += 1

    if show_venue:
        venues = sorted(matches_df["venue"].unique())
        with cols[col_idx]:
            filters["venue"] = st.selectbox(
                "🏟️ Venue",
                options=["All"] + venues,
                key=f"{key_prefix}_venue",
            )
        col_idx += 1

    if show_opponent:
        team_selected = filters.get("team", "All")
        if team_selected != "All":
            # Show only opponents this team has played
            opp_matches = matches_df[
                (matches_df["team1"] == team_selected) |
                (matches_df["team2"] == team_selected)
            ]
            opponents = set()
            for _, row in opp_matches.iterrows():
                if row["team1"] == team_selected:
                    opponents.add(row["team2"])
                else:
                    opponents.add(row["team1"])
            opponents = sorted(opponents)
        else:
            opponents = sorted(set(matches_df["team1"].unique()) | set(matches_df["team2"].unique()))

        with cols[col_idx]:
            filters["opponent"] = st.selectbox(
                "⚔️ Opponent",
                options=["All"] + opponents,
                key=f"{key_prefix}_opponent",
            )
        col_idx += 1

    return filters


def apply_match_filters(matches_df, filters):
    """Apply filter selections to matches DataFrame."""
    df = matches_df.copy()

    team = filters.get("team", "All")
    if team != "All":
        df = df[(df["team1"] == team) | (df["team2"] == team)]

    year = filters.get("year", "All")
    if year != "All":
        df = df[df["year"] == int(year)]

    venue = filters.get("venue", "All")
    if venue != "All":
        df = df[df["venue"] == venue]

    opponent = filters.get("opponent", "All")
    if opponent != "All":
        df = df[(df["team1"] == opponent) | (df["team2"] == opponent)]

    return df


def apply_delivery_filters(deliveries_df, matches_df, filters):
    """Apply filter selections to deliveries DataFrame."""
    # First filter matches
    filtered_matches = apply_match_filters(matches_df, filters)
    match_ids = filtered_matches["match_id"].tolist()

    df = deliveries_df[deliveries_df["match_id"].isin(match_ids)]

    team = filters.get("team", "All")
    if team != "All":
        # Only include deliveries where this team is batting
        df = df[df["batting_team"] == team]

    return df
