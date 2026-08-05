import sys
import os
import time
import threading
import requests
import uvicorn
import pandas as pd

sys.path.insert(0, os.getcwd())
from main import app
from src.core.gestor_diagnostico import GestorDiagnostico
from src.config import settings

SERVER_PORT = 8009
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")

def test_01_root_endpoint():
    print("\n--- TEST 1: Verificar Endpoint Raíz / ---")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    data = res.json()
    assert data["estado"] == "online"
    print(f"✅ Root OK: {data['sistema']}")

def test_02_webhook_get_verification():
    print("\n--- TEST 2: Verificar Webhook Meta GET ---")
    token = settings.VERIFY_TOKEN
    challenge = "test_challenge_12345"
    url = f"{BASE_URL}/api/v1/webhook?hub.mode=subscribe&hub.verify_token={token}&hub.challenge={challenge}"
    
    res = requests.get(url)
    assert res.status_code == 200
    assert res.text == challenge
    print(f"✅ Webhook GET Meta Verification OK: Challenge retornado = {res.text}")

def test_03_webhook_post_async_meta_payload():
    print("\n--- TEST 3: Webhook POST (Meta Cloud API) Asíncrono < 2s ---")
    meta_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "51987654321",
                        "type": "text",
                        "text": {"body": "Siento un chillido feo al frenar el auto"}
                    }]
                }
            }]
        }]
    }

    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/v1/webhook", json=meta_payload)
    t1 = time.time()
    elapsed_ms = (t1 - t0) * 1000

    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "procesado"
    assert elapsed_ms < 2000, f"Error: La respuesta demoró {elapsed_ms:.2f} ms (> 2000 ms)"
    print(f"✅ Webhook POST Meta OK: Respuesta en {elapsed_ms:.2f} ms (< 2000 ms) | Status: {res_json['status']}")

def test_04_webhook_post_async_twilio_payload():
    print("\n--- TEST 4: Webhook POST (Twilio Form Payload) Asíncrono ---")
    form_data = {
        "From": "whatsapp:+51912345678",
        "Body": "El motor cascabelea al acelerar en subida"
    }

    t0 = time.time()
    res = requests.post(
        f"{BASE_URL}/api/v1/webhook", 
        data=form_data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    t1 = time.time()
    elapsed_ms = (t1 - t0) * 1000

    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "procesado"
    assert elapsed_ms < 2000
    print(f"✅ Webhook POST Twilio OK: Respuesta en {elapsed_ms:.2f} ms")

def test_05_gestor_diagnostico_orquestador():
    print("\n--- TEST 5: Verificar Orquestador GestorDiagnostico (ML + RAG + LLM) ---")
    gestor = GestorDiagnostico()
    sintoma = "Pedal de freno se siente esponjoso al presionar"
    
    # 1. Test ML directo
    falla_ml, confianza = gestor.modelo_ml.predecir_falla_con_confianza(sintoma)
    assert falla_ml is not None
    assert confianza >= 0.0
    print(f"  • ML Prediction: '{falla_ml}' (Confianza: {confianza*100:.1f}%)")

    # 2. Test RAG directo
    contexto, titulo = gestor.motor_rag.recuperar_contexto(sintoma)
    assert contexto is not None
    print(f"  • RAG Retrieval: '{titulo}'")

    # 3. Test Flujo completo
    respuesta = gestor.procesar_consulta_texto(sintoma, placa="TEST-99", marca_modelo="Toyota Yaris")
    assert "🛠️ **1. Posible Falla Vehicular" in respuesta or "Posible Falla" in respuesta
    assert "📖 **2. Procedimiento Técnico" in respuesta or "Procedimiento" in respuesta
    assert "⏱️ **3. Tiempo Estimado" in respuesta or "Tiempo Estimado" in respuesta
    print("✅ GestorDiagnostico completó la orquestación en 3 secciones exitosamente.")

def test_06_rest_endpoint_diagnostico():
    print("\n--- TEST 6: Endpoint REST POST /api/v1/diagnostico/analizar ---")
    payload = {
        "sintoma": "El motor tiembla en minimo y la aguja de RPM oscila",
        "marca": "Hyundai",
        "modelo": "Elantra",
        "anio": 2017
    }

    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/v1/diagnostico/analizar", json=payload)
    t1 = time.time()
    elapsed_ms = (t1 - t0) * 1000

    assert res.status_code == 200
    data = res.json()
    assert "falla_predicha" in data
    assert "confianza" in data
    assert "respuesta_explicativa" in data
    assert "tiempo_respuesta_ms" in data
    print(f"✅ REST API Diagnóstico OK: Falla predicha = '{data['falla_predicha']}' ({data['confianza']}%) | Latencia = {elapsed_ms:.2f} ms")

def test_07_tracker_diagnosticos_continuous_logging():
    print("\n--- TEST 7: Verificar Registro Continuo en data/tracker_diagnosticos.csv (3 Fichas Tesis) ---")
    tracker_path = settings.TRACKER_PATH
    assert os.path.exists(tracker_path), f"Error: No existe el archivo {tracker_path}"
    
    df = pd.read_csv(tracker_path)
    columnas_esperadas = [
        "item", "fase", "fecha", "placa", "marca_modelo", "sintoma", 
        "falla_real", "chatbot_prediccion", "campos_completos", 
        "tiempo_diagnostico_minutos", "prediccion_correcta"
    ]
    for col in columnas_esperadas:
        assert col in df.columns, f"Falta la columna {col} en tracker_diagnosticos.csv"
        
    registros_totales = len(df)
    post_test_count = len(df[df['fase'] == 'Post-test'])
    print(f"✅ Tracker CSV OK: Total {registros_totales} registros ({post_test_count} Post-test). Todas las columnas de las 3 Fichas presentes.")

if __name__ == "__main__":
    print("=" * 80)
    print("EJECUTANDO SUITE COMPLETA DE PRUEBAS PARA AGENTE 2 (BACKEND & APIS)")
    print("=" * 80)
    
    # Iniciar servidor Uvicorn en segundo plano
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1.5) # Esperar arranque del servidor HTTP

    try:
        test_01_root_endpoint()
        test_02_webhook_get_verification()
        test_03_webhook_post_async_meta_payload()
        test_04_webhook_post_async_twilio_payload()
        test_05_gestor_diagnostico_orquestador()
        test_06_rest_endpoint_diagnostico()
        # Dar un momento breve para asegurar que las BackgroundTasks escriban en disco
        time.sleep(1.0)
        test_07_tracker_diagnosticos_continuous_logging()
        print("=" * 80)
        print("🎉 TODAS LAS PRUEBAS DEL AGENTE 2 HAN PASADO CON ÉXITO")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ FALLÓ UNA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
