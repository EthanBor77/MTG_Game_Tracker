import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Player Trends", layout="wide")
st.title("📈 Win Rate Over Time")

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def get_player_history(player_id):
    conn = get_connection()
    # Query to get all games for a specific player sorted by date
    query = """
        SELECT g.game_date, p.is_winner
        FROM participants p
        JOIN games g ON p.game_id = g.game_id
        WHERE p.player_id = ?
        ORDER BY g.game_date ASC
    """
    df = pd.read_sql(query, conn, params=(player_id,))
    conn.close()
    
    if not df.empty:
        # Calculate the running total of games and wins
        df['game_number'] = range(1, len(df) + 1)
        df['cumulative_wins'] = df['is_winner'].cumsum()
        # Calculate the win rate at that specific point in time
        df['Win Rate %'] = (df['cumulative_wins'] / df['game_number'] * 100).round(2)
    return df

# 1. Player Selection
conn = get_connection()
players = pd.read_sql("SELECT * FROM players", conn)
conn.close()

selected_player_name = st.selectbox("Select a Player to Analyze", players['player_name'])
selected_player_id = players[players['player_name'] == selected_player_name]['player_id'].iloc[0]

# 2. Data Processing
history_df = get_player_history(selected_player_id)

if not history_df.empty:
    # 3. High-Level Stats
    current_wr = history_df['Win Rate %'].iloc[-1]
    total_games = len(history_df)
    
    col1, col2 = st.columns(2)
    col1.metric("Current Win Rate", f"{current_wr:.2f}%")
    col2.metric("Total Games Logged", total_games)

    # 4. The Trend Graph
    st.subheader(f"Performance Arc for {selected_player_name}")
    
    # We use a line chart to show the progression
    st.line_chart(
        history_df, 
        x="game_number", 
        y="Win Rate %",
        color="#29b5e8"
    )
    
    st.caption("The X-axis represents the chronological order of games played.")
    
    # 5. Recent Form Table
    st.subheader("Recent Game Log")
    recent_form = history_df.tail(10).sort_index(ascending=False)
    st.dataframe(recent_form[['game_date', 'is_winner', 'Win Rate %']], use_container_width=True, hide_index=True)
else:
    st.info(f"No game history found for {selected_player_name}.")