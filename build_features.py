import pandas as pd
import sqlite3

conn = sqlite3.connect("fifa.db")

# Step 1: Load all World Cup matches
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

print(f"Loaded {len(matches)} matches")

# Step 2: Build a "team stats" table -- average goals scored and conceded,
# using BOTH home and away appearances for each team.
#
# NOTE (known simplification, documented honestly):
# These averages use a team's ENTIRE history, not just matches before each
# specific prediction point. This is a simplified approach for this stage of
# the project. A more rigorous version would calculate "average so far, at
# the time of each match" to avoid any data leakage. This is a planned
# future upgrade -- see README roadmap.

# Goals scored: combine home appearances (home_goals) and away appearances (away_goals)
home_scoring = matches[["home_team", "home_goals"]].rename(
    columns={"home_team": "team", "home_goals": "goals_scored"}
)
away_scoring = matches[["away_team", "away_goals"]].rename(
    columns={"away_team": "team", "away_goals": "goals_scored"}
)
all_scoring = pd.concat([home_scoring, away_scoring])
avg_scored = all_scoring.groupby("team")["goals_scored"].mean().reset_index()
avg_scored.columns = ["team", "avg_goals_scored"]

# Goals conceded: when a team is home, they concede away_goals; when away, they concede home_goals
home_conceding = matches[["home_team", "away_goals"]].rename(
    columns={"home_team": "team", "away_goals": "goals_conceded"}
)
away_conceding = matches[["away_team", "home_goals"]].rename(
    columns={"away_team": "team", "home_goals": "goals_conceded"}
)
all_conceding = pd.concat([home_conceding, away_conceding])
avg_conceded = all_conceding.groupby("team")["goals_conceded"].mean().reset_index()
avg_conceded.columns = ["team", "avg_goals_conceded"]

# Combine into one team_stats table
team_stats = avg_scored.merge(avg_conceded, on="team")
print(f"\nCalculated stats for {len(team_stats)} teams")
print(team_stats.sort_values("avg_goals_scored", ascending=False).head(10))

# Step 3: Encode tournament stage as a number
# (models need numbers, not text -- this is a simple manual encoding)
stage_encoding = {
    "Group 1": 0, "Group 2": 0, "Group 3": 0, "Group 4": 0,
    "Group 5": 0, "Group 6": 0, "Group A": 0, "Group B": 0,
    "Group C": 0, "Group D": 0, "Group E": 0, "Group F": 0,
    "Group G": 0, "Group H": 0,
    "Round of 16": 1, "Quarterfinals": 2, "Semifinals": 3,
    "Match for third place": 3, "Final": 4,
    "First round": 0, "Preliminary round": 0,
}
matches["stage_encoded"] = matches["stage"].map(stage_encoding).fillna(0)

# Step 4: Attach each team's stats to every match (as the FEATURES for that match)
matches = matches.merge(
    team_stats.rename(columns={
        "team": "home_team",
        "avg_goals_scored": "home_avg_scored",
        "avg_goals_conceded": "home_avg_conceded",
    }),
    on="home_team",
    how="left",
)
matches = matches.merge(
    team_stats.rename(columns={
        "team": "away_team",
        "avg_goals_scored": "away_avg_scored",
        "avg_goals_conceded": "away_avg_conceded",
    }),
    on="away_team",
    how="left",
)

# Drop any rows where we couldn't find stats (shouldn't happen, but safety check)
before = len(matches)
matches = matches.dropna(
    subset=["home_avg_scored", "home_avg_conceded", "away_avg_scored", "away_avg_conceded"]
)
print(f"\nDropped {before - len(matches)} rows with missing team stats")
print(f"Final dataset: {len(matches)} matches ready for modeling")

# Step 5: Save this feature-engineered dataset as a new table in our database
matches.to_sql("match_features", conn, if_exists="replace", index=False)
print("\nSaved as 'match_features' table in fifa.db")

print("\nSample of final features:")
print(matches[[
    "home_team", "away_team", "home_avg_scored", "home_avg_conceded",
    "away_avg_scored", "away_avg_conceded", "stage_encoded",
    "home_goals", "away_goals"
]].head(5))

conn.close()