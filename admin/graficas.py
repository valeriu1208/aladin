import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import seaborn as sns
from pyproj import Transformer
import folium
from streamlit_folium import st_folium
import requests

FASTAPI_URL = "http://127.0.0.1:8000/load"
FASTAPI_URL1 = "http://127.0.0.1:8000/reload"
# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(page_title="Zonas de Calor Barcelona", layout="wide")

# --------------------------------------------------
# CARGA Y PREPROCESADO (CACHEADO)
# --------------------------------------------------
@st.cache_data

def load_and_prepare_data():
    pd1= Path(__file__).parent.parent / "datasets" / "2024_1.csv"
    df = pd.read_csv(pd1)
    df = df.dropna(subset=['Coordenada_UTM_X_ED50','Coordenada_UTM_Y_ED50'])

    # Conversión UTM ED50 -> WGS84
    transformer = Transformer.from_crs("EPSG:23031", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(
        df['Coordenada_UTM_X_ED50'].values,
        df['Coordenada_UTM_Y_ED50'].values
    )
    df['lon'] = lon
    df['lat'] = lat

    # Densidad con KDTree
    coords = df[['Coordenada_UTM_X_ED50','Coordenada_UTM_Y_ED50']].values
    tree = KDTree(coords)
    counts = tree.query_radius(coords, r=500, count_only=True)

    df['accident_density'] = counts
    median = np.median(counts)
    df['hay_accidente'] = (counts > median).astype(int)

    return df

# --------------------------------------------------
# ENTRENAMIENTO DEL MODELO (CACHEADO)
# --------------------------------------------------
@st.cache_resource

def train_model(df):
    X = df[['Coordenada_UTM_X_ED50','Coordenada_UTM_Y_ED50']]
    y = df['hay_accidente']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    model = MLPClassifier(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    return model, scaler, X_test, y_test

# --------------------------------------------------
# CREAR MAPA (NO DEPENDE DEL THRESHOLD)
# --------------------------------------------------

def create_map(df):
    m = folium.Map(location=[41.387, 2.17], zoom_start=12, tiles="cartodbpositron")

    sample_df = df.sample(n=min(3000, len(df)), random_state=1)

    for row in sample_df.itertuples():
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=3,
            color='red' if row.hay_accidente == 1 else 'green',
            fill=True,
            fill_opacity=0.5
        ).add_to(m)
    return m

# --------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------
st.subheader("Data Actions")
col1, col2 , col3 = st.columns(3)
with st.form("Load or reload"):
    with col1:
        r = st.button("Load")
        if r:
            response = requests.post(FASTAPI_URL, timeout=10)
            st.success("Data Load was made correctly")
    with col2:
        s = st.button("Reload")
        if s:
            response = requests.post(FASTAPI_URL1, timeout=10)
            st.success("Data was Reloaded correctly")
df = load_and_prepare_data()
model, scaler, X_test, y_test = train_model(df)

# Sidebar
st.sidebar.title("⚙️ Configuración")
risk_threshold = st.sidebar.slider("Umbral de riesgo (%)", 0, 100, 60)

# --------------------------------------------------
# EVALUACIÓN DEPENDIENTE DEL THRESHOLD
# --------------------------------------------------

y_proba = model.predict_proba(X_test)[:,1] * 100
y_pred = (y_proba >= risk_threshold).astype(int)
accuracy = accuracy_score(y_test, y_pred)

# --------------------------------------------------
# INTERFAZ
# --------------------------------------------------

st.title("🚦 Zonas de Calor de Accidentes en Barcelona")
st.caption("App optimizada · Sin recálculos innecesarios · Mapas reales")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", f"{accuracy*100:.2f}%")
col2.metric("Zonas alto riesgo", int((df['hay_accidente']==1).sum()))
col3.metric("Zonas bajo riesgo", int((df['hay_accidente']==0).sum()))

# --------------------------------------------------
# MAPA (SESSION STATE)
# --------------------------------------------------

st.subheader("🗺️ Mapa de calor (interactivo)")

if "accident_map" not in st.session_state:
    st.session_state.accident_map = create_map(df)

st_folium(st.session_state.accident_map, width=1100, height=600)

# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Matriz de confusión**")
    cm = confusion_matrix(y_test, y_pred)
    labels = ["Seguro", "Peligro"]  # Etiquetas personalizadas
    fig_cm, ax_cm = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm,xticklabels=labels, yticklabels=labels)
    ax_cm.set_xlabel("Predicción")
    ax_cm.set_ylabel("Real")
    st.pyplot(fig_cm)

with col2:
    st.markdown("**Reporte de clasificación**")
    report = classification_report(y_test, y_pred, output_dict=True)
    st.dataframe(pd.DataFrame(report).transpose())

# --------------------------------------------------
# PREDICCIÓN PUNTUAL
# --------------------------------------------------

st.subheader("🔍 Predicción puntual")
colx, coly = st.columns(2)

with colx:
    x = st.number_input("UTM X", value=float(df.iloc[0]['Coordenada_UTM_X_ED50']))
with coly:
    y_val = st.number_input("UTM Y", value=float(df.iloc[0]['Coordenada_UTM_Y_ED50']))

if st.button("Predecir"):
    sample_scaled = scaler.transform([[x, y_val]])
    prob = model.predict_proba(sample_scaled)[0][1] * 100

    coords = df[['Coordenada_UTM_X_ED50','Coordenada_UTM_Y_ED50']].values
    tree = KDTree(coords)
    density = tree.query_radius([[x, y_val]], r=500, count_only=True)[0]

    st.write(f"Probabilidad de riesgo: **{prob:.2f}%**")
    st.write(f"Densidad local: **{density} accidentes**")

    if prob >= risk_threshold:
        st.error("⚠️ ZONA PELIGROSA")
    else:
        st.success("✅ ZONA SEGURA")