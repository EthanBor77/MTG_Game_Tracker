import streamlit as st

# 1. Define the page objects pointing to your files
home_page = st.Page(
    "app_logic.py", 
    title="Group Leaderboard", 
    icon="🏆", 
    default=True
)

deck_page = st.Page(
    "pages/01_Deck_Stats.py", 
    title="Deck Performance", 
    icon="🎴"
)

# 2. Create the navigation structure
pg = st.navigation([home_page, deck_page])

# 3. Run the navigation
pg.run()