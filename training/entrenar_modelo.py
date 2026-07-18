import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import os

# 1. Cargar el dataset en español
if not os.path.exists("data/dataset_sintomas.csv"):
    print("Error: No se encontró 'data/dataset_sintomas.csv'. Ejecuta primero 'generar_dataset.py'.")
    exit()

df = pd.read_csv("data/dataset_sintomas.csv", encoding="utf-8")

# Mostrar información básica del dataset
print(f"Cargadas {len(df)} filas del dataset de síntomas.")

X = df['sintoma']
y = df['falla']

# 2. Vectorización del texto (TF-IDF)
# Convertimos el texto a números de forma que el modelo de Machine Learning lo entienda.
# Quitamos acentos y pasamos todo a minúsculas.
vectorizador = TfidfVectorizer(lowercase=True, strip_accents='unicode')
X_vectorizado = vectorizador.fit_transform(X)

# 3. Entrenar el modelo (Usamos Random Forest por ser muy robusto para clasificar texto pequeño)
# Dado que el dataset es pequeño para un split grande, lo entrenamos con todos los datos para la demo,
# pero imprimiremos el reporte de entrenamiento.
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_vectorizado, y)

# Evaluamos en el mismo set para confirmar que aprende los patrones básicos
predicciones = modelo.predict(X_vectorizado)
exactitud = accuracy_score(y, predicciones)
print(f"Exactitud del entrenamiento: {exactitud * 100:.2f}%")

# 4. Guardar el modelo y el vectorizador
# Esto nos permite cargar el "cerebro" entrenado en el script del Chatbot o la API sin re-entrenar.
os.makedirs("models", exist_ok=True)
joblib.dump(modelo, 'models/modelo_diagnostico.pkl')
joblib.dump(vectorizador, 'models/vectorizador_tfidf.pkl')

print("¡Modelo 'models/modelo_diagnostico.pkl' y Vectorizador 'models/vectorizador_tfidf.pkl' guardados con éxito!")
