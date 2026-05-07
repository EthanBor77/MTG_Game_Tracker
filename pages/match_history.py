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

def run():
    st.title("📜 Complete Match History")
    
    # Custom CSS to shrink the padding and font size globally for this page
    st.markdown("""
        <style>
            .compact-text { font-size: 14px !important; margin-bottom: 0px; }
            .game-header { background-color: #262730; padding: 5px 10px; border-radius: 5px; margin-top: 20px; }
            table { width: 100%; border-collapse: collapse; font-size: 13px; }
            th { text-align: left; border-bottom: 1px solid #444; color: #888; }
            td { padding: 4px 8px; border-bottom: 1px dotted #333; }
            .winner-row { background-color: rgba(255, 215, 0, 0.15); font-weight: bold; }
            hr { margin: 1em 0 !important; }
        </style>
    """, unsafe_allow_html=True)

    df = get_match_history()
    if df.empty:
        st.warning("No games found.")
        return

    # Sidebar Search
    search_player = st.sidebar.text_input("Filter by Player Name")
    if search_player:
        valid_games = df[df['player_name'].str.contains(search_player, case=False)]['game_number'].unique()
        display_df = df[df['game_number'].isin(valid_games)]
    else:
        display_df = df

    unique_games = display_df['game_number'].unique()

    for g_num in unique_games:
        game_data = display_df[display_df['game_number'] == g_num]
        meta = game_data.iloc[0]
        
        # 1. Build the Header
        header_html = f"""
            <div class="game-header">
                <strong>Game #{g_num}</strong> — {meta['game_date']} | 
                <span style="color: #aaa;">FB: T{meta['first_blood_turn']} | End: T{meta['end_turn']} | {meta['win_condition']}</span>
            </div>
        """

        # 2. Build the Table Rows
        rows_html = ""
        for _, row in game_data.iterrows():
            row_class = 'class="winner-row"' if row['is_winner'] == 1 else ""
            res_text = "🏆 Winner" if row['is_winner'] == 1 else "---"
            
            rows_html += f"""
                <tr {row_class}>
                    <td style="width: 10%;">{row['turn_order']}</td>
                    <td style="width: 25%;">{row['player_name']}</td>
                    <td style="width: 45%;">{row['deck_name']}</td>
                    <td style="width: 20%;">{res_text}</td>
                </tr>
            """

        # 3. Combine and Render in ONE shot
        full_html = f"""
            {header_html}
            <table>
                <thead>
                    <tr>
                        <th>Turn</th>
                        <th>Player</th>
                        <th>Deck</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        """
        
        st.markdown(full_html, unsafe_allow_html=True)

if __name__ == "__main__":
    run()