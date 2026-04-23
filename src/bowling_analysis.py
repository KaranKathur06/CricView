"""
CricView Bowling Analysis Module
=================================
Complete bowling analytics — the module that was entirely missing from the original app.
"""

import pandas as pd
import numpy as np


def top_wicket_takers(deliveries_df, n=15, team=None):
    """Get top wicket takers with full bowling stats."""
    df = deliveries_df.copy()
    if team and team != "All":
        df = df[df["bowling_team"] == team]

    result = df.groupby("bowler").agg(
        balls=("runs_total", "count"),
        runs_conceded=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
        dot_balls=("runs_total", lambda x: (x == 0).sum()),
        fours_conceded=("is_four", "sum"),
        sixes_conceded=("is_six", "sum"),
        matches=("match_id", "nunique"),
    ).reset_index()

    result["overs"] = (result["balls"] / 6).round(1)
    result["economy"] = (result["runs_conceded"] / (result["balls"] / 6)).round(2)
    result["bowling_avg"] = (result["runs_conceded"] / result["wickets"].replace(0, np.nan)).round(2)
    result["bowling_sr"] = (result["balls"] / result["wickets"].replace(0, np.nan)).round(2)
    result["dot_pct"] = (result["dot_balls"] / result["balls"] * 100).round(2)

    result = result[result["balls"] >= 30].sort_values("wickets", ascending=False).head(n)
    result = result.rename(columns={"bowler": "player"})
    return result


def bowler_career_summary(deliveries_df, player_name):
    """Full bowling career summary."""
    df = deliveries_df[deliveries_df["bowler"] == player_name]
    if len(df) == 0:
        return None

    balls = len(df)
    runs = int(df["runs_total"].sum())
    wickets = int(df["is_wicket"].sum())
    dots = int((df["runs_total"] == 0).sum())
    fours = int(df["is_four"].sum())
    sixes = int(df["is_six"].sum())

    # Best bowling figures per match
    match_wickets = df.groupby("match_id").agg(
        wickets=("is_wicket", "sum"),
        runs=("runs_total", "sum"),
    ).reset_index()

    best_match = match_wickets.sort_values(
        ["wickets", "runs"], ascending=[False, True]
    ).iloc[0] if len(match_wickets) > 0 else None

    return {
        "player": player_name,
        "matches": df["match_id"].nunique(),
        "balls_bowled": balls,
        "overs": round(balls / 6, 1),
        "runs_conceded": runs,
        "wickets": wickets,
        "economy": round(runs / max(balls / 6, 1), 2),
        "bowling_avg": round(runs / max(wickets, 1), 2),
        "bowling_sr": round(balls / max(wickets, 1), 2),
        "dot_balls": dots,
        "dot_pct": round(dots / max(balls, 1) * 100, 2),
        "fours_conceded": fours,
        "sixes_conceded": sixes,
        "best_figures": f"{int(best_match['wickets'])}/{int(best_match['runs'])}" if best_match is not None else "N/A",
    }


def bowler_phase_splits(deliveries_df, player_name):
    """Bowling stats by phase."""
    df = deliveries_df[deliveries_df["bowler"] == player_name]

    phases = []
    for phase in ["powerplay", "middle", "death"]:
        phase_df = df[df["phase"] == phase]
        balls = len(phase_df)
        if balls == 0:
            continue
        runs = int(phase_df["runs_total"].sum())
        phases.append({
            "phase": phase.title(),
            "balls": balls,
            "overs": round(balls / 6, 1),
            "runs": runs,
            "wickets": int(phase_df["is_wicket"].sum()),
            "economy": round(runs / max(balls / 6, 1), 2),
            "dot_pct": round(len(phase_df[phase_df["runs_total"] == 0]) / balls * 100, 2),
        })

    return pd.DataFrame(phases) if phases else pd.DataFrame()


def bowler_vs_teams(deliveries_df, player_name):
    """Bowling performance against each team."""
    df = deliveries_df[deliveries_df["bowler"] == player_name]

    result = df.groupby("batting_team").agg(
        balls=("runs_total", "count"),
        runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
    ).reset_index()

    result["economy"] = (result["runs"] / (result["balls"] / 6)).round(2)
    result["avg"] = (result["runs"] / result["wickets"].replace(0, np.nan)).round(2)
    result = result.sort_values("wickets", ascending=False)
    result = result.rename(columns={"batting_team": "opponent"})
    return result


def bowler_yearly_stats(deliveries_df, matches_df, player_name):
    """Year-by-year bowling stats."""
    df = deliveries_df[deliveries_df["bowler"] == player_name]
    df = df.merge(matches_df[["match_id", "year"]], on="match_id", how="left")

    result = df.groupby("year").agg(
        balls=("runs_total", "count"),
        runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
        matches=("match_id", "nunique"),
    ).reset_index()

    result["economy"] = (result["runs"] / (result["balls"] / 6)).round(2)
    return result.sort_values("year")


def best_economy_bowlers(deliveries_df, n=10, min_overs=10):
    """Best economy rate bowlers (min overs qualification)."""
    result = deliveries_df.groupby("bowler").agg(
        balls=("runs_total", "count"),
        runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
    ).reset_index()

    result["overs"] = result["balls"] / 6
    result["economy"] = (result["runs"] / result["overs"]).round(2)
    result = result[result["overs"] >= min_overs]
    result = result.sort_values("economy").head(n)
    result = result.rename(columns={"bowler": "player"})
    return result


def death_bowling_specialists(deliveries_df, n=10, min_balls=50):
    """Best death overs (16-19) bowlers by economy."""
    df = deliveries_df[deliveries_df["phase"] == "death"]

    result = df.groupby("bowler").agg(
        balls=("runs_total", "count"),
        runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
        dots=("runs_total", lambda x: (x == 0).sum()),
    ).reset_index()

    result["economy"] = (result["runs"] / (result["balls"] / 6)).round(2)
    result["dot_pct"] = (result["dots"] / result["balls"] * 100).round(2)
    result = result[result["balls"] >= min_balls]
    result = result.sort_values("economy").head(n)
    result = result.rename(columns={"bowler": "player"})
    return result
