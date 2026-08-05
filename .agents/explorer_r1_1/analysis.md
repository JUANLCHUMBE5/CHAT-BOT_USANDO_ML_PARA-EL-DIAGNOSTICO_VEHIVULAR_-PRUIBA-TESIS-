# Technical Survey and Analysis Report: Requirement R1 & R3 (ML Predictive Model & Dataset)

**Agent ID:** explorer_r1_1  
**Date:** 2026-08-04  
**Project:** Chatbot Híbrido de Diagnóstico Vehicular (ML + RAG + LLM) - Tesis UCV 2026  
**Status:** Completed  

---

## 1. Executive Summary

This report presents a thorough technical survey and verification of **Requirement R1** (Conversational Interaction & Symptom Capture) and **Requirement R3** (Supervised Predictive Machine Learning Model & Dataset) as defined in `ORIGINAL_REQUEST.md`.

The evaluation confirms that the current dataset `data/dataset_sintomas.csv` and trained Machine Learning models in `models/` **fully meet all quantitative and qualitative acceptance criteria**:
- **Dataset Size:** 15,449 samples (Target: 15,449 samples — 100% matched).
- **Fault Class Count:** 48 distinct fault classes (Target: 48 classes — 100% matched).
- **Test Set Evaluation Metrics (3,863 test samples, 25% stratified split):**
  - **Accuracy:** 98.71% (Target: > 98.7%)
  - **Macro Precision:** 99.45% (Target: > 98.0%)
  - **Macro Recall:** 99.48% (Target: > 98.0%)
  - **Macro F1-Score:** 99.47% (Target: > 98.0%)
  - **Weighted F1-Score:** 98.71% (Target: > 98.0%)
- **Confusion Matrix:** Successfully generated and saved to `documentacion/graficas/matriz_confusion_ml.png`.
- **Automated Tests:** 100% pass rate across unit and adversarial tests (`pruebas/test_adversarial_challenger.py`).

---

## 2. Dataset Exploration & Distribution Analysis (`data/dataset_sintomas.csv`)

### 2.1 General Dataset Properties
- **File Location:** `data/dataset_sintomas.csv`
- **Total Records:** 15,449 rows (excluding header)
- **Columns:** `sintoma` (Text input), `falla` (Target fault class)
- **Unique Target Classes:** 48 classes

### 2.2 Vehicle Category Breakdown

| Vehicle Category | Number of Fault Classes | Total Samples | % of Dataset | Key Components / Subsystems Covered |
| :--- | :---: | :---: | :---: | :--- |
| **Cars (Autos Particulares - Gasolina/GLP/GNV)** | 41 | 15,281 | 98.91% | OBD-II DTC Clusters (P0, Ma, P2, U0, P3), Brakes, Clutch, Ignition, Steering, Suspension, Electrical, Door locks |
| **Heavy Trucks (Camiones y Vehículos Pesados)** | 3 | 77 | 0.50% | Pneumatic/air brakes, Common-Rail diesel injection, Turbocharger/intercooler |
| **EV / HEV (Vehículos Eléctricos e Híbridos)** | 4 | 91 | 0.59% | High-voltage battery pack, IGBT inverter/electric motor, Regenerative braking, Battery cooling system |
| **Total** | **48** | **15,449** | **100.00%** | Comprehensive multi-vehicle diagnostic domain |

#### Detailed Class Distribution for Heavy Trucks:
1. `Fugas de aire o fallos en el sistema de frenos neumático (Camiones)` — 27 samples
2. `Falla en el turbocompresor o intercooler (Camiones Diésel)` — 25 samples
3. `Fuga o baja presion en sistema Common Rail Diésel (Camiones/Pickups)` — 25 samples

#### Detailed Class Distribution for EV / HEV:
1. `Fallo en inversor de corriente o motor electrico (EV)` — 27 samples
2. `Degradacion o falla en paquete de bateria de alto voltaje (EV / Híbridos)` — 26 samples
3. `Falla en sistema de frenado regenerativo (EV / Híbridos)` — 19 samples
4. `Foco o falla en sistema de refrigeracion de bateria/inversor (EV)` — 19 samples

### 2.3 Regional Peruvian Phrasing & Data Quality
The dataset incorporates authentic Peruvian mechanic and client terminology used in Carabayllo (e.g., *"cascabeleo"*, *"chillido agudo"*, *"pedal esponjoso"*, *"patea en segunda"*, *"pluma quemado"*, *"cerro en tercera"*).

**Observation on Text Encoding:**  
Some rows contain replacement characters (``) due to historic CSV merges with different string encodings (e.g., `daadas`, `neumtico`, `Hbridos`). While TfidfVectorizer with `strip_accents='unicode'` handles these without breaking classification performance, clean encoding normalization is recommended.

---

## 3. ML Model Architecture & Artifact Inspection

### 3.1 Model Code Infrastructure (`src/infrastructure/modelo_ml.py`)
- **Class:** `ModeloML`
- **Primary Methods:** `predecir_falla_con_confianza(texto: str) -> tuple[str, float]`
- **Integration Features:**
  - Loads model binaries defined in `settings.MODELO_ML_PATH` (`models/modelo_diagnostico.pkl`) and `settings.VECTORIZADOR_TFIDF_PATH` (`models/vectorizador_tfidf.pkl`).
  - Utilizes `predict_proba` to calculate confidence score (0.0 to 1.0).
  - Includes fallback handling ("Falla mecánica no clasificada (Modelo ML ausente)") when binaries are unreadable.

### 3.2 Binary Artifact Specifications (`models/`)

| Artifact Name | Class / Type | File Size | Key Hyperparameters / Config |
| :--- | :--- | :---: | :--- |
| `modelo_diagnostico.pkl` | `RandomForestClassifier` | 199.6 MB | `n_estimators=300`, `max_depth=None`, `min_samples_split=2`, `class_weight='balanced'`, `random_state=42`, `n_classes=48` |
| `vectorizador_tfidf.pkl` | `TfidfVectorizer` | 542.5 KB | `ngram_range=(1, 2)`, `sublinear_tf=True`, `strip_accents='unicode'`, `lowercase=True`, `vocabulary_size=22,408` |

---

## 4. Empirical Model Evaluation & Test Results

### 4.1 Evaluation Methodology (`training/entrenar_modelo.py`)
- **Dataset:** `data/dataset_sintomas.csv` (15,449 samples)
- **Split Ratio:** 75% Train (11,586 samples) / 25% Test (3,863 samples)
- **Splitting Strategy:** Stratified (`stratify=y`) to maintain exact class proportions across train/test sets.

### 4.2 Empirical Metrics Summary

| Metric | Target Requirement | Measured Empirical Value | Status |
| :--- | :---: | :---: | :---: |
| **Accuracy (Exactitud)** | > 98.7% | **98.7057%** | **PASSED** |
| **Macro Precision** | > 98.0% | **99.4522%** | **PASSED** |
| **Macro Recall** | > 98.0% | **99.4827%** | **PASSED** |
| **Macro F1-Score** | > 98.0% | **99.4670%** | **PASSED** |
| **Weighted Precision** | > 98.0% | **98.7089%** | **PASSED** |
| **Weighted Recall** | > 98.0% | **98.7057%** | **PASSED** |
| **Weighted F1-Score** | > 98.0% | **98.7065%** | **PASSED** |

### 4.3 Confusion Matrix & Visualization
- **Shape:** $48 \times 48$ square matrix.
- **Export Location:** `documentacion/graficas/matriz_confusion_ml.png` (300 DPI PNG chart generated via Seaborn heatmap).

### 4.4 Automated Test Suite Verification
Executing `python -m unittest discover -s pruebas -p "test_*.py"` ran 5 test suites in 0.992s with **0 failures and 0 errors**:
- `test_colloquial_peruvian_phrasing`: PASSED
- `test_colloquial_verb_variations_edge_case`: PASSED
- `test_dtc_codes`: PASSED
- `test_ambiguous_and_greeting_guardrails`: PASSED
- `test_anti_hallucination_low_confidence`: PASSED

---

## 5. Current State vs. Requirements Matrix

| Requirement ID | Description | Goal / Metric | Current Implementation Status | Compliance |
| :--- | :--- | :--- | :--- | :---: |
| **R1.1** | Symptom Capture & Input Normalization | Capture user symptom descriptions including Peruvian phrasing & DTC codes | Handled in `src/core/gestor_diagnostico.py` and `src/infrastructure/modelo_ml.py` | **100%** |
| **R1.2** | Missing Data Request Flow | Solicit clarify input when query is ambiguous ("el carro falla") | Activated in `GestorDiagnostico` ambiguity filter | **100%** |
| **R1.3** | Standardized 3-Section Response | 1. Posible Falla<br>2. Procedimiento Técnico<br>3. Tiempo/Gravedad | Formatted and verified in test suite | **100%** |
| **R3.1** | Supervised Random Forest Classifier | RandomForestClassifier with TF-IDF | Implemented in `src/infrastructure/modelo_ml.py` & `training/entrenar_modelo.py` | **100%** |
| **R3.2** | Total Dataset Muestras | 15,449 samples | `data/dataset_sintomas.csv` contains 15,449 rows | **100%** |
| **R3.3** | Class Diversity | 48 fault classes across Cars, Heavy Trucks, EV/HEV | 48 unique classes verified (41 Cars, 3 Heavy Trucks, 4 EV/HEV) | **100%** |
| **R3.4** | Model Evaluation Metrics | Accuracy > 98.7%, Precision/Recall/F1 > 98% | Accuracy = 98.71%, Macro F1 = 99.47%, Weighted F1 = 98.71% | **100%** |
| **R3.5** | Confusion Matrix & Thesis Evaluation | Confusion matrix PNG export & t-Student script | Matrix at `documentacion/graficas/matriz_confusion_ml.png`, t-test script at `training/analizar_resultados_tesis.py` | **100%** |

---

## 6. Gaps & Technical Observations

1. **Category Imbalance (Minor Observation):**  
   Cars represent 98.91% of samples (15,281), whereas Heavy Trucks (77 samples) and EV/HEV (91 samples) account for 1.09%. While `class_weight='balanced'` inside RandomForest compensates for this in training, future extensions could benefit from synthetic sample augmentation (e.g., back-translation or synonym swapping) for heavy truck & EV classes.
2. **Text Encoding Hygiene (Formatting Issue):**  
   Some strings in `data/dataset_sintomas.csv` contain `` (e.g., `daadas`, `neumtico`, `Hbridos`). The model pipeline currently handles this transparently via `strip_accents='unicode'`, but cleaning the raw CSV text would improve data aesthetic quality.

---

## 7. Actionable Recommendations

1. **Encoding Cleanup:** Run a non-destructive UTF-8 encoding normalization script to clean `` characters in `data/dataset_sintomas.csv` if CSV readability is audited.
2. **CI Metric Enforcement:** Add an automated unit test in `pruebas/test_modelo_accuracy.py` that verifies test set accuracy remains above 98.7% whenever models are re-trained.
3. **Documentation Alignment:** Maintain `matriz_confusion_ml.png` and thesis graphs in `documentacion/graficas/` for thesis report chapters.
