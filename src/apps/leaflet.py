from threading import Thread

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

st.title("POC Leaflet")
with st.expander("Description"):
    st.markdown(
        "Cette application illustre l'utilisation de threads pour charger des données depuis l'API ODWB et les afficher sur une carte Leaflet."
    )


@st.cache_data(show_spinner=False)
def get_data_for_province(page):
    ODWB_API_URL = "https://www.odwb.be/api/explore/v2.1/catalog/datasets/communes_s3/records"
    offset = (page - 1) * 100
    url = f"{ODWB_API_URL}?limit=100&offset={offset}"
    return requests.get(url).json()["results"]


class ODWBDataLoader(Thread):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.results = []

    def run(self):
        self.results = get_data_for_province(self.page)


with st.spinner("Chargement des données...", show_time=True):
    odwb_data = []
    threads = [ODWBDataLoader(page) for page in [1, 2, 3]]  # 261 communes, 100 par page
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for thread in threads:
        odwb_data.extend(thread.results)

data = pd.DataFrame(odwb_data)

sorted_names = sorted(data["nom"])
namur_position = sorted_names.index("Namur")
name = st.selectbox(
    label="Choisir une commune",
    label_visibility="collapsed",
    index=namur_position,
    options=sorted_names,
)

if name:
    municipality = data[data["nom"] == name].copy()
    col1, col2 = st.columns(2)
    with col1:
        # Créer un DataFrame transposé avec conversion de types pour éviter les erreurs PyArrow
        municipality.index = municipality["nom_court"]
        # Transposer et convertir tous les types en string pour éviter les erreurs PyArrow
        transposed = municipality.T
        transposed.columns = [str(col) for col in transposed.columns]
        # Convertir toutes les valeurs en string pour assurer la compatibilité PyArrow
        for col in transposed.columns:
            transposed[col] = transposed[col].astype(str)
        st.dataframe(transposed)
    with col2:
        # Récupérer les données géométriques de la commune
        geom_data = municipality.iloc[0]["geom"]
        latitude = municipality.iloc[0]["geopoint_administration"]["lat"]
        longitude = municipality.iloc[0]["geopoint_administration"]["lon"]
        # Centrer la carte sur la commune sélectionnée
        map = folium.Map(location=[latitude, longitude], zoom_start=11)
        # Ajouter le MultiPolygon de la commune
        folium.GeoJson(
            geom_data,
            style_function=lambda feature: {
                "fillColor": "lightblue",
                "color": "blue",
                "weight": 2,
                "fillOpacity": 0.3,
            },
            popup=folium.Popup(municipality.iloc[0]["nom_court"], parse_html=True),
            tooltip=municipality.iloc[0]["nom_court"],
        ).add_to(map)
        # Ajouter un marqueur pour le point d'administration
        folium.Marker(
            [latitude, longitude],
            popup="Administration",
            icon=folium.Icon(icon="home", color="blue"),
        ).add_to(map)
        # Afficher la carte avec st_folium
        st_folium(map, width=800, height=400)
