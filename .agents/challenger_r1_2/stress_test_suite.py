import sys
import os
import time
import threading
import concurrent.futures
import requests
import uvicorn
import pandas as pd
import numpy as np

# Reconfigure stdout for UTF-8 on Windows console
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.getcwd())
from main import app
from src.core.gestor_diagnostico import GestorDiagnostico
from src.infrastructure.motor_rag import MotorRAG
from src.infrastructure.modelo_ml import ModeloML
from src.config import settings

SERVER_PORT = 8011
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")

def stress_test_concurrency(total_requests=100, concurrency=20):
    print(f"\n================================================================================")
    print(f"STRESS TEST CONCURRENCY: {total_requests} Requests across {concurrency} Concurrent Workers")
    print(f"================================================================================")

    url_webhook = f"{BASE_URL}/api/v1/webhook"
    url_rest = f"{BASE_URL}/api/v1/diagnostico/analizar"

    meta_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "51999888777",
                        "type": "text",
                        "text": {"body": "Freno se siente esponjoso al presionar en bajada"}
                    }]
                }
            }]
        }]
    }

    rest_payload = {
        "sintoma": "El motor tiembla en minimo y la aguja de RPM oscila",
        "marca": "Toyota",
        "modelo": "Yaris",
        "anio": 2019
    }

    latencies_webhook = []
    latencies_rest = []
    failures = 0

    def make_webhook_request(req_id):
        t0 = time.perf_counter()
        try:
            res = requests.post(url_webhook, json=meta_payload, timeout=5.0)
            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000
            if res.status_code == 200:
                return ("webhook", elapsed_ms, True)
            else:
                return ("webhook", elapsed_ms, False)
        except Exception as e:
            t1 = time.perf_counter()
            return ("webhook", (t1 - t0) * 1000, False)

    def make_rest_request(req_id):
        t0 = time.perf_counter()
        try:
            res = requests.post(url_rest, json=rest_payload, timeout=5.0)
            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000
            if res.status_code == 200:
                return ("rest", elapsed_ms, True)
            else:
                return ("rest", elapsed_ms, False)
        except Exception as e:
            t1 = time.perf_counter()
            return ("rest", (t1 - t0) * 1000, False)

    # Launch Concurrent Execution
    t_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests // 2):
            futures.append(executor.submit(make_webhook_request, i))
            futures.append(executor.submit(make_rest_request, i))

        for future in concurrent.futures.as_completed(futures):
            req_type, elapsed, success = future.result()
            if success:
                if req_type == "webhook":
                    latencies_webhook.append(elapsed)
                else:
                    latencies_rest.append(elapsed)
            else:
                failures += 1

    t_end = time.perf_counter()
    total_time_sec = t_end - t_start
    total_successful = len(latencies_webhook) + len(latencies_rest)
    rps = total_successful / total_time_sec

    print(f"• Total Requests Processed: {total_requests}")
    print(f"• Successful: {total_successful} | Failures: {failures}")
    print(f"• Total Execution Time: {total_time_sec:.3f} seconds")
    print(f"• Throughput: {rps:.2f} Requests/sec")

    all_latencies = latencies_webhook + latencies_rest
    p50 = np.percentile(all_latencies, 50)
    p95 = np.percentile(all_latencies, 95)
    p99 = np.percentile(all_latencies, 99)
    max_lat = np.max(all_latencies)
    min_lat = np.min(all_latencies)
    mean_lat = np.mean(all_latencies)

    print(f"\nLatency Distribution Across All Concurrent Endpoints:")
    print(f"  - Min Latency:    {min_lat:.2f} ms")
    print(f"  - Mean Latency:   {mean_lat:.2f} ms")
    print(f"  - P50 (Median):   {p50:.2f} ms")
    print(f"  - P95 Latency:    {p95:.2f} ms")
    print(f"  - P99 Latency:    {p99:.2f} ms")
    print(f"  - Max Latency:    {max_lat:.2f} ms")

    # Assert SLA: all latencies < 2000 ms (2.0 seconds)
    assert max_lat < 2000.0, f"SLA Violation: Max latency was {max_lat:.2f} ms (>= 2000 ms)"
    assert failures == 0, f"Failure detected during stress test: {failures} failed requests"
    print(f"\n✅ PASS: Continuous async concurrent response time < 2.0s under load ({concurrency} workers, max lat: {max_lat:.2f} ms).")
    return {
        "total": total_requests,
        "successful": total_successful,
        "failures": failures,
        "throughput_rps": rps,
        "min_lat_ms": min_lat,
        "mean_lat_ms": mean_lat,
        "p50_lat_ms": p50,
        "p95_lat_ms": p95,
        "p99_lat_ms": p99,
        "max_lat_ms": max_lat
    }


def stress_test_guardrails():
    print(f"\n================================================================================")
    print(f"STRESS TEST ANTI-HALLUCINATION GUARDRAILS")
    print(f"================================================================================")

    gestor = GestorDiagnostico()
    ml = ModeloML()
    rag = MotorRAG()

    # 1. Greetings & Contact Initial Filter
    print("\n--- 1. Greetings / Initial Contact Interception ---")
    greetings = [
        "hola", "buenas tardes", "buenos dias", "buenas noches",
        "hola tengo un problema", "hola que tal", "saludos", "ayuda"
    ]
    for g in greetings:
        resp = gestor.procesar_consulta_texto(g)
        assert "CarBot" in resp or "Por favor, cuéntame" in resp, f"Greeting not intercepted for: {g}"
        print(f"  [PASS Greeting] '{g}' -> {resp[:65]}...")

    # 2. Ambiguous & Short Inputs Filter
    print("\n--- 2. Ambiguous / Incomplete Inputs Interception ---")
    ambiguous = [
        "mi auto falla", "tengo un problema", "el carro falla",
        "ruido", "falla el carro", "freno", "motor"
    ]
    for amb in ambiguous:
        resp = gestor.procesar_consulta_texto(amb)
        assert "especifique el síntoma" in resp, f"Ambiguous input not intercepted for: {amb}"
        print(f"  [PASS Ambiguous] '{amb}' -> {resp[:65]}...")

    # 3. Out-Of-Domain / Low Confidence (< 5%) Filter
    print("\n--- 3. Low Confidence / OOD Anti-Hallucination Filter (< 5%) ---")
    nonsense_inputs = [
        "qwertyuiop asdfghjkl zxcvbnm",
        "receta para cocinar ceviche de pescado peruano",
        "x7z9q k2w0m 999",
        "supercalifragilisticexpialidocious"
    ]
    for text in nonsense_inputs:
        pred, conf = ml.predecir_falla_con_confianza(text)
        resp = gestor.procesar_consulta_texto(text)
        assert conf < 0.05 or "Síntoma no reconocido" in resp or "especifique el síntoma" in resp, f"Hallucination leak for: {text}"
        print(f"  [PASS Low Conf/OOD] '{text}' (Conf: {conf*100:.2f}%) -> Intercepted with safe response")

    # 4. RAG Missing Fallback Handling
    print("\n--- 4. RAG Missing Fallback Safe Handling ---")
    resp_fallback = gestor.generar_respuesta_conversacional(
        pregunta="Falla inusual en modulo secundario",
        diagnostico_ml="Falla Electrónica Auxiliar",
        contexto_manual="No se encontró información específica",
        confianza_ml=0.50,
        titulo_manual="Coincidencia baja"
    )
    assert "No se encontró un procedimiento específico" in resp_fallback, "Fallback response not triggered for missing RAG"
    assert "🛠️ **1. Posible Falla Vehicular" in resp_fallback
    assert "📖 **2. Procedimiento Técnico" in resp_fallback
    assert "⏱️ **3. Tiempo Estimado" in resp_fallback
    print(f"  [PASS RAG Missing Fallback] Generated safe fallback:\n{resp_fallback}")

    print(f"\n✅ PASS: All anti-hallucination guardrails passed stress testing.")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1.5)

    try:
        metrics = stress_test_concurrency(total_requests=100, concurrency=20)
        stress_test_guardrails()
        print("\n" + "="*80)
        print("🎉 EMPIRICAL STRESS TEST SUITE COMPLETED SUCCESSFULLY")
        print("="*80)
    except Exception as e:
        print(f"\n❌ STRESS TEST FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
