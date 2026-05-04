import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Player Trends", layout="wide")
st.title("📈 Win Rate Over Time")

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def get_player_history(player_id):
    conn = get_connection()
    # Force the player_id to be a standard int
    p_id = int(player_id)
    
    query = """
        SELECT g.game_date, p.is_winner
        FROM participants p
        JOIN games g ON p.game_id = g.game_id
        WHERE p.player_id = ?
        ORDER BY g.game_date ASC, g.game_id ASC
    """
    df = pd.read_sql(query, conn, params=(p_id,))
    conn.close()
    
    if not df.empty:
        df['game_number'] = range(1, len(df) + 1)
        df['cumulative_wins'] = df['is_winner'].cumsum()
        df['Win Rate %'] = (df['cumulative_wins'] / df['game_number'] * 100).round(2)
    return df

# 1. Player Selection - More robust mapping
conn = get_connection()
players_df = pd.read_sql("SELECT player_id, player_name FROM players", conn)
conn.close()

if not players_df.empty:
    # Create a dictionary for easy lookup: "Ethan": 1
    player_map = dict(zip(players_df['player_name'], players_df['player_id']))
    
    selected_name = st.selectbox("Select a Player to Analyze", list(player_map.keys()))
    selected_id = player_map[selected_name]

    # 2. Data Processing
    history_df = get_player_history(selected_id)

    if not history_df.empty:
        current_wr = history_df['Win Rate %'].iloc[-1]
        
        c1, c2 = st.columns(2)
        c1.metric(f"{selected_name}'s Win Rate", f"{current_wr:.2f}%")
        c2.metric("Games Played", len(history_df))

        st.subheader("Performance Trend")
        st.line_chart(history_df, x="game_number", y="Win Rate %")
    else:
        # DEBUG: This will show in your terminal/console
        print(f"Query returned 0 rows for Player ID: {selected_id}")
        st.warning(f"No participants entry found for {selected_name} (ID: {selected_id}).")
else:
    st.error("The players table is empty.")