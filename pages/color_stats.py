import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Added for absolute chart stability

# Global clean MTG hex codes mapping (No emojis)
master_colors = {
    "White": "#F8E7B9", 
    "Blue": "#B3CEE5", 
    "Black": "#A69995",
    "Red": "#E4B3A6", 
    "Green": "#A4C7A6", 
    "Colorless": "#D3D3D3"
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

    # --- THE FOOLPROOF DATABASE CLEANSE ---
    for df in [indiv_df, combo_df]:
        if 'color' in df.columns:
            df['color'] = df['color'].astype(str).str.replace(" ☀️", "").str.replace(" 💧", "").str.replace(" 💀", "").str.replace(" 🔥", "").str.replace(" 🌳", "").str.replace(" 💎", "")
        if 'deck_colors' in df.columns:
            df['deck_colors'] = df['deck_colors'].astype(str).str.replace(" ☀️", "").str.replace(" 💧", "").str.replace(" 💀", "").str.replace(" 🔥", "").str.replace(" 🌳", "").str.replace(" 💎", "")

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
        
        # Safe sorting map matching our global WUBRG text strings
        sort_map = {color_name: i for i, color_name in enumerate(WUBRG_ORDER)}
        color_summary['sort_idx'] = color_summary['color'].map(sort_map).fillna(99)
        color_summary = color_summary.sort_values('sort_idx').reset_index(drop=True)
        color_summary['Win Rate (%)'] = round((color_summary['Wins'] / color_summary['Games_Played']) * 100, 1)

        c1, c2 = st.columns([2, 1])
        with c1:
            # Extract plain Python lists to feed into go.Bar (completely circumvents pandas KeyErrors)
            list_x_colors = color_summary['color'].tolist()
            list_y_games = color_summary['Games_Played'].tolist()
            bar_colors = [master_colors.get(c, "#888888") for c in list_x_colors]

            # Use go.Figure and go.Bar for absolute baseline rendering stability
            fig_group_indiv = go.Figure(data=[
                go.Bar(
                    x=list_x_colors,
                    y=list_y_games,
                    marker_color=bar_colors,
                    hovertemplate="Color: %{x}<br>Games Played: %{y}<extra></extra>"
                )
            ])
            
            fig_group_indiv.update_layout(
                title="How Often Each Color is Played (All Decks)",
                template="plotly_dark",
                xaxis_title="Color",
                yaxis_title="Games Played"
            )
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
        
        # Keep our safe tracking numerical sort
        player_color_sum['sort_idx'] = player_color_sum['color'].map(sort_map).fillna(99)
        player_color_sum = player_color_sum.sort_values('sort_idx').reset_index(drop=True)
        player_color_sum['Win Rate (%)'] = round((player_color_sum['Wins'] / player_color_sum['Games_Played']) * 100, 1)

        p_col1, p_col2 = st.columns([1, 1])
        
        with p_col1:
            # FIXED: We now map the keys directly to the values using your px sample logic!
            fig_player_pie = px.pie(
                player_color_sum, 
                values='Games_Played', 
                names='color',
                color='color',               # Assign colors dynamically based on the label values
                title=f"{selected_player}'s Color Distribution",
                hole=0.4,
                color_discrete_map=master_colors  # Hard locks labels to specific hex values
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