import os
import numpy as np
from scipy.io import wavfile

# Archivo de audio que vamos a analizar
nombre_audio = "grabacion.wav"

if not os.path.exists(nombre_audio):
    print("=" * 70)
    print(f"Error: No se encontró el archivo '{nombre_audio}'.")
    print("Graba un audio primero usando: python grabar_y_diagnosticar.py")
    print("=" * 70)
    exit()

print("=" * 70)
print("🔍 ANALIZADOR FÍSICO DE AUDIO (VOZ VS. RUIDO MECÁNICO)")
print("=" * 70)

# 1. Leer el archivo de audio usando scipy (no requiere compilar C++)
frecuencia_muestreo, datos_audio = wavfile.read(nombre_audio)

# Si el audio es estéreo (2 canales), lo convertimos a mono promediando
if len(datos_audio.shape) > 1:
    datos_audio = datos_audio.mean(axis=1)

# Normalizar los datos del audio entre -1 y 1
datos_normalizados = datos_audio / np.max(np.abs(datos_audio))

# 2. Calcular la Energía RMS (Volumen medio del audio)
energia_rms = np.sqrt(np.mean(datos_normalizados**2))

# 3. Aplicar la Transformada de Fourier (FFT) para analizar el espectro de frecuencias
fft_resultado = np.abs(np.fft.rfft(datos_normalizados))
frecuencias = np.fft.rfftfreq(len(datos_normalizados), d=1.0/frecuencia_muestreo)

# Encontrar la frecuencia dominante (la que tiene más energía)
indice_maximo = np.argmax(fft_resultado)
frecuencia_dominante = frecuencias[indice_maximo]

# Calcular el porcentaje de energía en altas frecuencias (ruidos agudos como chillidos, > 2000 Hz)
indices_agudos = np.where(frecuencias > 2000)[0]
energia_aguda = np.sum(fft_resultado[indices_agudos])
energia_total = np.sum(fft_resultado)
ratio_agudo = (energia_aguda / energia_total) * 100 if energia_total > 0 else 0

print(f"-> Volumen/Energía RMS detectada: {energia_rms:.4f}")
print(f"-> Frecuencia dominante en el audio: {frecuencia_dominante:.2f} Hz")
print(f"-> Porcentaje de frecuencias agudas (>2000Hz): {ratio_agudo:.2f}%")
print("-" * 70)

# 4. Clasificación inteligente basada en límites físicos (Umbrales)
UMBRAL_SILENCIO = 0.01  # Si la energía es menor a esto, es silencio
UMBRAL_RUIDO_AGUDO = 15.0 # Si más del 15% del espectro es agudo, es ruido/chillido mecánico

if energia_rms < UMBRAL_SILENCIO:
    print("DECISIÓN DEL CHATBOT: [SILENCIO O AUDIO VACÍO]")
    print("Acción sugerida: Responder 'No se escuchó nada, por favor graba de nuevo'.")
elif ratio_agudo > UMBRAL_RUIDO_AGUDO:
    print("DECISIÓN DEL CHATBOT: [RUIDO MECÁNICO DETECTADO (POSIBLE FALLA)]")
    print("Acción sugerida: Omitir transcripción de texto y enviar el audio al Clasificador Acústico.")
else:
    print("DECISIÓN DEL CHATBOT: [VOZ HUMANA DETECTADA]")
    print("Acción sugerida: Enviar el audio a la API de Whisper para transcripción de texto.")

print("=" * 70)
