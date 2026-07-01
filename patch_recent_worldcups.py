"""
patch_recent_worldcups.py
-------------------------
Extracts 2018 and 2022 World Cup matches from the 'results' table
and appends them to the 'world_cup_matches' table in fifa.db.
"""

import sqlite3
import pandas as pd

print("Connecting to fifa.db...")
conn = sqlite3.connect("fifa.db")

# 1. Fetch recent World Cup matches from the general 'results' table
query = """
    SELECT 
        date, 
        home_team, 
        away_team, 
        home_score, 
        away_score, 
        city
    FROM results
    WHERE tournament = 'FIFA World Cup' 
      AND date > '2015-01-01'
"""
recent_matches = pd.read_sql_query(query, conn)

if len(recent_matches) == 0:
    print("⚠️ WARNING: Your results.csv stops at 2017. No 2018 or 2022 matches found.")
    print("Please download the updated 'International football results from 1872 to 2024' dataset from Kaggle.")
else:
    print(f"✅ Found {len(recent_matches)} recent World Cup matches in the results table!")
    
    # 2. Format them to match the structure of the world_cup_matches table
    # We have to extract the Year from the date string
    recent_matches['Year'] = pd.to_datetime(recent_matches['date']).dt.year
    
    # Rename columns to match what our other scripts expect
    formatted_matches = pd.DataFrame({
        'Year': recent_matches['Year'],
        'Datetime': recent_matches['date'],
        'Stage': 'Group/Knockout', # Simplified since results table doesn't have stage
        'Stadium': 'Unknown',
        'City': recent_matches['city'],
        'Home Team Name': recent_matches['home_team'],
        'Home Team Goals': recent_matches['home_score'],
        'Away Team Goals': recent_matches['away_score'],
        'Away Team Name': recent_matches['away_team'],
        'Attendance': 0,
        'Half-time Home Goals': 0,
        'Half-time Away Goals': 0,
        'Referee': 'Unknown',
        'Assistant 1': 'Unknown',
        'Assistant 2': 'Unknown',
        'RoundID': 0,
        'MatchID': 0,
        'Home Team Initials': recent_matches['home_team'].str[:3].str.upper(),
        'Away Team Initials': recent_matches['away_team'].str[:3].str.upper()
    })
    
    # 3. Check if we already appended them to avoid duplicates
    existing_years = pd.read_sql_query("SELECT DISTINCT Year FROM world_cup_matches", conn)
    
    if 2018 in existing_years['Year'].values or 2022 in existing_years['Year'].values:
        print("⏭️ Matches already patched in the database! Skipping insertion.")
    else:
        # Append to the existing world_cup_matches table
        formatted_matches.to_sql("world_cup_matches", conn, if_exists="append", index=False)
        print("🎉 Successfully added 2018 and 2022 matches to world_cup_matches table!")
        
        # Verify the new max year
        max_year = pd.read_sql_query("SELECT MAX(Year) as max_year FROM world_cup_matches", conn).iloc[0]['max_year']
        print(f"The latest World Cup in our database is now: {max_year}")

conn.close()
