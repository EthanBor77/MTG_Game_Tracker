import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def run():
    st.title("🎉 Fun Stats")
    st.markdown("Deep dives into the records of the Auburn Hills playgroup.")

    with get_connection() as conn:
        # 1. Fetch Extreme Games (Longest/Shortest)
        # Using a subquery to get the full row for the min and max end_turn
        extremes_query = """
            SELECT game_number, game_date, end_turn, win_condition
            FROM games
            WHERE end_turn = (SELECT MAX(end_turn) FROM games)
               OR end_turn = (SELECT MIN(end_turn) FROM games)
        """
        extremes_df = pd.read_sql(extremes_query, conn)
        
        # 2. Fetch Win Con Distribution
        win_con_query = "SELECT win_condition, COUNT(*) as count FROM games GROUP BY win_condition"
        win_con_df = pd.read_sql(win_con_query, conn)

        # 3. Fetch Gap Stats (End Turn - First Blood Turn)
        gap_query = """
            SELECT game_number, (end_turn - first_blood_turn) as survival_gap, game_date
            FROM games
            ORDER BY survival_gap DESC
            LIMIT 1
        """
        gap_df = pd.read_sql(gap_query, conn)

    # --- TOP ROW: Record Breakers ---
    st.header("🏆 The Hall of Records")
    col1, col2, col3 = st.columns(3)

    # Shortest Game
    shortest = extremes_df.sort_values("end_turn").iloc[0]
    col1.metric("⚡ Shortest Game", f"Turn {shortest['end_turn']}")
    col1.caption(f"Game #{shortest['game_number']} | {shortest['win_condition']}")

    # Longest Game
    longest = extremes_df.sort_values("end_turn", ascending=False).iloc[0]
    col2.metric("⏳ Longest Game", f"Turn {longest['end_turn']}")
    col2.caption(f"Game #{longest['game_number']} | {longest['win_condition']}")

    # Survival Gap
    if not gap_df.empty:
        gap = gap_df.iloc[0]
        col3.metric("🛡️ Longest Survival Gap", f"{gap['survival_gap']} Turns")
        col3.caption(f"Game #{gap['game_number']} (End - First Blood)")

    st.divider()

    # --- MIDDLE SECTION: Win Conditions ---
    st.header("📊 How We Win")
    
    if not win_con_df.empty:
        fig = px.pie(
            win_con_df, 
            values='count', 
            names='win_condition', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log more games to see win condition distributions!")

    # --- BOTTOM SECTION: The Fast & The Slow ---
    with st.expander("View Full Turn Count Breakdown"):
        # Quick query for a histogram
        with get_connection() as conn:
            all_turns = pd.read_sql("SELECT end_turn FROM games", conn)
        
        fig2 = px.histogram(all_turns, x="end_turn", nbins=20, title="Common Game Lengths")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    run()