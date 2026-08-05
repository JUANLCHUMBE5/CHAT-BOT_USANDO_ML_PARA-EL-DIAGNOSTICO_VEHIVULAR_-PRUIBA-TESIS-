# Infrastructure Documentation: E2E Testing Architecture & Feature Coverage

## 1. Overview
This document establishes the formal End-to-End (E2E) Test Infrastructure for the **Hybrid Vehicle Diagnostic Chatbot (ML + RAG + LLM)** deployed in automotive workshops in Carabayllo (2026). The testing framework validates system robustness, multi-vehicle diagnostic accuracy, API readiness, guardrail effectiveness, and scientific validity of thesis hypotheses.

---

## 2. 4-Tier Test Architecture

```
+-----------------------------------------------------------------------------------+
|                        4-TIER E2E TEST ARCHITECTURE                               |
+-----------------------------------------------------------------------------------+
| Tier 1: Core ML Classifier & Multi-Vehicle Data Integration                       |
|   - 42 Diagnostic Classes | RandomForest (300 estimators) | TF-IDF Vectorizer     |
|   - Multi-Vehicle: Cars (Gasolina/GLP/GNV), Heavy Trucks, EV/HEV                  |
|   - Metrics: >99% Test Accuracy, F1-Score, Precision, Recall, Confusion Matrix    |
+-----------------------------------------------------------------------------------+
| Tier 2: Knowledge Base, Vector RAG Retrieval & Conversational Guardrails          |
|   - FAISS Vectorstore | Manual Indexing (12 Technical Modules)                    |
|   - DTC OBD-II Code Normalization (e.g., P0300 misfire, C0035/C0040 brakes)        |
|   - Guardrails: Greeting intercept, Ambiguity slot-filling requests (<5 words)    |
+-----------------------------------------------------------------------------------+
| Tier 3: Presentation Layer, REST APIs, Webhooks & 4-Layer Decoupling              |
|   - FastAPI Backend (main.py) | CLI Interface (probar_diagnostico.py)             |
|   - REST Endpoint: POST /api/v1/diagnostico/analizar                              |
|   - Webhooks: GET Meta Verification, POST Meta Cloud API & Twilio (<2000 ms)     |
|   - Data Layer: Continuous logging to data/tracker_diagnosticos.csv (11 columns)  |
+-----------------------------------------------------------------------------------+
| Tier 4: Statistical Evaluation & Thesis Hypothesis Testing                        |
|   - Paired t-Student Test (scipy.stats.ttest_rel) on Pre-test vs Post-test times  |
|   - 3 Thesis Indicators: % Precision, % Completeness, Avg Diagnostic Time         |
|   - Automated Chart Generation: documentacion/graficas/ (Boxplot & Bar Charts)    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Tier Specifications & Scope

### Tier 1: Core ML Classifier & Multi-Vehicle Data Integration
- **Target File(s)**: `src/infrastructure/modelo_ml.py`, `training/entrenar_modelo.py`
- **Dataset**: `data/dataset_sintomas.csv` (4,190 samples, 42 classes)
- **Vehicle Scope**:
  1. **Cars (Gasolina / GLP / GNV)**: Ignition, fuel injection, brake pads/discs, clutch, suspension, electrical systems, door locks/chapas.
  2. **Heavy Trucks & Commercial Vehicles**: Pneumatic/air brakes (Scania APS Dataset), diesel common-rail injection (3500-DEFault Diesel), heavy transmission (SEU Gearbox), hydraulic steering (ZeMA Hydraulic).
  3. **Electric & Hybrid Vehicles (EV/HEV)**: HV lithium battery degradation (Zenodo Li-ion Battery), IGBT power inverter (PMSM Inverter), traction motor, regenerative braking (EVIoT), thermal management, Toyota Prius Gen 3 eCVT.
- **Verification Criteria**:
  - Classifier accuracy exceeds 99% on 20% test split.
  - Evaluation outputs macro & weighted F1-score, Precision, Recall, and saves `matriz_confusion.png`.

### Tier 2: Knowledge Base, Vector RAG Retrieval & Conversational Guardrails
- **Target File(s)**: `src/infrastructure/motor_rag.py`, `pruebas/test_patrones_diagnostico.py`
- **Knowledge Sources**: `manuales_taller/manual_procedimientos.txt` (12 workshop procedures)
- **Search Engine**: TF-IDF + Cosine Similarity / FAISS index (Dimension 380, Similarity threshold >= 0.12).
- **Features Tested**:
  - **Greeting Intercept**: Intercepts initial greetings ("Hola tengo problemas") returning welcome message without model invocation.
  - **Ambiguity Guardrail**: Detects generic queries ("el carro falla", <5 words) and prompts user for specific symptom context.
  - **DTC Expansion**: Resolves diagnostic codes (e.g. `P0300`, `C0035`, `C0040`) to precise step-by-step repair guides.

### Tier 3: Presentation Layer, REST APIs, Webhooks & 4-Layer Decoupling
- **Target File(s)**: `main.py`, `src/interfaces/api/v1/webhook.py`, `pruebas/test_backend_y_webhooks.py`
- **Endpoints Verified**:
  - `GET /`: Health check endpoint, returns status `"online"`.
  - `GET /api/v1/webhook`: Meta WhatsApp verification (`hub.mode=subscribe`, `hub.verify_token`, `hub.challenge`).
  - `POST /api/v1/webhook`: Asynchronous JSON payload parsing for Meta Cloud API & URL-encoded Form data for Twilio (Response latency < 2000 ms).
  - `POST /api/v1/diagnostico/analizar`: Structured JSON diagnostic request returning predicted fault, confidence %, step-by-step guidance, and response latency.
- **Data Logging**:
  - Background tasks continuously record diagnosis entries into `data/tracker_diagnosticos.csv` with 11 standard thesis columns (`item`, `fase`, `fecha`, `placa`, `marca_modelo`, `sintoma`, `falla_real`, `chatbot_prediccion`, `campos_completos`, `tiempo_diagnostico_minutos`, `prediccion_correcta`).

### Tier 4: Statistical Evaluation & Thesis Hypothesis Testing
- **Target File(s)**: `training/analizar_resultados_tesis.py`
- **Data Input**: `data/tracker_diagnosticos.csv` (Pre-test N=30 vs Post-test N=30)
- **Thesis Indicators Evaluated**:
  1. **Ficha 1 (Precision)**: % Correct predictions (Pre-test 80.00% vs Post-test 90.00%, +10.00% gain).
  2. **Ficha 2 (Completeness)**: % Complete diagnostic sheets (Pre-test 73.33% vs Post-test 100.00%, +26.67% gain).
  3. **Ficha 3 (Efficiency)**: Average diagnostic time per vehicle (Pre-test 33.57 min vs Post-test 9.07 min, -24.50 min reduction).
- **Hypothesis Testing**:
  - Paired t-Student test (`scipy.stats.ttest_rel`) yields T-statistic = 29.4162, P-value = 0.00000000 (< 0.05), rejecting $H_0$ and accepting $H_1$.
- **Automated Graphics**: Exports `comparacion_tiempos_diagnostico.png` and `comparacion_calidad_diagnostico.png` to `documentacion/graficas/`.

---

## 4. Feature Coverage Matrix

| Feature ID | Feature Description | Tier | Coverage Scope | Test Script | Status |
|------------|---------------------|------|----------------|-------------|--------|
| **F-01** | Multi-Vehicle Symptoms (42 Classes) | Tier 1 | Cars, Heavy Trucks, EV/HEV | `training/entrenar_modelo.py` | VERIFIED |
| **F-02** | Supervised ML Classifier (>99% Acc) | Tier 1 | RandomForest (300 estimators) | `training/entrenar_modelo.py` | VERIFIED |
| **F-03** | Technical Manual Vector RAG Index | Tier 2 | FAISS + TF-IDF (12 procedures) | `pruebas/test_patrones_diagnostico.py` | VERIFIED |
| **F-04** | Greeting Intercept Guardrail | Tier 2 | Conversational greeting response | `pruebas/test_patrones_diagnostico.py` | VERIFIED |
| **F-05** | Ambiguous Query Slot-Filling | Tier 2 | Interactive detail request | `pruebas/test_patrones_diagnostico.py` | VERIFIED |
| **F-06** | DTC Code Expansion (OBD-II) | Tier 2 | P0300, C0035, C0040 resolution | `pruebas/test_patrones_diagnostico.py` | VERIFIED |
| **F-07** | 3-Section Response Formatting | Tier 2 | Falla, Procedimiento, Tiempo | `pruebas/test_patrones_diagnostico.py` | VERIFIED |
| **F-08** | Root API Endpoint (`GET /`) | Tier 3 | System status verification | `pruebas/test_backend_y_webhooks.py` | VERIFIED |
| **F-09** | Meta Webhook Verification (`GET`) | Tier 3 | Meta hub.challenge response | `pruebas/test_backend_y_webhooks.py` | VERIFIED |
| **F-10** | Async Webhook Processing (`POST`) | Tier 3 | Meta Cloud API & Twilio (<2s) | `pruebas/test_backend_y_webhooks.py` | VERIFIED |
| **F-11** | REST Diagnostic Endpoint (`POST`) | Tier 3 | `/api/v1/diagnostico/analizar` | `pruebas/test_backend_y_webhooks.py` | VERIFIED |
| **F-12** | Continuous Logging in Tracker CSV | Tier 3 | 11 columns in `tracker_diagnosticos.csv` | `pruebas/test_backend_y_webhooks.py` | VERIFIED |
| **F-13** | Thesis Indicators Calculation | Tier 4 | Fichas 1, 2, 3 metrics | `training/analizar_resultados_tesis.py` | VERIFIED |
| **F-14** | t-Student Hypothesis Test | Tier 4 | `scipy.stats.ttest_rel` paired test | `training/analizar_resultados_tesis.py` | VERIFIED |
| **F-15** | Academic Chart Export | Tier 4 | PNG figures in `documentacion/graficas/` | `training/analizar_resultados_tesis.py` | VERIFIED |

---

## 5. Architectural Mapping (4 Decoupled Layers)

1. **Presentation Layer**:
   - `main.py` (FastAPI Server entry point)
   - `src/interfaces/api/v1/webhook.py` (Meta Cloud API & Twilio Webhook Router)
   - `probar_diagnostico.py` (Interactive CLI Interface)
2. **Application Layer**:
   - `src/core/gestor_diagnostico.py` (Central Diagnostic Orchestrator)
   - `src/core/audio_processor.py` (Voice symptom processing pipeline)
3. **AI Infrastructure Layer**:
   - `src/infrastructure/modelo_ml.py` (TF-IDF + RandomForest Classifier Engine)
   - `src/infrastructure/motor_rag.py` (FAISS / Vector Similarity Engine for Technical Manuals)
4. **Data Infrastructure Layer**:
   - `data/dataset_sintomas.csv` (4,190 multi-vehicle diagnostic samples)
   - `data/tracker_diagnosticos.csv` (Thesis tracking database)
   - `models/modelo_diagnostico.pkl` & `vectorizador_tfidf.pkl` (Trained model binaries)
   - `manuales_taller/` (Workshop manual sources)

---

## 6. Execution Environment & Dependencies
- **Python Version**: 3.10+
- **Key Dependencies**: `fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `numpy`, `scipy`, `faiss-cpu` / `scikit-learn cosine_similarity`, `matplotlib`, `seaborn`, `requests`, `python-multipart`.
