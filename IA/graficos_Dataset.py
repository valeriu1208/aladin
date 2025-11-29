# ============================================
# Análisis Exploratorio de Datos (EDA)
# Dataset: TABLA_ACCIDENTES_24.XLSX
# ============================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuración general
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10,6)

file_path= Path (__file__).parent.parent / "datasets" / "TABLA_ACCIDENTES_242.xlsx"
# 1. Cargar el dataset
df = pd.read_excel(file_path)



# ============================================
# 1. Gráfico de barras para TIPO_ACCIDENTE
plt.figure()
sns.countplot(data=df, x='TIPO_ACCIDENTE', order=df['TIPO_ACCIDENTE'].value_counts().index, palette='viridis')
plt.title('Distribución por tipo de accidente')
plt.xlabel('Tipo de accidente')
plt.ylabel('Cantidad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ============================================
# 2. Gráfico de barras para DÍA_SEMANA
plt.figure()
sns.countplot(data=df, x='DIA_SEMANA', order=df['DIA_SEMANA'].value_counts().index, palette='magma')
plt.title('Distribución de accidentes por día de la semana')
plt.xlabel('Día de la semana')
plt.ylabel('Cantidad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ============================================
# 3. Histograma para Nº_VÍCTIMAS
plt.figure()
sns.histplot(df['TOTAL_VICTIMAS_30DF'], bins=20, kde=True, color='blue')
plt.title('Distribución del número de víctimas  por accidente')
plt.xlabel('Número de víctimas')
plt.ylabel('Frecuencia')
plt.tight_layout()
plt.xlim(0,5)
plt.show()


# ============================================
# 4. Histograma para carreteras con más accidentes (excluyendo "No inventariada")

# Filtrar carreteras excluyendo "No inventariada"
df_filtrado = df[df['CARRETERA'] != 'No inventariada']

# Agrupar por carretera y contar accidentes
accidentes_por_carretera = df_filtrado['CARRETERA'].value_counts().head(10)

# Configuración general
sns.set(style="whitegrid")
plt.figure(figsize=(12,8))

# Gráfico de barras horizontal
sns.barplot(x=accidentes_por_carretera.values, y=accidentes_por_carretera.index, palette='coolwarm')
plt.title('Top 10 carreteras con más accidentes (sin No inventariada)')
plt.xlabel('Número de accidentes')
plt.ylabel('Carretera')
plt.tight_layout()
plt.show()

# Mostrar resultados en consola
print("Top 10 carreteras con más accidentes (sin No inventariada):")
print(accidentes_por_carretera)
