import numpy as np

class AudioProcessor:
    """Clase encargada de procesar las señales de audio físicas (FFT y RMS)."""
    
    def __init__(self, samplerate: int = 44100):
        self.samplerate = samplerate
        self.umbral_silencio = 0.01
        self.umbral_ruido_agudo = 15.0  # Porcentaje de agudos > 2000Hz

    def normalizar_audio(self, datos_audio: np.ndarray) -> np.ndarray:
        """Normaliza la amplitud del audio para evitar problemas de volumen."""
        maximo = np.max(np.abs(datos_audio))
        if maximo > 0:
            return datos_audio / maximo
        return datos_audio

    def analizar_audio(self, datos_audio_crudos: np.ndarray) -> tuple:
        """
        Analiza las propiedades físicas del audio.
        Retorna: (Tipo de entrada: 'Silencio'|'Ruido Mecánico'|'Voz Humana', Detalle/Diagnóstico)
        """
        if len(datos_audio_crudos) == 0:
            return "Silencio", "Señal de audio vacía."

        # Aplanar y normalizar
        datos_normalizados = self.normalizar_audio(datos_audio_crudos.flatten())
        
        # Calcular energía RMS (Root Mean Square)
        energia_rms = np.sqrt(np.mean(datos_normalizados**2))
        
        if energia_rms < self.umbral_silencio:
            return "Silencio", "No se detectaron niveles significativos de audio."

        # Aplicar Transformada Rápida de Fourier (FFT) para análisis espectral
        fft_resultado = np.abs(np.fft.rfft(datos_normalizados))
        frecuencias = np.fft.rfftfreq(len(datos_normalizados), d=1.0/self.samplerate)

        # Encontrar frecuencia dominante
        indice_maximo = np.argmax(fft_resultado)
        frecuencia_dominante = frecuencias[indice_maximo]

        # Porcentaje de frecuencias agudas (> 2000 Hz) para aislar ruidos metálicos
        indices_agudos = np.where(frecuencias > 2000)[0]
        energia_aguda = np.sum(fft_resultado[indices_agudos])
        energia_total = np.sum(fft_resultado)
        ratio_agudo = (energia_aguda / energia_total) * 100 if energia_total > 0 else 0

        # Decidir según la firma acústica espectral
        if ratio_agudo > self.umbral_ruido_agudo:
            # Clasificación física simplificada basada en frecuencia dominante
            if 2000 <= frecuencia_dominante < 5000:
                diagnostico = "Desgaste en la faja del alternador (Chillido de faja)"
            elif frecuencia_dominante >= 5000:
                diagnostico = "Pastillas de freno cristalizadas o desgastadas (Fricción de metal)"
            else:
                diagnostico = "Cascabeleo / Golpeteo interno en los cilindros del motor"
            return "Ruido Mecánico", diagnostico
        else:
            # Audio con firma de voz humana
            return "Voz Humana", "Señal correspondiente a voz hablada (para transcripción)."
