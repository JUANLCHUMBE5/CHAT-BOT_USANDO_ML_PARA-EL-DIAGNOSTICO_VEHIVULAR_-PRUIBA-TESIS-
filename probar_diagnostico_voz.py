import os
import joblib

# Intentamos importar la librería de reconocimiento de voz.
# Si no está instalada, le indicaremos al usuario cómo instalarla.
try:
    import speech_recognition as sr
except ImportError:
    print("=" * 70)
    print("¡Falta instalar la librería de reconocimiento de voz!")
    print("Para continuar, ejecuta el siguiente comando en tu terminal:")
    print("pip install SpeechRecognition")
    print("=" * 70)
    exit()

# 1. Cargar el modelo y vectorizador previamente entrenados
if not os.path.exists("modelo_diagnostico.pkl") or not os.path.exists("vectorizador_tfidf.pkl"):
    print("Error: Primero debes entrenar el modelo en tu notebook o ejecutando entrenar_modelo.py")
    exit()

modelo = joblib.load('modelo_diagnostico.pkl')
vectorizador = joblib.load('vectorizador_tfidf.pkl')

# Archivo de audio de prueba
nombre_audio = "grabacion.wav"

print("=" * 70)
print("PRUEBA DE DIAGNÓSTICO POR VOZ (SPEECH-TO-TEXT + MACHINE LEARNING)")
print(f"Buscando el archivo de audio: '{nombre_audio}' en la carpeta del proyecto...")
print("=" * 70)

if not os.path.exists(nombre_audio):
    print(f"\n[!] INSTRUCCIÓN:")
    print(f"Para hacer la prueba, graba un audio con tu voz diciendo un síntoma")
    print(f"(ejemplo: 'tengo un chillido fuerte en los frenos' o 'el motor esta cascabeleando').")
    print(f"Guarda ese archivo en formato WAV con el nombre '{nombre_audio}' en esta misma carpeta.")
    print("\n*Puedes usar la aplicación 'Grabadora de voz' de Windows y renombrar el archivo.*")
    exit()

# 2. Inicializar el reconocedor de voz de Google (Gratuito, no requiere API Key)
reconocedor = sr.Recognizer()

try:
    print("\n[Paso 1] Leyendo el archivo de audio...")
    with sr.AudioFile(nombre_audio) as origen:
        audio_data = reconocedor.record(origen)
        
    print("[Paso 2] Transcribiendo voz a texto (Google Speech recognition)...")
    # Reconocer texto en español
    texto_transcrito = reconocedor.recognize_google(audio_data, language="es-PE")
    
    print("-" * 60)
    print(f"Texto Transcrito: \"{texto_transcrito}\"")
    print("-" * 60)
    
    # 3. Pasar el texto transcrito al clasificador de Machine Learning
    entrada_vec = vectorizador.transform([texto_transcrito])
    prediccion = modelo.predict(entrada_vec)[0]
    probabilidades = modelo.predict_proba(entrada_vec)
    confianza = max(probabilidades[0])
    
    print("\n[Paso 3] Procesando diagnóstico con Machine Learning...")
    print("*" * 60)
    print(f"Diagnóstico de Falla: {prediccion}")
    print(f"Confianza de la IA: {confianza * 100:.2f}%")
    print("*" * 60)
    
except sr.UnknownValueError:
    print("\nError: No se pudo entender el audio. Asegúrate de hablar claro y sin mucho ruido.")
except sr.RequestError as e:
    print(f"\nError de conexión con el servicio de transcripción: {e}")
except Exception as ex:
    print(f"\nOcurrió un error inesperado: {ex}")
