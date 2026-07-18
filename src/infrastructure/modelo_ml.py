import os
import joblib

class ModeloML:
    """Clase encargada de encapsular el modelo de clasificación de texto de Machine Learning."""
    
    def __init__(self, modelo_path: str = "models/modelo_diagnostico.pkl", vectorizador_path: str = "models/vectorizador_tfidf.pkl"):
        self.modelo_path = modelo_path
        self.vectorizador_path = vectorizador_path
        self.modelo = None
        self.vectorizador = None
        self._cargar_modelos()

    def _cargar_modelos(self):
        if os.path.exists(self.modelo_path) and os.path.exists(self.vectorizador_path):
            self.modelo = joblib.load(self.modelo_path)
            self.vectorizador = joblib.load(self.vectorizador_path)
            print("📢 [Infraestructura] Modelo ML cargado correctamente.")
        else:
            print("⚠️ [Infraestructura] Advertencia: Archivos de modelo ML no encontrados.")

    def predecir_falla(self, texto: str) -> str:
        """Predice la categoría de la falla basándose en el síntoma de texto."""
        if not self.modelo or not self.vectorizador:
            return "Falla mecánica no clasificada (Modelo ML ausente)"
            
        try:
            entrada_vec = self.vectorizador.transform([texto])
            prediccion = self.modelo.predict(entrada_vec)[0]
            return prediccion
        except Exception as e:
            print(f"❌ Error al predecir falla con el modelo ML: {e}")
            return "Error de predicción"
