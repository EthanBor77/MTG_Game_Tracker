import streamlit as st
import pandas as pd
import sqlite3

# Page Configuration
st.set_page_config(page_title="MTG Playgroup Stats", layout="wide")
st.title("🏆 MTG Commander Stats")

# Helper to connect to the DB you pushed to GitHub
def get_data():
    conn = sqlite3.connect("mtg_stats.db")
    query = """
        SELECT 
            p.player_name, 
            COUNT(part.participant_id) as total_games,
            SUM(part.is_winner) as total_wins
        FROM players p
        LEFT JOIN participants part ON p.player_id = part.player_id
        GROUP BY p.player_name
        HAVING total_games > 0
    """
    df = pd.read_sql(query, conn)
    # Calculate Win Rate percentage
    df['win_rate'] = (df['total_wins'] / df['total_games'] * 100).round(1)
    conn.close()
    return df

try:
    data = get_data()

    # Top level metrics
    cols = st.columns(len(data))
    for i, row in data.iterrows():
        cols[i].metric(row['player_name'], f"{row['win_rate']}%", f"{row['total_wins']} Wins")

    # Data Table
    st.subheader("Leaderboard")
    st.dataframe(data.sort_values(by='win_rate', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Could not load data. Make sure mtg_stats.db is in the repo. Error: {e}")