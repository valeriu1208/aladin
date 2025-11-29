import pandas as pd
import numpy as np
from pathlib import Path

# === 1. Cargar CSV ===
file_path = Path(__file__).parent.parent / "datasets" / "TABLA_ACCIDENTES_24.csv"
df = pd.read_csv(file_path, sep=';', encoding='latin1')

# === 2. Convertir TIPO_ACCIDENTE a numérico si es categórico ===
if df["TIPO_ACCIDENTE"].dtype == "object":
    df["TIPO_ACCIDENTE"] = df["TIPO_ACCIDENTE"].astype("category").cat.codes

# === 3. Reemplazar NaN por -1 (para tenerlos en cuenta) ===
df = df.replace(np.nan, -1)

# === 4. Seleccionar solo columnas numéricas ===
numeric_cols = df.select_dtypes(include=[np.number]).columns

# === 5. Calcular la correlación con TIPO_ACCIDENTE ===
correlations = df[numeric_cols].corr()["TIPO_ACCIDENTE"].drop("TIPO_ACCIDENTE")

# === 6. Media de correlaciones absolutas ===
mean_corr = correlations.abs().mean()

# === 7. Mantener columnas con correlación >= media ===
cols_to_keep = correlations[correlations.abs() >= mean_corr].index.tolist()

# Añadir columna objetivo
cols_to_keep = ["TIPO_ACCIDENTE"] + cols_to_keep

df_filtrado = df[cols_to_keep]

print("Correlaciones:")
print(correlations)
print("\nMedia:", mean_corr)
print("\nColumnas seleccionadas:", cols_to_keep)