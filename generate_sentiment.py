"""
generate_sentiment.py
---------------------
Creates a mini-dataset of iconic World Cup match reviews and uses 
the TextBlob NLP library to calculate their sentiment (polarity).

Polarity goes from -1.0 (very negative) to 1.0 (very positive).
The results are saved to the SQLite database (team_clusters table was last week,
this week it's match_commentary).

Run this ONCE before updating the dashboard:
    python generate_sentiment.py
"""

import pandas as pd
import sqlite3
from textblob import TextBlob

# ── Step 1: Create our mock commentary dataset ────────────────────────────────
# These are iconic matches in World Cup history with descriptions 
# mimicking sports journalism.
data = [
    {
        "year": 1950, "match": "Uruguay vs Brazil", 
        "commentary": "An absolute shocker! The Maracanazo is a tragedy for Brazil. A devastating and heartbreaking loss on home soil."
    },
    {
        "year": 1954, "match": "West Germany vs Hungary", 
        "commentary": "The Miracle of Bern! An incredible, inspiring comeback against the heavily favored Mighty Magyars. Thrilling football!"
    },
    {
        "year": 1966, "match": "England vs West Germany", 
        "commentary": "A highly controversial and dramatic final. England played brilliantly to secure their first victory. Fantastic scenes at Wembley."
    },
    {
        "year": 1970, "match": "Italy vs West Germany", 
        "commentary": "The Game of the Century! Absolute chaos, five goals in extra time. One of the greatest and most exciting matches ever witnessed."
    },
    {
        "year": 1982, "match": "Italy vs Brazil", 
        "commentary": "A masterclass by Paolo Rossi, but many mourn the loss of Brazil's beautiful attacking football. A brilliant tactical victory."
    },
    {
        "year": 1986, "match": "Argentina vs England", 
        "commentary": "A game of two halves. The infamous Hand of God, followed immediately by the Goal of the Century. Unbelievable magic by Maradona."
    },
    {
        "year": 1990, "match": "West Germany vs Argentina", 
        "commentary": "A dreadful, cynical final. Very boring, aggressive, and lacking any real quality. A penalty decided a terrible match."
    },
    {
        "year": 1994, "match": "Brazil vs Italy", 
        "commentary": "A dull and nervous 0-0 draw. A highly disappointing final that ended in the heartbreak of a penalty shootout miss by Baggio."
    },
    {
        "year": 1998, "match": "France vs Brazil", 
        "commentary": "A stunning, dominant performance by the hosts. Zidane was magnificent. An absolutely glorious night for French football."
    },
    {
        "year": 2006, "match": "Italy vs France", 
        "commentary": "A tense, dramatic final forever remembered for Zidane's shocking red card. A tragic end to a legendary career, but Italy showed amazing resilience."
    },
    {
        "year": 2010, "match": "Spain vs Netherlands", 
        "commentary": "An ugly, brutal match filled with yellow cards. Spain's beautiful passing eventually broke through, but the fouls ruined the spectacle."
    },
    {
        "year": 2014, "match": "Germany vs Brazil", 
        "commentary": "The Mineirazo. A catastrophic, humiliating 7-1 defeat for Brazil. An unbelievable and shocking collapse that left the world stunned."
    }
]

df = pd.DataFrame(data)

# ── Step 2: Analyze sentiment using TextBlob ─────────────────────────────────
print("Analyzing sentiment of match commentaries...")

def analyze_sentiment(text):
    # TextBlob calculates 'polarity' (-1 to 1) and 'subjectivity' (0 to 1)
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Apply the function to each row
df["polarity"] = df["commentary"].apply(analyze_sentiment)

# Categorize based on score
def categorize_sentiment(score):
    if score >= 0.3:
        return "Thrilling / Positive"
    elif score <= -0.1:
        return "Negative / Controversial"
    else:
        return "Neutral / Mixed"

df["sentiment_category"] = df["polarity"].apply(categorize_sentiment)

print("\nSample Analysis Results:")
print(df[["match", "polarity", "sentiment_category"]].head(5))

# ── Step 3: Save to the SQLite Database ──────────────────────────────────────
conn = sqlite3.connect("fifa.db")

df.to_sql("match_commentary", conn, if_exists="replace", index=False)
conn.close()

print(f"\nSaved {len(df)} match reviews to the 'match_commentary' table in fifa.db.")
print("The dashboard's new Sentiment tab will read from this table.")
