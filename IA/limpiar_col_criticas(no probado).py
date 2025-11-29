import pandas as pd
from pathlib import Path

# Cargar el dataset
file_path= Path (__file__).parent.parent / "datasets" / "TABLA_ACCIDENTES_24.XLSX"
df = pd.read_excel(file_path)

# 1. Mostrar porcentaje de valores nulos por columna
nulos_por_columna = df.isnull().mean() * 100
print("Porcentaje de valores nulos por columna:\n")
print(nulos_por_columna.sort_values(ascending=False))

# 2. Identificar columnas críticas (ejemplo: FECHA_ACCIDENTE, CARRETERA, TIPO_ACCIDENTE)
columnas_criticas = ['FECHA_ACCIDENTE', 'CARRETERA', 'TIPO_ACCIDENTE']

# 3. Eliminar filas con nulos en columnas críticas
df_limpio = df.dropna(subset=columnas_criticas)

# 4. Opcional: eliminar filas con nulos en TODAS las columnas
# df_limpio = df.dropna()

# 5. Mostrar dimensiones antes y después
print(f"Dimensiones originales: {df.shape}")
print(f"Dimensiones después de limpieza: {df_limpio.shape}")

# 6. Exportar dataset limpio a Excel
df_limpio.to_excel("TABLA_ACCIDENTES_24_LIMPIO.xlsx", index=False)
print("Dataset limpio exportado como TABLA_ACCIDENTES_24_LIMPIO.xlsx")