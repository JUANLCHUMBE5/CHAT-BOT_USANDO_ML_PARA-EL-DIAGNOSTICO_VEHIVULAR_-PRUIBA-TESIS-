# Detailed Analysis Report: Requirements R1 & R4 Codebase Audit

**Project**: Chatbot Vehicular usando Machine Learning para Diagnóstico en Carabayllo  
**Analyst**: Codebase Explorer 1  
**Date**: 2026-07-26  
**Target Scope**: Requirement R1 (System Requirements & Conversational Interaction) & Requirement R4 (4-Layer Architecture: Presentation & Application Layers)

---

## 1. Executive Summary

This report presents a thorough analysis of the existing codebase under `src/interfaces/`, `src/core/`, `main.py`, `pruebas/`, and documentation files. The audit focuses on evaluating compliance with **Requirement R1** (Conversational Interaction, Symptom Extraction, Slot-Filling / Missing Data Prompts, and Standardized Response Structure) and **Requirement R4** (4-Layer Modular Architecture, specifically Presentation & Application Layer Decoupling).

### Summary of Key Findings:
1. **Requirement R1 (Conversational Interaction)**:
   - **Symptom Extraction**: ⚠️ **Basic/Implicit**. Raw user input text is directly forwarded to ML classification and TF-IDF RAG without explicit entity parsing, symptom normalization, or keyword extraction.
   - **Slot-Filling / Interactive Missing-Data Flow**: ❌ **NOT Implemented**. The system operates in a single-turn, stateless manner (`procesar_consulta_texto`). There is no dialogue manager, session tracker, or prompt mechanism to detect incomplete inputs (e.g., missing vehicle brand, model, noise condition) and ask follow-up clarification questions.
   - **Standardized Response Structure**: ⚠️ **Partially Implemented**. The system outputs a predicted failure (`diagnostico_ml`) and technical manual procedure (`contexto_manual`). However, it lacks explicit, standardized fields for **"Recomendación Técnica"** (formally categorized) and **"Tiempo Estimado"** (estimated repair or response time is completely missing from core response outputs).

2. **Requirement R4 (4-Layer Architecture & Decoupling)**:
   - **Presentation Layer (`src/interfaces/`)**: Properly structured into FastAPI v1 router (`router.py`) with endpoints for WhatsApp Webhook (`webhook.py`) and REST Diagnostic API (`diagnostico.py`).
   - **Application Layer (`src/core/`)**: Managed by `GestorDiagnostico` and `AudioProcessor`.
   - **Decoupling Assessment**: ⚠️ **Minor Architectural Leaks Detected**. `diagnostico.py` bypasses the core application service method (`procesar_consulta_texto`) and directly accesses internal core attributes (`gestor.modelo_ml.predecir_falla`, `gestor.motor_rag.recuperar_contexto`, `gestor.generar_respuesta_conversacional`), violating encapsulation between Presentation and Application layers. Additionally, prototype CLI scripts in `pruebas/` load `.pkl` models directly from root, bypassing `src/`.

---

## 2. Deep-Dive Evaluation: Requirement R1 (System Requirements & Conversational Interaction)

### 2.1 Symptom Extraction (Extracción de Síntomas)
- **Current Implementation**:
  - `src/interfaces/api/v1/endpoints/diagnostico.py:26-27`:
    ```python
    if not consulta.sintoma.strip():
        raise HTTPException(status_code=400, detail="El síntoma no puede estar vacío.")
    ```
  - `src/interfaces/api/v1/endpoints/webhook.py:49-52`:
    ```python
    if tipo_mensaje == "text":
        texto_cliente = msg["text"]["body"]
        respuesta = gestor.procesar_consulta_texto(texto_cliente)
    ```
  - `src/core/gestor_diagnostico.py:17-32`:
    ```python
    def procesar_consulta_texto(self, texto_usuario: str) -> str:
        diagnostico_predictivo = self.modelo_ml.predecir_falla(texto_usuario)
        contexto_manual, titulo_manual = self.motor_rag.recuperar_contexto(texto_usuario)
        respuesta_explicativa = self.generar_respuesta_conversacional(...)
        return respuesta_explicativa
    ```
- **Analysis**:
  - The input text string is passed raw into `modelo_ml.predecir_falla` and `motor_rag.recuperar_contexto`.
  - There is no specialized NLP module or rule-based extractor to isolate symptoms (e.g., "vibra pedal de freno", "chillido agudo en motor") from conversational filler (e.g., "Hola buenos días quisiera saber por qué...").

### 2.2 Interactive Missing-Data Prompt Flow / Slot-Filling (Slot-Filling e Interacción de Datos Faltantes)
- **Current Implementation**:
  - `GestorDiagnostico` contains no session memory, user state dictionary, or turn tracker.
  - If a user sends a vague message like `"mi carro suena"`, the system immediately executes `modelo_ml.predecir_falla("mi carro suena")` and `motor_rag.recuperar_contexto("mi carro suena")` in a single pass.
- **Analysis**:
  - **Deficit**: Requirement R1 requires an interactive prompt flow when symptom information is incomplete.
  - Currently, the system lacks:
    1. A slot evaluator (to verify if symptom details like sound type, component, frequency, vehicle make/model are present).
    2. A session state manager (e.g., Redis or in-memory dict keyed by `remitente` phone number).
    3. A conversational slot-filling prompt generator (e.g., *"¿El ruido ocurre al frenar o al acelerar?"*).

### 2.3 Standardized Response Structure (Posible Falla, Recomendación Técnica, Tiempo Estimado)
- **Current Implementation**:
  - `src/core/gestor_diagnostico.py:97-111` (Local fallback generator):
    ```python
    return (
        f"🛠️ **CarBot - Asistente de Taller**\n\n"
        f"El modelo de Machine Learning sugiere que la falla se asocia con: **{diagnostico_ml}**.\n\n"
        f"📖 *Procedimiento según el manual de taller*:\n"
        f"{contexto_manual}\n\n"
        f"¿Necesitas que te ayude a buscar otra falla o procedimiento técnico en el manual?"
    )
    ```
  - `src/interfaces/api/v1/endpoints/diagnostico.py:14-19` (REST Pydantic Model):
    ```python
    class ResultadoDiagnostico(BaseModel):
        sintoma: str
        diagnostico_ml: str
        manual_recuperado: str
        respuesta_explicativa: str
    ```
- **Analysis**:
  - **Posible Falla**: Covered by `diagnostico_ml`.
  - **Recomendación Técnica**: Extracted within `contexto_manual` or LLM text, but not structured into an explicit, dedicated field or labeled sub-section `"Recomendación Técnica"`.
  - **Tiempo Estimado (Estimated Time)**: ❌ **MISSING**. Neither the core application nor the API models include an estimated repair time (e.g., *"Tiempo estimado de reparación: 45 - 60 minutos"*) or estimated response duration.

---

## 3. Deep-Dive Evaluation: Requirement R4 (4-Layer Architecture - Presentation & Application)

### 3.1 Architecture Overview & Component Mapping

```
+-----------------------------------------------------------------------------------+
| 1. PRESENTATION LAYER (src/interfaces/ & main.py)                                 |
| - main.py                                                                         |
| - src/interfaces/api/v1/router.py                                               |
| - src/interfaces/api/v1/endpoints/webhook.py                                    |
| - src/interfaces/api/v1/endpoints/diagnostico.py                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. APPLICATION LAYER / CORE (src/core/)                                           |
| - src/core/gestor_diagnostico.py (GestorDiagnostico)                              |
| - src/core/audio_processor.py (AudioProcessor)                                   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. AI / INFRASTRUCTURE LAYER (src/infrastructure/)                                |
| - src/infrastructure/modelo_ml.py (ModeloML)                                     |
| - src/infrastructure/motor_rag.py (MotorRAG)                                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 4. DATA LAYER (data/, models/, manuales_taller/)                                 |
| - data/dataset_sintomas.csv, tracker_diagnosticos.csv                            |
| - models/modelo_diagnostico.pkl, vectorizador_tfidf.pkl                           |
| - manuales_taller/manual_procedimientos.txt                                       |
+-----------------------------------------------------------------------------------+
```

### 3.2 Evaluation of Presentation Layer (`src/interfaces/`)
- `main.py`:
  - Initializes FastAPI application.
  - Mounts `api_router` under prefix `/api/v1`.
  - Configures environment variables (`.env`).
  - Responsibilities strictly aligned with presentation server lifecycle.
- `src/interfaces/api/v1/endpoints/webhook.py`:
  - Implements Meta Webhook protocol (`GET /webhook` verification token check).
  - Handles incoming JSON payloads from Meta (`POST /webhook`).
  - Calls `gestor.procesar_consulta_texto(texto_cliente)` or `gestor.procesar_consulta_audio(audio_id)`.
  - Dispatches outgoing HTTP POST to Meta Graph API (`enviar_mensaje_whatsapp`).

### 3.3 Evaluation of Application Layer (`src/core/`)
- `src/core/gestor_diagnostico.py`:
  - Instantiates `ModeloML()`, `MotorRAG()`, and `AudioProcessor()`.
  - Provides entry point methods: `procesar_consulta_texto` and `procesar_consulta_audio`.
  - Handles Gemini API prompt augmentation and fallback formatting.
- `src/core/audio_processor.py`:
  - Implements signal processing algorithms (RMS energy calculation, FFT spectral analysis, high-frequency ratio thresholding).

### 3.4 Decoupling Assessment & Layer Leaks

1. **Abstraction Leak in `diagnostico.py`**:
   - In `src/interfaces/api/v1/endpoints/diagnostico.py:31-41`:
     ```python
     # Bypasses gestor.procesar_consulta_texto()
     diagnostico_ml = gestor.modelo_ml.predecir_falla(consulta.sintoma)
     contexto_manual, _ = gestor.motor_rag.recuperar_contexto(consulta.sintoma)
     respuesta_explicativa = gestor.generar_respuesta_conversacional(...)
     ```
   - **Architectural Violation**: The presentation endpoint exposes and orchestrates `gestor`'s internal infrastructure attributes (`modelo_ml`, `motor_rag`) instead of invoking a single application layer facade method.

2. **Hardcoded Meta HTTP Transporter in `webhook.py`**:
   - `webhook.py:71-93` defines `enviar_mensaje_whatsapp()`.
   - While HTTP endpoints belong in presentation, network delivery to Meta Graph API should ideally be abstracted into an infrastructure messaging adapter (e.g., `src/infrastructure/whatsapp_client.py`) to allow isolated unit testing.

3. **Bypass in Test Scripts**:
   - `pruebas/probar_diagnostico.py` loads `modelo_diagnostico.pkl` directly via `joblib.load()` rather than consuming `GestorDiagnostico` or `ModeloML`.

---

## 4. Requirement Compliance Summary Matrix

| Requirement Aspect | Current Code Location | Compliance Status | Key Deficits / Gaps |
|---|---|---|---|
| **R1: Symptom Extraction** | `diagnostico.py:26`, `gestor_diagnostico.py:17` | ⚠️ Partial | Input text is used raw without entity parsing or symptom normalization. |
| **R1: Slot-Filling / Missing Data Flow** | None | ❌ Missing | System is 100% single-turn. No state management, session memory, or missing-data prompt prompts. |
| **R1: Standardized Structure - Posible Falla** | `gestor_diagnostico.py:98-107` | ✅ Implemented | Included as `diagnostico_ml`. |
| **R1: Standardized Structure - Recomendación Técnica** | `gestor_diagnostico.py:108-109` | ⚠️ Partial | Present in text output, but not structured as a distinct output field. |
| **R1: Standardized Structure - Tiempo Estimado** | None | ❌ Missing | Estimated repair time or response time is completely missing from response structure. |
| **R4: Presentation Layer Definition** | `main.py`, `src/interfaces/api/v1/` | ✅ Implemented | Clean FastAPI router structure and Webhook setup. |
| **R4: Application Layer Definition** | `src/core/gestor_diagnostico.py` | ✅ Implemented | Orchestrates ML, RAG, and LLM logic. |
| **R4: Presentation-Application Decoupling** | `diagnostico.py:31-41` | ⚠️ Minor Leaks | REST endpoint accesses internal `gestor.modelo_ml` and `gestor.motor_rag` attributes directly. |

---

## 5. Architectural Recommendations for Implementation

1. **Implement Dialogue State & Slot-Filling in `src/core/`**:
   - Add a `SesionUsuario` manager in `src/core/` to track dialogue turn state per phone number.
   - Add a slot-checker method in `GestorDiagnostico` to evaluate symptom completeness (e.g., checking if noise type, system location, or vehicle condition are present). If incomplete, return a clarification prompt.

2. **Standardize Output Data Contracts**:
   - Update `ResultadoDiagnostico` in `diagnostico.py` and response formatter in `gestor_diagnostico.py` to explicitly return:
     - `posible_falla: str`
     - `recomendacion_tecnica: str`
     - `tiempo_estimado: str` (e.g., "30-45 minutos de inspección / reparación")
     - `procedimiento_manual: str`

3. **Encapsulate Application Layer Access in REST Endpoints**:
   - Refactor `src/interfaces/api/v1/endpoints/diagnostico.py` to call `gestor.procesar_consulta_texto(consulta.sintoma)` or a structured core method `gestor.diagnosticar_sintoma_estructurado(consulta.sintoma)`, eliminating direct endpoint access to `gestor.modelo_ml` and `gestor.motor_rag`.
