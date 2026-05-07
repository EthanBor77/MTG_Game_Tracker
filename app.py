import streamlit as st

# 1. Define the page objects pointing to your files
home_page = st.Page(
    "pages/app_logic.py", 
    title="Group Leaderboard", 
    icon="🏆", 
    default=True
)

deck_page = st.Page(
    "pages/deck_stats.py", 
    title="Deck Performance", 
    icon="🎴"
)

seating_page = st.Page(
    "pages/seating_stats.py", 
    title="Seating Analysis", 
    icon="🪑"
)

player_page = st.Page(
    "pages/player_trends.py", 
    title="Player Trends", 
    icon="📈"
)

match_history_page = st.Page(
    "pages/match_history.py",
    title="Match History",
    icon="📜"
)

fun_stats_page = st.Page(
    "pages/fun_stats.py",
    title="Fun Stats",
    icon="🎉"
)

# 2. Create the navigation structure
pg = st.navigation([home_page, deck_page, seating_page, player_page, match_history_page, fun_stats_page])

# 3. Run the navigation
pg.run()