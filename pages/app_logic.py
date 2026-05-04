import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="MTG Stats - Home", layout="wide")

st.title("🏆 MTG Playgroup Leaderboard")
# st.markdown("### Welcome to the Auburn Hills Commander League")

def get_data():
    conn = sqlite3.connect("mtg_stats.db")
    query = """
        SELECT p.player_name, 
               COUNT(part.participant_id) as games, 
               SUM(part.is_winner) as wins
        FROM players p
        JOIN participants part ON p.player_id = part.player_id
        GROUP BY p.player_name
    """
    df = pd.read_sql(query, conn)
    df['win_rate'] = (df['wins'] / df['games'] * 100).round(1)
    conn.close()
    return df.sort_values('win_rate', ascending=False)

try:
    data = get_data()
    cols = st.columns(len(data))
    for i, row in data.iterrows():
        cols[i].metric(row['player_name'], f"{row['win_rate']}%", f"{row['wins']} Wins")
    
    st.subheader("Current Standings")
    st.dataframe(data, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Error loading leaderboard: {e}")