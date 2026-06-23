import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Page config -- sets the browser tab title and layout
st.set_page_config(page_title="FIFA World Cup Analyzer", layout="wide")

st.title("FIFA World Cup Analyzer")
st.write("Exploring 90+ years of World Cup history using SQL + Python")

# Connect to our SQLite database
conn = sqlite3.connect("fifa.db")

# Section 1: Top scoring teams (World Cup only)
st.header("Top 10 Teams by Home Goals (World Cup matches)")

query_top_scorers = """
SELECT [Home Team Name] as team, SUM([Home Team Goals]) as total_home_goals
FROM world_cup_matches
GROUP BY [Home Team Name]
ORDER BY total_home_goals DESC
LIMIT 10
"""
top_scorers = pd.read_sql_query(query_top_scorers, conn)
st.dataframe(top_scorers)
# Bar chart: visualize the same data
fig_bar = px.bar(
    top_scorers,
    x="team",
    y="total_home_goals",
    title="Top 10 Teams by Home Goals (World Cup)",
    labels={"team": "Team", "total_home_goals": "Total Home Goals"},
)
st.plotly_chart(fig_bar, use_container_width=True)

# Section 2: Matches per World Cup year
st.header("Number of Matches per World Cup Year")

query_matches_per_year = """
SELECT Year as year, COUNT(*) as matches
FROM world_cup_matches
GROUP BY Year
ORDER BY Year
"""
matches_per_year = pd.read_sql_query(query_matches_per_year, conn)
st.dataframe(matches_per_year)
# Line chart: visualize the same data
fig_line = px.line(
    matches_per_year,
    x="year",
    y="matches",
    title="Number of World Cup Matches per Year",
    labels={"year": "Year", "matches": "Number of Matches"},
    markers=True,
)
st.plotly_chart(fig_line, use_container_width=True)
# Section 3: Average goals per match, per World Cup year
st.header("Average Goals per Match, by World Cup Year")
st.write("Has football become more attacking or more defensive over the decades?")

query_avg_goals = """
SELECT
    Year as year,
    AVG([Home Team Goals] + [Away Team Goals]) as avg_goals_per_match
FROM world_cup_matches
GROUP BY Year
ORDER BY Year
"""
avg_goals = pd.read_sql_query(query_avg_goals, conn)
st.dataframe(avg_goals)

fig_avg_goals = px.line(
    avg_goals,
    x="year",
    y="avg_goals_per_match",
    title="Average Goals per Match Across World Cup History",
    labels={"year": "Year", "avg_goals_per_match": "Avg Goals per Match"},
    markers=True,
)
st.plotly_chart(fig_avg_goals, use_container_width=True)

# Section 4: Most frequent World Cup matchups (rivalries)
st.header("Most Frequent World Cup Matchups")
st.write("Which two teams have faced each other the most times in World Cup history?")

query_rivalries = """
SELECT
    CASE WHEN [Home Team Name] < [Away Team Name]
         THEN [Home Team Name] ELSE [Away Team Name] END as team_a,
    CASE WHEN [Home Team Name] < [Away Team Name]
         THEN [Away Team Name] ELSE [Home Team Name] END as team_b,
    COUNT(*) as times_played
FROM world_cup_matches
GROUP BY team_a, team_b
ORDER BY times_played DESC
LIMIT 10
"""
rivalries = pd.read_sql_query(query_rivalries, conn)
st.dataframe(rivalries)

fig_rivalries = px.bar(
    rivalries,
    x="times_played",
    y=rivalries["team_a"] + " vs " + rivalries["team_b"],
    orientation="h",
    title="Top 10 Most Played World Cup Matchups",
    labels={"x": "Times Played", "y": "Matchup"},
)
st.plotly_chart(fig_rivalries, use_container_width=True)

conn.close()