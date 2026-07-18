import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MotorRAG:
    """Clase encargada de indexar y buscar información dentro de los manuales técnicos (RAG)."""
    
    def __init__(self, manual_path: str = "manuales_taller/manual_procedimientos.txt"):
        self.manual_path = manual_path
        self.documentos = []
        self.titulos = []
        self.vectorizador = None
        self.documentos_vectorizados = None
        self._indexar_manual()

    def _indexar_manual(self):
        if not os.path.exists(self.manual_path):
            print(f"⚠️ [Infraestructura] Error: No se encontró el manual en {self.manual_path}")
            return
            
        try:
            with open(self.manual_path, "r", encoding="utf-8") as f:
                contenido = f.read()
            
            # Separar secciones por delimitador ===
            secciones = [sec.strip() for sec in contenido.split("===") if sec.strip()]
            for sec in secciones:
                lineas = sec.split("\n")
                titulo = lineas[0] if lineas else "Procedimiento de Taller"
                cuerpo = "\n".join(lineas[1:])
                self.titulos.append(titulo)
                self.documentos.append(cuerpo)
                
            # Inicializar matriz TF-IDF
            self.vectorizador = TfidfVectorizer(lowercase=True, strip_accents='unicode')
            self.documentos_vectorizados = self.vectorizador.fit_transform(self.documentos)
            print(f"📢 [Infraestructura] RAG indexado con éxito: {len(self.documentos)} procedimientos técnicos.")
        except Exception as e:
            print(f"❌ Error al indexar manual en RAG: {e}")

    def recuperar_contexto(self, consulta: str, umbral: float = 0.15) -> tuple:
        """Busca el procedimiento técnico más relevante para la consulta (RETRIEVAL)."""
        if not self.vectorizador or len(self.documentos) == 0:
            return "Manual técnico no indexado o ausente.", "Desconocido"
            
        try:
            consulta_vec = self.vectorizador.transform([consulta])
            similitudes = cosine_similarity(consulta_vec, self.documentos_vectorizados)[0]
            indice_mejor = np.argmax(similitudes)
            mejor_similitud = similitudes[indice_mejor]
            
            if mejor_similitud < umbral:
                return "No se encontró un procedimiento específico en nuestros manuales para esta consulta.", "Coincidencia baja"
                
            return self.documentos[indice_mejor], self.titulos[indice_mejor]
        except Exception as e:
            print(f"❌ Error durante la recuperación semántica en RAG: {e}")
            return "Error al buscar en el manual.", "Error"
