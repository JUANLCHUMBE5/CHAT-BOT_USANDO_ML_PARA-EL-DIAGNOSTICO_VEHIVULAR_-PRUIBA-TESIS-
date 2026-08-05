import os
import sys
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix

# Add project root to sys.path
PROJECT_ROOT = r"c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.infrastructure.motor_rag import MotorRAG

def run_empirical_stress_tests():
    print("=" * 80)
    print("EMPIRICAL STRESS TEST SUITE - CHALLENGER R1_1")
    print("=" * 80)

    # ---------------------------------------------------------
    # TEST 1: DATASET VALIDATION
    # ---------------------------------------------------------
    print("\n--- TEST 1: DATASET VALIDATION (data/dataset_sintomas.csv) ---")
    dataset_path = os.path.join(PROJECT_ROOT, "data", "dataset_sintomas.csv")
    assert os.path.exists(dataset_path), f"Dataset file missing at {dataset_path}"

    df = pd.read_csv(dataset_path, encoding="utf-8")
    row_count = len(df)
    unique_faults = df["falla"].nunique()

    print(f"Dataset Row Count: {row_count}")
    print(f"Unique Fault Classes: {unique_faults}")
    
    test1_pass = (row_count == 15449) and (unique_faults == 48)
    print(f"TEST 1 RESULT: {'PASS' if test1_pass else 'FAIL'}")
    print(f"  - Row Count Expected: 15449 | Actual: {row_count}")
    print(f"  - Fault Classes Expected: 48 | Actual: {unique_faults}")

    # ---------------------------------------------------------
    # TEST 2: MODEL TRAINING & STRATIFIED EVALUATION (25% TEST SET)
    # ---------------------------------------------------------
    print("\n--- TEST 2: STRATIFIED 25% EVALUATION ON RANDOM FOREST ---")
    X = df["sintoma"]
    y = df["falla"]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents='unicode',
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    X_vec = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.25, random_state=42, stratify=y
    )

    test_samples_count = X_test.shape[0]
    print(f"Train samples: {X_train.shape[0]}, Test samples: {test_samples_count}")

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        class_weight='balanced'
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    macro_precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
    macro_recall = recall_score(y_test, y_pred, average='macro', zero_division=0)

    print(f"Accuracy:            {accuracy * 100:.4f}% (Threshold > 98.7%)")
    print(f"Macro F1-Score:      {macro_f1 * 100:.4f}% (Threshold > 98.0%)")
    print(f"Weighted F1-Score:   {weighted_f1 * 100:.4f}%")
    print(f"Macro Precision:     {macro_precision * 100:.4f}%")
    print(f"Macro Recall:        {macro_recall * 100:.4f}%")

    # Generate confusion matrix artifact
    labels = sorted(list(y.unique()))
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    artifacts_dir = os.path.join(PROJECT_ROOT, ".agents", "challenger_r1_1", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Save CSV and TXT matrix artifacts
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_csv_path = os.path.join(artifacts_dir, "confusion_matrix_empirical.csv")
    cm_df.to_csv(cm_csv_path)

    cm_txt_path = os.path.join(artifacts_dir, "confusion_matrix_empirical.txt")
    with open(cm_txt_path, "w", encoding="utf-8") as f:
        f.write(f"Empirical Confusion Matrix (N={test_samples_count}, Acc={accuracy*100:.4f}%, MacroF1={macro_f1*100:.4f}%)\n\n")
        f.write(cm_df.to_string())

    cm_path = cm_csv_path
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        plt.figure(figsize=(14, 12))
        sns.heatmap(cm, annot=False, cmap='Blues')
        plt.title(f'Empirical Confusion Matrix (N={test_samples_count}, Acc={accuracy*100:.2f}%, F1={macro_f1*100:.2f}%)')
        plt.xlabel('Predicted Class')
        plt.ylabel('True Class')
        plt.tight_layout()
        img_path = os.path.join(artifacts_dir, "confusion_matrix_empirical.png")
        plt.savefig(img_path, dpi=200)
        plt.close()
        cm_path = img_path
    except Exception as e:
        print(f"Matplotlib image generation skipped due to environment restriction: {e}")
        print(f"Exported confusion matrix in CSV format to: {cm_csv_path}")

    test2_pass = (test_samples_count == 3863) and (accuracy > 0.987) and (macro_f1 > 0.980) and os.path.exists(cm_path)
    print(f"Confusion Matrix artifact saved to: {cm_path}")
    print(f"TEST 2 RESULT: {'PASS' if test2_pass else 'FAIL'}")
    print(f"  - Test Samples Expected: 3863 | Actual: {test_samples_count}")
    print(f"  - Accuracy > 98.7%: {'PASS' if accuracy > 0.987 else 'FAIL'} ({accuracy*100:.2f}%)")
    print(f"  - Macro F1 > 98.0%: {'PASS' if macro_f1 > 0.980 else 'FAIL'} ({macro_f1*100:.2f}%)")

    # ---------------------------------------------------------
    # TEST 3: RAG QUERY EXPANSION & FAISS RETRIEVAL STRESS-TEST
    # ---------------------------------------------------------
    print("\n--- TEST 3: RAG QUERY EXPANSION & FAISS RETRIEVAL STRESS-TEST ---")
    rag = MotorRAG(manual_path=os.path.join(PROJECT_ROOT, "manuales_taller", "manual_procedimientos.txt"))
    
    test_queries = [
        # DTC codes
        ("P0300", ["misfire", "bujias", "encendido", "cascabeleo"]),
        ("C0035", ["pastillas de freno", "freno", "chillido"]),
        ("C0040", ["liquido de frenos", "purga", "esponjoso"]),
        ("P0505", ["valvula iac", "cuerpo de aceleracion", "ralenti"]),
        ("P0562", ["bateria", "alternador", "arranque"]),
        # Peruvian mechanic idioms
        ("Tengo un chillido feo al frenar en la bajada", ["pastillas de freno", "freno", "chillido"]),
        ("El motor presenta cascabeleo fuerte al acelerar", ["bujias", "encendido", "motor"]),
        ("Siento el pedal esponjoso y no frena bien", ["liquido de frenos", "purga", "freno"]),
    ]

    rag_results = []
    all_rag_pass = True

    for query, expected_keywords in test_queries:
        expanded_query = rag._expandir_consulta(query)
        contexto, titulo = rag.recuperar_contexto(query)

        # Check keyword presence in expanded query or context/title
        combined_text = f"{expanded_query} {titulo} {contexto}".lower()
        keyword_matches = [kw for kw in expected_keywords if kw in combined_text]
        match_success = len(keyword_matches) > 0 and titulo != "Coincidencia baja" and titulo != "Desconocido"

        if not match_success:
            all_rag_pass = False

        rag_results.append({
            "Query": query,
            "Expanded": expanded_query,
            "Retrieved Title": titulo,
            "Matched Keywords": keyword_matches,
            "Status": "PASS" if match_success else "FAIL"
        })

        print(f"\nQuery: '{query}'")
        print(f"  -> Expanded: '{expanded_query}'")
        print(f"  -> Retrieved Section: '{titulo}'")
        print(f"  -> Match Status: {'PASS' if match_success else 'FAIL'}")

    test3_pass = all_rag_pass
    print(f"\nTEST 3 RESULT: {'PASS' if test3_pass else 'FAIL'}")

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------
    overall_pass = test1_pass and test2_pass and test3_pass
    print("\n" + "=" * 80)
    print(f"EMPIRICAL STRESS-TEST VERDICT: {'APPROVE' if overall_pass else 'REQUEST_CHANGES'}")
    print("=" * 80)

    return {
        "overall_pass": overall_pass,
        "test1_pass": test1_pass,
        "test2_pass": test2_pass,
        "test3_pass": test3_pass,
        "row_count": row_count,
        "unique_faults": unique_faults,
        "test_samples_count": test_samples_count,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "cm_path": cm_path,
        "rag_results": rag_results
    }

if __name__ == "__main__":
    run_empirical_stress_tests()
