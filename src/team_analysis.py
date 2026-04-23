"""
CricView Team Analysis Module
==============================
Team-level aggregations, head-to-head, toss analysis.
"""

import pandas as pd
import numpy as np


def team_overview(matches_df, deliveries_df, team_name, opponent=None):
    """Comprehensive team overview stats."""
    # Filter matches involving this team
    team_matches = matches_df[
        (matches_df["team1"] == team_name) | (matches_df["team2"] == team_name)
    ]

    if opponent and opponent != "All":
        team_matches = team_matches[
            (team_matches["team1"] == opponent) | (team_matches["team2"] == opponent)
        ]

    total_matches = len(team_matches)
    if total_matches == 0:
        return {k: 0 for k in [
            "total_matches", "wins", "losses", "no_results",
            "win_pct", "avg_score", "highest_score",
            "total_fours", "total_sixes",
        ]}

    wins = len(team_matches[team_matches["winner"] == team_name])
    no_results = len(team_matches[team_matches["winner"] == "No Result"])
    losses = total_matches - wins - no_results
    win_pct = round(wins / max(total_matches - no_results, 1) * 100, 2)

    # Batting stats from deliveries
    match_ids = team_matches["match_id"].tolist()
    bat_df = deliveries_df[
        (deliveries_df["match_id"].isin(match_ids)) &
        (deliveries_df["batting_team"] == team_name)
    ]

    # Innings totals
    innings_totals = bat_df.groupby(["match_id", "innings"])["runs_total"].sum()

    return {
        "total_matches": total_matches,
        "wins": wins,
        "losses": losses,
        "no_results": no_results,
        "win_pct": win_pct,
        "avg_score": round(innings_totals.mean(), 1) if len(innings_totals) > 0 else 0,
        "highest_score": int(innings_totals.max()) if len(innings_totals) > 0 else 0,
        "total_fours": int(bat_df["is_four"].sum()),
        "total_sixes": int(bat_df["is_six"].sum()),
    }


def team_top_performers(deliveries_df, team_name, opponent=None, n=10):
    """Top batters and bowlers for a team."""
    bat_df = deliveries_df[deliveries_df["batting_team"] == team_name]
    bowl_df = deliveries_df[deliveries_df["bowling_team"] != team_name]
    bowl_df = deliveries_df[deliveries_df["bowling_team"] == team_name]
    # bowling_team in deliveries = team that's bowling, but bowler plays FOR bowling_team
    # Actually: bowler column + we need bowling_team to match
    bowl_df = deliveries_df[
        (deliveries_df["bowler"].isin(
            deliveries_df[deliveries_df["batting_team"] != team_name]["bowler"].unique()
        )) &
        (deliveries_df["batting_team"] != team_name)
    ]
    # Simpler: just filter deliveries where the bowling side is this team
    bowl_df = deliveries_df[deliveries_df["bowling_team"] == team_name]

    if opponent and opponent != "All":
        bat_df = bat_df[bat_df["bowling_team"] == opponent]
        bowl_df = bowl_df[bowl_df["batting_team"] == opponent]

    # Top batters
    top_batters = bat_df.groupby("batter").agg(
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
    ).reset_index()
    top_batters["sr"] = (top_batters["runs"] / top_batters["balls"] * 100).round(2)
    top_batters = top_batters.sort_values("runs", ascending=False).head(n)
    top_batters = top_batters.rename(columns={"batter": "player"})

    # Top bowlers
    top_bowlers = bowl_df.groupby("bowler").agg(
        balls=("runs_total", "count"),
        runs_conceded=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
    ).reset_index()
    top_bowlers["economy"] = (top_bowlers["runs_conceded"] / (top_bowlers["balls"] / 6)).round(2)
    top_bowlers = top_bowlers.sort_values("wickets", ascending=False).head(n)
    top_bowlers = top_bowlers.rename(columns={"bowler": "player"})

    return top_batters, top_bowlers


def team_phase_performance(deliveries_df, team_name, opponent=None):
    """Team performance by phase."""
    df = deliveries_df[deliveries_df["batting_team"] == team_name]
    if opponent and opponent != "All":
        df = df[df["bowling_team"] == opponent]

    phases = []
    for phase in ["powerplay", "middle", "death"]:
        phase_df = df[df["phase"] == phase]
        balls = len(phase_df)
        if balls == 0:
            continue
        runs = int(phase_df["runs_total"].sum())
        matches = phase_df["match_id"].nunique()
        phases.append({
            "phase": phase.title(),
            "total_runs": runs,
            "avg_runs_per_match": round(runs / max(matches, 1), 1),
            "run_rate": round(runs / (balls / 6), 2),
            "wickets_lost": int(phase_df["is_wicket"].sum()),
            "boundaries": int(phase_df["is_four"].sum() + phase_df["is_six"].sum()),
        })

    return pd.DataFrame(phases) if phases else pd.DataFrame()


def head_to_head(matches_df, team_a, team_b):
    """Head-to-head record between two teams."""
    h2h = matches_df[
        ((matches_df["team1"] == team_a) & (matches_df["team2"] == team_b)) |
        ((matches_df["team1"] == team_b) & (matches_df["team2"] == team_a))
    ]

    total = len(h2h)
    if total == 0:
        return {"total": 0, "team_a_wins": 0, "team_b_wins": 0, "no_result": 0}

    return {
        "total": total,
        "team_a_wins": len(h2h[h2h["winner"] == team_a]),
        "team_b_wins": len(h2h[h2h["winner"] == team_b]),
        "no_result": len(h2h[h2h["winner"] == "No Result"]),
    }


def toss_analysis(matches_df, team_name=None):
    """Toss impact analysis."""
    df = matches_df.copy()
    if team_name and team_name != "All":
        df = df[
            (df["team1"] == team_name) | (df["team2"] == team_name)
        ]

    total = len(df)
    valid = df[df["winner"] != "No Result"]

    toss_win_match_win = len(valid[valid["toss_winner"] == valid["winner"]])
    bat_first_wins = len(valid[
        (valid["toss_decision"] == "bat") & (valid["toss_winner"] == valid["winner"])
    ])
    field_first_wins = len(valid[
        (valid["toss_decision"] == "field") & (valid["toss_winner"] == valid["winner"])
    ])

    bat_choices = len(df[df["toss_decision"] == "bat"])
    field_choices = len(df[df["toss_decision"] == "field"])

    return {
        "total_matches": total,
        "toss_win_match_win": toss_win_match_win,
        "toss_win_match_win_pct": round(toss_win_match_win / max(len(valid), 1) * 100, 2),
        "bat_first_chosen": bat_choices,
        "field_first_chosen": field_choices,
        "bat_first_win_pct": round(bat_first_wins / max(bat_choices, 1) * 100, 2),
        "field_first_win_pct": round(field_first_wins / max(field_choices, 1) * 100, 2),
    }


def team_yearly_performance(matches_df, team_name):
    """Year-by-year team performance."""
    df = matches_df[
        (matches_df["team1"] == team_name) | (matches_df["team2"] == team_name)
    ]

    result = []
    for year in sorted(df["year"].unique()):
        year_df = df[df["year"] == year]
        valid = year_df[year_df["winner"] != "No Result"]
        matches = len(year_df)
        wins = len(year_df[year_df["winner"] == team_name])
        result.append({
            "year": int(year),
            "matches": matches,
            "wins": wins,
            "losses": len(valid) - wins,
            "win_pct": round(wins / max(len(valid), 1) * 100, 2),
        })

    return pd.DataFrame(result) if result else pd.DataFrame()
