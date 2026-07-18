import joblib
import os

# Cargar el modelo y el vectorizador
if not os.path.exists("modelo_diagnostico.pkl") or not os.path.exists("vectorizador_tfidf.pkl"):
    print("Error: No se encontraron los archivos del modelo. Ejecuta primero 'generar_dataset.py' y 'entrenar_modelo.py'.")
    exit()

modelo = joblib.load('modelo_diagnostico.pkl')
vectorizador = joblib.load('vectorizador_tfidf.pkl')

print("=" * 60)
print("SISTEMA DE PREDICCIÓN DE DIAGNÓSTICO VEHICULAR (PROTOTIPO ML)")
print("Escribe el síntoma que notas en el auto para predecir la falla.")
print("Escribe 'salir' para finalizar.")
print("=" * 60)

while True:
    entrada = input("\nIntroduce síntoma: ")
    if entrada.lower() == 'salir':
        break
    
    # 1. Transformar la entrada del usuario usando el mismo vectorizador
    entrada_vec = vectorizador.transform([entrada])
    
    # 2. Predecir la falla y la probabilidad
    prediccion = modelo.predict(entrada_vec)[0]
    probabilidades = modelo.predict_proba(entrada_vec)
    clases = modelo.classes_
    
    # Obtener el porcentaje de confianza
    max_prob = max(probabilidades[0])
    
    print("-" * 50)
    print(f"Diagnóstico Sugerido: {prediccion}")
    print(f"Confianza del modelo: {max_prob * 100:.2f}%")
    print("-" * 50)
