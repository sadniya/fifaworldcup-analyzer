"""
dashboard.py
------------
FIFA World Cup Analyzer — Premium Dark Dashboard
Built with: SQLite · Streamlit · Plotly · scikit-learn

Run with:
    python -m streamlit run dashboard.py
"""

import sqlite3
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ─────────────────────────────────────────────────────────
# Split into font load + styles (Streamlit handles smaller blocks more reliably)
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

_CSS = """
<style>
html, body { font-family: 'Inter', sans-serif !important; }

[data-testid="stMetric"] {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 16px;
  padding: 20px 24px;
  transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(66,153,225,0.15);
  border-color: rgba(66,153,225,0.35);
}
[data-testid="stMetricLabel"] {
  color: #8ba3c0 !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] { color: #e8f1fd !important; font-weight: 700 !important; }

.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 9px !important;
  color: #8ba3c0 !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
}

.stButton > button {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 10px 28px !important;
  box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
  transition: all 0.25s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(37,99,235,0.55) !important;
}

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# ── Plotly dark chart defaults ────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
PRIMARY   = "#3b82f6"   # bright blue
SECONDARY = "#f59e0b"   # amber
ACCENT    = "#10b981"   # emerald green
COLORS_4  = ["#3b82f6", "#f59e0b", "#10b981", "#ec4899"]

# ── Database connection (shared across all tabs) ──────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("fifa.db", check_same_thread=False)

conn = get_conn()

@st.cache_data
def run_query(sql: str) -> pd.DataFrame:
    """Cache every SQL result so switching tabs doesn't re-query the database."""
    return pd.read_sql_query(sql, conn)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 8px 0 16px;'>
          <div style='font-size:2.4rem'>⚽</div>
          <div style='font-size:1.1rem; font-weight:700; color:#e8f1fd;'>FIFA World Cup</div>
          <div style='font-size:0.75rem; color:#8ba3c0; margin-top:2px;'>Historical Analyzer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption("📊 DATA COVERAGE")
    st.markdown(
        "<small style='color:#8ba3c0;'>World Cup matches: **1930–2014**<br>"
        "International matches: **1872–2017**</small>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption("🛠 TECH STACK")
    st.markdown(
        "<small style='color:#8ba3c0;'>SQLite · Pandas · Streamlit<br>"
        "Plotly · scikit-learn · KMeans</small>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption("⚡ LIVE TOURNAMENT")
    st.markdown(
        "<small style='color:#f59e0b;'>FIFA World Cup 2026<br>"
        "Jun 11 – Jul 19, 2026 🏆</small>",
        unsafe_allow_html=True,
    )

# ── Animated gradient header ─────────────────────────────────────────────────
st.markdown(
    """
    <div style='
        background: linear-gradient(135deg, #1e3a5f 0%, #1a2744 50%, #0f172a 100%);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 20px;
        padding: 36px 40px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    '>
      <div style='
          position:absolute; top:-40px; right:-40px;
          width:200px; height:200px;
          background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
          border-radius: 50%;
      '></div>
      <div style='display:flex; align-items:center; gap:16px; flex-wrap:wrap;'>
        <div>
          <div style='font-size:0.7rem; font-weight:600; color:#3b82f6; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;'>
            ⚡ World Cup 2026 Is Live Right Now
          </div>
          <h1 style='font-size:2rem; font-weight:800; color:#e8f1fd; margin:0; line-height:1.2;'>
            FIFA World Cup Analyzer
          </h1>
          <p style='color:#8ba3c0; margin:8px 0 0; font-size:0.95rem;'>
            90+ years of World Cup history · SQL · Machine Learning · Interactive Charts
          </p>
        </div>
        <div style='margin-left:auto;'>
          <div style='
              background: linear-gradient(135deg, #064e3b, #065f46);
              border: 1px solid rgba(16,185,129,0.4);
              border-radius: 10px; padding: 8px 16px; text-align:center;
          '>
            <div style='font-size:0.65rem; color:#6ee7b7; letter-spacing:0.1em; font-weight:600;'>DATASET</div>
            <div style='font-size:1.1rem; font-weight:700; color:#10b981;'>4,572 Matches</div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 8 navigation tabs ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏆 Overview",
    "⚽ Top Scorers",
    "📈 Trends",
    "🔥 Rivalries",
    "🤖 Match Predictor",
    "🎯 Team Clusters",
    "📰 Sentiment",
    "💬 Ask the Data",
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    stats = run_query(
        """
        SELECT
            COUNT(*) as total_matches,
            MIN(Year) as first_year,
            MAX(Year) as last_year,
            SUM([Home Team Goals] + [Away Team Goals]) as total_goals,
            COUNT(DISTINCT [Home Team Name]) as total_teams
        FROM world_cup_matches
        """
    )
    row = stats.iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⚽ Total Matches",  f"{int(row['total_matches']):,}")
    c2.metric("🥅 Goals Scored",   f"{int(row['total_goals']):,}")
    c3.metric("🏟 First World Cup", int(row["first_year"]))
    c4.metric("📅 Latest in Data", int(row["last_year"]))
    c5.metric("🌍 Teams Ever",     int(row["total_teams"]))

    st.markdown("---")

    # Goals per match across all years — mini sparkline
    gpm = run_query(
        """
        SELECT Year as year,
               ROUND(AVG([Home Team Goals] + [Away Team Goals]), 2) as avg_goals
        FROM world_cup_matches
        GROUP BY Year ORDER BY Year
        """
    )

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig_spark = go.Figure()
        fig_spark.add_trace(go.Scatter(
            x=gpm["year"], y=gpm["avg_goals"],
            mode="lines+markers",
            line=dict(color=PRIMARY, width=3),
            marker=dict(size=7, color=PRIMARY, line=dict(color="white", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.12)",
            hovertemplate="<b>%{x}</b><br>Avg goals: %{y}<extra></extra>",
        ))
        fig_spark.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=dict(text="Average Goals per Match — All Tournaments", font=dict(size=14, color="#e8f1fd")),
            height=280,
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(title="", showgrid=False, color="#8ba3c0"),
            yaxis=dict(title="Goals / Match", gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
        )
        st.plotly_chart(fig_spark, use_container_width=True)

    with col_b:
        st.markdown(
            """
            <div style='background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                        border-radius:14px; padding:20px;'>
              <div style='font-size:0.8rem; color:#8ba3c0; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:12px;'>
                About this project
              </div>
              <p style='color:#c9d8ee; font-size:0.87rem; line-height:1.6; margin:0;'>
                Built alongside the live <strong style='color:#f59e0b;'>FIFA World Cup 2026</strong> tournament.<br><br>
                Explores 84 years of World Cup history using real SQL queries,
                interactive Plotly charts, a trained <strong style='color:#3b82f6;'>Random Forest model</strong>
                for match prediction, and <strong style='color:#10b981;'>KMeans clustering</strong>
                to group teams by playing style.
              </p>
              <div style='margin-top:16px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08);'>
                <div style='font-size:0.7rem; color:#ef4444; font-weight:600;'>⚠ DATA NOTE</div>
                <div style='font-size:0.78rem; color:#8ba3c0; margin-top:4px;'>
                  Dataset covers 1930–2014. Does not include 2018 or 2022 tournaments.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — TOP SCORERS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Top 15 Teams by Total Goals Scored (World Cup History)")
    st.caption("Combines both home and away goals — a team's goals scored regardless of which side they played on.")

    top_teams = run_query(
        """
        SELECT team, SUM(goals) as total_goals, SUM(matches) as matches_played,
               ROUND(CAST(SUM(goals) AS FLOAT) / SUM(matches), 2) as goals_per_match
        FROM (
            SELECT [Home Team Name] as team, SUM([Home Team Goals]) as goals, COUNT(*) as matches
            FROM world_cup_matches GROUP BY [Home Team Name]
            UNION ALL
            SELECT [Away Team Name] as team, SUM([Away Team Goals]) as goals, COUNT(*) as matches
            FROM world_cup_matches GROUP BY [Away Team Name]
        )
        GROUP BY team
        ORDER BY total_goals DESC
        LIMIT 15
        """
    )

    col_chart, col_info = st.columns([3, 1])
    with col_chart:
        fig_top = px.bar(
            top_teams, x="total_goals", y="team",
            orientation="h",
            color="goals_per_match",
            color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#3b82f6"], [1, "#93c5fd"]],
            labels={"total_goals": "Total Goals", "team": "", "goals_per_match": "Goals/Match"},
            template=PLOTLY_TEMPLATE,
            text="total_goals",
        )
        fig_top.update_traces(
            textposition="outside",
            textfont=dict(color="#e8f1fd", size=11),
            hovertemplate="<b>%{y}</b><br>Total goals: %{x}<br>Goals/match: %{marker.color:.2f}<extra></extra>",
        )
        fig_top.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=480, margin=dict(l=0, r=60, t=10, b=0),
            yaxis=dict(autorange="reversed", color="#c9d8ee"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
            coloraxis_colorbar=dict(title="Goals/Match", tickfont=dict(color="#8ba3c0")),
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_info:
        st.dataframe(
            top_teams[["team", "total_goals", "goals_per_match"]].rename(
                columns={"team": "Team", "total_goals": "Goals", "goals_per_match": "Per Match"}
            ),
            use_container_width=True, hide_index=True, height=480,
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRENDS
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### How Has the World Cup Changed Over the Decades?")

    trends = run_query(
        """
        SELECT
            Year as year,
            COUNT(*) as matches,
            ROUND(AVG([Home Team Goals] + [Away Team Goals]), 2) as avg_goals,
            SUM([Home Team Goals] + [Away Team Goals]) as total_goals,
            COUNT(DISTINCT [Home Team Name]) as teams
        FROM world_cup_matches
        GROUP BY Year ORDER BY Year
        """
    )

    col_l, col_r = st.columns(2)

    with col_l:
        fig_matches = go.Figure()
        fig_matches.add_trace(go.Bar(
            x=trends["year"], y=trends["matches"],
            name="Matches played",
            marker_color=PRIMARY,
            opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Matches: %{y}<extra></extra>",
        ))
        fig_matches.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title=dict(text="Matches Played per Tournament", font=dict(color="#e8f1fd", size=13)),
            height=300, margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(color="#8ba3c0"), yaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
            showlegend=False,
        )
        st.plotly_chart(fig_matches, use_container_width=True)

    with col_r:
        fig_goals = go.Figure()
        fig_goals.add_trace(go.Scatter(
            x=trends["year"], y=trends["avg_goals"],
            mode="lines+markers",
            name="Avg goals/match",
            line=dict(color=SECONDARY, width=3),
            marker=dict(size=8, color=SECONDARY, line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.1)",
            hovertemplate="<b>%{x}</b><br>Avg goals: %{y}<extra></extra>",
        ))
        fig_goals.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title=dict(text="Average Goals per Match Over Time", font=dict(color="#e8f1fd", size=13)),
            height=300, margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(color="#8ba3c0"), yaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
            showlegend=False,
        )
        st.plotly_chart(fig_goals, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📊 Full Numbers by Tournament Year")
    st.dataframe(
        trends.rename(columns={
            "year": "Year", "matches": "Matches", "avg_goals": "Avg Goals/Match",
            "total_goals": "Total Goals", "teams": "Teams",
        }),
        use_container_width=True, hide_index=True,
    )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — RIVALRIES
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔥 Most Frequent World Cup Rivalries")
    st.caption("Matchups sorted by number of times these two teams have met in World Cup competition.")

    rivalries = run_query(
        """
        SELECT
            CASE WHEN [Home Team Name] < [Away Team Name]
                 THEN [Home Team Name] ELSE [Away Team Name] END as team_a,
            CASE WHEN [Home Team Name] < [Away Team Name]
                 THEN [Away Team Name] ELSE [Home Team Name] END as team_b,
            COUNT(*) as times_played,
            SUM(CASE WHEN [Home Team Goals] > [Away Team Goals] THEN 1 ELSE 0 END) as home_wins,
            SUM(CASE WHEN [Home Team Goals] = [Away Team Goals] THEN 1 ELSE 0 END) as draws,
            SUM(CASE WHEN [Home Team Goals] < [Away Team Goals] THEN 1 ELSE 0 END) as away_wins
        FROM world_cup_matches
        GROUP BY team_a, team_b
        ORDER BY times_played DESC
        LIMIT 12
        """
    )
    rivalries["matchup"] = rivalries["team_a"] + " vs " + rivalries["team_b"]

    col_chart, col_breakdown = st.columns([3, 2])
    with col_chart:
        fig_riv = px.bar(
            rivalries, x="times_played", y="matchup",
            orientation="h",
            color_discrete_sequence=[PRIMARY],
            template=PLOTLY_TEMPLATE,
            labels={"times_played": "Times Played", "matchup": ""},
            text="times_played",
        )
        fig_riv.update_traces(
            textposition="outside",
            textfont=dict(color="#e8f1fd", size=11),
            marker_color=PRIMARY,
            hovertemplate="<b>%{y}</b><br>Meetings: %{x}<extra></extra>",
        )
        fig_riv.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=450, margin=dict(l=0, r=60, t=10, b=0),
            yaxis=dict(autorange="reversed", color="#c9d8ee"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
        )
        st.plotly_chart(fig_riv, use_container_width=True)

    with col_breakdown:
        st.markdown("##### Win / Draw / Loss breakdown")
        for _, r in rivalries.head(8).iterrows():
            total = r["times_played"]
            hw = int(r["home_wins"])
            d  = int(r["draws"])
            aw = int(r["away_wins"])
            # The team listed first alphabetically is "team_a"
            ta, tb = r["team_a"], r["team_b"]
            pct_a = round(hw / total * 100)
            pct_d = round(d  / total * 100)
            pct_b = round(aw / total * 100)
            st.markdown(
                f"""
                <div style='margin-bottom:10px; background:rgba(255,255,255,0.04);
                            border-radius:10px; padding:10px 14px;'>
                  <div style='font-size:0.78rem; font-weight:600; color:#e8f1fd; margin-bottom:6px;'>
                    {ta} <span style='color:#8ba3c0;'>vs</span> {tb}
                  </div>
                  <div style='display:flex; border-radius:6px; overflow:hidden; height:12px;'>
                    <div style='width:{pct_a}%; background:#3b82f6;'></div>
                    <div style='width:{pct_d}%; background:#6b7280;'></div>
                    <div style='width:{pct_b}%; background:#f59e0b;'></div>
                  </div>
                  <div style='display:flex; justify-content:space-between; font-size:0.68rem; color:#8ba3c0; margin-top:4px;'>
                    <span style='color:#3b82f6;'>{ta[:3].upper()} {hw}W</span>
                    <span>{d}D</span>
                    <span style='color:#f59e0b;'>{aw}W {tb[:3].upper()}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — MATCH PREDICTOR
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🤖 Match Outcome Predictor")
    st.caption(
        "Random Forest model trained on 1930–2014 World Cup historical data. "
        "Predictions are based on each team's historical scoring and conceding averages."
    )

    # Load model and team stats
    model_ready = False
    try:
        model = joblib.load("model.pkl")
        team_stats_df = pd.read_csv("team_stats.csv")
        all_teams = sorted(team_stats_df["team"].dropna().unique().tolist())
        model_ready = True
    except FileNotFoundError:
        st.warning(
            "⚠️ Model not trained yet. Run these two commands in your terminal first:\n\n"
            "```\npython build_features.py\npython train_model.py\n```\n\n"
            "Then refresh this page."
        )

    if model_ready:
        STAGE_MAP = {
            "Group Stage": 0,
            "Round of 16": 1,
            "Quarterfinal": 2,
            "Semifinal": 3,
            "Final": 4,
        }

        col_home, col_vs, col_away = st.columns([2, 0.5, 2])
        with col_home:
            st.markdown("**🏠 Home Team**")
            home_team = st.selectbox("Select home team", all_teams, index=all_teams.index("Brazil") if "Brazil" in all_teams else 0, key="home_team_sel", label_visibility="collapsed")
        with col_vs:
            st.markdown("<div style='text-align:center; padding-top:32px; font-size:1.3rem; color:#8ba3c0; font-weight:700;'>VS</div>", unsafe_allow_html=True)
        with col_away:
            st.markdown("**✈️ Away Team**")
            default_away = "Germany" if "Germany" in all_teams else (all_teams[1] if len(all_teams) > 1 else all_teams[0])
            away_team = st.selectbox("Select away team", all_teams, index=all_teams.index(default_away), key="away_team_sel", label_visibility="collapsed")

        stage = st.selectbox("🏟️ Match Stage", list(STAGE_MAP.keys()), index=4)

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            predict_clicked = st.button("⚡ Predict Outcome", use_container_width=True)

        if predict_clicked:
            if home_team == away_team:
                st.error("Please select two different teams.")
            else:
                home_row = team_stats_df[team_stats_df["team"] == home_team].iloc[0]
                away_row = team_stats_df[team_stats_df["team"] == away_team].iloc[0]

                features = pd.DataFrame([{
                    "home_avg_scored":    home_row["avg_scored"],
                    "home_avg_conceded":  home_row["avg_conceded"],
                    "away_avg_scored":    away_row["avg_scored"],
                    "away_avg_conceded":  away_row["avg_conceded"],
                    "stage_encoded":      STAGE_MAP[stage],
                }])

                proba = model.predict_proba(features)[0]
                classes = model.classes_
                prob_dict = dict(zip(classes, proba))

                home_win_p = prob_dict.get("Home Win", 0)
                draw_p     = prob_dict.get("Draw", 0)
                away_win_p = prob_dict.get("Away Win", 0)
                predicted  = max(prob_dict, key=prob_dict.get)

                # Result banner
                color_map = {"Home Win": "#3b82f6", "Draw": "#6b7280", "Away Win": "#f59e0b"}
                st.markdown(
                    f"""
                    <div style='
                        background: linear-gradient(135deg, {color_map[predicted]}22, {color_map[predicted]}11);
                        border: 1px solid {color_map[predicted]}66;
                        border-radius: 16px; padding: 24px 32px; margin: 20px 0; text-align:center;
                    '>
                      <div style='font-size:0.75rem; color:#8ba3c0; letter-spacing:0.12em; text-transform:uppercase; font-weight:600;'>
                        Predicted Result
                      </div>
                      <div style='font-size:2rem; font-weight:800; color:{color_map[predicted]}; margin:8px 0;'>
                        {predicted}
                      </div>
                      <div style='font-size:0.9rem; color:#c9d8ee;'>
                        {home_team} {'wins' if predicted == 'Home Win' else ('draws with' if predicted == 'Draw' else 'loses to')} {away_team}
                        &nbsp;&middot;&nbsp; {stage}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Probability bars
                st.markdown("#### Probability breakdown")
                results_data = {
                    "Outcome": [f"🏠 {home_team} Win", "🤝 Draw", f"✈️ {away_team} Win"],
                    "Probability": [home_win_p, draw_p, away_win_p],
                    "Color": ["#3b82f6", "#6b7280", "#f59e0b"],
                }
                fig_prob = go.Figure()
                for outcome, prob, col in zip(results_data["Outcome"], results_data["Probability"], results_data["Color"]):
                    fig_prob.add_trace(go.Bar(
                        x=[prob], y=[outcome],
                        orientation="h",
                        marker_color=col,
                        text=f"{prob:.1%}",
                        textposition="outside",
                        textfont=dict(color="#e8f1fd", size=13, family="Inter"),
                        hovertemplate=f"<b>{outcome}</b>: {prob:.1%}<extra></extra>",
                    ))
                fig_prob.update_layout(
                    template=PLOTLY_TEMPLATE,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False, height=200,
                    margin=dict(l=0, r=80, t=0, b=0),
                    xaxis=dict(range=[0, 1], tickformat=".0%", gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
                    yaxis=dict(color="#c9d8ee"),
                    barmode="overlay",
                )
                st.plotly_chart(fig_prob, use_container_width=True)

                # Team stat comparison
                st.markdown("#### Team stat comparison")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(f"{home_team} — Avg Goals Scored",   f"{home_row['avg_scored']:.2f}")
                    st.metric(f"{home_team} — Avg Goals Conceded", f"{home_row['avg_conceded']:.2f}")
                with c2:
                    st.metric(f"{away_team} — Avg Goals Scored",   f"{away_row['avg_scored']:.2f}")
                    st.metric(f"{away_team} — Avg Goals Conceded", f"{away_row['avg_conceded']:.2f}")

                st.info(
                    "ℹ️ This model was trained on 1930–2014 World Cup data using each team's historical "
                    "scoring and conceding averages as features. Accuracy is ~55–65%, which is realistic "
                    "for football — the sport is inherently unpredictable. The value here is in correctly "
                    "building, training, evaluating, and deploying a classification model."
                )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 — TEAM CLUSTERS
# ════════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### 🎯 Team Playing Style Clusters (KMeans)")
    st.caption(
        "Teams grouped by playing style using KMeans clustering on two dimensions: "
        "average goals scored (attacking) vs average goals conceded (defensive). "
        "4 clusters emerge naturally."
    )

    clusters_ready = False
    try:
        cluster_df = run_query("SELECT * FROM team_clusters")
        clusters_ready = True
    except Exception:
        st.warning(
            "⚠️ Cluster data not generated yet. Run in your terminal:\n\n"
            "```\npython build_features.py\npython cluster_teams.py\n```\n\nThen refresh."
        )

    if clusters_ready:
        # Map numeric cluster to label if needed
        if "cluster_label" not in cluster_df.columns:
            cluster_df["cluster_label"] = "Cluster " + cluster_df["cluster"].astype(str)

        fig_clusters = px.scatter(
            cluster_df,
            x="avg_scored",
            y="avg_conceded",
            color="cluster_label",
            text="team",
            color_discrete_sequence=COLORS_4,
            template=PLOTLY_TEMPLATE,
            labels={
                "avg_scored": "Avg Goals Scored per Match (Attacking)",
                "avg_conceded": "Avg Goals Conceded per Match (Defensive)",
                "cluster_label": "Playing Style",
            },
            hover_data={"avg_scored": ":.2f", "avg_conceded": ":.2f", "team": True},
        )
        fig_clusters.update_traces(
            textposition="top center",
            textfont=dict(size=9, color="rgba(255,255,255,0.6)"),
            marker=dict(size=10, line=dict(width=1.2, color="rgba(255,255,255,0.3)")),
        )
        fig_clusters.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=550,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0", zeroline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0", zeroline=False),
            legend=dict(
                bgcolor="rgba(255,255,255,0.04)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(color="#c9d8ee"),
            ),
        )
        st.plotly_chart(fig_clusters, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Teams by Cluster")
        for label in sorted(cluster_df["cluster_label"].unique()):
            teams_in = cluster_df[cluster_df["cluster_label"] == label]["team"].sort_values().tolist()
            with st.expander(f"**{label}** — {len(teams_in)} teams"):
                st.write(", ".join(teams_in))
    


    # ════════════════════════════════════════════════════════════════════════════════
# TAB 7 — SENTIMENT ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown("### 📰 Match Commentary Sentiment")
    st.caption("NLP analysis of iconic World Cup matches using TextBlob. Matches are scored from -1 (Negative) to +1 (Positive).")

    try:
        sentiment_df = run_query("SELECT * FROM match_commentary")
        
        # Sort by polarity (most positive first)
        sentiment_df = sentiment_df.sort_values(by="polarity", ascending=True)

        col_chart, col_data = st.columns([2, 1])

        with col_chart:
            # Create a color map based on sentiment
            color_map = {
                "Thrilling / Positive": "#10b981", # Green
                "Negative / Controversial": "#ef4444", # Red
                "Neutral / Mixed": "#6b7280" # Gray
            }
            
            fig_sent = px.bar(
                sentiment_df,
                x="polarity", 
                y="match",
                orientation="h",
                color="sentiment_category",
                color_discrete_map=color_map,
                template=PLOTLY_TEMPLATE,
                labels={"polarity": "Sentiment Score", "match": ""}
            )
            fig_sent.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=450, margin=dict(l=0, r=20, t=10, b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#8ba3c0"),
                yaxis=dict(color="#c9d8ee"),
                legend=dict(title="")
            )
            st.plotly_chart(fig_sent, use_container_width=True)

        with col_data:
            st.markdown("#### The Commentary")
            # Show the raw text so users can see WHY a match got its score
            for _, row in sentiment_df.sort_values(by="polarity", ascending=False).iterrows():
                st.markdown(f"**{row['match']}** ({row['year']})")
                st.markdown(f"<i style='color:#8ba3c0;'>\"{row['commentary']}\"</i>", unsafe_allow_html=True)
                st.markdown("---")

    except Exception:
        st.warning("⚠️ Run `python generate_sentiment.py` in the terminal first to analyze the text.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 8 — ASK THE DATA (NATURAL LANGUAGE TO SQL)
# ════════════════════════════════════════════════════════════════════════════════
with tab8:
    st.markdown("### 💬 Ask the Data")
    st.caption("Ask a question in plain English. The app will parse your intent and translate it into a SQL query.")

    # 1. Get the user's question
    question = st.text_input("Type your question (e.g., 'Who hosted the most matches?', 'Who are the biggest rivals?', 'How many goals did teams score?')")

    if question:
        question_lower = question.lower()
        
        # 2. Intent Parsing: Look for keywords to figure out what they want
        if "host" in question_lower or "city" in question_lower:
            st.info("💡 **Intent Detected:** You are asking about hosts or cities.")
            
            # Show them the SQL we are going to run
            sql = "SELECT City, COUNT(*) as matches_hosted FROM world_cup_matches GROUP BY City ORDER BY matches_hosted DESC LIMIT 10"
            # st.code(sql, language="sql")
            
            # Run it and show the result
            answer_df = run_query(sql)
            st.dataframe(answer_df, hide_index=True)

        elif "rival" in question_lower or "against" in question_lower or "face" in question_lower:
            st.info("💡 **Intent Detected:** You are asking about frequent matchups/rivalries.")
            sql = """
            SELECT
                CASE WHEN [Home Team Name] < [Away Team Name] THEN [Home Team Name] ELSE [Away Team Name] END as team_a,
                CASE WHEN [Home Team Name] < [Away Team Name] THEN [Away Team Name] ELSE [Home Team Name] END as team_b,
                COUNT(*) as times_played
            FROM world_cup_matches
            GROUP BY team_a, team_b
            ORDER BY times_played DESC
            LIMIT 10
            """
            # st.code(sql, language="sql")
            answer_df = run_query(sql)
            st.dataframe(answer_df, hide_index=True)

        elif "goal" in question_lower or "score" in question_lower or "top" in question_lower:
            st.info("💡 **Intent Detected:** You are asking about goals or top scoring teams.")
            sql = """
            SELECT [Home Team Name] as team, SUM([Home Team Goals]) as total_home_goals
            FROM world_cup_matches
            GROUP BY [Home Team Name]
            ORDER BY total_home_goals DESC
            LIMIT 10
            """
            # st.code(sql, language="sql")
            answer_df = run_query(sql)
            st.dataframe(answer_df, hide_index=True)
            
        else:
            # Fallback if we don't understand the question
            st.warning("I couldn't quite understand that question. Try asking about 'hosts', 'rivals', or 'goals'.")