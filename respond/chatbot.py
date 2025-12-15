import streamlit as st
import requests
from groq import Groq
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pyproj import Transformer
# ---------------- CONFIGURACIÓN ----------------
FASTAPI_URL = "http://127.0.0.1:8000/predict"

client = Groq(api_key=st.secrets["auth"]["GROQ_API_KEY"])

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Eres un asistente experto en seguridad vial y análisis de zonas urbanas."
        }
    ]

if "model" not in st.session_state:
    st.session_state.model = "llama-3.1-8b-instant"

# ---------------- UTILIDADES ----------------
def extraer_coordenadas(texto: str):
    """
    Extrae dos números del texto (x, y).
    Ejemplo esperado: '432100 4589200'
    """
    numeros = re.findall(r"-?\d+\.?\d*", texto)
    if len(numeros) >= 2:
        return float(numeros[0]), float(numeros[1])
    return None, None


def consultar_fastapi(x: float, y: float) -> dict:
    payload = {
        "x": x,
        "y": y
    }

    response = requests.post(FASTAPI_URL, json=payload, timeout=10)

    if response.status_code != 200:
        raise RuntimeError("Error consultando FastAPI")

    return response.json()

def consultar_fastapi1(texto: str) -> dict:
    geolocator1 = Nominatim(user_agent="Finder1")
    gtcode = RateLimiter(geolocator1.geocode, min_delay_seconds=1)
    textinfo = gtcode(texto)
    latitud,longitud = textinfo.latitude, textinfo.longitude
    transformer = Transformer.from_crs(
        "EPSG:4326",     # WGS84 lat/lon
        "EPSG:23031",    # ED50 / UTM zone 30N
        always_xy=True)
    x,y = transformer.transform(longitud,latitud)
    return x,y

def construir_prompt_groq(resultado: dict) -> str:
    return f"""
Se han analizado datos reales de accidentes de tráfico para una zona concreta.

Resultados:
- Probabilidad de accidente: {resultado['probability_percent']:.2f}%
- Accidentes cercanos en el radio analizado: {resultado['density_within_radius']}
- ¿Zona peligrosa?: {"Sí" if resultado['is_dangerous'] else "No"}

Explica este resultado al usuario de forma clara y comprensible,
e incluye una recomendación práctica.
"""


# ---------------- UI ----------------
st.title("Chatbot de Seguridad Vial")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- INPUT USUARIO ----------------
if prompt := st.chat_input("Introduce coordenadas o pregunta por una zona (ej. 432100 4589200)"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    x, y = extraer_coordenadas(prompt)
    if x is None or y is None:
        x,y = consultar_fastapi1(prompt)
        print(x,y)
    with st.chat_message("assistant"):
        if x is None or y is None:
            respuesta = "Por favor, introduce dos coordenadas numéricas (x y)."
            st.markdown(respuesta)
        else:
            # 1️⃣ FastAPI
            resultado = consultar_fastapi(x, y)

            # 2️⃣ Construir prompt para Groq
            prompt_groq = construir_prompt_groq(resultado)

            # 3️⃣ Groq genera explicación
            stream = client.chat.completions.create(
                model=st.session_state.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en seguridad vial urbana."},
                    {"role": "user", "content": prompt_groq}
                ],
                stream=True
            )

            response_text = ""
            container = st.empty()

            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    response_text += delta.content
                    container.markdown(response_text)

            respuesta = response_text

        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta}
        )
