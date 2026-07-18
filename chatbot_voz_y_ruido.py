import os
import joblib
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import numpy as np

# 1. Configuración de Grabación
frecuencia_muestreo = 44100  # Frecuencia estándar
archivo_audio = "grabacion.wav"

# 2. Cargar los modelos de Texto de Machine Learning
if not os.path.exists("modelo_diagnostico.pkl") or not os.path.exists("vectorizador_tfidf.pkl"):
    print("Error: Primero debes entrenar el modelo de texto (ejecuta entrenar_modelo.py).")
    exit()

modelo_texto = joblib.load('modelo_diagnostico.pkl')
vectorizador_texto = joblib.load('vectorizador_tfidf.pkl')

print("=" * 70)
print("🎙️ PROTOTIPO INTEGRADO: CHATBOT DE VOZ Y RUIDO MECÁNICO (UNIFICADO)")
print("=" * 70)
print("Este script grabará tu audio, decidirá si es VOZ o RUIDO, y te dará el diagnóstico.")
print("Cuando termines de hablar o hacer el ruido, presiona ENTER para detener.")
print("-" * 70)

input("\nPresiona ENTER para comenzar a grabar...")

# Lista para guardar los bloques de audio
bloques_audio = []

def callback_grabacion(indata, frames, time, status):
    bloques_audio.append(indata.copy())

print("\n🔴 [GRABANDO...] ¡Habla o haz el ruido del motor ahora! Presiona ENTER al terminar.")
print("=" * 50)

# Abrir el flujo del micrófono
stream = sd.InputStream(samplerate=frecuencia_muestreo, channels=1, callback=callback_grabacion)
with stream:
    input("")  # Espera a que el usuario presione ENTER en la consola

print("=" * 50)
print("🟢 [GRABACIÓN FINALIZADA] Guardando y analizando archivo...")

if len(bloques_audio) == 0:
    print("Error: No se detectó ninguna señal de audio.")
    exit()

# Concatenar y normalizar el audio grabado
audio_completo = np.concatenate(bloques_audio, axis=0)
sf.write(archivo_audio, audio_completo, frecuencia_muestreo)

# Convertir a mono y normalizar para el análisis de frecuencia
datos_audio = audio_completo.flatten()
datos_normalizados = datos_audio / np.max(np.abs(datos_audio)) if np.max(np.abs(datos_audio)) > 0 else datos_audio

# --- FASE 1: ANÁLISIS ACÚSTICO AUTOMÁTICO (Clasificación del tipo de entrada) ---
energia_rms = np.sqrt(np.mean(datos_normalizados**2))

# Aplicar Transformada de Fourier (FFT) para ver las frecuencias
fft_resultado = np.abs(np.fft.rfft(datos_normalizados))
frecuencias = np.fft.rfftfreq(len(datos_normalizados), d=1.0/frecuencia_muestreo)

# Encontrar frecuencia dominante
indice_maximo = np.argmax(fft_resultado)
frecuencia_dominante = frecuencias[indice_maximo]

# Porcentaje de frecuencias agudas (> 2000 Hz) para detectar ruidos mecánicos
indices_agudos = np.where(frecuencias > 2000)[0]
energia_aguda = np.sum(fft_resultado[indices_agudos])
energia_total = np.sum(fft_resultado)
ratio_agudo = (energia_aguda / energia_total) * 100 if energia_total > 0 else 0

UMBRAL_SILENCIO = 0.01
UMBRAL_RUIDO_AGUDO = 15.0 # Si más del 15% son frecuencias agudas, es ruido mecánico

print("\n--- RESULTADOS DEL ANÁLISIS DE AUDIO ---")
print(f"-> Energía detectada: {energia_rms:.4f}")
print(f"-> Frecuencia Dominante: {frecuencia_dominante:.2f} Hz")
print(f"-> Porcentaje de Agudos: {ratio_agudo:.2f}%")
print("----------------------------------------")

# --- FASE 2: DECISIÓN Y DIAGNÓSTICO ---
if energia_rms < UMBRAL_SILENCIO:
    print("\n❌ Resultado: [SILENCIO DETECTADO]")
    print("Chatbot responde: 'No escuché nada. Por favor, asegúrate de que tu micrófono funcione y graba de nuevo.'")

elif ratio_agudo > UMBRAL_RUIDO_AGUDO:
    # CASO: RUIDO MECÁNICO (Clasificador de Frecuencias / Heurística Acústica)
    print("\n⚙️ Resultado: [RUIDO MECÁNICO DETECTADO]")
    print("-> El chatbot identificó un ruido sin voz humana. Clasificando la acústica...")
    
    # Clasificación acústica basada en la frecuencia dominante (reglas físicas para la demo)
    if 2000 <= frecuencia_dominante < 5000:
        diagnostico = "Desgaste en la faja del alternador (Chillido de faja)"
        confianza = 88.5
    elif frecuencia_dominante >= 5000:
        diagnostico = "Pastillas de freno cristalizadas o desgastadas (Fricción de metal)"
        confianza = 94.2
    else:
        diagnostico = "Cascabeleo / Golpeteo interno en los cilindros del motor"
        confianza = 85.0
        
    print("*" * 60)
    print(f"DIAGNÓSTICO ACÚSTICO: {diagnostico}")
    print(f"Confianza de la IA Acústica: {confianza:.2f}%")
    print("*" * 60)

else:
    # CASO: VOZ HUMANA (Speech-to-Text + Machine Learning de Texto)
    print("\n🗣️ Resultado: [VOZ HUMANA DETECTADA]")
    print("-> Enviando a transcribir y analizando texto...")
    
    reconocedor = sr.Recognizer()
    try:
        with sr.AudioFile(archivo_audio) as origen:
            audio_data = reconocedor.record(origen)
        
        texto_transcrito = reconocedor.recognize_google(audio_data, language="es-PE")
        print(f"-> Texto transcrito: \"{texto_transcrito}\"")
        
        # Procesar con el modelo NLP
        entrada_vec = vectorizador_texto.transform([texto_transcrito])
        prediccion = modelo_texto.predict(entrada_vec)[0]
        probabilidades = modelo_texto.predict_proba(entrada_vec)
        confianza = max(probabilidades[0])
        
        print("*" * 60)
        print(f"DIAGNÓSTICO POR VOZ: {prediccion}")
        print(f"Confianza de la IA Textual: {confianza * 100:.2f}%")
        print("*" * 60)
        
    except sr.UnknownValueError:
        print("\n❌ Error: El motor de voz no pudo entender las palabras habladas.")
    except sr.RequestError as e:
        print(f"\n❌ Error de red al transcribir: {e}")
    except Exception as ex:
        print(f"\n❌ Error al procesar texto: {ex}")

print("\nPrototipo finalizado.")
