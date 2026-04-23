"""
CricView ETL Pipeline
=====================
Transforms ~2,800 Cricsheet JSON match files into:
  1. SQLite database (data/cricket.db)
  2. Parquet cache files (data/processed/*.parquet)

Usage:
    python scripts/ingest.py --json-dir "path/to/JSON DATA" --output-dir "data"

This script only needs to run ONCE. After that, the app loads from parquet.
"""

import os
import sys
import json
import sqlite3
import argparse
import time
from pathlib import Path

import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.constants import get_phase


def create_tables(conn: sqlite3.Connection):
    """Create normalized database schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id    TEXT PRIMARY KEY,
            match_date  TEXT,
            year        INTEGER,
            city        TEXT,
            venue       TEXT,
            team1       TEXT,
            team2       TEXT,
            toss_winner TEXT,
            toss_decision TEXT,
            winner      TEXT,
            win_type    TEXT,
            win_margin  INTEGER,
            player_of_match TEXT,
            event_name  TEXT,
            overs       INTEGER DEFAULT 20
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id    TEXT NOT NULL,
            innings     INTEGER,
            batting_team TEXT,
            bowling_team TEXT,
            over_num    INTEGER,
            ball_num    INTEGER,
            batter      TEXT,
            non_striker TEXT,
            bowler      TEXT,
            runs_batter INTEGER DEFAULT 0,
            runs_extras INTEGER DEFAULT 0,
            runs_total  INTEGER DEFAULT 0,
            extras_type TEXT,
            is_wicket   INTEGER DEFAULT 0,
            wicket_kind TEXT,
            player_out  TEXT,
            phase       TEXT,
            is_four     INTEGER DEFAULT 0,
            is_six      INTEGER DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(match_id)
        );

        CREATE INDEX IF NOT EXISTS idx_del_match ON deliveries(match_id);
        CREATE INDEX IF NOT EXISTS idx_del_batter ON deliveries(batter);
        CREATE INDEX IF NOT EXISTS idx_del_bowler ON deliveries(bowler);
        CREATE INDEX IF NOT EXISTS idx_del_team ON deliveries(batting_team);
        CREATE INDEX IF NOT EXISTS idx_del_phase ON deliveries(phase);
        CREATE INDEX IF NOT EXISTS idx_del_match_inn ON deliveries(match_id, innings);
        CREATE INDEX IF NOT EXISTS idx_matches_year ON matches(year);
        CREATE INDEX IF NOT EXISTS idx_matches_venue ON matches(venue);
    """)
    conn.commit()


def parse_win_info(outcome: dict) -> tuple:
    """Extract win type and margin from outcome dict."""
    if not outcome:
        return "no result", 0
    if "winner" not in outcome:
        result = outcome.get("result", "no result")
        return result, 0
    by = outcome.get("by", {})
    if "runs" in by:
        return "runs", by["runs"]
    elif "wickets" in by:
        return "wickets", by["wickets"]
    else:
        return "other", 0


def ingest_json_files(json_dir: str, db_path: str):
    """Parse all JSON match files and insert into SQLite."""
    conn = sqlite3.connect(db_path)
    create_tables(conn)

    json_path = Path(json_dir)
    json_files = sorted(json_path.glob("*.json"))
    total = len(json_files)

    if total == 0:
        print(f"❌ No JSON files found in {json_dir}")
        return conn

    print(f"📂 Found {total} JSON files in {json_dir}")
    print(f"🔄 Processing...")

    match_count = 0
    delivery_count = 0
    skipped = 0
    errors = 0

    for i, json_file in enumerate(json_files):
        if (i + 1) % 200 == 0 or i == 0:
            pct = ((i + 1) / total) * 100
            print(f"   [{pct:5.1f}%] Processing file {i+1}/{total}...")

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            errors += 1
            continue

        info = data.get("info", {})

        # Filter: only male T20 matches with 20 overs
        gender = info.get("gender", "")
        overs = info.get("overs", 0)
        if gender != "male" or overs != 20:
            skipped += 1
            continue

        match_id = json_file.stem
        dates = info.get("dates", [])
        match_date = dates[0] if dates else None
        year = int(match_date[:4]) if match_date else None
        teams = info.get("teams", [])
        if len(teams) < 2:
            skipped += 1
            continue

        outcome = info.get("outcome", {})
        win_type, win_margin = parse_win_info(outcome)
        winner = outcome.get("winner", "No Result")

        pom_list = info.get("player_of_match", [])
        player_of_match = pom_list[0] if pom_list else None

        event = info.get("event", {})
        event_name = event.get("name", "") if isinstance(event, dict) else ""

        # Insert match
        try:
            conn.execute("""
                INSERT OR IGNORE INTO matches
                (match_id, match_date, year, city, venue, team1, team2,
                 toss_winner, toss_decision, winner, win_type, win_margin,
                 player_of_match, event_name, overs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, match_date, year,
                info.get("city", "Unknown"),
                info.get("venue", "Unknown"),
                teams[0], teams[1],
                info.get("toss", {}).get("winner", ""),
                info.get("toss", {}).get("decision", ""),
                winner, win_type, win_margin,
                player_of_match, event_name, overs,
            ))
            match_count += 1
        except sqlite3.IntegrityError:
            continue

        # Insert deliveries
        delivery_batch = []
        for innings_idx, inning in enumerate(data.get("innings", []), 1):
            team = inning.get("team", "Unknown")
            bowling_team = teams[1] if team == teams[0] else teams[0]

            for over in inning.get("overs", []):
                over_num = over.get("over", 0)
                phase = get_phase(over_num)

                for ball_idx, delivery in enumerate(over.get("deliveries", []), 1):
                    runs = delivery.get("runs", {})
                    runs_batter = runs.get("batter", 0)
                    runs_extras = runs.get("extras", 0)
                    runs_total = runs.get("total", 0)

                    extras = delivery.get("extras", {})
                    extras_type = ", ".join(extras.keys()) if extras else ""

                    wickets = delivery.get("wickets", [])
                    is_wicket = 1 if wickets else 0
                    wicket_kind = wickets[0].get("kind", "") if wickets else ""
                    player_out = wickets[0].get("player_out", "") if wickets else ""

                    is_four = 1 if runs_batter == 4 else 0
                    is_six = 1 if runs_batter == 6 else 0

                    delivery_batch.append((
                        match_id, innings_idx, team, bowling_team,
                        over_num, ball_idx,
                        delivery.get("batter", ""),
                        delivery.get("non_striker", ""),
                        delivery.get("bowler", ""),
                        runs_batter, runs_extras, runs_total,
                        extras_type, is_wicket, wicket_kind, player_out,
                        phase, is_four, is_six,
                    ))
                    delivery_count += 1

        if delivery_batch:
            conn.executemany("""
                INSERT INTO deliveries
                (match_id, innings, batting_team, bowling_team,
                 over_num, ball_num, batter, non_striker, bowler,
                 runs_batter, runs_extras, runs_total,
                 extras_type, is_wicket, wicket_kind, player_out,
                 phase, is_four, is_six)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, delivery_batch)

    conn.commit()

    print(f"\n✅ ETL Complete!")
    print(f"   📊 Matches inserted: {match_count}")
    print(f"   ⚾ Deliveries inserted: {delivery_count:,}")
    print(f"   ⏭️  Skipped (non-T20/female): {skipped}")
    print(f"   ❌ Errors: {errors}")

    return conn


def generate_parquet_cache(db_path: str, output_dir: str):
    """Generate pre-aggregated parquet files from SQLite."""
    conn = sqlite3.connect(db_path)
    processed_dir = Path(output_dir) / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🔄 Generating parquet cache files...")

    # 1. Matches parquet
    matches_df = pd.read_sql("SELECT * FROM matches", conn)
    matches_df.to_parquet(processed_dir / "matches.parquet", index=False)
    print(f"   ✅ matches.parquet ({len(matches_df)} rows)")

    # 2. Deliveries parquet
    deliveries_df = pd.read_sql("SELECT * FROM deliveries", conn)
    deliveries_df.to_parquet(processed_dir / "deliveries.parquet", index=False)
    print(f"   ✅ deliveries.parquet ({len(deliveries_df):,} rows)")

    # 3. Player batting stats
    batting_sql = """
        SELECT
            batter as player,
            COUNT(DISTINCT match_id) as matches,
            COUNT(*) as balls_faced,
            SUM(runs_batter) as runs,
            SUM(is_four) as fours,
            SUM(is_six) as sixes,
            SUM(is_wicket) as dismissals,
            ROUND(CAST(SUM(runs_batter) AS REAL) / NULLIF(SUM(is_wicket), 0), 2) as batting_avg,
            ROUND(CAST(SUM(runs_batter) AS REAL) / COUNT(*) * 100, 2) as strike_rate,
            ROUND(CAST(SUM(is_four) + SUM(is_six) AS REAL) / COUNT(*) * 100, 2) as boundary_pct,
            ROUND(CAST(SUM(CASE WHEN runs_batter = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as dot_pct
        FROM deliveries
        GROUP BY batter
        HAVING balls_faced >= 10
        ORDER BY runs DESC
    """
    batting_df = pd.read_sql(batting_sql, conn)
    batting_df.to_parquet(processed_dir / "player_batting.parquet", index=False)
    print(f"   ✅ player_batting.parquet ({len(batting_df)} players)")

    # 4. Player batting phase splits
    phase_batting_sql = """
        SELECT
            batter as player,
            phase,
            COUNT(*) as balls_faced,
            SUM(runs_batter) as runs,
            SUM(is_four) as fours,
            SUM(is_six) as sixes,
            SUM(is_wicket) as dismissals,
            ROUND(CAST(SUM(runs_batter) AS REAL) / COUNT(*) * 100, 2) as strike_rate
        FROM deliveries
        GROUP BY batter, phase
        HAVING balls_faced >= 5
    """
    phase_bat_df = pd.read_sql(phase_batting_sql, conn)
    phase_bat_df.to_parquet(processed_dir / "player_batting_phase.parquet", index=False)
    print(f"   ✅ player_batting_phase.parquet ({len(phase_bat_df)} rows)")

    # 5. Player bowling stats
    bowling_sql = """
        SELECT
            bowler as player,
            COUNT(DISTINCT match_id) as matches,
            COUNT(*) as balls_bowled,
            SUM(runs_total) as runs_conceded,
            SUM(is_wicket) as wickets,
            SUM(CASE WHEN runs_total = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(is_four) as fours_conceded,
            SUM(is_six) as sixes_conceded,
            ROUND(CAST(SUM(runs_total) AS REAL) / (COUNT(*) / 6.0), 2) as economy,
            ROUND(CAST(SUM(runs_total) AS REAL) / NULLIF(SUM(is_wicket), 0), 2) as bowling_avg,
            ROUND(CAST(COUNT(*) AS REAL) / NULLIF(SUM(is_wicket), 0), 2) as bowling_sr,
            ROUND(CAST(SUM(CASE WHEN runs_total = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as dot_pct
        FROM deliveries
        GROUP BY bowler
        HAVING balls_bowled >= 10
        ORDER BY wickets DESC
    """
    bowling_df = pd.read_sql(bowling_sql, conn)
    bowling_df.to_parquet(processed_dir / "player_bowling.parquet", index=False)
    print(f"   ✅ player_bowling.parquet ({len(bowling_df)} players)")

    # 6. Player bowling phase splits
    phase_bowling_sql = """
        SELECT
            bowler as player,
            phase,
            COUNT(*) as balls_bowled,
            SUM(runs_total) as runs_conceded,
            SUM(is_wicket) as wickets,
            SUM(CASE WHEN runs_total = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(CAST(SUM(runs_total) AS REAL) / (COUNT(*) / 6.0), 2) as economy,
            ROUND(CAST(SUM(CASE WHEN runs_total = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as dot_pct
        FROM deliveries
        GROUP BY bowler, phase
        HAVING balls_bowled >= 5
    """
    phase_bowl_df = pd.read_sql(phase_bowling_sql, conn)
    phase_bowl_df.to_parquet(processed_dir / "player_bowling_phase.parquet", index=False)
    print(f"   ✅ player_bowling_phase.parquet ({len(phase_bowl_df)} rows)")

    # 7. Team stats
    team_sql = """
        SELECT
            t.team,
            COUNT(*) as matches_played,
            SUM(CASE WHEN m.winner = t.team THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.winner != t.team AND m.winner != 'No Result' THEN 1 ELSE 0 END) as losses,
            ROUND(CAST(SUM(CASE WHEN m.winner = t.team THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as win_pct
        FROM (
            SELECT team1 as team, match_id FROM matches
            UNION ALL
            SELECT team2 as team, match_id FROM matches
        ) t
        JOIN matches m ON t.match_id = m.match_id
        GROUP BY t.team
        HAVING matches_played >= 3
        ORDER BY win_pct DESC
    """
    team_df = pd.read_sql(team_sql, conn)
    team_df.to_parquet(processed_dir / "team_stats.parquet", index=False)
    print(f"   ✅ team_stats.parquet ({len(team_df)} teams)")

    # 8. Venue stats
    venue_sql = """
        SELECT
            venue,
            city,
            COUNT(*) as matches_hosted,
            ROUND(AVG(CASE WHEN innings = 1 THEN inn_total END), 1) as avg_first_innings,
            ROUND(AVG(CASE WHEN innings = 2 THEN inn_total END), 1) as avg_second_innings
        FROM (
            SELECT
                m.venue,
                m.city,
                d.match_id,
                d.innings,
                SUM(d.runs_total) as inn_total
            FROM deliveries d
            JOIN matches m ON d.match_id = m.match_id
            GROUP BY m.venue, m.city, d.match_id, d.innings
        )
        GROUP BY venue, city
        HAVING matches_hosted >= 2
        ORDER BY matches_hosted DESC
    """
    venue_df = pd.read_sql(venue_sql, conn)
    venue_df.to_parquet(processed_dir / "venue_stats.parquet", index=False)
    print(f"   ✅ venue_stats.parquet ({len(venue_df)} venues)")

    # 9. Yearly aggregated stats
    yearly_sql = """
        SELECT
            m.year,
            COUNT(DISTINCT m.match_id) as matches,
            SUM(d.runs_total) as total_runs,
            SUM(d.is_four) as total_fours,
            SUM(d.is_six) as total_sixes,
            SUM(d.is_wicket) as total_wickets,
            COUNT(*) as total_balls,
            ROUND(CAST(SUM(d.runs_total) AS REAL) / COUNT(*) * 6, 2) as avg_run_rate
        FROM deliveries d
        JOIN matches m ON d.match_id = m.match_id
        GROUP BY m.year
        ORDER BY m.year
    """
    yearly_df = pd.read_sql(yearly_sql, conn)
    yearly_df.to_parquet(processed_dir / "yearly_stats.parquet", index=False)
    print(f"   ✅ yearly_stats.parquet ({len(yearly_df)} years)")

    conn.close()
    print(f"\n🎉 All parquet cache files generated in {processed_dir}")


def main():
    parser = argparse.ArgumentParser(description="CricView ETL Pipeline")
    parser.add_argument(
        "--json-dir",
        default=r"C:\STUDY\PROGRAMS\PYTHON\T20 MEN'S CRICKET ANALYSIS DASHBOARD\Datasets\JSON DATA",
        help="Path to directory containing Cricsheet JSON files",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent.parent / "data"),
        help="Output directory for database and parquet files",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(output_dir / "cricket.db")

    print("=" * 60)
    print("  🏏 CricView ETL Pipeline")
    print("=" * 60)
    print(f"  📂 JSON Source:  {args.json_dir}")
    print(f"  💾 Database:     {db_path}")
    print(f"  📦 Output:       {output_dir}")
    print("=" * 60)

    start = time.time()

    # Phase 1: JSON → SQLite
    conn = ingest_json_files(args.json_dir, db_path)
    conn.close()

    # Phase 2: SQLite → Parquet
    generate_parquet_cache(db_path, str(output_dir))

    elapsed = time.time() - start
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    print(f"🚀 Ready! Run the app with: streamlit run app.py")


if __name__ == "__main__":
    main()
