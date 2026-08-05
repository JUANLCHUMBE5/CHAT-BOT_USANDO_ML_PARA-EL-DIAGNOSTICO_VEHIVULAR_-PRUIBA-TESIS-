# Handoff Report — explorer_r1_1

**Task:** Technical Survey & Exploration of Requirement R1 & R3 (ML Predictive Model & Dataset)  
**Agent Directory:** `c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\.agents\explorer_r1_1`  
**Date:** 2026-08-04  

---

## 1. Observation

Direct observations and evidence collected:

1. **Dataset Properties (`data/dataset_sintomas.csv`)**:
   - Total row count: `15,449` rows (excluding header). Verified via Python Pandas execution:
     `Total rows: 15449`
   - Unique fault classes: `48` distinct classes. Verified via `df['falla'].nunique()`:
     `Unique fault classes count: 48`
   - Vehicle category breakdown:
     - Cars (Autos Particulares): 41 classes, 15,281 samples
     - Heavy Trucks (Camiones y Vehículos Pesados): 3 classes, 77 samples (`Fugas de aire o fallos en el sistema de frenos neumático (Camiones)`: 27, `Falla en el turbocompresor o intercooler (Camiones Diésel)`: 25, `Fuga o baja presion en sistema Common Rail Diésel (Camiones/Pickups)`: 25)
     - EV / HEV (Vehículos Eléctricos e Híbridos): 4 classes, 91 samples (`Fallo en inversor de corriente o motor electrico (EV)`: 27, `Degradacion o falla en paquete de bateria de alto voltaje (EV / Híbridos)`: 26, `Falla en sistema de frenado regenerativo (EV / Híbridos)`: 19, `Foco o falla en sistema de refrigeracion de bateria/inversor (EV)`: 19)

2. **Model Infrastructure & Binaries (`src/infrastructure/modelo_ml.py` and `models/`)**:
   - `src/infrastructure/modelo_ml.py`: `ModeloML` class wraps model execution and exposes `predecir_falla_con_confianza(texto) -> tuple[str, float]`.
   - `models/modelo_diagnostico.pkl`: Size `199,603,353` bytes (~199.6 MB), `sklearn.ensemble.RandomForestClassifier` with `n_estimators=300`, `max_depth=None`, `class_weight='balanced'`, `random_state=42`, `n_classes=48`.
   - `models/vectorizador_tfidf.pkl`: Size `542,548` bytes (~542.5 KB), `sklearn.feature_extraction.text.TfidfVectorizer` with `ngram_range=(1, 2)`, `sublinear_tf=True`, `strip_accents='unicode'`, vocabulary size `22,408` features.

3. **Empirical Model Evaluation (Test Set: 3,863 samples / 25% Stratified Split)**:
   - Command executed: Stratified `train_test_split(test_size=0.25, random_state=42, stratify=y)` on 15,449 samples using `RandomForestClassifier(n_estimators=300, class_weight='balanced')`.
   - Results:
     - `Accuracy: 98.7057%`
     - `Macro Precision: 99.4522%`
     - `Macro Recall: 99.4827%`
     - `Macro F1-Score: 99.4670%`
     - `Weighted Precision: 98.7089%`
     - `Weighted Recall: 98.7057%`
     - `Weighted F1-Score: 98.7065%`
     - `Confusion Matrix shape: (48, 48)` exported to `documentacion/graficas/matriz_confusion_ml.png` via `training/entrenar_modelo.py`.

4. **Automated Test Suite (`pruebas/`)**:
   - Command executed: `python -m unittest discover -s pruebas -p "test_*.py"`
   - Output: `Ran 5 tests in 0.992s - OK`. All tests passed including Peruvian colloquialisms, DTC code parsing, ambiguous guardrails, and anti-hallucination checks.

---

## 2. Logic Chain

1. **Step 1 (Dataset Integrity)**:
   Observation 1 confirms that `data/dataset_sintomas.csv` contains exactly 15,449 samples across 48 unique fault classes. The domain coverage spans Cars (41 classes), Heavy Trucks (3 classes), and EV/HEV (4 classes), matching the acceptance criteria in `ORIGINAL_REQUEST.md`.

2. **Step 2 (Model Architecture & Binary State)**:
   Observation 2 confirms that `src/infrastructure/modelo_ml.py` correctly interfaces with `models/modelo_diagnostico.pkl` (RandomForest 300 trees, balanced weights) and `models/vectorizador_tfidf.pkl` (TF-IDF 22,408 n-gram features).

3. **Step 3 (Quantitative Performance Verification)**:
   Observation 3 establishes that evaluating the model on 3,863 test samples (25% stratified test split) yields an empirical accuracy of 98.7057% (> 98.7%), macro F1-score of 99.4670% (> 98%), and weighted F1-score of 98.7065% (> 98%). The 48x48 confusion matrix visualization is properly generated at `documentacion/graficas/matriz_confusion_ml.png`.

4. **Step 4 (System Integration & Test Validation)**:
   Observation 4 confirms that running unit/adversarial tests against `GestorDiagnostico` and `ModeloML` achieves a 100% pass rate. Colloquial Peruvian mechanic phrasing ("cascabeleo", "chillido feo", "pedal esponjoso") and DTC codes are correctly processed.

---

## 3. Caveats

- **Imbalanced class representation**: While class counts total 48 classes and total dataset is 15,449, 98.91% of samples belong to traditional cars/DTC clusters, while Heavy Trucks (77 samples) and EV/HEV (91 samples) account for 1.09%. Model training balances class weights (`class_weight='balanced'`), but heavy truck/EV classes have lower sample counts (19-27 per class).
- **Encoding artifacts**: Specific Spanish accents in `data/dataset_sintomas.csv` contain `` replacement characters from previous text concatenations (e.g. `daadas`, `neumtico`, `Hbridos`). This does not affect classification performance due to `strip_accents='unicode'`, but clean encoding normalization is recommended if CSV readability is audited.

---

## 4. Conclusion

Requirements **R1** and **R3** are **FULLY SATISFIED** and empirically verified.
- Dataset size: **15,449 samples** (Goal: 15,449) — **MET**.
- Class diversity: **48 classes** covering Cars, Heavy Trucks, EV/HEV — **MET**.
- Accuracy on 3,863 test samples: **98.71%** (Goal: > 98.7%) — **MET**.
- F1-Score on test set: **99.47% Macro / 98.71% Weighted** (Goal: > 98.0%) — **MET**.
- Confusion Matrix & Automated Tests: **Generated and 100% Passing** — **MET**.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Dataset Count & Classes**:
   ```powershell
   python -c "import pandas as pd; df=pd.read_csv('data/dataset_sintomas.csv'); print('Rows:', len(df)); print('Classes:', df['falla'].nunique())"
   ```
   *Expected Output*: `Rows: 15449`, `Classes: 48`.

2. **Verify Model Metrics & Confusion Matrix**:
   ```powershell
   python training/entrenar_modelo.py
   ```
   *Expected Output*: Accuracy ~98.71%, Macro F1 ~99.47%, and image generated at `documentacion/graficas/matriz_confusion_ml.png`.

3. **Run Automated Test Suite**:
   ```powershell
   python -m unittest discover -s pruebas -p "test_*.py"
   ```
   *Expected Output*: `Ran 5 tests ... OK`.
