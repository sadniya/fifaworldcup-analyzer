import pandas as pd
import sqlite3

# Step 1: Load the CSVs we already explored
results = pd.read_csv("results.csv/results.csv")
wc = pd.read_csv("worldcup.csv/WorldCupMatches.csv")

# Step 2: Clean up WorldCupMatches a bit before saving
# Some rows in this dataset are blank/NaN (formatting artifacts from the original file)
# We drop rows where Year is missing, since a match with no year is unusable
wc = wc.dropna(subset=["Year"])

# Step 3: Connect to (or create) a SQLite database file
# This single .db file IS your SQL database -- no server needed
conn = sqlite3.connect("fifa.db")

# Step 4: Write each DataFrame into the database as a table
results.to_sql("results", conn, if_exists="replace", index=False)
wc.to_sql("world_cup_matches", conn, if_exists="replace", index=False)

print("Database created: fifa.db")
print("Tables created: 'results' and 'world_cup_matches'")

# Step 5: Quick sanity check -- run a real SQL query against it
check = pd.read_sql_query("SELECT COUNT(*) as total_matches FROM world_cup_matches", conn)
print("\nSanity check -- total World Cup matches in DB:")
print(check)

conn.close()