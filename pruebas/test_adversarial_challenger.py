import os
import sys
import unittest

# Configure stdout for UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.gestor_diagnostico import GestorDiagnostico
from src.infrastructure.motor_rag import MotorRAG
from src.infrastructure.modelo_ml import ModeloML

class TestAdversarialChallenger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gestor = GestorDiagnostico()
        cls.rag = MotorRAG()
        cls.ml = ModeloML()

    def test_colloquial_peruvian_phrasing(self):
        """Test colloquial Peruvian automotive phrasing."""
        test_cases = [
            ("el carro presenta un cascabeleo feo cuando subo el cerro en tercera", "cascabeleo"),
            ("al frenar se escucha un chillido horribles en la rueda delantera", "chillido"),
            ("el pedal de freno se siente esponjoso y se va hasta el fondo", "esponjoso"),
            ("se me apaga el carro cuando me detengo en el semaforo en minimo", "apaga"),
        ]
        
        for input_text, key_term in test_cases:
            pred, conf = self.ml.predecir_falla_con_confianza(input_text)
            resp = self.gestor.procesar_consulta_texto(input_text)
            
            # Confidence must be above system threshold (5%)
            self.assertGreater(conf, 0.05, f"Confidence too low ({conf}) for: {input_text}")
            self.assertIn("Posible Falla Vehicular", resp, f"Failed 3-section format for: {input_text}")
            self.assertIn("Procedimiento Técnico", resp)
            self.assertIn("Tiempo Estimado", resp)
            print(f"[PASS Colloquial] '{input_text}' -> Pred: '{pred}' (Conf: {conf*100:.1f}%)")

    def test_colloquial_verb_variations_edge_case(self):
        """Expose edge cases where colloquial verbs (cascabelea, chilla, patea) hit ambiguity filter vs processed."""
        verb_variations = [
            ("el motor cascabelea fuerte al acelerar en subida", "cascabelea"),
            ("la rueda chilla feo cuando piso el freno", "chilla"),
            ("la caja patea al meter segunda velocidad en taller", "patea")
        ]
        for input_text, verb in verb_variations:
            resp = self.gestor.procesar_consulta_texto(input_text)
            pred, conf = self.ml.predecir_falla_con_confianza(input_text)
            print(f"[VERB EVAL] Input: '{input_text}' | Pred: '{pred}' (Conf: {conf*100:.1f}%) -> Resp snippet: {resp[:70]}...")

    def test_dtc_codes(self):
        """Test diagnostic trouble codes (DTC P0300, C0035, P0505, P0562)."""
        dtc_cases = [
            ("Codigo P0300 misfire en motor", "DTC P0300"),
            ("Scanner indica falla C0035 pastillas de freno chillido", "C0035"),
            ("Codigo P0505 falla cuerpo aceleracion iac minimo", "P0505"),
            ("DTC P0562 voltaje de bateria bajo en arranque", "P0562"),
        ]
        for input_text, dtc_code in dtc_cases:
            context, title = self.rag.recuperar_contexto(input_text)
            resp = self.gestor.procesar_consulta_texto(input_text)
            self.assertNotIn("Error al buscar", context)
            self.assertIn("Posible Falla Vehicular", resp)
            print(f"[PASS DTC Code] '{input_text}' -> RAG Matched Title: '{title}'")

    def test_ambiguous_and_greeting_guardrails(self):
        """Test guardrails against ambiguous terms, greetings, and short non-informative inputs."""
        greetings = ["hola", "buenas tardes", "hola tengo un problema"]
        for g in greetings:
            resp = self.gestor.procesar_consulta_texto(g)
            self.assertIn("CarBot", resp)
            self.assertTrue("¿Qué problema o síntoma presenta tu vehículo hoy?" in resp or "especifique el síntoma" in resp)
            print(f"[PASS Greeting Guardrail] '{g}' -> Intercepted by initial contact filter.")

        ambiguous = ["mi auto falla", "tengo un problema", "el carro falla"]
        for amb in ambiguous:
            resp = self.gestor.procesar_consulta_texto(amb)
            self.assertTrue("especifique el síntoma" in resp or "CarBot" in resp)
            print(f"[PASS Ambiguous Guardrail] '{amb}' -> Intercepted by ambiguity filter.")

    def test_anti_hallucination_low_confidence(self):
        """Test out-of-domain / random gibberish input anti-hallucination handling."""
        nonsense_inputs = [
            "qwertyuiop asdfghjkl zxcvbnm",
            "receta para cocinar ceviche de pescado"
        ]
        for text in nonsense_inputs:
            resp = self.gestor.procesar_consulta_texto(text)
            is_safe = ("especifique el síntoma" in resp or 
                       "Síntoma no reconocido" in resp or 
                       "CarBot" in resp or
                       "No se encontró un procedimiento" in resp)
            self.assertTrue(is_safe, f"Hallucination risk for input: '{text}' -> {resp}")
            print(f"[PASS Anti-Hallucination] '{text}' -> Intercepted with safe response.")

if __name__ == "__main__":
    unittest.main()
