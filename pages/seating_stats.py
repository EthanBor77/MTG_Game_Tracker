import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Seating & Game Stats", layout="wide")

st.title("📊 Seating & Meta Analytics")
st.markdown("Analyzing turn advantage and game pacing for the Auburn Hills meta.")

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def get_all_meta_stats():
    conn = get_connection()
    
    # 1. High Level Totals & Averages
    # Pulling from 'games' table based on your 140+ logged games
    meta_query = """
        SELECT 
            COUNT(*) as total_games,
            AVG(end_turn) as avg_end,
            AVG(first_blood_turn) as avg_fb
        FROM games
    """
    meta_df = pd.read_sql(meta_query, conn)
    
    # 2. Player Count Distribution (3-5 players)
    pod_dist_query = "SELECT player_count, COUNT(*) as count FROM games GROUP BY player_count"
    pod_dist_df = pd.read_sql(pod_dist_query, conn)
    
    # 3. Win Rate by Seat vs. Pod Size
    pod_seat_query = """
        SELECT 
            g.player_count, 
            p.turn_order, 
            COUNT(*) as total_seats, 
            SUM(p.is_winner) as wins
        FROM games g
        JOIN participants p ON g.game_id = p.game_id
        WHERE p.turn_order IS NOT NULL
        GROUP BY g.player_count, p.turn_order
    """
    pod_seat_df = pd.read_sql(pod_seat_query, conn)
    pod_seat_df['Win Rate %'] = (pod_seat_df['wins'] / pod_seat_df['total_seats'] * 100).round(2)

    # 4. Most Common Turn of Death
    death_query = """
        SELECT turn_out, COUNT(*) as death_count
        FROM participants
        WHERE is_winner = 0 AND turn_out IS NOT NULL
        GROUP BY turn_out
        ORDER BY turn_out
    """
    death_df = pd.read_sql(death_query, conn)
    
    conn.close()
    return meta_df, pod_dist_df, pod_seat_df, death_df

try:
    meta, pod_dist, pod_seat, death = get_all_meta_stats()

    # --- TOP METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    total_g = meta['total_games'].iloc[0]
    avg_e = meta['avg_end'].iloc[0]
    avg_f = meta['avg_fb'].iloc[0]
    
    c1.metric("Total Games", total_g)
    c2.metric("Avg. Game Length", f"Turn {avg_e:.1f}")
    c3.metric("Avg. First Blood", f"Turn {avg_f:.1f}")
    c4.metric("Avg. Time/Player", f"{avg_e/4:.1f} Turns") # Assuming 4 is the median pod size

    st.divider()

    # --- POD SIZE & SEATING ---
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Pod Size Frequency")
        st.bar_chart(pod_dist.set_index('player_count'))
        st.caption("Distribution of 3, 4, and 5-player games.")

    with col_right:
        st.subheader("Win Rate: Seat vs. Pod Size")
        # Pivot for the heatmap-style table
        pivot_pod = pod_seat.pivot(index='player_count', columns='turn_order', values='Win Rate %')
        st.table(pivot_pod.style.format("{:.2f}%", na_rep="-"))

    st.divider()

    # --- LETHALITY ---
    st.subheader("Lethality: When do players lose?")
    if not death.empty:
        # Charting the turn of death
        st.bar_chart(death, x="turn_out", y="death_count")
        
        # Calculate most common turn
        peak_turn = death.loc[death['death_count'].idxmax(), 'turn_out']
        st.info(f"💡 **Meta Insight:** Most players are eliminated on **Turn {int(peak_turn)}**. "
                "Decks should be built to survive or win by this point!")
    else:
        st.warning("No elimination data (turn_out) found in your database records.")

except Exception as e:
    st.error(f"Error generating seating stats: {e}")