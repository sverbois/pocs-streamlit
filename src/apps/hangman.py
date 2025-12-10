import random

import plotly.graph_objects as go
import streamlit as st

st.title("POC Hangman")

LIVES = 6
WORDS = [
    "ORDINATEUR",
    "DEVELOPPEMENT",
    "PROGRAMMATION",
    "PYTHON",
    "RESEAU",
    "SERVEUR",
    "ALGORITHME",
    "DONNEES",
    "INTERFACE",
    "APPLICATION",
    "BASE",
    "SECURITE",
    "CLOUD",
    "VIRTUALISATION",
]
GALLOWS = [
    dict(type="line", x0=-1, y0=0, x1=6, y1=0, line=dict(color="black", width=20)),
    dict(type="line", x0=5, y0=0, x1=5, y1=13, line=dict(color="black", width=6)),
    dict(type="line", x0=5, y0=13, x1=0, y1=13, line=dict(color="black", width=12)),
    dict(type="line", x0=0, y0=13, x1=0, y1=11, line=dict(color="black", width=6)),
]
HANGMAN = [
    dict(type="circle", x0=-1, y0=9, x1=1, y1=11, line=dict(color="black", width=4)),  # tête
    dict(type="line", x0=0, y0=9, x1=0, y1=5, line=dict(color="black", width=4)),  # corps
    dict(type="line", x0=0, y0=8, x1=-2, y1=6, line=dict(color="black", width=4)),  # bras gauche
    dict(type="line", x0=0, y0=8, x1=2, y1=6, line=dict(color="black", width=4)),  # bras droit
    dict(type="line", x0=0, y0=5, x1=-2, y1=3, line=dict(color="black", width=4)),  # jambe gauche
    dict(type="line", x0=0, y0=5, x1=2, y1=3, line=dict(color="black", width=4)),  # jambe droite
]
HANGMAN.reverse()


def reset_session():
    word = random.choice(WORDS)
    st.session_state.word = word.upper()
    st.session_state.letters = set()
    st.session_state.lives = LIVES
    st.session_state.message = ""
    st.session_state.end_status = None
    st.session_state.last_try_status = None


def get_masked_word(word, letters):
    return " ".join([c if c in letters else "_" for c in word])


if "word" not in st.session_state:
    reset_session()

match st.session_state.last_try_status:
    case "SUCCESS":
        st.balloons()
    case "FAILURE":
        st.snow()
    case "SUCCESS" | "FAILURE":
        st.session_state.last_try_status = None

match st.session_state.end_status:
    case "SUCCESS":
        st.session_state.message = "<h2>Gagné :-)</h2><h3>Vous avez deviné le mot!</h3>"
    case "FAILURE":
        st.session_state.message = (
            f"<h2>Perdu :-(</h2><h3>Le mot à trouvé était : {st.session_state.word.upper()}.</h3>"
        )

col1, col2 = st.columns(2)
with col1:
    with st.expander("Description"):
        st.markdown(
            "Cette application implémente le Jeu du Pendu pour illustrer l'utilisation des sessions dans Streamlit."
        )
    st.header(f"MOT : {get_masked_word(st.session_state.word, st.session_state.letters)}")
    if st.session_state.end_status is None:
        options = [chr(i) for i in range(65, 91) if chr(i) not in st.session_state.letters]  # A-Z
        letter = st.pills(
            "Choisir une lettre",
            options,
            selection_mode="single",
            label_visibility="collapsed",
        )
        if letter:
            st.session_state.letters.add(letter)
            if letter in st.session_state.word:
                st.session_state.last_try_status = "SUCCESS"
                if all(letter in st.session_state.letters for letter in st.session_state.word):
                    st.session_state.end_status = "SUCCESS"
            else:
                st.session_state.lives -= 1
                st.session_state.last_try_status = "FAILURE"
                if st.session_state.lives == 0:
                    st.session_state.end_status = "FAILURE"
            st.rerun()
    else:
        st.html(st.session_state.message)
    st.header(f" VIE(S) : {st.session_state.lives * '❤️'}")
    if st.button("Nouvelle partie"):
        reset_session()
        st.rerun()

with col2:
    fig = go.Figure()
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        scaleanchor="y",
        scaleratio=1,
    )
    fig.update_yaxes(
        range=[0, 13],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    fig.update_layout(
        shapes=GALLOWS + HANGMAN[st.session_state.lives :],
        margin=dict(l=0, r=0, t=0, b=0),
    )

    st.plotly_chart(fig, config={"staticPlot": True})
