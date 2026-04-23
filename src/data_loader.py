"""
CricView Data Loader
====================
Loads pre-processed parquet files into memory using @st.cache_resource.
Cold start: <1 second (vs 60s+ for raw JSON parsing).
"""

import streamlit as st
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@st.cache_resource(show_spinner=False)
def load_matches() -> pd.DataFrame:
    """Load matches DataFrame from parquet."""
    path = DATA_DIR / "matches.parquet"
    if not path.exists():
        st.error("⚠️ Data not found. Run `python scripts/ingest.py` first.")
        st.stop()
    df = pd.read_parquet(path)
    df["match_date"] = pd.to_datetime(df["match_date"])
    return df


@st.cache_resource(show_spinner=False)
def load_deliveries() -> pd.DataFrame:
    """Load deliveries DataFrame from parquet."""
    path = DATA_DIR / "deliveries.parquet"
    if not path.exists():
        st.error("⚠️ Data not found. Run `python scripts/ingest.py` first.")
        st.stop()
    return pd.read_parquet(path)


@st.cache_resource(show_spinner=False)
def load_player_batting() -> pd.DataFrame:
    """Load pre-aggregated player batting stats."""
    return pd.read_parquet(DATA_DIR / "player_batting.parquet")


@st.cache_resource(show_spinner=False)
def load_player_batting_phase() -> pd.DataFrame:
    """Load player batting phase-wise splits."""
    return pd.read_parquet(DATA_DIR / "player_batting_phase.parquet")


@st.cache_resource(show_spinner=False)
def load_player_bowling() -> pd.DataFrame:
    """Load pre-aggregated player bowling stats."""
    return pd.read_parquet(DATA_DIR / "player_bowling.parquet")


@st.cache_resource(show_spinner=False)
def load_player_bowling_phase() -> pd.DataFrame:
    """Load player bowling phase-wise splits."""
    return pd.read_parquet(DATA_DIR / "player_bowling_phase.parquet")


@st.cache_resource(show_spinner=False)
def load_team_stats() -> pd.DataFrame:
    """Load pre-aggregated team stats."""
    return pd.read_parquet(DATA_DIR / "team_stats.parquet")


@st.cache_resource(show_spinner=False)
def load_venue_stats() -> pd.DataFrame:
    """Load pre-aggregated venue stats."""
    return pd.read_parquet(DATA_DIR / "venue_stats.parquet")


@st.cache_resource(show_spinner=False)
def load_yearly_stats() -> pd.DataFrame:
    """Load yearly aggregated stats."""
    return pd.read_parquet(DATA_DIR / "yearly_stats.parquet")


def get_all_teams(matches_df: pd.DataFrame) -> list:
    """Get sorted list of all unique teams."""
    teams = set(matches_df["team1"].unique()) | set(matches_df["team2"].unique())
    return sorted(teams)


def get_all_players(deliveries_df: pd.DataFrame) -> list:
    """Get sorted list of all unique players."""
    players = set(deliveries_df["batter"].unique()) | set(deliveries_df["bowler"].unique())
    return sorted(players)


def get_all_venues(matches_df: pd.DataFrame) -> list:
    """Get sorted list of all unique venues."""
    return sorted(matches_df["venue"].unique())


def get_year_range(matches_df: pd.DataFrame) -> tuple:
    """Get min and max years."""
    return int(matches_df["year"].min()), int(matches_df["year"].max())
