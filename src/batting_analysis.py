"""
CricView Batting Analysis Module
=================================
All batting-specific analytics computations.
"""

import pandas as pd
import numpy as np


def top_run_scorers(deliveries_df, n=15, team=None, year=None):
    """Get top run scorers with optional team/year filter."""
    df = deliveries_df.copy()
    if team and team != "All":
        df = df[df["batting_team"] == team]
    if year and year != "All":
        # Need match data merged for year filter
        pass

    result = df.groupby("batter").agg(
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        dismissals=("is_wicket", "sum"),
    ).reset_index()

    result["strike_rate"] = (result["runs"] / result["balls"] * 100).round(2)
    result["batting_avg"] = (result["runs"] / result["dismissals"].replace(0, np.nan)).round(2)
    result = result.sort_values("runs", ascending=False).head(n)
    result = result.rename(columns={"batter": "player"})
    return result


def player_career_summary(deliveries_df, matches_df, player_name):
    """Get comprehensive career summary for a single player."""
    bat_df = deliveries_df[deliveries_df["batter"] == player_name]
    bowl_df = deliveries_df[deliveries_df["bowler"] == player_name]

    # Batting stats
    bat_matches = bat_df["match_id"].nunique()
    total_runs = int(bat_df["runs_batter"].sum())
    balls_faced = len(bat_df)
    fours = int(bat_df["is_four"].sum())
    sixes = int(bat_df["is_six"].sum())
    dismissals = int(bat_df["is_wicket"].sum())
    strike_rate = round(total_runs / max(balls_faced, 1) * 100, 2)
    batting_avg = round(total_runs / max(dismissals, 1), 2)
    boundary_pct = round((fours + sixes) / max(balls_faced, 1) * 100, 2)
    dot_pct = round(len(bat_df[bat_df["runs_batter"] == 0]) / max(balls_faced, 1) * 100, 2)

    # Highest score per innings
    innings_runs = bat_df.groupby(["match_id", "innings"])["runs_batter"].sum()
    highest_score = int(innings_runs.max()) if len(innings_runs) > 0 else 0

    # 50s and 100s
    fifties = int((innings_runs >= 50).sum())
    hundreds = int((innings_runs >= 100).sum())

    # Bowling stats
    bowl_matches = bowl_df["match_id"].nunique()
    balls_bowled = len(bowl_df)
    runs_conceded = int(bowl_df["runs_total"].sum())
    wickets = int(bowl_df["is_wicket"].sum())
    economy = round(runs_conceded / max(balls_bowled / 6, 1), 2)
    bowling_avg = round(runs_conceded / max(wickets, 1), 2)
    bowling_sr = round(balls_bowled / max(wickets, 1), 2)

    return {
        "player": player_name,
        "bat_matches": bat_matches,
        "total_runs": total_runs,
        "balls_faced": balls_faced,
        "fours": fours,
        "sixes": sixes,
        "dismissals": dismissals,
        "strike_rate": strike_rate,
        "batting_avg": batting_avg,
        "highest_score": highest_score,
        "fifties": fifties,
        "hundreds": hundreds,
        "boundary_pct": boundary_pct,
        "dot_pct": dot_pct,
        "bowl_matches": bowl_matches,
        "balls_bowled": balls_bowled,
        "runs_conceded": runs_conceded,
        "wickets": wickets,
        "economy": economy,
        "bowling_avg": bowling_avg,
        "bowling_sr": bowling_sr,
    }


def player_phase_splits(deliveries_df, player_name):
    """Get batting stats by phase (powerplay/middle/death)."""
    df = deliveries_df[deliveries_df["batter"] == player_name]

    phases = []
    for phase in ["powerplay", "middle", "death"]:
        phase_df = df[df["phase"] == phase]
        balls = len(phase_df)
        if balls == 0:
            continue
        runs = int(phase_df["runs_batter"].sum())
        phases.append({
            "phase": phase.title(),
            "balls": balls,
            "runs": runs,
            "fours": int(phase_df["is_four"].sum()),
            "sixes": int(phase_df["is_six"].sum()),
            "sr": round(runs / balls * 100, 2),
            "dot_pct": round(len(phase_df[phase_df["runs_batter"] == 0]) / balls * 100, 2),
        })

    return pd.DataFrame(phases) if phases else pd.DataFrame()


def player_vs_teams(deliveries_df, player_name):
    """Performance breakdown by opponent team."""
    df = deliveries_df[deliveries_df["batter"] == player_name]

    result = df.groupby("bowling_team").agg(
        balls=("runs_batter", "count"),
        runs=("runs_batter", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        dismissals=("is_wicket", "sum"),
    ).reset_index()

    result["sr"] = (result["runs"] / result["balls"] * 100).round(2)
    result["avg"] = (result["runs"] / result["dismissals"].replace(0, np.nan)).round(2)
    result = result.sort_values("runs", ascending=False)
    result = result.rename(columns={"bowling_team": "opponent"})
    return result


def player_innings_list(deliveries_df, matches_df, player_name, n=20):
    """Get last N innings details."""
    df = deliveries_df[deliveries_df["batter"] == player_name]

    innings = df.groupby(["match_id", "innings"]).agg(
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        out=("is_wicket", "max"),
    ).reset_index()

    innings["sr"] = (innings["runs"] / innings["balls"] * 100).round(1)

    # Merge with match info
    innings = innings.merge(
        matches_df[["match_id", "match_date", "venue", "team1", "team2"]],
        on="match_id",
        how="left",
    )
    innings = innings.sort_values("match_date", ascending=False).head(n)
    return innings


def player_yearly_runs(deliveries_df, matches_df, player_name):
    """Runs scored per year."""
    df = deliveries_df[deliveries_df["batter"] == player_name]
    df = df.merge(matches_df[["match_id", "year"]], on="match_id", how="left")

    result = df.groupby("year").agg(
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        matches=("match_id", "nunique"),
    ).reset_index()

    result["sr"] = (result["runs"] / result["balls"] * 100).round(2)
    return result.sort_values("year")


def top_partnerships(deliveries_df, n=10, team=None):
    """Top batting partnerships."""
    df = deliveries_df.copy()
    if team and team != "All":
        df = df[df["batting_team"] == team]

    # Create partnership key (sorted pair)
    df["partnership"] = df.apply(
        lambda r: " & ".join(sorted([r["batter"], r["non_striker"]])), axis=1
    )

    result = df.groupby("partnership").agg(
        runs=("runs_total", "sum"),
        balls=("runs_total", "count"),
    ).reset_index()

    result["run_rate"] = (result["runs"] / result["balls"] * 6).round(2)
    result = result.sort_values("runs", ascending=False).head(n)
    return result
