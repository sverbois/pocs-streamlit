from threading import Thread

import pandas as pd
import requests
import streamlit as st

BASE_ODWB_SEARCH_URL = "https://www.odwb.be/api/explore/v2.1/catalog/datasets/namur-arbres/records?where=nom_simplifie IS NOT NULL and hauteur IS NOT NULL"


@st.cache_data(show_spinner=False)
def load_data_from_odwb():
    def get_page_number():  # Nombre de pages à récupérer de 100 enregistrements par page
        response = requests.get(f"{BASE_ODWB_SEARCH_URL}&limit=0")
        page_number = (response.json()["total_count"] // 100) + 1
        return min(page_number, 100)  # offset + limit doit rester < 10000

    page_number = get_page_number()
    odwb_data = []
    threads = [ODWBDataLoader(page) for page in range(page_number)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for thread in threads:
        odwb_data.extend(thread.results)
    return odwb_data


class ODWBDataLoader(Thread):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.results = []

    def load_data(self):
        offset = self.page * 100  # OWDB limite les requêtes à 100 enregistrements
        url = f"{BASE_ODWB_SEARCH_URL}&limit=100&offset={offset}"
        response = requests.get(url)
        return response.json()["results"]

    def run(self):
        self.results = self.load_data()


def filter_data(data, name=None, locality=None, min_height=0):
    # Commencer avec un masque qui sélectionne toutes les lignes
    mask = pd.Series([True] * len(data), index=data.index)
    # Appliquer le filtre par nom vernaculaire
    if name is not None:
        mask = mask & (data["nom_simplifie"] == name)
    # Appliquer le filtre par localité
    if locality is not None:
        mask = mask & (data["acom_nom_m"] == locality)
    # Appliquer le filtre par hauteur minimale
    if min_height > 0:
        mask = mask & (data["hauteur"] >= min_height)
    # Appliquer le masque final une seule fois
    return data[mask]


st.set_page_config(page_title="Arbres de Namur", layout="wide")
st.title("Arbres de la ville de Namur")
with st.expander("Description"):
    st.markdown("Petite application Streamlit de visualisation des données des arbres de la ville de Namur.")

with st.spinner("Chargement des données...", show_time=True):
    odwb_data = load_data_from_odwb()

data = pd.json_normalize(odwb_data)

# Renommer les colonnes pour l'utilisation de st.map
if "geo_point_2d.lat" in data.columns and "geo_point_2d.lon" in data.columns:
    data = data.rename(columns={"geo_point_2d.lat": "latitude", "geo_point_2d.lon": "longitude"})

st.header("Sélection d'arbres")
with st.container(horizontal=True):
    name_filter = st.selectbox(
        label="Type",
        index=None,
        placeholder="Tous",
        options=sorted(data["nom_simplifie"].dropna().unique().tolist()),
    )
    locality_filter = st.selectbox(
        label="Localité",
        index=None,
        placeholder="Toutes",
        options=sorted(data["acom_nom_m"].dropna().unique().tolist()),
    )
    min_height_filter = st.slider(
        label="Hauteur minimale (m)",
        min_value=0,
        max_value=int(data["hauteur"].max()),
        value=0,
    )


filtered_data = filter_data(
    data,
    name=name_filter,
    locality=locality_filter,
    min_height=min_height_filter,
)

st.subheader(f"Nombre d'arbres dans la sélection : {len(filtered_data)}")
st.dataframe(filtered_data)

st.subheader("Localisation des arbres de la sélection")
st.map(filtered_data, latitude="latitude", longitude="longitude", zoom=11, size=1, color="#198754")

st.subheader("Nombre d'arbres en fonction de la hauteur dans la sélection")
height_counts = filtered_data[filtered_data["hauteur"] > 0]["hauteur"].astype(int).value_counts().sort_index()
st.bar_chart(
    height_counts,
    x_label="Hauteur (m)",
    y_label="Nombre d'arbres",
)

st.divider()

st.header("Arbres par localité")
st.scatter_chart(
    data[data["hauteur"] > 0],
    x="acom_nom_m",
    y="hauteur",
    x_label="Localité",
    y_label="Hauteur (m)",
)
