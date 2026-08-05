# Execution Plan: Chatbot Híbrido de Diagnóstico Vehicular

## Overview
This plan implements the hybrid vehicular diagnostic chatbot for mechanical workshops in Carabayllo across 6 methodology phases, 4 architectural layers, CRISP-DM, predictive ML modeling, RAG+LLM synthesis, and statistical hypothesis testing (t-Student).

## Dual Track Strategy

### Track 1: E2E Testing Track (Requirement-Driven, Opaque-Box)
- Build E2E test suite covering Tiers 1-4 (Feature Coverage, Boundary/Corner, Cross-Feature Combinations, Real-World Application Scenarios).
- Publish `TEST_READY.md` upon completion.
- Include automated execution harness for thesis indicator calculations (% accuracy, % completeness, response times, t-Student statistical test).

### Track 2: Implementation Track (Milestone-Based Development)
- **M1: System Requirements & Conversational Interaction (R1)**
  - Implement symptom extraction and interactive missing data prompt flow.
  - Implement standardized diagnostic output (posible falla, recomendación técnica, tiempo estimado).
- **M2: CRISP-DM Data Prep & Knowledge Base (R2)**
  - Clean and encode vehicular diagnostic dataset.
  - Build and index technical manuals into vector store for RAG.
- **M3: Predictive ML Modeling & Validation Metrics (R3)**
  - Train and validate classification model (RandomForest/XGBoost).
  - Generate full evaluation metrics: Accuracy, Precision, Recall, F1-score, Confusion Matrix.
- **M4: 4-Layer Architecture Decoupling (R4)**
  - Ensure clean decoupling across Presentation, Application, AI (ML+RAG+LLM), and Data layers.
- **M5: E2E Verification, Guardrails & Statistical Evaluation (R5 & Hypothesis Test)**
  - Implement hallucination guardrails.
  - Execute evaluation harness and export statistical report with t-Student test results.

## Quality & Integrity Assurance
- Every milestone requires direct verification (Explorer -> Worker -> Reviewer -> Challenger -> Forensic Auditor).
- Mandatory Forensic Auditor check (`teamwork_preview_auditor`) to ensure authentic implementation without mock hardcoding.
