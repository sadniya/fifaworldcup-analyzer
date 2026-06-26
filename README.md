# FIFA World Cup Analyzer

Exploring 90+ years of FIFA World Cup history using SQL, Python, and interactive visualizations.

Built as a learning project to practice SQL, data analysis, and dashboard development -- timed alongside the FIFA World Cup 2026 tournament.

## Progress

**Before** -- initial working dashboard, all sections stacked vertically:

![Before](screenshots/before_v1_dashboard.png)

**After** -- added sidebar navigation, side-by-side layouts, headline metrics, and a consistent color theme:

![After - Overview](screenshots/after_v2_overview.png)
![After - Rivalries](screenshots/after_v2_rivalries.png)

## What it does

- Loads historical football match data into a SQLite database
- Runs SQL queries to answer real questions about World Cup history:
  - Which teams have scored the most goals?
  - How has the average number of goals per match changed over the decades?
  - Which two teams have faced each other most often in World Cup history?
  - How many matches were played in each tournament year?
- Visualizes the results in an interactive Streamlit dashboard using Plotly charts

## Tech stack

- Python -- pandas for data loading and cleaning
- SQLite -- lightweight SQL database, no server required
- Streamlit -- web dashboard framework
- Plotly -- interactive charts

## Data sources

This project uses two public Kaggle datasets:

1. International football results, 1872-2017: https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017
2. FIFA World Cup dataset: https://www.kaggle.com/datasets/abecklas/fifa-world-cup

Known data limitation: the World Cup matches dataset stops at 2014. It does not include the 2018 or 2022 tournaments, since the original dataset predates them.

## Setup instructions

1. Clone this repo:
   git clone https://github.com/sadniya/fifaworldcup-analyzer.git
   cd fifaworldcup-analyzer

2. Install dependencies:
   pip install pandas streamlit plotly

3. Download the two datasets linked above from Kaggle, and place them in this structure:
   results.csv/results.csv
   worldcup.csv/WorldCupMatches.csv

4. Build the SQLite database:
   python build_database.py

5. Run the dashboard:
   python -m streamlit run dashboard.py

6. Open the URL shown in the terminal (usually http://localhost:8501) in your browser.

## Project structure

build_database.py -- loads CSVs into a SQLite database (fifa.db)
sql_queries.py -- standalone exploratory SQL queries (terminal output)
dashboard.py -- the Streamlit + Plotly dashboard
explore_data.py -- initial data exploration script

## What I learned

- Writing SQL queries with GROUP BY, aggregate functions, and CASE WHEN logic
- Loading pandas DataFrames into a SQL database with to_sql()
- Building an interactive dashboard with Streamlit
- Creating charts with Plotly Express
- Handling real-world messy data (missing values, inconsistent team names like Germany vs Germany FR)

## Roadmap / next steps

- Migrate from SQLite to PostgreSQL
- Add a goal prediction model trained on historical data
- Add team clustering (playing style similarity) using KMeans
- Add sentiment analysis on World Cup news/social commentary
- Patch the 2018/2022 data gap

