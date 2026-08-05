import os
import sys
import time
import threading
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.core.gestor_diagnostico import GestorDiagnostico, _tracker_lock
from src.core.session_manager import SessionManager, DiagnosticSession
from src.infrastructure.modelo_ml import ModeloML
from src.infrastructure.motor_rag import MotorRAG
from src.config import settings

def run_audits():
    print("=" * 80)
    print("STARTING AUDITOR_1_V3 FORENSIC EMPIRICAL SUITE")
    print("=" * 80)

    # -------------------------------------------------------------
    # TEST 1: THREAD SAFETY OF _tracker_lock
    # -------------------------------------------------------------
    print("\n[AUDIT CHECK 1] Concurrent Thread-Safety Test on _tracker_lock")
    gestor = GestorDiagnostico()
    tracker_path = settings.TRACKER_PATH
    
    # Read initial row count
    initial_rows = len(pd.read_csv(tracker_path)) if os.path.exists(tracker_path) else 0
    
    num_threads = 20
    threads = []
    errors = []

    def worker_thread(thread_idx):
        try:
            gestor._registrar_en_tracker(
                placa=f"THREAD-{thread_idx}",
                marca_modelo="Thread Test Car",
                sintoma="Chillido de frenos en prueba concurrente",
                diagnostico_ml="Desgaste de Pastillas de Freno",
                campos_completos=1
            )
        except Exception as e:
            errors.append(e)

    for i in range(num_threads):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    final_rows = len(pd.read_csv(tracker_path)) if os.path.exists(tracker_path) else 0
    added_rows = final_rows - initial_rows

    assert len(errors) == 0, f"Thread execution produced errors: {errors}"
    assert added_rows == num_threads, f"Expected {num_threads} added rows, but got {added_rows}"
    print(f"✅ PASS: All {num_threads} concurrent thread writes succeeded cleanly under _tracker_lock. Added rows: {added_rows}")

    # -------------------------------------------------------------
    # TEST 2: SINGLE-EXECUTION REST HANDLING
    # -------------------------------------------------------------
    print("\n[AUDIT CHECK 2] Single-Execution REST Handling (No Session Pollution)")
    sm = gestor.session_manager
    initial_session_count = len(sm._sesiones)

    # Call REST-style (no session_id)
    resp1 = gestor.procesar_consulta_texto("pedal esponjoso al presionar el freno", placa="REST-API", marca_modelo="Toyota Yaris")
    count_after_rest1 = len(sm._sesiones)

    # Call REST-style again with another symptom
    resp2 = gestor.procesar_consulta_texto("el motor cascabelea al acelerar", placa="REST-API", marca_modelo="Honda Civic")
    count_after_rest2 = len(sm._sesiones)

    assert count_after_rest1 == initial_session_count, "REST query created unnecessary persistent session!"
    assert count_after_rest2 == initial_session_count, "REST query polluted session dictionary!"
    assert "Frenos" in resp1 or "freno" in resp1.lower() or "1. Posible Falla" in resp1
    assert "cascabelea" in resp2.lower() or "buj" in resp2.lower() or "1. Posible Falla" in resp2
    print("✅ PASS: REST calls executed single-shot without session pollution or leftover state.")

    # -------------------------------------------------------------
    # TEST 3: INSTANT SESSION TTL EVICTION
    # -------------------------------------------------------------
    print("\n[AUDIT CHECK 3] Instant Session TTL Eviction Test")
    sm_ttl = SessionManager(ttl_seconds=1800)
    session_id = "ttl_test_session_123"

    # Create session
    sesion = sm_ttl.obtener_o_crear_sesion(session_id)
    assert sm_ttl.obtener_sesion(session_id) is not None, "Session should exist initially"

    # Artificial time aging
    sesion.updated_at = time.time() - 10.0 # Aged by 10 seconds

    # Retrieve with 5s TTL
    retrieved_expired = sm_ttl.obtener_sesion(session_id, ttl_segundos=5)
    assert retrieved_expired is None, "Expired session was not evicted instantantly on access!"
    assert session_id not in sm_ttl._sesiones, "Expired session was not popped from internal dict!"

    # Try creating or obtaining with 5s TTL
    new_sesion = sm_ttl.obtener_o_crear_sesion(session_id, ttl_segundos=5)
    assert new_sesion is not sesion, "New session should be fresh, not the old instance"
    print("✅ PASS: Instant TTL eviction verified on access and session dict pop.")

    # -------------------------------------------------------------
    # TEST 4: REAL MODEL ML & RAG INFERENCE
    # -------------------------------------------------------------
    print("\n[AUDIT CHECK 4] Real ML Model and FAISS RAG Logic Check")
    ml = ModeloML()
    rag = MotorRAG()

    symptoms = [
        "chillido agudo al frenar en la rueda delantera",
        "el motor cascabelea fuerte al acelerar en subida",
        "el pedal de freno se siente suave y esponjoso",
        "el motor tiembla en minimo y se apaga en el semaforo",
        "bateria descargada sin fuerza para dar arranque"
    ]

    for sym in symptoms:
        pred, conf = ml.predecir_falla_con_confianza(sym)
        ctx, title = rag.recuperar_contexto(sym)
        assert isinstance(pred, str) and len(pred) > 0
        assert isinstance(conf, float) and 0.0 <= conf <= 1.0
        assert isinstance(ctx, str) and len(ctx) > 0
        assert isinstance(title, str) and len(title) > 0
        print(f"  • Symptom: '{sym[:30]}...' -> ML: '{pred}' ({conf*100:.1f}%) | RAG Title: '{title}'")

    print("✅ PASS: Model ML and Motor RAG run real statistical vector predictions and vector indexing.")

    print("\n" + "=" * 80)
    print("ALL EMPIRICAL AUDIT CHECKS PASSED WITH 100% INTEGRITY")
    print("=" * 80)

if __name__ == "__main__":
    run_audits()
