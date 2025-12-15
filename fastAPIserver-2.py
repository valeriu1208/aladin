#En aquest arxiu definirem la API que s'encargará de rebre les sol.licituds i procesarlas amb la IA que implementarem més endevant
#Per poder fer servir la API en cuestió fem servir "uvicorn fastAPIserver:app --reload" i s'obrirá en local
#Abans de tot, farem servir les llibreries de FastAPI que es una manera fácil i sentzilla de poder crearla
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from scipy.spatial.distance import cdist
import pickle
import unicodedata

# API app
app = FastAPI()

# Globals to hold data and model
_DATA_CSV = Path(__file__).parent / "datasets" / "2024_1.csv"
pickle_iris = Path(__file__).parent / "datasets" / "pickle_model_iris.pkl"
pickle_scaler = Path(__file__).parent / "datasets" / "pickle_model_scaler.pkl"
pickle_model = Path(__file__).parent / "datasets" / "pickle_model_Madrid.pkl"
pickle_median_density = Path(__file__).parent / "datasets" / "pickle_model_median_density.pkl"
pickle_training_radius = Path(__file__).parent / "datasets" / "pickle_model_training_radius.pkl"
iris = None
scaler = None
model = None
median_density = None
training_radius = None
coord_x_col = None
coord_y_col = None


class PredictRequest(BaseModel):
    x: float
    y: float
    risk_threshold: Optional[float] = 60.0
    radius: Optional[int] = 500


def _calculate_density_for_df(df, radius=500):
    # detect coordinate columns dynamically
    xcol, ycol = _detect_coordinate_columns(df)
    coords = df[[xcol, ycol]].to_numpy()
    # pairwise distances (may use memory but dataset is a city year)
    d = cdist(coords, coords, metric='euclidean')
    densities = (d < radius).sum(axis=1)
    return densities


def _detect_coordinate_columns(df):
    """Detect common coordinate column names in a dataframe and return (xcol, ycol)."""
    def _normalize(s: str) -> str:
        s = str(s)
        s = s.strip().lower()
        # remove accents
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(ch for ch in s if not unicodedata.combining(ch))
        # replace non-alnum with underscore
        s = ''.join(ch if ch.isalnum() else '_' for ch in s)
        # collapse underscores
        while '__' in s:
            s = s.replace('__', '_')
        return s.strip('_')

    # build map normalized -> original
    norm_map = { _normalize(c): c for c in df.columns }

    # candidate normalized names (cover common variations)
    candidates = [
        ('coordenada_x_utm', 'coordenada_y_utm'),
        ('coordenada_utm_x_ed50', 'coordenada_utm_y_ed50'),
        ('utm_x', 'utm_y'),
        ('longitud', 'latitud'),
        ('x', 'y'),
    ]

    for nx, ny in candidates:
        if nx in norm_map and ny in norm_map:
            return norm_map[nx], norm_map[ny]

    # fallback: try to find any pair where names contain coord/utm/x and coord/utm/y
    cols_norm = list(norm_map.keys())
    for a in cols_norm:
        for b in cols_norm:
            if a != b and (('coord' in a) or ('coorden' in a) or ('utm' in a) or a == 'x') and (('coord' in b) or ('coorden' in b) or ('utm' in b) or b == 'y'):
                return norm_map[a], norm_map[b]

    raise ValueError('No se pudieron detectar columnas de coordenadas en el dataset. Columnas disponibles: ' + ', '.join(df.columns))


def load_and_train(csv_path: Optional[Path] = None, radius: int = 500, xcol: Optional[str] = None, ycol: Optional[str] = None):
    """Carga el CSV, calcula densidad, crea la variable binaria y entrena el modelo.
    Esta función no imprime nada (pensada para uso por la API).
    """
    global iris, scaler, model, median_density

    csv_path = csv_path or _DATA_CSV
    # try to infer separator (some CSVs use commas, others semicolons)
    df = pd.read_csv(csv_path, sep=None, engine='python')
    # Detect coordinate columns and ensure they exist (or use provided)
    if xcol is None or ycol is None:
        try:
            xcol, ycol = _detect_coordinate_columns(df)
        except Exception as e:
            # surface a clearer error
            raise ValueError(f"No se pudieron detectar columnas de coordenadas: {e}")
    else:
        # validate provided names exist
        if xcol not in df.columns or ycol not in df.columns:
            raise ValueError(f"Columnas proporcionadas no encontradas en CSV: {xcol}, {ycol}")

    globals()['coord_x_col'] = xcol
    globals()['coord_y_col'] = ycol
    # El dataset ya contiene solo registros de accidentes; solo necesitamos coordenadas
    df = df.dropna(subset=[xcol, ycol])

    # calcular densidad
    df['accident_density'] = _calculate_density_for_df(df, radius=radius)

    # binaria: alto riesgo si density > median
    median_density = df['accident_density'].median()
    df['hay_accidente'] = (df['accident_density'] > median_density).astype(int)

    # features y target
    X = df[[xcol, ycol]]
    y = df['hay_accidente']

    # normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # entrenar modelo simple
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.02, random_state=1, stratify=y)
    model = MLPClassifier(alpha=1, max_iter=1000)
    model.fit(X_train, y_train)

    # guardar en globals
    iris = df
    globals()['scaler'] = scaler
    globals()['model'] = model
    globals()['median_density'] = median_density
    globals()['training_radius'] = radius

@app.get('/load')
@app.post('/load')
def load_from_pickle():
    """Intenta cargar los modelos desde pickle. Si existen y son válidos, los carga."""
    global iris, scaler, model, median_density, training_radius
    try:
        if pickle_model.exists() and pickle_iris.exists() and pickle_scaler.exists() and pickle_median_density.exists():
            with open(pickle_model, 'rb') as f:
                model = pickle.load(f)
            with open(pickle_iris, 'rb') as f:
                iris = pickle.load(f)
            with open(pickle_scaler, 'rb') as f:
                scaler = pickle.load(f)
            with open(pickle_median_density, 'rb') as f:
                median_density = pickle.load(f)
            if pickle_training_radius.exists():
                with open(pickle_training_radius, 'rb') as f:
                    training_radius = pickle.load(f)
            globals()['model'] = model
            globals()['iris'] = iris
            globals()['scaler'] = scaler
            globals()['median_density'] = median_density
            # detect and store coordinate column names
            try:
                cx, cy = _detect_coordinate_columns(iris)
                globals()['coord_x_col'] = cx
                globals()['coord_y_col'] = cy
            except Exception:
                globals()['coord_x_col'] = None
                globals()['coord_y_col'] = None
            globals()['training_radius'] = training_radius
            return True
    except Exception:
        pass
    return False




def _predict_from_model(x: float, y: float, risk_threshold: float = 60.0, radius: int = 500):
    """Usada internamente por el endpoint predict. Devuelve dict listo para JSON."""
    if iris is None or model is None or scaler is None:
        raise RuntimeError('Modelo no cargado')

    sample = np.array([[x, y]])
    sample_scaled = scaler.transform(sample)
    probs = model.predict_proba(sample_scaled)[0]
    # probability of class 1 (alto riesgo)
    accident_probability = float(probs[1] * 100) if len(probs) > 1 else float(max(probs) * 100)

    # density real
    # Use detected coordinate columns
    xcol = coord_x_col if coord_x_col is not None else _detect_coordinate_columns(iris)[0]
    ycol = coord_y_col if coord_y_col is not None else _detect_coordinate_columns(iris)[1]
    distances = np.sqrt((iris[xcol] - x) ** 2 + (iris[ycol] - y) ** 2)
    actual_density = int((distances < radius).sum())

    is_dangerous = accident_probability >= float(risk_threshold)

    return {
        'x': x,
        'y': y,
        'radius': radius,
        'probability_percent': accident_probability,
        'density_within_radius': actual_density,
        'risk_threshold': float(risk_threshold),
        'is_dangerous': bool(is_dangerous),
        'trained_radius': training_radius,
        'trained_median_density': median_density
    }

@app.post('/predict')
def predict(req: PredictRequest):
    try:
        res = _predict_from_model(req.x, req.y, risk_threshold=req.risk_threshold, radius=req.radius)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/predict')
def predict_get(x: float, y: float, risk_threshold: float = 60.0, radius: int = 500):
    """Endpoint GET para predecir usando parámetros de consulta: /predict?x=...&y=...&risk_threshold=..."""
    try:
        res = _predict_from_model(x, y, risk_threshold=risk_threshold,radius=radius)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/reload')
@app.post('/reload')
def reload_data(radius: int = 500, xcol: Optional[str] = None, ycol: Optional[str] = None):
    try:
        load_and_train(radius=radius, xcol=xcol, ycol=ycol)
        # Guardar modelos con pickle abriendo los archivos correctamente
        with open(pickle_model, 'wb') as f:
            pickle.dump(model, f)
        with open(pickle_iris, 'wb') as f:
            pickle.dump(iris, f)
        with open(pickle_scaler, 'wb') as f:
            pickle.dump(scaler, f)
        with open(pickle_median_density, 'wb') as f:
            pickle.dump(median_density, f)
        with open(pickle_training_radius, 'wb') as f:
            pickle.dump(radius, f)

        return {
            'status': 'ok',
            'message': f'CSV recargado y modelo reentrenado. Archivos guardados en: {pickle_model.parent}',
            'radius': radius,
            'trained_radius': training_radius,
            'median_density': median_density,
            'coord_x_col': coord_x_col,
            'coord_y_col': coord_y_col,
            'n_samples': len(iris) if iris is not None else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/info')
def info():
    """Devuelve información del modelo cargado actual y metadatos."""
    return {
        'model_loaded': bool(model is not None),
        'n_samples': len(iris) if iris is not None else 0,
        'trained_radius': training_radius,
        'median_density': median_density,
        'coord_x_col': coord_x_col,
        'coord_y_col': coord_y_col,
    }
