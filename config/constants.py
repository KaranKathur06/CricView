"""
CricView Constants — Phase definitions, team metadata, column mappings
"""

# ── Phase Definitions (over-based) ───────────────────────────
PHASES = {
    "powerplay": (0, 5),    # Overs 0–5 (over_num 0-indexed in Cricsheet)
    "middle":    (6, 15),   # Overs 6–15
    "death":     (16, 19),  # Overs 16–19
}

def get_phase(over_num: int) -> str:
    """Return phase name for a given over number (0-indexed)."""
    if over_num <= 5:
        return "powerplay"
    elif over_num <= 15:
        return "middle"
    else:
        return "death"

# ── Team Name Normalization ──────────────────────────────────
TEAM_SHORT_NAMES = {
    "India":          "IND",
    "Australia":      "AUS",
    "England":        "ENG",
    "South Africa":   "SA",
    "New Zealand":    "NZ",
    "Pakistan":       "PAK",
    "Sri Lanka":      "SL",
    "West Indies":    "WI",
    "Bangladesh":     "BAN",
    "Afghanistan":    "AFG",
    "Zimbabwe":       "ZIM",
    "Ireland":        "IRE",
    "Netherlands":    "NED",
    "Scotland":       "SCO",
    "Namibia":        "NAM",
    "Oman":           "OMA",
    "U.S.A.":         "USA",
    "Nepal":          "NEP",
    "Papua New Guinea": "PNG",
    "United Arab Emirates": "UAE",
    "Hong Kong":      "HK",
    "Canada":         "CAN",
    "Uganda":         "UGA",
}

# ── Team Flag Emojis ─────────────────────────────────────────
TEAM_FLAGS = {
    "India":        "🇮🇳",
    "Australia":    "🇦🇺",
    "England":      "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "South Africa": "🇿🇦",
    "New Zealand":  "🇳🇿",
    "Pakistan":     "🇵🇰",
    "Sri Lanka":    "🇱🇰",
    "West Indies":  "🌴",
    "Bangladesh":   "🇧🇩",
    "Afghanistan":  "🇦🇫",
    "Zimbabwe":     "🇿🇼",
    "Ireland":      "🇮🇪",
    "Netherlands":  "🇳🇱",
    "Scotland":     "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Namibia":      "🇳🇦",
    "Oman":         "🇴🇲",
    "U.S.A.":       "🇺🇸",
    "Nepal":        "🇳🇵",
}

# ── Column Mappings (Standardized) ───────────────────────────
MATCH_COLS = [
    "match_id", "match_date", "year", "city", "venue",
    "team1", "team2", "toss_winner", "toss_decision",
    "winner", "win_type", "win_margin",
    "player_of_match", "event_name", "overs",
]

DELIVERY_COLS = [
    "match_id", "innings", "batting_team", "bowling_team",
    "over_num", "ball_num", "batter", "non_striker", "bowler",
    "runs_batter", "runs_extras", "runs_total",
    "extras_type", "is_wicket", "wicket_kind", "player_out",
    "phase", "is_four", "is_six",
]

# ── KPI Icons ────────────────────────────────────────────────
KPI_ICONS = {
    "matches":  "🏏",
    "teams":    "🏟️",
    "players":  "👤",
    "runs":     "🏃",
    "fours":    "4️⃣",
    "sixes":    "6️⃣",
    "wickets":  "🎯",
    "balls":    "⚾",
    "win_rate": "🏆",
    "sr":       "⚡",
    "avg":      "📊",
    "economy":  "💰",
}
