import os
import joblib
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import numpy as np

# 1. Configuración de Grabación
frecuencia = 44100  # Frecuencia de muestreo estándar
archivo_salida = "grabacion.wav"

# 2. Cargar el modelo de diagnóstico
if not os.path.exists("modelo_diagnostico.pkl") or not os.path.exists("vectorizador_tfidf.pkl"):
    print("Error: Primero debes entrenar el modelo (ejecuta entrenar_modelo.py o notebook.ipynb).")
    exit()

modelo = joblib.load('modelo_diagnostico.pkl')
vectorizador = joblib.load('vectorizador_tfidf.pkl')

print("=" * 70)
print("🎙️ SISTEMA DE GRABACIÓN ILIMITADA Y DIAGNÓSTICO EN VIVO")
print("=" * 70)
print("Ahora la grabación no se detendrá sola. Habla a tu ritmo.")
print("Cuando termines de hablar, presiona ENTER para detener la grabación.")
print("-" * 70)

input("\nPresiona ENTER cuando estés listo para comenzar a hablar...")

# Lista para almacenar los bloques de audio grabados
bloques_audio = []

# Función Callback para capturar el flujo de audio del micrófono en tiempo real
def callback_grabacion(indata, frames, time, status):
    if status:
        print(status)
    bloques_audio.append(indata.copy())

# Iniciar la grabación de forma no bloqueante (continua)
print("\n🔴 [GRABANDO...] Habla ahora. Presiona ENTER cuando termines.")
print("=" * 50)

# Abrimos el flujo de entrada de audio
stream = sd.InputStream(samplerate=frecuencia, channels=1, callback=callback_grabacion)
with stream:
    input("")  # Queda esperando a que el usuario presione ENTER en la consola

print("=" * 50)
print("🟢 [GRABACIÓN DETENIDA] Procesando audio...")

# 3. Concatenar y guardar la grabación completa
if len(bloques_audio) == 0:
    print("Error: No se detectó ninguna señal de audio grabada.")
    exit()

# Unimos todos los bloques capturados en un solo array de audio
audio_completo = np.concatenate(bloques_audio, axis=0)

# Guardamos el archivo final
sf.write(archivo_salida, audio_completo, frecuencia)
print(f"Archivo guardado como '{archivo_salida}' con éxito.")

# 4. Transcribir de Voz a Texto
reconocedor = sr.Recognizer()

try:
    print("\n[Paso 1] Leyendo el audio grabado...")
    with sr.AudioFile(archivo_salida) as origen:
        audio_data = reconocedor.record(origen)
        
    print("[Paso 2] Transcribiendo voz a texto (Google Speech Recognition)...")
    texto_transcrito = reconocedor.recognize_google(audio_data, language="es-PE")
    
    print("-" * 60)
    print(f"Texto Transcrito: \"{texto_transcrito}\"")
    print("-" * 60)
    
    # 5. Diagnosticar con Machine Learning
    entrada_vec = vectorizador.transform([texto_transcrito])
    prediccion = modelo.predict(entrada_vec)[0]
    probabilidades = modelo.predict_proba(entrada_vec)
    confianza = max(probabilidades[0])
    
    print("\n[Paso 3] Ejecutando predicción con Machine Learning...")
    print("*" * 60)
    print(f"Diagnóstico de Falla: {prediccion}")
    print(f"Confianza de la IA: {confianza * 100:.2f}%")
    print("*" * 60)

except sr.UnknownValueError:
    print("\nError: No se pudo entender tu voz. Intenta de nuevo hablando más fuerte o claro.")
except sr.RequestError as e:
    print(f"\nError de conexión con el servidor de transcripción: {e}")
except Exception as ex:
    print(f"\nOcurrió un error inesperado al procesar el audio: {ex}")
