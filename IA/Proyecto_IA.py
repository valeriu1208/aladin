import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


file_path = Path(__file__).parent.parent / "datasets" / "TABLA_ACCIDENTES_24.csv"
if not file_path.exists():
	raise FileNotFoundError(f"Dataset not found at {file_path}. Please check the path.")

df = pd.read_csv(file_path, sep=';', encoding='latin1')

# Matriz de correlación (solo columnas numéricas) y heatmap
corrmat = df.corr(numeric_only=True)
print("Matriz de correlación (primeras filas):")
print(corrmat.head())

# ---- Estadísticas rápidas: máxima correlación entre pares distintos ----
n = corrmat.shape[0]
if n == 0:
	print("No hay columnas numéricas para calcular correlaciones.")
else:
	mask = ~np.eye(n, dtype=bool)
	masked = corrmat.where(mask)
	if masked.isnull().all().all():
		print("No hay pares de columnas numéricas para calcular la correlación fuera de la diagonal.")
	else:
		max_pair = masked.stack().idxmax()
		max_value = masked.stack().max()
		print(f"Máxima correlación entre {max_pair[0]} y {max_pair[1]}: {max_value:.4f}")

		abs_masked = corrmat.abs().where(mask)
		abs_pair = abs_masked.stack().idxmax()
		abs_value = abs_masked.stack().max()
		orig_value = corrmat.loc[abs_pair[0], abs_pair[1]]
		print(f"Máxima correlación en valor absoluto entre {abs_pair[0]} y {abs_pair[1]}: {orig_value:.4f} (|r|={abs_value:.4f})")

	# ---- Visualización: dividir en bloques si la matriz es grande ----
	out_dir = Path(__file__).parent.parent / "outputs"
	out_dir.mkdir(parents=True, exist_ok=True)

	# Umbral para decidir si particionar: si más de 30 variables numéricas, dividir
	TILE = 25
	if n <= 30:
		# Figura única, tamaño adaptado al número de variables
		fig_size = (max(10, n * 0.35), max(8, n * 0.35))
		plt.figure(figsize=fig_size)
		sns.heatmap(corrmat, vmax=.8, square=True, annot=True, cmap="coolwarm")
		plt.title("Matriz de Correlación - TABLA_ACCIDENTES_24")
		plt.tight_layout()
		out_path = out_dir / "correlation_tabla_accidentes_24.png"
		plt.savefig(out_path, dpi=200)
		plt.close()
		print(f"Heatmap guardado en: {out_path} (figsize={fig_size})")
	else:
		# Dividir en bloques TILE x TILE y guardar cada bloque por separado
		cols = list(corrmat.columns)
		saved_files = []
		for i in range(0, n, TILE):
			for j in range(0, n, TILE):
				sub = corrmat.iloc[i:i+TILE, j:j+TILE]
				if sub.size == 0:
					continue
				# Evitar anotaciones si el bloque es grande (hace ilegible)
				annotate = sub.shape[0] <= 20 and sub.shape[1] <= 20
				w = max(4, sub.shape[1] * 0.35)
				h = max(4, sub.shape[0] * 0.35)
				fig, ax = plt.subplots(figsize=(w, h))
				sns.heatmap(sub, vmax=.8, square=True, annot=annotate, cmap="coolwarm", ax=ax,
							cbar=True)
				r0 = i
				r1 = i + sub.shape[0] - 1
				c0 = j
				c1 = j + sub.shape[1] - 1
				ax.set_title(f"Corr cols {r0}-{r1} vs {c0}-{c1}")
				fig.tight_layout()
				block_path = out_dir / f"correlation_tabla_accidentes_24_block_{r0}_{c0}.png"
				fig.savefig(block_path, dpi=200)
				plt.close(fig)
				saved_files.append(block_path)

		if saved_files:
			print(f"Se guardaron {len(saved_files)} bloques de correlación en: {out_dir}")
			# Mostrar los primeros 5 archivos creados
			for p in saved_files[:5]:
				print(f"  - {p}")
		else:
			print("No se generaron bloques de correlación.")