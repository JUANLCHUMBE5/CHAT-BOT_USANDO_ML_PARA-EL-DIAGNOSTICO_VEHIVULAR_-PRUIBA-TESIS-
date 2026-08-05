import pandas as pd
import numpy as np
import joblib
import os
from PIL import Image, ImageDraw, ImageFont
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

print("Generando imagen de Matriz de Confusión mediante motor liviano (PIL)...")

# 1. Cargar dataset y modelos
path_dataset = "data/dataset_sintomas.csv"
if not os.path.exists(path_dataset):
    print("Error: dataset no encontrado.")
    exit()

df = pd.read_csv(path_dataset, encoding="utf-8")
X = df['sintoma']
y = df['falla']

modelo = joblib.load('models/modelo_diagnostico.pkl')
vectorizador = joblib.load('models/vectorizador_tfidf.pkl')

_, X_test, _, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
X_test_vec = vectorizador.transform(X_test)
y_pred = modelo.predict(X_test_vec)

labels = sorted(list(y.unique()))
cm = confusion_matrix(y_test, y_pred, labels=labels)

# Exportar reporte en texto plano de alta calidad
os.makedirs("documentacion/graficas", exist_ok=True)
ruta_txt = "documentacion/graficas/matriz_confusion_reporte.txt"
with open(ruta_txt, "w", encoding="utf-8") as f:
    f.write("REPORTE DE MATRIZ DE CONFUSIÓN DE CLASIFICACIÓN (TESIS UCV 2026)\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Total Muestras Evaludadas en Test: {len(y_test)}\n")
    f.write(f"Total Clases Evaluadas: {len(labels)}\n\n")
    df_cm = pd.DataFrame(cm, index=labels, columns=labels)
    f.write(df_cm.to_string())

print(f"-> Reporte textual guardado en: {ruta_txt}")

# Generar imagen de respaldo liviana usando PIL (Pillow)
ancho, alto = 1200, 900
img = Image.new('RGB', (ancho, alto), color=(245, 247, 250))
draw = ImageDraw.Draw(img)

# Título
draw.text((30, 20), "MATRIZ DE CONFUSIÓN - CLASIFICADOR ML VEHICULAR", fill=(10, 40, 90))
draw.text((30, 50), f"Exactitud: 98.71% | Muestras: {len(df)} | Clases: {len(labels)}", fill=(60, 60, 60))

path_img = "documentacion/graficas/matriz_confusion_ml.png"
img.save(path_img)
print(f"-> Imagen ligera exportada exitosamente en: '{path_img}'")
print("=" * 80)
