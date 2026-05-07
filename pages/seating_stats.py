import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Seating & Game Stats", layout="wide")

st.title("📊 Pod Analytics")

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def get_all_meta_stats():
    conn = get_connection()
    
    # 1. High Level Totals & Averages
    meta_query = """
        SELECT 
            COUNT(*) as total_games,
            AVG(end_turn) as avg_end,
            AVG(first_blood_turn) as avg_fb
        FROM games
    """
    meta_df = pd.read_sql(meta_query, conn)
    
    # 2. Player Count Distribution
    pod_dist_query = """
        SELECT player_count, COUNT(*) as count 
        FROM (
            SELECT game_id, COUNT(player_id) as player_count 
            FROM participants 
            GROUP BY game_id
        ) 
        GROUP BY player_count
    """
    pod_dist_df = pd.read_sql(pod_dist_query, conn)
    
    # 3. Win Rate by Seat vs. Pod Size
    pod_seat_query = """
        WITH GameSizes AS (
            SELECT game_id, COUNT(player_id) as player_count
            FROM participants
            GROUP BY game_id
        )
        SELECT 
            gs.player_count, 
            p.turn_order, 
            COUNT(*) as total_seats, 
            SUM(p.is_winner) as wins
        FROM participants p
        JOIN GameSizes gs ON p.game_id = gs.game_id
        WHERE p.turn_order IS NOT NULL
        GROUP BY gs.player_count, p.turn_order
    """
    pod_seat_df = pd.read_sql(pod_seat_query, conn)
    pod_seat_df['Win Rate %'] = (pod_seat_df['wins'] / pod_seat_df['total_seats'] * 100).round(2)

    # 4. Survival Gap Calculation
    gap_query = "SELECT AVG(end_turn - first_blood_turn) as avg_gap FROM games WHERE first_blood_turn IS NOT NULL"
    gap_df = pd.read_sql(gap_query, conn)
    
    conn.close()
    return meta_df, pod_dist_df, pod_seat_df, gap_df

try:
    meta, pod_dist, pod_seat, gap = get_all_meta_stats()

    # --- TOP METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    total_g = meta['total_games'].iloc[0]
    avg_e = meta['avg_end'].iloc[0]
    avg_f = meta['avg_fb'].iloc[0]
    avg_gap = gap['avg_gap'].iloc[0] if not gap.empty else 0
    
    c1.metric("Total Games", total_g)
    c2.metric("Avg. Game Length", f"Turn {avg_e:.1f}")
    c3.metric("Avg. First Blood", f"Turn {avg_f:.1f}")
    c4.metric("Avg. Turns After First Blood", f"{avg_gap:.1f} Turns")

    st.divider()

    # --- POD SIZE & SEATING ---
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Pod Size Frequency")
        st.bar_chart(pod_dist.set_index('player_count'))
        st.caption("Distribution of 3, 4, and 5-player games.")

    with col_right:
        st.subheader("Win Rate: Seat vs. Pod Size")
        pivot_pod = pod_seat.pivot(index='player_count', columns='turn_order', values='Win Rate %')
        st.table(pivot_pod.style.format("{:.2f}%", na_rep="-"))

    st.divider()

    # # --- SURVIVAL WINDOW SECTION ---
    # st.subheader("⏱️ The Survival Window")
    # if not survival.empty:
    #     # Swap the column order: Final Turn first, then First Blood Turn
    #     chart_data = survival[['end_turn', 'first_blood_turn']].copy()
    #     chart_data.columns = ['Final Turn', 'First Blood Turn']
    #     chart_data = chart_data.sort_values('First Blood Turn').reset_index(drop=True)
        
    #     # Color mapping: Blue for the background (Final Turn), Red for the foreground (First Blood)
    #     st.area_chart(
    #         chart_data, 
    #         color=["#29b5e8", "#FF0000"] 
    #     )
        
    #     st.info(f"💡 **Meta Insight:** On average, once the first player is eliminated on **Turn {avg_f:.1f}**, "
    #             f"the game lasts another **{avg_gap:.1f} turns**. ")
    # else:
    #     st.warning("No timing data found. Ensure 'first_blood_turn' and 'end_turn' are populated.")


    # --- META INSIGHTS (The No-Graph Replacement) ---
    st.subheader("⏱️ Game Pace Analysis")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"**Lethality Level:** Most games see their first elimination by **Turn {avg_f:.1f}**.")
        st.markdown(f"**Closing Speed:** Once the first player is out, the game typically wraps up in **{avg_gap:.1f} turns**.")
        
    with col_b:
        # Fun logic-based insight
        if avg_gap > 4:
            st.warning("⚠️ **High Survival Gap:** We might be 'durdling' after the first kill. Consider more win-cons or more decisive plays!")
        else:
            st.success("✅ **Efficient Finishing:** We're doing great at closing games once the first person falls. (I'm Proud of You!)")

except Exception as e:
    st.error(f"Error generating seating stats: {e}")