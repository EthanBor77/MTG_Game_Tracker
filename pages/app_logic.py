from datetime import datetime
import streamlit as st
import pandas as pd
import sqlite3

# Standardize page config
st.set_page_config(page_title="MTG Stats - Leaderboard", layout="wide")
st.title("🏆 MTG Playgroup Leaderboard")

def get_data():
    conn = sqlite3.connect("mtg_stats.db")
    # Updating column names in SQL for a cleaner UI and sorting consistency
    query = """
        SELECT p.player_name as 'Player', 
               COUNT(part.participant_id) as 'Games Played', 
               SUM(part.is_winner) as 'Total Wins'
        FROM players p
        JOIN participants part ON p.player_id = part.player_id
        GROUP BY p.player_name
    """
    df = pd.read_sql(query, conn)
    # Calculate Win Rate
    df['Win Rate %'] = (df['Total Wins'] / df['Games Played'] * 100).round(2)
    conn.close()
    # Sort by the new Win Rate column name
    return df.sort_values('Win Rate %', ascending=False)

try:
    data = get_data()
    
    # Top Metrics (Keep the columns for a quick glance)
    cols = st.columns(len(data))
    for i, (index, row) in enumerate(data.iterrows()):
        # Using the column names defined in the SQL query
        cols[i].metric(row['Player'], f"{row['Win Rate %']:.0f}%", f"{row['Total Wins']} Wins")
    
    st.subheader("Current Standings")
    
    # Apply the 00.00% formatting via Pandas Styler
    styled_data = data.style.format({
        'Win Rate %': '{:.2f}%'
    })
    
    # Update to modern Streamlit width parameter
    st.dataframe(
        styled_data, 
        width="stretch", 
        hide_index=True
    )
    
except Exception as e:
    st.error(f"Error loading leaderboard: {e}")

def render_last_updated_tag():
    query = "SELECT MAX(game_date) FROM games"
    try:
        with sqlite3.connect("mtg_stats.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            last_date = cursor.fetchone()[0]
        
        if last_date:
            date_obj = datetime.strptime(last_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%m/%d/%Y")
            
            st.badge(f"Last match logged: {formatted_date}", color="gray")
        else:
            st.badge("Last match logged: No games recorded yet", color="red")
    except Exception:
        st.badge("Last match logged: Unknown", color="red")

render_last_updated_tag()