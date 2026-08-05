# Technical Survey and Exploration Report: Requirements R4 & R5

**Agent**: `explorer_r1_3`  
**Working Directory**: `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\.agents\explorer_r1_3`  
**Date**: 2026-08-04  
**Scope**: Exploration of Requirements R4 & R5 and associated Acceptance Criteria (4-Layer Architecture, FastAPI response performance, Student's t-test calculation, thesis indicators export, and test suite health).

---

## 1. Executive Summary

This report presents a thorough technical survey and analysis of the Chatbot Híbrido de Diagnóstico Vehicular system with respect to **Requirement R4 (4-Layer Architecture)** and **Requirement R5 (Testing, Guardrails & Statistical Evaluation of Thesis Variables)**.

Key findings:
1. **4-Layer Architecture (R4)**: Cleanly implemented and fully decoupled into Presentation (`src/interfaces/`), Application (`src/core/`), AI Infrastructure (`src/infrastructure/`), and Data (`data/`, `models/`, `manuales_taller/`).
2. **FastAPI & E2E Performance**: Server entry point `main.py` loads instantly and endpoints operate well within the < 2 second requirement (Webhook async response in 3.01–4.55 ms; REST diagnostic endpoint `/api/v1/diagnostico/analizar` in 28.32 ms).
3. **Statistical Hypothesis Testing (R5)**: The script `training/analizar_resultados_tesis.py` computes the paired Student's t-test using `scipy.stats.ttest_rel` on `data/tracker_diagnosticos.csv`, resulting in **T = 29.4162, P = 0.00000000 (< 0.05)**, rejecting $H_0$ and accepting the general thesis hypothesis.
4. **Thesis Indicators**: Evaluates Ficha 1 (% Precision: 80.00% Pre vs 99.81% Post), Ficha 2 (% Completeness: 73.33% Pre vs 100.00% Post), and Ficha 3 (Avg Diagnostic Time: 33.57 min Pre vs 1.15 min Post).
5. **Test Suite Health**: All automated test scripts (`test_patrones_diagnostico.py`, `test_backend_y_webhooks.py`, `test_session_manager.py`, `test_adversarial_challenger.py`) passed cleanly with 100% pass rates. `TEST_READY.md` is present at the project root.

---

## 2. Decoupled 4-Layer Architecture Survey (R4)

| Layer | Path / Component | Responsibilities & Decoupling Verification |
|---|---|---|
| **1. Presentation (Presentación)** | `main.py`<br>`src/interfaces/api/v1/router.py`<br>`src/interfaces/api/v1/endpoints/diagnostico.py`<br>`src/interfaces/api/v1/endpoints/webhook.py`<br>`src/interfaces/api/v1/schemas.py` | Exposes REST API `/api/v1/diagnostico/analizar` and Webhook `/api/v1/webhook` (Meta WhatsApp & Twilio payloads). Uses Pydantic DTOs (`SymptomRequestDTO`, `DiagnosticResponseDTO`, `WhatsAppWebhookPayloadDTO`). Handlers remain thin, delegating core processing via FastAPI `run_in_threadpool` and `BackgroundTasks`. |
| **2. Application (Aplicación)** | `src/core/gestor_diagnostico.py`<br>`src/core/session_manager.py`<br>`src/core/audio_processor.py`<br>`src/core/logger.py` | `GestorDiagnostico` orchestrates the ML + RAG + LLM workflow. Implements slot-filling for ambiguous inputs, multi-turn session tracking (`SessionManager`), audio pre-processing (`AudioProcessor`), structured 3-section output generation, and diagnostic logging to `data/tracker_diagnosticos.csv`. |
| **3. AI Infrastructure (Inteligencia Artificial)** | `src/infrastructure/modelo_ml.py`<br>`src/infrastructure/motor_rag.py` | Encapsulates AI dependencies.<br>- `ModeloML`: Loads Random Forest classifier & TF-IDF vectorizer, performs inference and confidence estimation.<br>- `MotorRAG`: Loads 25 technical manuals (58 procedural chunks), builds FAISS IndexFlatIP vector index with L2 normalized TF-IDF embeddings, query expansion with DTC codes, similarity thresholding (0.12). |
| **4. Data (Datos)** | `data/dataset_sintomas.csv`<br>`data/tracker_diagnosticos.csv`<br>`models/modelo_diagnostico.pkl`<br>`models/vectorizador_tfidf.pkl`<br>`manuales_taller/manual_procedimientos.txt` | Holds the 15,449-sample training dataset across 48 failure classes, model artifacts, technical manual corpus, and 1,622 evaluation logs tracking Pre-test and Post-test experimental metrics. |

---

## 3. Statistical Analysis & Thesis Indicators (R5)

### Script Location
- Script path: `training/analizar_resultados_tesis.py` *(Note: User prompt query referenced `pruebas/analizar_resultados_tesis.py`; actual verified path is `training/analizar_resultados_tesis.py`)*.
- Data source: `data/tracker_diagnosticos.csv` (1,622 total records: 30 Pre-test, 1,592 Post-test).

### Evaluated Thesis Indicators (Chapter IV)
1. **Ficha 1: Predicción de Fallas Vehiculares (Precisión)**
   - Pre-test: 24 / 30 correct predictions (**80.00%**)
   - Post-test: 1,572 / 1,575 correct predictions (**99.81%**)
   - **Improvement**: **+19.81%** increase in prediction accuracy.

2. **Ficha 2: Control de Información Diagnóstica (Completitud)**
   - Pre-test: 22 / 30 complete records (**73.33%**)
   - Post-test: 1,575 / 1,575 complete records (**100.00%**)
   - **Improvement**: **+26.67%** increase in complete diagnostic records.

3. **Ficha 3: Eficiencia del Diagnóstico (Tiempos)**
   - Pre-test Average: **33.57 min** per vehicle
   - Post-test Average: **1.15 min** per vehicle
   - **Reduction**: **-32.41 minutes** saved per vehicle diagnostic.

### Paired Student's t-test Calculation
- Formula: `scipy.stats.ttest_rel(pre_test['tiempo_diagnostico_minutos'], post_test['tiempo_diagnostico_minutos'])`
- **T-Statistic**: **29.4162**
- **P-Value**: **0.00000000** ($p < 0.05$)
- **Scientific Conclusion**: Reject $H_0$ (null hypothesis) and accept General Hypothesis $H_1$: *"El chatbot utilizando Machine Learning influye y mejora significativamente el diagnóstico vehicular en los talleres mecánicos de Carabayllo, 2026."*

---

## 4. FastAPI Server & Endpoint Latency Verification

| Endpoint | Test Method | Observed Latency | Requirement Threshold | Status |
|---|---|---|---|---|
| `GET /` | Root health check | < 5 ms | < 2,000 ms | PASS |
| `GET /api/v1/webhook` | Meta verification challenge | < 2 ms | < 2,000 ms | PASS |
| `POST /api/v1/webhook` | Asynchronous Meta/Twilio Webhook | 3.01 ms – 4.55 ms | < 2,000 ms | PASS |
| `POST /api/v1/diagnostico/analizar` | REST API diagnostic analysis | 28.32 ms | < 2,000 ms | PASS |
| Background Task | Full ML + RAG + LLM orchestration | 69.33 ms – 72.85 ms | Asynchronous | PASS |

---

## 5. Test Suite Health & Automated Verification

| Script / Test Suite | Executed Command | Results / Metrics | Status |
|---|---|---|---|
| Diagnostic Patterns & Guardrails | `python pruebas/test_patrones_diagnostico.py` | 4 / 4 tests passed (ambiguity, greeting, 3-section format, DTC P0300). | PASS |
| Backend & Webhook Integration | `python pruebas/test_backend_y_webhooks.py` | 7 / 7 tests passed (Uvicorn server, root, GET/POST webhooks, REST API, CSV tracker schema). | PASS |
| Multi-turn Session Manager | `python pruebas/test_session_manager.py` | Session state transitions and slot-filling turn aggregation verified. | PASS |
| Adversarial Challenger Suite | `python pruebas/test_adversarial_challenger.py` | 5 / 5 tests passed (greeting guardrails, anti-hallucination intercept, Peruvian slang, DTC resolution). | PASS |
| Thesis Statistical Analysis | `python training/analizar_resultados_tesis.py` | t-Student $T = 29.4162, P = 0.00000000$, statistical tables verified. | PASS |
| System Readiness File | Check `TEST_READY.md` | Present at project root with step-by-step verification commands. | PASS |

---

## 6. Current State vs. Requirements Matrix

| Requirement / Acceptance Criteria | Target Specification | Current State | Compliance |
|---|---|---|---|
| **R4. 4-Layer Architecture Decoupling** | Presentation, Application, AI, Data decoupled. | Cleanly structured in `src/interfaces/`, `src/core/`, `src/infrastructure/`, `data/`, `main.py`. | **FULL COMPLIANCE** |
| **R5. Statistical Hypothesis Testing** | Paired t-Student test with $p < 0.05$. | Implemented in `training/analizar_resultados_tesis.py` using `scipy.stats.ttest_rel`. Yields $T = 29.4162, P = 0.00000000$. | **FULL COMPLIANCE** |
| **R5. Thesis Indicators Export** | Accuracy, completeness, and response time. | Exported and formatted for Chapter IV thesis defense. | **FULL COMPLIANCE** |
| **FastAPI Performance** | Server startup and response < 2 seconds. | Endpoint latencies between 3.01 ms and 28.32 ms. | **FULL COMPLIANCE** |
| **Test Suite Health** | Passing E2E / component test suites. | All test suites in `pruebas/` pass cleanly. `TEST_READY.md` exists. | **FULL COMPLIANCE** |

---

## 7. Gaps & Recommendations

1. **Path Mapping Clarification**:
   - *Observation*: Prompts and legacy references occasionally refer to `pruebas/analizar_resultados_tesis.py`.
   - *Recommendation*: Keep `training/analizar_resultados_tesis.py` as the canonical location, or add a thin wrapper in `pruebas/analizar_resultados_tesis.py` redirecting to `training/analizar_resultados_tesis.py` to ensure compatibility with callers expecting it under `pruebas/`.

2. **Matplotlib Application Control Environment Issue**:
   - *Observation*: Running `training/analizar_resultados_tesis.py` on restricted Windows environments returns: `[Error] Error al generar las graficas: DLL load failed while importing _backend_agg: Una directiva de Control de aplicaciones bloqueó este archivo.`
   - *Recommendation*: Wrap plot generation in `try...except` (already done) or use pure headless backend setting (`matplotlib.use('Agg')`) so statistical output text always runs without interruption regardless of graphic backend OS policies.

3. **Continuous Monitoring**:
   - Keep running `python pruebas/test_backend_y_webhooks.py` and `python pruebas/test_patrones_diagnostico.py` as regression check before final presentation.
