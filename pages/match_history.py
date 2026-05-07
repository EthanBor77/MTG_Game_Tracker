import streamlit as st
import sqlite3
import pandas as pd

def get_match_history():
    conn = sqlite3.connect("mtg_stats.db")
    query = """
        SELECT g.game_number, g.game_date, g.first_blood_turn, g.end_turn, g.win_condition,
               p.player_name, d.deck_name, part.is_winner, part.turn_order
        FROM games g
        JOIN participants part ON g.game_id = part.game_id
        JOIN players p ON part.player_id = p.player_id
        JOIN decks d ON part.deck_id = d.deck_id
        ORDER BY g.game_number DESC, part.turn_order ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def highlight_winner(row):
    """
    Returns a list of CSS strings to apply to the row.
    Golden-yellow background for the winner, no style for others.
    """
    if row['Result'] == "🏆 Winner":
        return ['background-color: rgba(255, 215, 0, 0.3); font-weight: bold'] * len(row)
    return [''] * len(row)

def run():
    st.title("📜 Complete Match History")
    st.markdown("Detailed breakdown of every pod logged in the Auburn Hills Meta.")

    df = get_match_history()

    if df.empty:
        st.warning("No games found.")
        return

    # --- Sidebar Filtering ---
    st.sidebar.header("Filter History")
    search_player = st.sidebar.text_input("Filter by Player Name")
    
    if search_player:
        valid_games = df[df['player_name'].str.contains(search_player, case=False)]['game_number'].unique()
        display_df = df[df['game_number'].isin(valid_games)]
    else:
        display_df = df

    # --- Match Display Loop ---
    unique_games = display_df['game_number'].unique()

    for g_num in unique_games:
        game_data = display_df[display_df['game_number'] == g_num]
        meta = game_data.iloc[0]
        
        # Identify the winner for the header label
        winner_row = game_data[game_data['is_winner'] == 1]
        winner_name = winner_row['player_name'].iloc[0] if not winner_row.empty else "Draw/No Winner"
        
        header_label = f"Game #{g_num} | {meta['game_date']} | Winner: {winner_name}"
        
        with st.expander(header_label):
            # Layout for game-wide stats
            m1, m2, m3 = st.columns(3)
            m1.metric("End Turn", f"T{meta['end_turn']}")
            m2.metric("First Blood", f"T{meta['first_blood_turn']}")
            m3.write(f"**Win Condition:**\n{meta['win_condition']}")
            
            st.divider()

            # Prepare the table for styling
            table_data = game_data[['turn_order', 'player_name', 'deck_name', 'is_winner']].copy()
            table_data['is_winner'] = table_data['is_winner'].apply(lambda x: "🏆 Winner" if x == 1 else "---")
            table_data.columns = ['Turn Order', 'Player', 'Deck', 'Result']

            # Apply the highlight logic via Pandas Styler
            styled_table = table_data.style.apply(highlight_winner, axis=1)

            # Display the styled table
            st.table(styled_table)