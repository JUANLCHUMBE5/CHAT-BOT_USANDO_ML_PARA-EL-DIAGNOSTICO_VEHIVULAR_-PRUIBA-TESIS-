# Project: Chatbot Híbrido de Diagnóstico Vehicular en talleres mecánicos de Carabayllo

## Architecture
4-Layer Modular Architecture:
1. Presentation Layer (`src/interfaces/api/v1/`, `main.py`, `probar_diagnostico.py` CLI)
2. Application Layer (`src/core/gestor_diagnostico.py`, session management / slot filling, `audio_processor.py`)
3. AI Layer (`src/infrastructure/modelo_ml.py`, `src/infrastructure/motor_rag.py`, Gemini LLM synthesizer)
4. Data Layer (`data/dataset_sintomas.csv`, `data/tracker_diagnosticos.csv`, `models/`, `manuales_taller/`)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Capture of Symptoms & Webhooks | Capture via REST, Webhook, CLI, Audio | M1 | R1 |
| 2 | Interactive Slot-Filling | Multi-turn session tracking for missing vehicle/symptom details | M1 | R1 |
| 3 | Standardized Response Output | 3-section output format (Falla, Recomendación, Tiempo) | M1 | R1 |
| 4 | CRISP-DM Data Prep & 48 Classes | 15,449 samples across 48 classes (Cars, Heavy Trucks, EV/HEV) with Peruvian idioms | M2 | R2 |
| 5 | RAG Knowledge Base & FAISS | 29 procedures indexing, DTC query expansion, threshold 0.12 | M2 | R2 |
| 6 | Predictive ML Modeling | RandomForestClassifier (300 trees), TF-IDF, >98.7% accuracy, F1 >98%, 48x48 Confusion Matrix | M3 | R3 |
| 7 | 4-Layer Modular Decoupling | Decoupled Presentation, Application, AI, Data layers with clean signatures | M4 | R4 |
| 8 | Guardrails & Anti-hallucination | Greeting, ambiguity, low confidence (<5%), fallback, LLM prompt guardrails | M5 | R5 |
| 9 | Statistical Evaluation (t-Student)| % Accuracy, % Completeness, Avg Time indicators, paired t-test export (t=29.4162, p<0.05) | M5 | R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 0 | E2E Testing Suite & Infrastructure | Test cases Tiers 1-4, `TEST_INFRA.md`, `TEST_READY.md` creation | none | DONE |
| 1 | M1: Presentation & App Interface Fix & Slot-Filling | Fix signature kwarg mismatch, handle webhooks, stateful slot-filling | none | DONE |
| 2 | M2: CRISP-DM Data Prep & Knowledge Base | 15,449 sample dataset, 48 fault classes, 29 RAG manuals vectorstore | none | VERIFIED |
| 3 | M3: Predictive ML Modeling & Validation Metrics | RandomForest >98.7% accuracy, F1 >98%, 48x48 confusion matrix PNG export | M2 | VERIFIED |
| 4 | M4: 4-Layer Architecture Integration & Decoupling | Integrate presentation endpoints with gestor, test webhooks (<2s latency) | M1, M3 | DONE |
| 5 | M5: Guardrails & Statistical Evaluation (t-Student)| Run R5 evaluation, paired t-Student report export (t=29.4162, p<0.05), PNG plots | M4 | VERIFIED |
| 6 | M6: E2E Verification & Forensic Integrity Audit | Execute full test panel (2 Reviewers, 2 Challengers, 1 Forensic Auditor) | M5, M0 | DONE |



## Interface Contracts
### Application Layer ↔ AI Layer
- `predict_diagnostic(symptoms: List[str]) -> Dict[str, Any]`: Retorna falla identificada, probabilidad y nivel de confianza.
- `retrieve_manual_context(query: str, top_k: int) -> List[Dict[str, Any]]`: Retorna fragmentos de manuales técnicos pertinentes.
- `generate_synthesized_response(prediction: str, context: List[str], symptom_details: Dict) -> Dict[str, str]`: Retorna estructura estandarizada (posible falla, recomendación técnica, tiempo estimado).

### Presentation Layer ↔ Application Layer
- `process_user_message(session_id: str, message: str) -> Dict[str, Any]` or `procesar_consulta_texto(texto_usuario: str, placa: Optional[str] = None, marca_modelo: Optional[str] = None, session_id: Optional[str] = None) -> str`: Handles conversation, tracks missing information, and delivers standardized report.

## Code Layout
- `src/interfaces/`: Presentation Layer (FastAPI endpoints, webhook router, CLI)
- `src/core/`: Application Layer (`gestor_diagnostico.py`, session state manager, audio processor)
- `src/infrastructure/`: AI & Data Infrastructure (`modelo_ml.py`, `motor_rag.py`)
- `data/`: Datasets (`dataset_sintomas.csv`, `tracker_diagnosticos.csv`)
- `models/`: Trained model binaries (`modelo_diagnostico.pkl`, `vectorizador_tfidf.pkl`)
- `manuales_taller/`: Workshop manual text sources for RAG vectorstore
- `pruebas/`: Test scripts, verification tools, statistical analysis (`analizar_resultados_tesis.py`)
- `documentacion/graficas/`: Exported confusion matrices and t-Student hypothesis plots
