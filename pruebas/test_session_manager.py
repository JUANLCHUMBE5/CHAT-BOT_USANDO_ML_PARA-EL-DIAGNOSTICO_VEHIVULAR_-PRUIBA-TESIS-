import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.session_manager import SessionManager, DiagnosticSession
from src.core.gestor_diagnostico import GestorDiagnostico

def test_session_manager_basic():
    print("--- PRUEBA SESSION MANAGER: Estado y Sesiones ---")
    sm = SessionManager()
    sesion = sm.obtener_o_crear_sesion("sess_test_1")
    assert sesion.session_id == "sess_test_1"
    
    sm.acumular_input_usuario("sess_test_1", "el carro falla", placa="ABC-123", marca_modelo="Toyota Yaris")
    assert sesion.obtener_sintoma_completo() == "el carro falla"
    assert sesion.placa == "ABC-123"
    assert sesion.marca_modelo == "Toyota Yaris"
    
    sm.acumular_input_usuario("sess_test_1", "chillido al frenar")
    assert sesion.obtener_sintoma_completo() == "el carro falla chillido al frenar"
    
    sm.reiniciar_sesion("sess_test_1")
    assert sesion.obtener_sintoma_completo() == ""
    print("✅ SessionManager tests básicos pasados con éxito.")

def test_multiturn_slot_filling():
    print("--- PRUEBA MULTITURNO: GestorDiagnostico Slot-Filling ---")
    gestor = GestorDiagnostico()
    session_id = "user_multiturn_999"

    # Turno 1: Usuario da consulta ambigua "el carro falla"
    res1 = gestor.procesar_consulta_texto("el carro falla", session_id=session_id)
    assert "especifique" in res1.lower() or "detalle" in res1.lower()
    print("  • Turno 1 OK: Aclaración solicitada al usuario.")

    # Turno 2: Usuario agrega detalle "siento un chillido feo al frenar"
    res2 = gestor.procesar_consulta_texto("siento un chillido feo al frenar el carro", session_id=session_id)
    assert "1. Posible Falla Vehicular" in res2
    assert "2. Procedimiento Técnico" in res2
    assert "3. Tiempo Estimado" in res2
    print("  • Turno 2 OK: Diagnóstico completado tras combinar turnos.")
    print("✅ Prueba multiturno completada exitosamente.")

if __name__ == "__main__":
    test_session_manager_basic()
    test_multiturn_slot_filling()
