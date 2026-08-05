# Technical Survey Analysis Report: Requirement R1 & R2 (RAG Knowledge Base, Technical Manuals & LLM Integration)

**Agent**: `explorer_r1_2`  
**Date**: 2026-08-04  
**Project**: Chatbot Híbrido de Diagnóstico Vehicular (Tesis UCV 2026 - Carabayllo)  
**Target Directory**: `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING`  

---

## 1. Executive Summary

This report presents a thorough technical survey and analysis of **Requirement R1 & R2** focusing on:
1. **RAG Knowledge Base & Technical Service Manuals**: Section verification of `manuales_taller/manual_procedimientos.txt`.
2. **RAG Retrieval Engine & FAISS Vectorstore**: Indexing mechanisms, similarity thresholds, and query expansion in `src/infrastructure/motor_rag.py`.
3. **Peruvian Mechanical Idioms**: Representation in `data/dataset_sintomas.csv` and handling in query preprocessing/slot-filling.
4. **LLM Integration & Prompt Engineering**: Gemini 1.5 Flash synthesis logic and enforcement of the 3 required structured sections (`Posible Falla`, `Procedimiento Técnico`, `Tiempo/Gravedad`).

---

## 2. Requirement Alignment & Goal Analysis

| Requirement Area | Target Specification | Current System Implementation | Status / Compliance |
|---|---|---|---|
| **Technical Manuals (RAG)** | Goal: $\ge 25$ technical service manuals/procedures in `manuales_taller/manual_procedimientos.txt`. | 29 distinct, fully detailed technical procedures formatted with `=== PROCEDIMIENTO:` section headers. | **COMPLIANT** (Exceeds goal: 29 vs 25) |
| **Vectorstore Engine** | FAISS Vectorstore Indexing & Cosine Similarity search with query expansion. | FAISS `IndexFlatIP` over L2-normalized TF-IDF embeddings with automatic DTC & colloquial idiom query expansion. | **COMPLIANT** |
| **Similarity Threshold** | Controlled retrieval threshold to filter irrelevant procedures. | `umbral = 0.12` default cosine similarity threshold in `MotorRAG.recuperar_contexto()`. | **COMPLIANT** |
| **Peruvian Idioms** | Integration of Carabayllo / Peruvian mechanic terminology in dataset and query handling. | 15,449 dataset rows with local phrasing ("cascabeleo", "chillido agudo", "pedal esponjoso", "buches", "hola maestro", "en carabayllo"); domain expansion dictionary in `motor_rag.py`. | **COMPLIANT** |
| **LLM Synthesis Logic** | Gemini 1.5 synthesis structured strictly into 3 sections (Posible Falla, Procedimiento Técnico, Tiempo/Gravedad). | Single-verdict prompt template sending ML prediction + RAG manual context to Gemini 1.5 Flash (`generateContent`), backed up by local 3-section fallback. | **COMPLIANT** |

---

## 3. Detailed Component Survey & Evidence Chain

### 3.1. RAG Knowledge Base (`manuales_taller/manual_procedimientos.txt`)

- **File Path**: `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\manuales_taller\manual_procedimientos.txt`
- **File Size**: 33,682 bytes | 376 lines.
- **Section Count**: **29 distinct procedures** (exceeds the 25 manual target).
- **Structure**: Each section is delineated by `=== PROCEDIMIENTO: [TITULO] ===` and includes:
  - Associated DTC error code (`Código de Falla Asociado`)
  - Compatible vehicle models in Peru (`Modelos Compatibles Frecuentes en Perú`)
  - Gravity and estimated shop time (`Gravedad` | `Tiempo Estimado de Taller`)
  - Observed symptoms (`Síntomas`)
  - Step-by-step technical instructions (`Instrucciones paso a paso`)
- **Domain Coverage**:
  - *Light Vehicles (Gasoline/GLP/GNV)*: Brakes (Pads/Discs, Fluid Flush, Drums/Shoes, ABS), Fuel Injection (Ultrasonic Cleaning, Throttle Body/IAC, Fuel Pump, MAF/MAP), Body/Locks, Suspension & Steering (Struts/Bushings, CV Joints, Tie Rods, Hydraulic/EPS), Transmission (Clutch kit, ATF/CVT fluid, Manual Gearbox), Engine (Spark plugs/Misfire, Timing belt/chain, Head gasket, Oil/Sump, CKP/CMP sensors), HVAC (Refrigerant R134a, AC Compressor, Evaporator), OBD-II Diagnostics (DTC Reading/Clearing, O2/Lambda sensor, STFT/LTFT Air-Fuel Ratio).
  - *Heavy Trucks*: Air brake systems (Scania / Volvo / SPN 1087).
  - *Electric & Hybrid Vehicles (EV/HEV)*: High Voltage Battery & IGBT Inverter (DTC P0A80).

### 3.2. FAISS Vectorstore & Retrieval Logic (`src/infrastructure/motor_rag.py`)

- **File Path**: `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\src\infrastructure\motor_rag.py`
- **Vectorization**: `TfidfVectorizer(lowercase=True, strip_accents='unicode')`.
- **FAISS Index Type**: `faiss.IndexFlatIP(dimension)` (Inner Product index). Prior to indexing and searching, document and query vectors are normalized via `faiss.normalize_L2()`, making Inner Product mathematically identical to exact Cosine Similarity.
- **Query Expansion (`_expandir_consulta`)**:
  ```python
  diccionario_dtc = {
      "p0300": "bujias cascabeleo misfire encendido",
      "p0301": "bujias cascabeleo misfire encendido",
      "c0035": "pastillas de freno chillido disco",
      "c0040": "purga liquido de frenos pedal esponjoso fuga",
      "p0505": "valvula iac cuerpo de aceleracion ralenti minimo apaga",
      "p0562": "bateria voltaje arranque alternador bornes",
      "chillido": "pastillas de freno freno",
      "esponjoso": "liquido de frenos purga fuga",
      "cascabelea": "bujias motor encendido",
      "cascabeleo": "bujias motor encendido",
      "se apaga": "valvula iac minimo ralenti"
  }
  ```
- **Retrieval Threshold**: `umbral = 0.12`. If `mejor_similitud < 0.12`, the system returns a safe fallback (`"No se encontró un procedimiento específico en nuestros manuales para esta consulta."`, `"Coincidencia baja"`), preventing irrelevant manual matches.

### 3.3. Peruvian Mechanical Idioms & Preprocessing

- **Dataset Representation**:
  - `data/dataset_sintomas.csv` contains 15,449 rows across 48 failure classes.
  - Phrasing embeds local Peruvian mechanics terminology and regional conversational patterns:
    - *Greetings / Openers*: "hola maestro", "amigo una consulta", "buenas tardes maestro", "sabes que", "resulta que", "mi carro presenta".
    - *Localities*: "en carabayllo", "en la pista", "cuando salgo a trabajar".
    - *Idiomatic terms*: "cascabeleo" (knocking/misfire), "chillido agudo" (brake squeal), "pedal esponjoso" / "pedal largo" (soft brake pedal), "golpe en buches" (strut noise), "clac clac al doblar" (CV joint noise), "juego en timón" (steering play), "pila de combustible" (fuel pump), "empaque soplado" (blown head gasket), "pateo de caja" (transmission shock).
- **Query Preprocessing in `src/core/gestor_diagnostico.py`**:
  - `_es_saludo_o_contacto_inicial()`: Intercepts generic greetings before ML classification.
  - `_es_consulta_ambigua()`: Detects vague inputs (< 3 words or general statements like "el carro falla") and requests specific symptom details (Slot-Filling trigger).
  - ML Vectorizer (`vectorizador_tfidf.pkl`): Trained on unigrams and bigrams (`ngram_range=(1,2)`), allowing seamless mapping of Peruvian idioms to standard failure classes.

### 3.4. LLM Integration & Structured Output (Gemini 1.5)

- **File Path**: `src/core/gestor_diagnostico.py` (`generar_respuesta_conversacional`)
- **API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
- **Prompt Engineering**:
  - Enforces the **Single Verdict Rule** to eliminate LLM hallucinations and contradictory diagnosis choices.
  - Passes the predicted ML class, ML confidence percentage, RAG manual title, and RAG manual step-by-step content into the prompt context.
  - Mandates output in **3 required sections**:
    1. 🛠️ **1. Posible Falla Vehicular**: Displays the ML-predicted diagnosis and confidence level.
    2. 📖 **2. Procedimiento Técnico de Reparación**: RAG-extracted step-by-step guide.
    3. ⏱️ **3. Tiempo Estimado y Gravedad**: Estimated labor time and urgency level.
- **Fallback Guarantee**: In case of API quota exhaustion, key absence, or network offline status, the orchestrator generates a deterministic local response adhering strictly to the same 3-section layout.

---

## 4. Current State vs Requirements Comparison Matrix

| Feature / Metric | Thesis Requirement | Survey Observation | Compliance |
|---|---|---|---|
| RAG Manual Sections | $\ge 25$ technical manuals | 29 technical procedure sections | Exceeds Requirement |
| Vectorstore Engine | FAISS similarity retrieval | FAISS `IndexFlatIP` + L2 Normalization + Query Expansion | Fully Compliant |
| Peruvian Idioms Support | Carabayllo workshop jargon | Enriched dataset (15,449 rows) + `_expandir_consulta` mapping | Fully Compliant |
| LLM Integration | Gemini 1.5 Flash structured synthesis | REST API call + single-verdict prompt template + 3-section format | Fully Compliant |
| Structured Sections | Posible Falla, Procedimiento Técnico, Tiempo/Gravedad | 3 exact markdown headers enforced in prompt and fallback | Fully Compliant |

---

## 5. Recommendations for Further Enhancement

1. **Expand RAG Query Expansion Dictionary**:
   - Add specific heavy truck (Scania / Volvo) and EV/HEV terms to `_expandir_consulta()` in `src/infrastructure/motor_rag.py` (e.g., `spn 1087` $\rightarrow$ `frenos de aire aire neumático camión`, `p0a80` $\rightarrow$ `bateria alto voltaje inversor igbt ev hev`).
2. **Log Retrieval Similarity Scores**:
   - Add debug/info logging of the raw FAISS similarity score in `recuperar_contexto()` to simplify monitoring of retrieval quality in production logs.
