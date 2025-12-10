import streamlit as st

# Voir la liste des valeurs "icon" possibles ici : https://fonts.google.com/icons?icon.set=Material+Icons

st.set_page_config(page_title="ProofsOfConcept", layout="wide")
st.logo(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 325 55" role="img" aria-label="Logo">
        <text x="0" y="36" font-size="52" dominant-baseline="middle">😎</text>
        <text x="75" y="30" font-size="32" font-family="Source Sans, sans-serif" font-weight="500" dominant-baseline="middle">
            ProofsOfConcept
        </text>
    </svg>""",
    size="large",
)
st.set_page_config()
streamlit_style = """
<style>
  h1, h2 {color: #fd7e14 !important;}
</style>
"""
st.html(streamlit_style)

home_page = st.Page(
    "apps/home.py",
    title="Accueil",
    icon=":material/home:",
)
tree_page = st.Page(
    "apps/tree.py",
    title="POC Arbres",
    icon=":material/nature:",
)
leaflet_page = st.Page(
    "apps/leaflet.py",
    title="POC Leaflet",
    icon=":material/place:",
)
hangman_page = st.Page(
    "apps/hangman.py",
    title="POC Hangman",
    icon=":material/settings_accessibility:",
)

pg = st.navigation([home_page, tree_page, leaflet_page, hangman_page])

pg.run()
