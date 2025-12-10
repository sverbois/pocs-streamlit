import streamlit as st

st.title("Streamlit POCs")
st.write("Utilisez la navigation pour accéder aux différents POCs.")

st.header("Pour tester localement")
st.code(
    """
git clone https://github.com/sverbois/pocs-streamlit.git
cd pocs-streamlit
make start""",
    language="bash",
)
