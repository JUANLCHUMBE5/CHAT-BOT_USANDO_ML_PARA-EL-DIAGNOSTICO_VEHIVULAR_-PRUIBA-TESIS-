# Evaluation & Analysis Report: Requirement R2 (CRISP-DM & RAG) & Requirement R3 (Predictive ML & Metrics)

**Target Codebase**: `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING`  
**Author**: Codebase Explorer 2  
**Date**: 2026-07-26  

---

## Executive Summary

This report delivers a thorough analysis of Requirement **R2** (CRISP-DM Data Preparation & RAG Knowledge Base) and Requirement **R3** (Predictive ML Model & Evaluation Metrics) across the diagnostic chatbot codebase.

Key findings include:
1. **Data & CRISP-DM (R2)**: CRISP-DM methodology is conceptualized in documentation (`documentacion/notas/explicacion_metodologia_y_software.md`), but data cleaning is limited to TF-IDF built-in lowercasing/accent stripping (`TfidfVectorizer(lowercase=True, strip_accents='unicode')`). Crucially, **train/test splitting (`train_test_split`) is omitted** in `training/entrenar_modelo.py` (model trained and evaluated on 100% of data).
2. **Predictive ML & Metrics (R3)**: Uses `RandomForestClassifier(n_estimators=100, random_state=42)`. Training exactitud (accuracy) is calculated (100%), but **Precisión, Recall, F1-score, and Matriz de Confusión are NOT calculated or exported** in training scripts (`training/entrenar_modelo.py`), despite `classification_report` being imported.
3. **RAG Mechanism (R2)**: RAG indexes `manuales_taller/manual_procedimientos.txt` by splitting on `===` headers, vectorizing chunk bodies via TF-IDF, and performing cosine similarity search (`sklearn.metrics.pairwise.cosine_similarity`) with a threshold of `0.15`.
4. **Integration**: `src/core/gestor_diagnostico.py` synthesizes ML prediction + RAG manual context into Gemini 1.5 Flash prompt or local fallback.

---

## 1. Codebase Component Inspection

### 1.1 Datasets (`data/`)
* **`data/dataset_sintomas.csv`** (63 rows, 7,151 bytes):
  - Created by `training/generar_dataset.py`.
  - Schema: `sintoma` (text input string), `falla` (target diagnostic class).
  - Contains symptom phrases in Spanish, including local Peruvian automotive jargon (e.g., *"cascabelea"*, *"rompemuelles"*, *"se chupa"*, *"timón"*).
* **`data/tracker_diagnosticos.csv`** (60 rows, 7,794 bytes):
  - Field experiment evaluation dataset used by `training/analizar_resultados_tesis.py`.
  - Contains 30 Pre-test records (without chatbot) and 30 Post-test records (with chatbot).
  - Schema includes: `item`, `fase`, `fecha`, `placa`, `marca_modelo`, `sintoma`, `falla_real`, `chatbot_prediccion`, `campos_completos`, `tiempo_diagnostico_minutos`, `prediccion_correcta`.

### 1.2 Trained Artifacts (`models/`)
* **`models/modelo_diagnostico.pkl`** (3,908,009 bytes): Saved Scikit-Learn `RandomForestClassifier` serialized via `joblib`.
* **`models/vectorizador_tfidf.pkl`** (5,228 bytes): Saved `TfidfVectorizer` serialized via `joblib`.

### 1.3 Workshop Knowledge Base (`manuales_taller/`)
* **`manuales_taller/manual_procedimientos.txt`** (35 lines, 2,850 bytes):
  - Structured text manual containing 3 mechanical repair procedures:
    1. `PROCEDIMIENTO: CAMBIO DE BUJÍAS (FALLAS DE MOTOR / CASCABELEO)` (lines 1-11)
    2. `PROCEDIMIENTO: REEMPLAZO DE PASTILLAS DE FRENO (CHILLIDO AL FRENAR)` (lines 13-23)
    3. `PROCEDIMIENTO: PURGA Y FUGA DE LÍQUIDO DE FRENOS (PEDAL ESPONJOSO)` (lines 25-34)
  - Delimited by `===` headers.

### 1.4 Infrastructure & Core Code (`src/`)
* **`src/infrastructure/modelo_ml.py`**:
  - Class `ModeloML`: loads `modelo_diagnostico.pkl` and `vectorizador_tfidf.pkl`.
  - Method `predecir_falla(texto: str) -> str`: transforms text via vectorizer and returns single string class prediction.
* **`src/infrastructure/motor_rag.py`**:
  - Class `MotorRAG`: reads `manual_procedimientos.txt`, splits by `===`, builds TF-IDF matrix for documents, and executes cosine similarity retrieval.
* **`src/core/gestor_diagnostico.py`**:
  - Class `GestorDiagnostico`: orchestrates `ModeloML`, `MotorRAG`, and `AudioProcessor`.
  - Method `procesar_consulta_texto(texto)`: calls `modelo_ml.predecir_falla`, `motor_rag.recuperar_contexto`, and `generar_respuesta_conversacional`.

---

## 2. Evaluation of CRISP-DM Methodology & Data Preparation

### 2.1 Applied CRISP-DM Steps
CRISP-DM (Cross-Industry Standard Process for Data Mining) phases evaluated in codebase:

| CRISP-DM Phase | Status in Code | Code Location & Observations |
|---|---|---|
| **1. Business Understanding** | Documented | Defined in `documentacion/notas/explicacion_metodologia_y_software.md` (lines 34-40). Goal: improve diagnostic time and accuracy in Carabayllo workshops. |
| **2. Data Understanding** | Applied | Implemented in `training/generar_dataset.py` (90 sample items reduced to 63 rows in CSV). |
| **3. Data Preparation: Cleaning** | Partial | **No dedicated cleaning pipeline** (no stopword removal, regex normalization, stemming). Text cleaning relies solely on `TfidfVectorizer(lowercase=True, strip_accents='unicode')` (`training/entrenar_modelo.py:25`). |
| **4. Data Preparation: Encoding** | Applied | Features (`sintoma`) encoded into TF-IDF numerical sparse matrix (`training/entrenar_modelo.py:26`). Target labels (`falla`) managed as string categorical classes. |
| **5. Data Preparation: Splitting** | **Missing** | `train_test_split` imported on line 4 of `training/entrenar_modelo.py`, but **commented out / bypassed** (lines 29-32). Model is trained on 100% of data. |
| **6. Modeling** | Applied | `RandomForestClassifier(n_estimators=100, random_state=42)` fitted in `training/entrenar_modelo.py:31-32`. |
| **7. Evaluation** | Partial | Training accuracy computed (`100.00%`). No test set evaluation performed. |
| **8. Deployment** | Applied | Models saved to `models/` via `joblib.dump` (`entrenar_modelo.py:42-43`) and loaded by `src/infrastructure/modelo_ml.py`. |

### 2.2 Discrepancies with Thesis Documentation
* In `documentacion/notas/preguntas_jurado_tesis_i.md` (line 141), the thesis defense guide states:
  > *"Evaluación: Análisis preliminar de la exactitud usando división de train/test."*
* However, in `training/entrenar_modelo.py` (lines 29-32), the actual code explicitly states:
  ```python
  # Dado que el dataset es pequeño para un split grande, lo entrenamos con todos los datos para la demo,
  # pero imprimiremos el reporte de entrenamiento.
  modelo = RandomForestClassifier(n_estimators=100, random_state=42)
  modelo.fit(X_vectorizado, y)
  ```
  Therefore, train/test splitting was **not applied** during training.

---

## 3. Evaluation of Predictive ML Model & Metrics (R3)

### 3.1 Model Classifier Architecture
- **Algorithm**: Scikit-Learn `RandomForestClassifier(n_estimators=100, random_state=42)`.
- **Feature Extraction**: Scikit-Learn `TfidfVectorizer(lowercase=True, strip_accents='unicode')`.
- **Alternative Classifiers**: XGBoost is not implemented or present in the codebase.

### 3.2 Evaluation Metrics Audit

| Requirement Metric | Found in Training Script? (`entrenar_modelo.py`) | Found in Notebook? (`presentacion_resultados_tesis.ipynb`) | Found in Thesis Script? (`analizar_resultados_tesis.py`) |
|---|---|---|---|
| **Exactitud (Accuracy)** | **Yes** (`accuracy_score(y, predicciones)` = 100.00%) | **Yes** (`accuracy_score` cell) | **Indirect** (Field accuracy: 66.67% vs 90.00%) |
| **Precisión (Precision)** | **No** (`classification_report` imported but unused) | **No** (Not executed for ML classes) | **No** (Only counts correct field predictions) |
| **Recall** | **No** | **No** | **No** |
| **F1-Score** | **No** | **No** | **No** |
| **Matriz de Confusión** | **No** | **Partial** (`ConfusionMatrixDisplay` plot cell exists for train set, not exported) | **No** |

### 3.3 Key Gaps in ML Metrics Implementation
1. **Unused Imports**: In `training/entrenar_modelo.py` line 6:
   ```python
   from sklearn.metrics import classification_report, accuracy_score
   ```
   `classification_report` is imported but never invoked.
2. **Lack of Generalization Testing**: Overfitting cannot be measured because there is no hold-out validation set or $k$-fold cross-validation.

---

## 4. Evaluation of RAG Indexing & Similarity Retrieval (R2)

### 4.1 Manual Structure & Parsing
- **Knowledge File**: `manuales_taller/manual_procedimientos.txt`.
- **Chunking Method**: In `src/infrastructure/motor_rag.py` lines 26-34:
  ```python
  secciones = [sec.strip() for sec in contenido.split("===") if sec.strip()]
  for sec in secciones:
      lineas = sec.split("\n")
      titulo = lineas[0] if lineas else "Procedimiento de Taller"
      cuerpo = "\n".join(lineas[1:])
      self.titulos.append(titulo)
      self.documentos.append(cuerpo)
  ```
  Chunks are created deterministically based on `===` section separators in the manual.

### 4.2 Vectorization & Similarity Retrieval
- **Vector Store**: Sparse TF-IDF matrix built using `TfidfVectorizer(lowercase=True, strip_accents='unicode')` (`motor_rag.py:36-37`).
- **Retrieval Pipeline** (`motor_rag.py:42-59`):
  1. Vectorize query: `consulta_vec = self.vectorizador.transform([consulta])`
  2. Compute Cosine Similarity: `similitudes = cosine_similarity(consulta_vec, self.documentos_vectorizados)[0]`
  3. Find Highest Match: `indice_mejor = np.argmax(similitudes)`
  4. Threshold Check: `if mejor_similitud < umbral:` (default `umbral = 0.15`).
  5. Fallback behavior: If `mejor_similitud < 0.15`, returns `"No se encontró un procedimiento específico en nuestros manuales para esta consulta."`, `"Coincidencia baja"`.

### 4.3 LLM Prompt Augmentation & Synthesis
- In `src/core/gestor_diagnostico.py` lines 65-111, `GestorDiagnostico` injects retrieved RAG context and ML prediction into Gemini 1.5 Flash prompt:
  ```python
  prompt_sistema = f"""
  Eres 'CarBot', un asistente técnico de soporte inteligente para el mecánico del taller en Carabayllo.
  
  Información del sistema de IA:
  - Nuestro modelo de Machine Learning predijo que la falla se asocia con: {diagnostico_ml}
  - Información del manual técnico de taller recuperada (RAG):
  {contexto_manual}
  
  Consulta técnica del mecánico: "{pregunta}"
  ...
  """
  ```

---

## 5. Summary of Gaps & Actionable Recommendations

To bring Requirements R2 and R3 to full technical and academic compliance:

1. **Implement Proper CRISP-DM Train/Test Split & Cross-Validation (R2/R3)**:
   - Modify `training/entrenar_modelo.py` to use `train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)` or Stratified K-Fold cross-validation.
2. **Calculate Complete ML Metrics Suite (R3)**:
   - Call `classification_report(y_test, y_pred, zero_division=0)` to compute Exactitud, Precisión, Recall, and F1-score per class and weighted average.
   - Generate and save `confusion_matrix` image artifact to `documentacion/graficas/matriz_confusion_ml.png`.
3. **Enhance Text Cleaning (R2)**:
   - Implement explicit text cleaning (stopword removal using NLTK/spaCy or custom Spanish list, regex punctuation removal) prior to TF-IDF vectorization.
4. **Expand RAG Knowledge Base Indexing (R2)**:
   - Allow indexing multiple text/PDF manuals in `manuales_taller/` dynamically rather than hardcoding a single text file path.

---

## 6. Verification Evidence

- `view_file` on `data/dataset_sintomas.csv` (63 rows)
- `view_file` on `data/tracker_diagnosticos.csv` (60 rows)
- `view_file` on `manuales_taller/manual_procedimientos.txt` (3 procedures, delimited by `===`)
- `view_file` on `training/entrenar_modelo.py` (Lines 4, 6, 25, 29-37 verified)
- `view_file` on `src/infrastructure/modelo_ml.py` (Lines 7, 16, 28-29 verified)
- `view_file` on `src/infrastructure/motor_rag.py` (Lines 9, 27, 36-37, 49-53 verified)
- `view_file` on `src/core/gestor_diagnostico.py` (Lines 20-30, 67-80 verified)
