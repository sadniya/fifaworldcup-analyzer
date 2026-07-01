"""
cluster_teams.py
----------------
Uses KMeans clustering to group World Cup teams by playing style.

Two dimensions:
  - avg_goals_scored   (attacking strength)
  - avg_goals_conceded (defensive strength)

4 clusters emerge naturally:
  - High scoring + low conceding  → Elite teams (Brazil, Germany, France)
  - High scoring + high conceding → Entertaining attackers
  - Low scoring + low conceding   → Defensive grinders
  - Low scoring + high conceding  → Struggling teams

Saves cluster labels back into fifa.db as 'team_clusters' table.

Run this ONCE before starting the dashboard:
    python cluster_teams.py
"""

import pandas as pd
import sqlite3
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ── Step 1: Load team stats from the feature-engineered table ─────────────────
conn = sqlite3.connect("fifa.db")

try:
    team_stats = pd.read_sql_query("SELECT team, avg_goals_scored as avg_scored, avg_goals_conceded as avg_conceded FROM team_stats_final", conn)
except Exception:
    print("ERROR: 'team_stats_final' table not found.")
    print("Run: python build_features.py  first.")
    conn.close()
    raise SystemExit(1)

print(f"Computing clusters for {len(team_stats)} teams...")
print(f"\nSample team stats:")
print(team_stats.sort_values("avg_scored", ascending=False).head(10))

# ── Step 2: Scale features before clustering ──────────────────────────────────
# KMeans is distance-based, so we standardize both columns so neither
# dominates just because of scale differences.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(team_stats[["avg_scored", "avg_conceded"]])

# ── Step 3: Run KMeans with 4 clusters ───────────────────────────────────────
# n_init=10 means KMeans tries 10 different starting points and picks the best.
# random_state=42 for reproducibility.
kmeans = KMeans(n_clusters=4, n_init=10, random_state=42)
team_stats["cluster"] = kmeans.fit_predict(X_scaled)

# ── Step 4: Give each cluster a human-readable label ─────────────────────────
# Look at cluster centroids (in original scale) to name each group meaningfully
centroids = team_stats.groupby("cluster")[["avg_scored", "avg_conceded"]].mean()
print(f"\nCluster centroids (in original scale):")
print(centroids.round(2))

# Assign names based on centroids: high score/low concede = elite, etc.
def label_cluster(cluster_id):
    scored = centroids.loc[cluster_id, "avg_scored"]
    conceded = centroids.loc[cluster_id, "avg_conceded"]
    # Split on median scored and conceded values across all clusters
    med_scored = centroids["avg_scored"].median()
    med_conceded = centroids["avg_conceded"].median()

    if scored >= med_scored and conceded <= med_conceded:
        return "Elite (High Attack, Strong Defence)"
    elif scored >= med_scored and conceded > med_conceded:
        return "Attackers (High Scoring, Leaky Defence)"
    elif scored < med_scored and conceded <= med_conceded:
        return "Grinders (Low Scoring, Solid Defence)"
    else:
        return "Developing (Low Scoring, High Concede)"

team_stats["cluster_label"] = team_stats["cluster"].apply(label_cluster)

print("\nTeam cluster assignments:")
for label in team_stats["cluster_label"].unique():
    teams = team_stats[team_stats["cluster_label"] == label]["team"].tolist()
    print(f"\n  {label}:")
    print(f"    {', '.join(teams[:10])}{'...' if len(teams) > 10 else ''}")

# ── Step 5: Save to database ──────────────────────────────────────────────────
team_stats.to_sql("team_clusters", conn, if_exists="replace", index=False)
conn.close()

print(f"\n\nSaved 'team_clusters' table to fifa.db ({len(team_stats)} teams)")
print("Dashboard's Team Clusters tab is now ready.")
