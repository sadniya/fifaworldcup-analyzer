"""
train_model.py
--------------
Trains a Random Forest classifier to predict World Cup match outcomes
(Home Win / Draw / Away Win) using historical team stats as features.

Run this ONCE to generate model.pkl -- then the dashboard loads that file
for live predictions without retraining every time.

Usage:
    python train_model.py
"""

import pandas as pd
import sqlite3
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ── Step 1: Load the feature-engineered match data from the database ──────────
conn = sqlite3.connect("fifa.db")

# match_features was created by build_features.py
# It has avg goals scored/conceded per team + stage encoding
try:
    matches = pd.read_sql_query("SELECT * FROM match_features", conn)
except Exception:
    print("ERROR: 'match_features' table not found in fifa.db.")
    print("Please run: python build_features.py  -- then try again.")
    conn.close()
    raise SystemExit(1)

conn.close()
print(f"Loaded {len(matches)} matches from match_features table")

# ── Step 2: Create the target label (what we're predicting) ──────────────────
# For each match: did the home team win, draw, or lose?
def result_label(row):
    if row["home_goals"] > row["away_goals"]:
        return "Home Win"
    elif row["home_goals"] == row["away_goals"]:
        return "Draw"
    else:
        return "Away Win"

matches["result"] = matches.apply(result_label, axis=1)

print("\nResult distribution (what the model is predicting):")
print(matches["result"].value_counts())
print(f"\nTotal classes: {matches['result'].nunique()}")

# ── Step 3: Select features ───────────────────────────────────────────────────
# These 5 numbers are the INPUTS the model will use to make each prediction.
# Explanation:
#   home_avg_scored      -- how many goals the home team typically scores per match
#   home_avg_conceded    -- how many goals the home team typically lets in
#   away_avg_scored      -- same for the away team
#   away_avg_conceded    -- same for the away team
#   stage_encoded        -- how deep in the tournament (0=group, 4=final)
FEATURE_COLS = [
    "home_avg_scored",
    "home_avg_conceded",
    "away_avg_scored",
    "away_avg_conceded",
    "stage_encoded",
]

X = matches[FEATURE_COLS]
y = matches["result"]

# ── Step 4: Split into training and test sets ─────────────────────────────────
# 80% of matches used to TRAIN the model, 20% kept aside to TEST it honestly.
# random_state=42 just means the split is reproducible (same split every run).
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTraining on {len(X_train)} matches, testing on {len(X_test)} matches")

# ── Step 5: Train a Random Forest classifier ──────────────────────────────────
# Random Forest = many decision trees, each trained slightly differently,
# then they vote together. More robust than a single decision tree.
# n_estimators=100 means 100 trees vote on each prediction.
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("\nModel training complete.")

# ── Step 6: Evaluate honestly ─────────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"Model Accuracy: {acc:.1%}")
print(f"{'='*50}")
print("\nPer-class breakdown:")
print(classification_report(y_test, y_pred))

print(
    "\nNote: 55-65% accuracy is realistic for football prediction -- the sport "
    "is genuinely unpredictable. What matters for a portfolio is that you "
    "trained, evaluated, and deployed a model correctly."
)

# ── Step 7: Save the model to disk ───────────────────────────────────────────
joblib.dump(model, "model.pkl")
print("\nModel saved as: model.pkl")
print("The dashboard will load this file for live predictions.")

# ── Step 8: Save team stats to a separate file for the dashboard dropdown ────
# The dashboard needs to know which teams exist and their avg stats
# so users can pick them from a dropdown.
conn = sqlite3.connect("fifa.db")
team_stats = pd.read_sql_query(
    """
    SELECT
        home_team as team,
        AVG(home_avg_scored) as avg_scored,
        AVG(home_avg_conceded) as avg_conceded
    FROM match_features
    GROUP BY home_team
    ORDER BY home_team
    """,
    conn,
)
conn.close()

team_stats.to_csv("team_stats.csv", index=False)
print(f"Team stats saved: team_stats.csv ({len(team_stats)} teams)")
print("\nAll done. You can now run: python -m streamlit run dashboard.py")
