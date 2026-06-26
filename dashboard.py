import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup Analyzer",
    layout="wide",
    page_icon="⚽",
)

# A consistent color theme used across every chart in this app
THEME_COLOR = "#2E5EAA"      # deep blue -- primary bars/lines
THEME_COLOR_2 = "#E8A33D"    # warm amber -- secondary accents
CHART_TEMPLATE = "plotly_white"

# ── Sidebar navigation ───────────────────────────────────────
st.sidebar.title("⚽ FIFA World Cup Analyzer")
st.sidebar.write("Exploring 90+ years of World Cup history using SQL + Python")
section = st.sidebar.radio(
    "Jump to section:",
    [
        "Overview",
        "Top Scoring Teams",
        "Matches per Year",
        "Goals per Match Trend",
        "Biggest Rivalries",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: Kaggle World Cup datasets (1930-2014). "
    "Built with SQLite + Streamlit + Plotly."
)

# ── Connect to database (shared across all sections) ────────
conn = sqlite3.connect("fifa.db")


@st.cache_data
def run_query(query):
    """Cache query results so switching sections doesn't re-hit the database every time."""
    return pd.read_sql_query(query, conn)


# ── Overview section: headline metrics ───────────────────────
if section == "Overview":
    st.title("FIFA World Cup Analyzer")
    st.write(
        "A look at 90+ years of World Cup history, built with SQL, Streamlit, and Plotly."
    )

    overview_stats = run_query(
        """
        SELECT
            COUNT(*) as total_matches,
            MIN(Year) as first_year,
            MAX(Year) as last_year,
            SUM([Home Team Goals] + [Away Team Goals]) as total_goals
        FROM world_cup_matches
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Matches", f"{int(overview_stats['total_matches'][0]):,}")
    col2.metric("Total Goals Scored", f"{int(overview_stats['total_goals'][0]):,}")
    col3.metric("First World Cup", int(overview_stats["first_year"][0]))
    col4.metric("Most Recent (in data)", int(overview_stats["last_year"][0]))

    st.markdown("---")
    st.write(
        "Use the sidebar to explore top scoring teams, how the game has changed "
        "over the decades, and the most frequent World Cup rivalries."
    )
    st.info(
        "**Known data limitation:** this dataset covers 1930-2014. "
        "The 2018 and 2022 World Cups are not included."
    )

# ── Section: Top Scoring Teams ───────────────────────────────
elif section == "Top Scoring Teams":
    st.header("Top 10 Teams by Home Goals (World Cup matches)")

    top_scorers = run_query(
        """
        SELECT [Home Team Name] as team, SUM([Home Team Goals]) as total_home_goals
        FROM world_cup_matches
        GROUP BY [Home Team Name]
        ORDER BY total_home_goals DESC
        LIMIT 10
        """
    )

    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        fig_bar = px.bar(
            top_scorers,
            x="team",
            y="total_home_goals",
            labels={"team": "Team", "total_home_goals": "Total Home Goals"},
            color_discrete_sequence=[THEME_COLOR],
            template=CHART_TEMPLATE,
        )
        fig_bar.update_layout(margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.dataframe(top_scorers, use_container_width=True, hide_index=True)

# ── Section: Matches per Year ─────────────────────────────────
elif section == "Matches per Year":
    st.header("Number of Matches per World Cup Year")

    matches_per_year = run_query(
        """
        SELECT Year as year, COUNT(*) as matches
        FROM world_cup_matches
        GROUP BY Year
        ORDER BY Year
        """
    )

    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        fig_line = px.line(
            matches_per_year,
            x="year",
            y="matches",
            labels={"year": "Year", "matches": "Number of Matches"},
            markers=True,
            color_discrete_sequence=[THEME_COLOR],
            template=CHART_TEMPLATE,
        )
        fig_line.update_layout(margin=dict(t=20))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_table:
        st.dataframe(matches_per_year, use_container_width=True, hide_index=True)

# ── Section: Goals per Match Trend ────────────────────────────
elif section == "Goals per Match Trend":
    st.header("Average Goals per Match, by World Cup Year")
    st.write("Has football become more attacking or more defensive over the decades?")

    avg_goals = run_query(
        """
        SELECT
            Year as year,
            AVG([Home Team Goals] + [Away Team Goals]) as avg_goals_per_match
        FROM world_cup_matches
        GROUP BY Year
        ORDER BY Year
        """
    )

    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        fig_avg_goals = px.line(
            avg_goals,
            x="year",
            y="avg_goals_per_match",
            labels={"year": "Year", "avg_goals_per_match": "Avg Goals per Match"},
            markers=True,
            color_discrete_sequence=[THEME_COLOR_2],
            template=CHART_TEMPLATE,
        )
        fig_avg_goals.update_layout(margin=dict(t=20))
        st.plotly_chart(fig_avg_goals, use_container_width=True)

    with col_table:
        st.dataframe(avg_goals, use_container_width=True, hide_index=True)

# ── Section: Biggest Rivalries ────────────────────────────────
elif section == "Biggest Rivalries":
    st.header("Most Frequent World Cup Matchups")
    st.write("Which two teams have faced each other the most times in World Cup history?")

    rivalries = run_query(
        """
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
    )

    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        fig_rivalries = px.bar(
            rivalries,
            x="times_played",
            y=rivalries["team_a"] + " vs " + rivalries["team_b"],
            orientation="h",
            labels={"x": "Times Played", "y": "Matchup"},
            color_discrete_sequence=[THEME_COLOR],
            template=CHART_TEMPLATE,
        )
        fig_rivalries.update_layout(margin=dict(t=20), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_rivalries, use_container_width=True)

    with col_table:
        st.dataframe(rivalries, use_container_width=True, hide_index=True)

conn.close()