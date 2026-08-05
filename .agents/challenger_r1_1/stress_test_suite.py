import sys
import os
import time
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import uvicorn

# Configurar path para importar desde la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app
from src.config import settings
from src.core.session_manager import SessionManager, DiagnosticSession
from src.core.gestor_diagnostico import GestorDiagnostico

SERVER_PORT = 8019
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")

class StressTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.logs = []

    def log(self, msg: str):
        print(msg)
        self.logs.append(msg)

    def assert_true(self, condition: bool, test_name: str, fail_msg: str):
        if condition:
            self.passed += 1
            self.log(f"  [PASS] {test_name}")
        else:
            self.failed += 1
            err = f"  [FAIL] {test_name}: {fail_msg}"
            self.log(err)
            self.errors.append(err)

def run_all_tests():
    tester = StressTester()
    tester.log("================================================================================")
    tester.log("  SUITE DE PRUEBAS ADVERSARIALES Y STRESS - CHALLENGER_1")
    tester.log("================================================================================")

    # --------------------------------------------------------------------------
    # CATEGORÍA 1: REST API /api/v1/diagnostico/analizar
    # --------------------------------------------------------------------------
    tester.log("\n--- CATEGORÍA 1: Endpoint REST /api/v1/diagnostico/analizar ---")

    # 1.1 Cadena vacía
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": ""})
    tester.assert_true(res.status_code == 400, "1.1 Cadena vacía sintoma=''", f"Esperado 400, obtenido {res.status_code}")

    # 1.2 Espacios en blanco
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": "     "})
    tester.assert_true(res.status_code == 400, "1.2 Espacios en blanco sintoma='   '", f"Esperado 400, obtenido {res.status_code}")

    # 1.3 Parámetro sintoma faltante
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"marca": "Toyota"})
    tester.assert_true(res.status_code == 422, "1.3 Parámetro 'sintoma' faltante", f"Esperado 422, obtenido {res.status_code}")

    # 1.4 JSON malformado (Sintaxis inválida)
    headers = {"Content-Type": "application/json"}
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", data="{sintoma: malformado}", headers=headers)
    tester.assert_true(res.status_code in (400, 422), "1.4 JSON malformado (sintaxis inválida)", f"Esperado 400/422, obtenido {res.status_code}")

    # 1.5 Tipos de datos inesperados
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": 12345})
    tester.assert_true(res.status_code in (422, 200), "1.5 Tipo de dato entero en sintoma (Pydantic coerciona o valida)", f"Status: {res.status_code}")

    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": ["chillido", "frenos"]})
    tester.assert_true(res.status_code == 422, "1.5 Tipo de dato lista en sintoma", f"Esperado 422, obtenido {res.status_code}")

    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": "frenos chillan", "anio": "dos mil diez"})
    tester.assert_true(res.status_code == 422, "1.5 Tipo de dato texto en anio", f"Esperado 422, obtenido {res.status_code}")

    # 1.6 Cadena extremadamente larga (100,000 caracteres)
    long_str = "freno " * 20000
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json={"sintoma": long_str})
    t_elapsed = (time.time() - t0) * 1000
    tester.assert_true(res.status_code == 200 and t_elapsed < 2000, "1.6 Cadena ultra larga (100,000 caracteres)", f"Status: {res.status_code}, Tiempo: {t_elapsed:.2f}ms")

    # 1.7 Inyección SQL, XSS, Caracteres Especiales y Emojis
    xss_sql_payload = {
        "sintoma": "<script>alert('xss')</script> SELECT * FROM usuarios WHERE '1'='1' 🚗🔥💥 pedal esponjoso",
        "marca": "'; DROP TABLE vehiculos; --",
        "modelo": "<img src=x onerror=alert(1)>"
    }
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json=xss_sql_payload)
    t_elapsed = (time.time() - t0) * 1000
    tester.assert_true(res.status_code == 200 and t_elapsed < 2000, "1.7 Payload con Inyección SQL / XSS / Emojis", f"Status: {res.status_code}, Tiempo: {t_elapsed:.2f}ms")

    # 1.8 Caracteres nulos / Unicode / Fuzzing
    fuzz_payload = {"sintoma": "Frenos \x00\x01\x02 \u0000 \ufffd tiemblan mucho"}
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json=fuzz_payload)
    tester.assert_true(res.status_code in (200, 400, 422), "1.8 Fuzzing de caracteres nulos/unicode", f"Status: {res.status_code}")

    # --------------------------------------------------------------------------
    # CATEGORÍA 2: WEBHOOK GET VERIFICATION
    # --------------------------------------------------------------------------
    tester.log("\n--- CATEGORÍA 2: Webhook GET /api/v1/webhook ---")

    # 2.1 Verificación válida
    token = settings.VERIFY_TOKEN
    res = requests.get(f"{BASE_URL}/api/v1/webhook?hub.mode=subscribe&hub.verify_token={token}&hub.challenge=CHALLENGE_OK_123")
    tester.assert_true(res.status_code == 200 and res.text == "CHALLENGE_OK_123", "2.1 Webhook GET token válido", f"Status: {res.status_code}, Response: '{res.text}'")

    # 2.2 Token incorrecto
    res = requests.get(f"{BASE_URL}/api/v1/webhook?hub.mode=subscribe&hub.verify_token=WRONG_TOKEN&hub.challenge=CHALLENGE_123")
    tester.assert_true(res.status_code == 403, "2.2 Webhook GET token incorrecto", f"Esperado 403, obtenido {res.status_code}")

    # 2.3 Parámetros faltantes
    res = requests.get(f"{BASE_URL}/api/v1/webhook")
    tester.assert_true(res.status_code == 403, "2.3 Webhook GET sin parámetros", f"Esperado 403, obtenido {res.status_code}")

    # --------------------------------------------------------------------------
    # CATEGORÍA 3: WEBHOOK POST ADVERSARIAL PAYLOADS
    # --------------------------------------------------------------------------
    tester.log("\n--- CATEGORÍA 3: Webhook POST Payloads Adversariales ---")

    # 3.1 JSON vacío
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/v1/webhook", json={})
    t_elapsed = (time.time() - t0) * 1000
    tester.assert_true(res.status_code == 200 and t_elapsed < 2000, "3.1 Webhook POST JSON vacío `{}`", f"Status: {res.status_code}, Tiempo: {t_elapsed:.2f}ms")

    # 3.2 Payload Meta incompleto / anidación parcial
    broken_meta_1 = {"entry": []}
    res = requests.post(f"{BASE_URL}/api/v1/webhook", json=broken_meta_1)
    tester.assert_true(res.status_code == 200, "3.2 Webhook POST Meta entry=[]", f"Status: {res.status_code}")

    broken_meta_2 = {"entry": [{"changes": [{"value": {"messages": []}}]}]}
    res = requests.post(f"{BASE_URL}/api/v1/webhook", json=broken_meta_2)
    tester.assert_true(res.status_code == 200, "3.2 Webhook POST Meta messages=[]", f"Status: {res.status_code}")

    # 3.3 Tipo de mensaje no soportado en Meta (location, sticker)
    unknown_type_meta = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "51999999999",
                        "type": "location",
                        "location": {"latitude": -11.85, "longitude": -77.03}
                    }]
                }
            }]
        }]
    }
    res = requests.post(f"{BASE_URL}/api/v1/webhook", json=unknown_type_meta)
    tester.assert_true(res.status_code == 200, "3.3 Webhook POST Meta tipo 'location'", f"Status: {res.status_code}")

    # 3.4 Twilio Form payload sin datos
    res = requests.post(
        f"{BASE_URL}/api/v1/webhook",
        data="",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tester.assert_true(res.status_code == 200, "3.4 Webhook POST Twilio Form vacío", f"Status: {res.status_code}")

    # 3.5 Twilio Form payload con caracteres raros
    res = requests.post(
        f"{BASE_URL}/api/v1/webhook",
        data="From=whatsapp%2B51900000000&Body=%F0%9F%9A%97%20Frenos%20malos%20%26%20humo",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tester.assert_true(res.status_code == 200, "3.5 Webhook POST Twilio UrlEncoded raro", f"Status: {res.status_code}")

    # --------------------------------------------------------------------------
    # CATEGORÍA 4: SESSION MANAGER & AISLAMIENTO DE ESTADO
    # --------------------------------------------------------------------------
    tester.log("\n--- CATEGORÍA 4: SessionManager & Aislamiento de Estado ---")

    sm = SessionManager(ttl_seconds=5)
    
    # 4.1 Aislamiento entre sesiones distintas
    s1 = sm.acumular_input_usuario("user_A", "falla en motor", placa="AAA-111", marca_modelo="Nissan Sentra")
    s2 = sm.acumular_input_usuario("user_B", "chillido al frenar", placa="BBB-222", marca_modelo="Toyota Corolla")

    tester.assert_true(s1.obtener_sintoma_completo() == "falla en motor" and s1.placa == "AAA-111", "4.1 Estado Usuario A aislado", f"Sintoma: {s1.obtener_sintoma_completo()}")
    tester.assert_true(s2.obtener_sintoma_completo() == "chillido al frenar" and s2.placa == "BBB-222", "4.1 Estado Usuario B aislado", f"Sintoma: {s2.obtener_sintoma_completo()}")
    tester.assert_true(s1.obtener_sintoma_completo() != s2.obtener_sintoma_completo(), "4.1 Sin fuga de estado (No leak between sessions)", "Las sesiones compartían síntomas")

    # 4.2 TTL y Limpieza de sesiones expiradas
    s1.updated_at = time.time() - 10 # Forzar expiración (> 5 seg)
    sm.obtener_o_crear_sesion("user_C") # Dispara _limpiar_sesiones_expiradas
    tester.assert_true("user_A" not in sm._sesiones, "4.2 Expiración de sesión inactiva (TTL)", "La sesión user_A no fue eliminada tras expirar")
    tester.assert_true("user_B" in sm._sesiones, "4.2 Preservación de sesión activa", "La sesión user_B fue eliminada por error")

    # 4.3 Carga masiva de sesiones en memoria (10,000 sesiones)
    t0 = time.time()
    for i in range(10000):
        sm.acumular_input_usuario(f"sess_stress_{i}", f"sintoma test {i}")
    t_elapsed = (time.time() - t0) * 1000
    tester.assert_true(len(sm._sesiones) >= 10000, "4.3 Creación masiva de 10,000 sesiones en memoria", f"Total sesiones: {len(sm._sesiones)}, Tiempo: {t_elapsed:.2f}ms")

    # 4.4 Flujo multiturno completo con GestorDiagnostico
    gestor = GestorDiagnostico()
    sess_id = "multiturn_stress_user_1"

    # Step 1: Saludo
    r1 = gestor.procesar_consulta_texto("Hola buenas tardes", session_id=sess_id)
    tester.assert_true("Hola" in r1 or "CarBot" in r1, "4.4 Multiturno Turno 1 (Saludo)", f"Respuesta: {r1[:50]}...")

    # Step 2: Ambiguo
    r2 = gestor.procesar_consulta_texto("tengo un problema", session_id=sess_id)
    tester.assert_true("especifique" in r2.lower() or "detalle" in r2.lower(), "4.4 Multiturno Turno 2 (Ambiguo)", f"Respuesta: {r2[:50]}...")

    # Step 3: Detalle complementario -> activa diagnóstico y limpia sesión
    r3 = gestor.procesar_consulta_texto("se siente un chillido al frenar", session_id=sess_id)
    tester.assert_true("Posible Falla" in r3, "4.4 Multiturno Turno 3 (Diagnóstico Completo)", f"Respuesta: {r3[:50]}...")

    # Step 4: Consulta posterior -> debe ser independiente (sesión limpia)
    r4 = gestor.procesar_consulta_texto("hola", session_id=sess_id)
    tester.assert_true("Hola" in r4 or "CarBot" in r4, "4.4 Multiturno Turno 4 (Sesión reiniciada tras diagnóstico)", f"Respuesta: {r4[:50]}...")

    # --------------------------------------------------------------------------
    # CATEGORÍA 5: PRUEBA DE CONCURRENCIA MASIVA Y LATENCIA (< 2 SEGUNDOS)
    # --------------------------------------------------------------------------
    tester.log("\n--- CATEGORÍA 5: Concurrencia Masiva y Medición de Latencia (< 2000 ms) ---")

    def make_rest_request(idx):
        payload = {
            "sintoma": f"Freno chillando y pedal esponjoso solicitud concurrente {idx}",
            "marca": "Toyota",
            "modelo": "Yaris",
            "anio": 2018
        }
        t_start = time.time()
        try:
            res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json=payload, timeout=5)
            t_end = time.time()
            return idx, res.status_code, (t_end - t_start) * 1000
        except Exception as e:
            return idx, 500, -1.0

    NUM_CONCURRENT = 50
    tester.log(f"Lanzando {NUM_CONCURRENT} peticiones HTTP REST concurrentes...")
    
    latencies = []
    statuses = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_rest_request, i) for i in range(NUM_CONCURRENT)]
        for f in as_completed(futures):
            idx, code, lat = f.result()
            statuses.append(code)
            if lat > 0:
                latencies.append(lat)

    ok_count = sum(1 for s in statuses if s == 200)
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    max_lat = max(latencies) if latencies else 0.0
    min_lat = min(latencies) if latencies else 0.0
    
    tester.log(f"  • Peticiones exitosas (HTTP 200): {ok_count}/{NUM_CONCURRENT}")
    tester.log(f"  • Latencia Mínima: {min_lat:.2f} ms")
    tester.log(f"  • Latencia Promedio: {avg_lat:.2f} ms")
    tester.log(f"  • Latencia Máxima: {max_lat:.2f} ms")

    tester.assert_true(ok_count == NUM_CONCURRENT, "5.1 100% de respuestas HTTP 200 en concurrencia", f"{ok_count}/{NUM_CONCURRENT} exitosas")
    tester.assert_true(max_lat < 2000.0, "5.2 Latencia Máxima < 2000 ms bajo carga concurrente", f"Máxima latencia observada: {max_lat:.2f} ms (> 2000 ms)")

    # Test de concurrencia en Webhook POST
    def make_webhook_request(idx):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": f"5190000{idx:04d}",
                            "type": "text",
                            "text": {"body": f"Frenos duros mensaje webhook concurrente {idx}"}
                        }]
                    }
                }]
            }]
        }
        t_start = time.time()
        try:
            res = requests.post(f"{BASE_URL}/api/v1/webhook", json=payload, timeout=5)
            t_end = time.time()
            return idx, res.status_code, (t_end - t_start) * 1000
        except Exception as e:
            return idx, 500, -1.0

    tester.log(f"Lanzando {NUM_CONCURRENT} peticiones Webhook POST concurrentes...")
    wb_latencies = []
    wb_statuses = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_webhook_request, i) for i in range(NUM_CONCURRENT)]
        for f in as_completed(futures):
            idx, code, lat = f.result()
            wb_statuses.append(code)
            if lat > 0:
                wb_latencies.append(lat)

    wb_ok = sum(1 for s in wb_statuses if s == 200)
    wb_max = max(wb_latencies) if wb_latencies else 0.0
    wb_avg = sum(wb_latencies) / len(wb_latencies) if wb_latencies else 0.0

    tester.log(f"  • Webhook Peticiones exitosas: {wb_ok}/{NUM_CONCURRENT}")
    tester.log(f"  • Webhook Latencia Promedio: {wb_avg:.2f} ms")
    tester.log(f"  • Webhook Latencia Máxima: {wb_max:.2f} ms")

    tester.assert_true(wb_ok == NUM_CONCURRENT, "5.3 100% Webhook respuestas HTTP 200 en concurrencia", f"{wb_ok}/{NUM_CONCURRENT}")
    tester.assert_true(wb_max < 2000.0, "5.4 Webhook Latencia Máxima < 2000 ms", f"Máxima: {wb_max:.2f} ms")

    # --------------------------------------------------------------------------
    # RESUMEN Y VEREDICTO FINAL
    # --------------------------------------------------------------------------
    tester.log("\n================================================================================")
    tester.log(f"RESUMEN DE PRUEBAS ADVERSARIALES:")
    tester.log(f"  • Pruebas Pasadas: {tester.passed}")
    tester.log(f"  • Pruebas Fallidas: {tester.failed}")
    if tester.failed == 0:
        tester.log("VEREDICTO FINAL: APPROVE (El sistema es robusto y cumple todos los criterios)")
    else:
        tester.log("VEREDICTO FINAL: REJECT (Se encontraron fallos o vulnerabilidades)")
    tester.log("================================================================================")

    # Guardar log completo en archivo
    log_file = os.path.join(os.path.dirname(__file__), "test_execution.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tester.logs))

    return tester.failed == 0

if __name__ == "__main__":
    # Iniciar servidor Uvicorn en hilo secundario
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2.0) # Esperar inicialización del servidor

    success = run_all_tests()
    if not success:
        sys.exit(1)
