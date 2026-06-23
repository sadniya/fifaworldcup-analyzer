import pandas as pd
import sqlite3

conn = sqlite3.connect("fifa.db")

# Query 1: Which countries have hosted the most World Cup matches?
print("=" * 50)
print("Query 1: Top 10 host cities by number of matches")
print("=" * 50)
q1 = """
SELECT City, COUNT(*) as matches_hosted
FROM world_cup_matches
GROUP BY City
ORDER BY matches_hosted DESC
LIMIT 10
"""
print(pd.read_sql_query(q1, conn))

# Query 2: Which teams have scored the most goals as the home team?
print("\n" + "=" * 50)
print("Query 2: Top 10 teams by home goals scored")
print("=" * 50)
q2 = """
SELECT [Home Team Name], SUM([Home Team Goals]) as total_home_goals
FROM world_cup_matches
GROUP BY [Home Team Name]
ORDER BY total_home_goals DESC
LIMIT 10
"""
print(pd.read_sql_query(q2, conn))

# Query 3: How many World Cup matches happened per decade?
print("\n" + "=" * 50)
print("Query 3: Matches per World Cup year")
print("=" * 50)
q3 = """
SELECT Year, COUNT(*) as matches_that_year
FROM world_cup_matches
GROUP BY Year
ORDER BY Year
"""
print(pd.read_sql_query(q3, conn))

# Query 4: Using the bigger 'results' table -- all-time top scoring home teams
# (this table covers ALL international matches, not just World Cup)
print("\n" + "=" * 50)
print("Query 4: Top 10 teams by home goals, ALL international matches")
print("=" * 50)
q4 = """
SELECT home_team, SUM(home_score) as total_home_goals, COUNT(*) as matches_played
FROM results
GROUP BY home_team
ORDER BY total_home_goals DESC
LIMIT 10
"""
print(pd.read_sql_query(q4, conn))

conn.close()