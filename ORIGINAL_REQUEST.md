# Original User Request

## 2026-07-26T16:56:05Z

<USER_REQUEST>
Desarrollo e implementación del Chatbot Híbrido de Diagnóstico Vehicular en talleres mecánicos de Carabayllo, estructurado bajo las 6 fases metodológicas de tesis: Scrum, CRISP-DM, Arquitectura Modular por Capas (ML + RAG + LLM) y Evaluación Experimental.

Working directory: c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING
Integrity mode: development

## Requirements

### R1. Requerimientos del Sistema e Interacción Conversacional
Definir e implementar la captura de síntomas vehiculares, el flujo de solicitud de datos faltantes cuando el usuario proporcione información incompleta, y la estructura estandarizada de respuesta (posible falla, recomendación técnica y tiempo estimado).

### R2. Preparación de Datos y Base de Conocimiento (CRISP-DM)
Aplicar la metodología CRISP-DM para la limpieza, codificación y estructuración de los registros de diagnóstico vehicular. Generar tanto el dataset de entrenamiento para el modelo predictivo como la base de conocimiento vectorial para el módulo RAG.

### R3. Modelado Predictivo con Machine Learning
Entrenar y validar el modelo predictivo de clasificación (Random Forest / XGBoost) para asociar síntomas con fallas vehiculares. Calcular métricas completas de desempeño: Exactitud, Precisión, Recall, F1-score y Matriz de Confusión.

### R4. Arquitectura Modular por Capas (Presentación, Aplicación, IA, Datos)
Implementar la arquitectura de 4 capas:
1. Capa de Presentación: Interfaz conversacional del Chatbot.
2. Capa de Aplicación: Control del flujo y lógica de negocio.
3. Capa de Inteligencia Artificial: Integración del modelo ML (predicción de falla), RAG (recuperación de manuales técnicos) y LLM (redacción clara de respuesta).
4. Capa de Datos: Base de datos para registros, diagnósticos e historial técnico.

### R5. Pruebas, Guardrails y Evaluación de Impacto (Variables de Tesis)
Validar experimentalmente que el RAG recupere información pertinente y el LLM no genere alucinaciones. Exportar el cálculo de los 3 indicadores de la variable dependiente: % de predicción correcta, % de registros completos y tiempo promedio de respuesta (con prueba t de Student).

## Acceptance Criteria

### Evaluación de ML y RAG
- [ ] El modelo ML calcula la matriz de confusión y métricas (Exactitud, Precisión, Recall, F1-score).
- [ ] El módulo RAG recupera fragmentos pertinentes de manuales técnicos sin alucinaciones del LLM.

### Integración por Capas
- [ ] Las 4 capas (Presentación, Aplicación, IA y Datos) están desacopladas y funcionando de forma modular.

### Métricas de Tesis
- [ ] Exportación automática del reporte estadístico con la prueba t de Student para la hipótesis general.
</USER_REQUEST>

## 2026-08-03T23:42:42Z

<USER_REQUEST>
Desarrollo y expansión del sistema de Diagnóstico Vehicular Híbrido (ML + RAG + LLM) para cubrir Autos Particulares, Camiones/Vehículos Pesados y Vehículos Eléctricos/Híbridos (EV/HEV).

Working directory: c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING
Integrity mode: development

## Requirements

### R1. Cobertura Multivehículo Ampliada (Autos, Camiones Pesados y Vehículos Eléctricos)
Integrar datasets públicos descargables de fallas mecánicas y electrónicas en:
1. Autos Particulares (Gasolina/GLP/GNV): Frenos, suspensión, inyección, embrague, electricidad y carrocería/chapas.
2. Camiones y Vehículos Pesados: Frenos neumáticos/aire (Scania APS Dataset), inyección diésel common-rail (3500-DEFault Diesel), transmisión pesada (SEU Gearbox), dirección hidráulica (ZeMA Hydraulic).
3. Vehículos Eléctricos e Híbridos (EV/HEV): Baterías de alto voltaje (Zenodo Li-ion Battery), inversor IGBT (PMSM Inverter Dataset), motor eléctrico, frenado regenerativo (EVIoT), gestión térmica y Toyota Prius Gen 3 eCVT.

### R2. Ingesta Automática y Procesamiento Masivo
Consolidar todas las fuentes externas en data/dataset_sintomas.csv enriqueciéndolo con modismos peruanos de talleres.

### R3. Re-entrenamiento Supervisado y Evaluación de Métricas
Entrenar el clasificador supervisado (Random Forest) evaluando métricas F1-Score y Exactitud especificadas por categoría.

## Acceptance Criteria

### Integración de Datos
- [x] Dataset consolidado data/dataset_sintomas.csv supera las 4,000 muestras combinadas (4,190 muestras actuales).
- [x] Cobertura de 42 clases distintas incluyendo Camiones Pesados y Vehículos Eléctricos (EV/HEV).

### Desempeño
- [x] El modelo ML clasifica con precisión > 99% en el set de prueba.
- [x] Servidor FastAPI main.py carga y responde en < 2 segundos.
</USER_REQUEST>

## 2026-08-04T23:57:50Z

<USER_REQUEST>
Desarrollo y expansión del sistema de Diagnóstico Vehicular Híbrido (ML + RAG + LLM) para la investigación de Tesis UCV 2026 (Carabayllo): "Chatbot utilizando machine learning para el diagnóstico vehicular en talleres mecánicos en Carabayllo 2026".

Working directory: c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING
Integrity mode: development

## Requirements

### R1. Cobertura Extensa de Diagnóstico Vehicular (ML + RAG + LLM)
Integrar datasets públicos masivos y manuales técnicos en:
1. Capa ML Supervisada (Random Forest + TF-IDF): Dataset de 15,449 muestras en 48 clases distintas de fallas (Frenos, Suspensión, Transmisión, Dirección, Inyección, Eléctrico, Carrocería/Chapas, Camiones Pesados y Vehículos Eléctricos/Híbridos).
2. Capa RAG Semántica (FAISS): 25 manuales técnicos estandarizados de procedimientos paso a paso en manuales_taller/manual_procedimientos.txt.
3. Capa LLM (Gemini 1.5): Síntesis estructurada en 3 secciones (Posible Falla, Procedimiento Técnico y Tiempo/Gravedad).

### R2. Ingesta Automática y Procesamiento de Modismos Peruanos
Consolidar todas las fuentes externas en data/dataset_sintomas.csv enriqueciéndolo con la terminología utilizada por los mecánicos y clientes en Carabayllo/Perú.

### R3. Evaluación Estadística de Tesis y Métricas
Entrenar el clasificador supervisado (Random Forest) evaluando Exactitud (> 98%), F1-Score (> 98%) y prueba t de Student (p < 0.05).

## Acceptance Criteria

### Integración de Datos
- [x] Dataset consolidado data/dataset_sintomas.csv alcanza las 15,449 muestras combinadas.
- [x] Base de conocimiento RAG cuenta con 25 manuales de servicio técnico estandarizados.
- [x] Cobertura de 48 clases distintas de fallas vehiculares.

### Desempeño y Validación
- [x] El modelo ML clasifica con precisión > 98.7% en el set de prueba (3,863 muestras evaluadas).
- [x] Servidor FastAPI main.py carga y responde en < 2 segundos.
</USER_REQUEST>
