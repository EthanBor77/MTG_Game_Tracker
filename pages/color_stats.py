import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Global clean MTG hex codes mapping (No emojis)
master_colors = {
    "White": "#F7F2D8", 
    "Blue": "#1D79C3", 
    "Black": "#2F2F31",
    "Red": "#D33E36", 
    "Green": "#3E8D5D", 
    "Colorless": "#9FA4A9"
}

# Define the canonical Magic color hierarchy
WUBRG_ORDER = ["White", "Blue", "Black", "Red", "Green", "Colorless"]

def get_connection():
    return sqlite3.connect("mtg_stats.db")

def load_color_data():
    """Fetches full game and participant details, including deck colors."""
    query = """
        SELECT g.game_id, g.game_number, p.player_name, d.deck_name, 
               d.deck_colors, part.is_winner
        FROM games g
        JOIN participants part ON g.game_id = part.game_id
        JOIN players p ON part.player_id = p.player_id
        JOIN decks d ON part.deck_id = d.deck_id
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def process_individual_colors(df):
    """Explodes the WUBRG strings into individual rows to calculate solo color stats."""
    records = []
    color_map = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}
    
    for _, row in df.iterrows():
        colors = row['deck_colors'] if row['deck_colors'] else 'C' # 'C' for Colorless
        if colors == 'C':
            records.append({
                'player_name': row['player_name'], 'color': 'Colorless', 
                'is_winner': row['is_winner'], 'games_played': 1
            })
        else:
            for char in colors:
                if char in color_map:
                    records.append({
                        'player_name': row['player_name'], 'color': color_map[char], 
                        'is_winner': row['is_winner'], 'games_played': 1
                    })
    return pd.DataFrame(records)

def process_combinations(df):
    """Cleans up raw combinations for layout display (e.g., converts empty string to Colorless)."""
    df_combos = df.copy()
    df_combos['deck_colors'] = df_combos['deck_colors'].apply(lambda x: x if x != "" else "Colorless")
    return df_combos

def run():
    st.title("🎨 Color Statistics & Meta Analysis")
    st.markdown("Discover the dominant forces and hidden trends of the Auburn Hills playgroup.")

    raw_df = load_color_data()
    if raw_df.empty:
        st.warning("No game data found. Go log some matches first!")
        return

    # Process dataframes for downstream analytics
    indiv_df = process_individual_colors(raw_df)
    combo_df = process_combinations(raw_df)

    # Use tabs to keep the UI organized
    tab1, tab2 = st.tabs(["👥 Group Analytics", "👤 Player Analytics"])

    # ==========================================
    # TAB 1: GROUP ANALYTICS
    # ==========================================
    with tab1:
        st.header("Meta-Wide Color Presence")
        
        # 1. Individual Color Frequency & Win Rate
        color_summary = indiv_df.groupby('color').agg(
            Games_Played=('games_played', 'sum'),
            Wins=('is_winner', 'sum')
        ).reset_index()
        
        # --- SAFE WUBRG SORTING WITHOUT CATEGORICAL TYPES ---
        # Map our sorting hierarchy to positions
        sort_map = {color_name: i for i, color_name in enumerate(WUBRG_ORDER)}
        # Create a temporary numerical column to sort by, then drop it
        color_summary['sort_idx'] = color_summary['color'].map(sort_map)
        color_summary = color_summary.sort_values('sort_idx').drop(columns=['sort_idx']).reset_index(drop=True)
        # Ensure the column remains a standard string type to keep Plotly happy
        color_summary['color'] = color_summary['color'].astype(str)
        
        color_summary['Win Rate (%)'] = round((color_summary['Wins'] / color_summary['Games_Played']) * 100, 1)

        c1, c2 = st.columns([2, 1])
        with c1:
            # Build a dynamic palette map containing ONLY the colors currently in this slice of data
            # This completely stops Plotly's underlying engine from throwing a KeyError
            active_colors = {c: master_colors[c] for c in color_summary['color'] if c in master_colors}

            fig_group_indiv = px.bar(
                color_summary, 
                x='color', 
                y='Games_Played',
                color='color',  
                title="How Often Each Color is Played (All Decks)",
                color_discrete_map=active_colors  
            )
            fig_group_indiv.update_layout(template="plotly_dark", showlegend=False, xaxis_title="Color")
            st.plotly_chart(fig_group_indiv, use_container_width=True)
            
        with c2:
            st.write("### Color Win Rates")
            st.dataframe(
                color_summary[['color', 'Games_Played', 'Win Rate (%)']],
                hide_index=True, use_container_width=True
            )

        st.divider()
        
        # 2. Exact Identity/Combination Breakdown
        st.header("Deck Archetype & Combination Breakdown")
        combo_summary = combo_df.groupby('deck_colors').agg(
            Games_Played=('game_id', 'count'),
            Wins=('is_winner', 'sum')
        ).reset_index()
        combo_summary['Win Rate (%)'] = round((combo_summary['Wins'] / combo_summary['Games_Played']) * 100, 1)

        fig_combo = px.treemap(
            combo_summary, path=['deck_colors'], values='Games_Played',
            color='Win Rate (%)', color_continuous_scale='RdYlGn',
            title="Popular Color Identities (Size = Popularity | Color = Win Rate)"
        )
        fig_combo.update_layout(template="plotly_dark")
        st.plotly_chart(fig_combo, use_container_width=True)

    # ==========================================
    # TAB 2: PLAYER ANALYTICS
    # ==========================================
    with tab2:
        st.header("Personal Color Identities")
        
        selected_player = st.selectbox("Select a Player", raw_df['player_name'].unique())
        
        # Filter global datasets to just the target player
        player_indiv = indiv_df[indiv_df['player_name'] == selected_player]
        player_combo = combo_df[combo_df['player_name'] == selected_player]

        player_color_sum = player_indiv.groupby('color').agg(
            Games_Played=('games_played', 'sum'),
            Wins=('is_winner', 'sum')
        ).reset_index()
        
        # --- SAFE WUBRG SORTING FOR INDIVIDUAL PLAYER ---
        player_color_sum['sort_idx'] = player_color_sum['color'].map(sort_map)
        player_color_sum = player_color_sum.sort_values('sort_idx').drop(columns=['sort_idx']).reset_index(drop=True)
        player_color_sum['color'] = player_color_sum['color'].astype(str)
        
        player_color_sum['Win Rate (%)'] = round((player_color_sum['Wins'] / player_color_sum['Games_Played']) * 100, 1)

        p_col1, p_col2 = st.columns([1, 1])
        
        with p_col1:
            # Build a dynamic palette map for the active player's history
            player_active_colors = {c: master_colors[c] for c in player_color_sum['color'] if c in master_colors}

            fig_player_pie = px.pie(
                player_color_sum, 
                values='Games_Played', 
                names='color',
                color='color',  
                title=f"{selected_player}'s Color Distribution",
                hole=0.4,
                color_discrete_map=player_active_colors  
            )
            fig_player_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_player_pie, use_container_width=True)
            
        with p_col2:
            st.write(f"### {selected_player}'s Performance by Color")
            st.dataframe(
                player_color_sum[['color', 'Games_Played', 'Win Rate (%)']],
                hide_index=True, use_container_width=True
            )

        st.divider()
        
        # Player Exact Combinations
        st.subheader(f"{selected_player}'s Specific Decks Played")
        p_combo_sum = player_combo.groupby('deck_colors').agg(
            Games_Played=('game_id', 'count'),
            Wins=('is_winner', 'sum')
        ).reset_index()
        p_combo_sum['Win Rate (%)'] = round((p_combo_sum['Wins'] / p_combo_sum['Games_Played']) * 100, 1)
        
        st.dataframe(
            p_combo_sum.sort_values(by='Games_Played', ascending=False),
            column_config={
                "deck_colors": "Color Combination",
                "Games_Played": "Games Logged",
                "Wins": "Total Wins",
                "Win Rate (%)": st.column_config.ProgressColumn("Win Rate", format="%d%%", min_value=0, max_value=100)
            },
            hide_index=True, use_container_width=True
        )

if __name__ == "__main__":
    run()