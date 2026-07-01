import pandas as pd
import sqlite3

conn = sqlite3.connect("fifa.db")

# ── Step 1: Load all World Cup matches and sort chronologically ───────────────
matches = pd.read_sql_query(
    """
    SELECT
        Year as year,
        Stage as stage,
        [Home Team Name] as home_team,
        [Away Team Name] as away_team,
        [Home Team Goals] as home_goals,
        [Away Team Goals] as away_goals
    FROM world_cup_matches
    """,
    conn,
)

# Drop any matches that haven't happened yet (missing goals) which cause NaN errors
matches = matches.dropna(subset=['home_goals', 'away_goals'])

matches = matches.sort_values(by="year").reset_index(drop=True)
print(f"Loaded {len(matches)} matches (including 2018 & 2022)")

# ── Step 2: The Leakage Fix (Time-Aware Averages) ─────────────────────────────
# We calculate a team's stats using ONLY matches that happened BEFORE current_year
def get_historical_stats(team, current_year):
    past_matches = matches[
        (matches['year'] < current_year) & 
        ((matches['home_team'] == team) | (matches['away_team'] == team))
    ]
    
    # If they are a debutant and have no history, they start with 0
    if len(past_matches) == 0:
        return 0.0, 0.0 
        
    goals_scored = 0
    goals_conceded = 0
    
    for _, m in past_matches.iterrows():
        if m['home_team'] == team:
            goals_scored += m['home_goals']
            goals_conceded += m['away_goals']
        else:
            goals_scored += m['away_goals']
            goals_conceded += m['home_goals']
            
    return goals_scored / len(past_matches), goals_conceded / len(past_matches)

print("\nComputing time-aware historical features for each match...")
print("(This prevents data leakage. It takes a few seconds to run!)")

home_features = matches.apply(lambda row: get_historical_stats(row['home_team'], row['year']), axis=1, result_type="expand")
away_features = matches.apply(lambda row: get_historical_stats(row['away_team'], row['year']), axis=1, result_type="expand")

matches['home_avg_scored'] = home_features[0]
matches['home_avg_conceded'] = home_features[1]
matches['away_avg_scored'] = away_features[0]
matches['away_avg_conceded'] = away_features[1]

# ── Step 3: Encode Stage ──────────────────────────────────────────────────────
stage_encoding = {
    "Group 1": 0, "Group 2": 0, "Group 3": 0, "Group 4": 0, "Group 5": 0, "Group 6": 0, 
    "Group A": 0, "Group B": 0, "Group C": 0, "Group D": 0, "Group E": 0, "Group F": 0,
    "Group G": 0, "Group H": 0, "Round of 16": 1, "Quarterfinals": 2, "Semifinals": 3,
    "Match for third place": 3, "Final": 4, "First round": 0, "Preliminary round": 0,
    "Group/Knockout": 0 # Catch-all for the 2018/2022 patch
}
matches["stage_encoded"] = matches["stage"].map(stage_encoding).fillna(0)

# ── Step 4: Save time-aware match features for the ML model ───────────────────
matches.to_sql("match_features", conn, if_exists="replace", index=False)
print("✅ Saved leakage-free 'match_features' to database")

# ── Step 5: Save final, global team stats for the Dashboard Predictor ─────────
# The dashboard needs the absolute latest stats (up to 2022) for future predictions
print("\nComputing final stats for Dashboard Predictor...")
all_teams = set(matches['home_team']).union(set(matches['away_team']))
final_stats = []
for team in all_teams:
    # Use year=2030 to ensure we average ALL matches up to 2022
    scored, conceded = get_historical_stats(team, 2030)
    final_stats.append({
        "team": team,
        "avg_goals_scored": scored,
        "avg_goals_conceded": conceded
    })

final_team_stats = pd.DataFrame(final_stats)
final_team_stats.to_csv("team_stats.csv", index=False)
final_team_stats.to_sql("team_stats_final", conn, if_exists="replace", index=False)
print("✅ Saved final 'team_stats.csv' for the dashboard")

conn.close()