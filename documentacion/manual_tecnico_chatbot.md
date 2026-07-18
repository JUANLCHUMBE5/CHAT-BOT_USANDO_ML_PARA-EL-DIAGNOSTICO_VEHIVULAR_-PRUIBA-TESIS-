# Manual Técnico del Código y Módulos de Diagnóstico
## Proyecto: Chatbot de Diagnóstico Vehicular Híbrido

Este manual técnico describe la estructura de archivos, el funcionamiento del código y aborda la discrepancia de la funcionalidad de audio entre tu borrador de informe de tesis y los scripts reales desarrollados en el proyecto.

---

## 1. El Mapeo del Audio en tu Tesis: Análisis y Recomendación

> [!WARNING]
> **Existe una discrepancia en tu informe actual**:
> En las páginas 4, 14 y 15 de tu borrador de tesis escribiste frases como:
> * *"Aunque la presente investigación no contempló la implementación de sensores físicos..."* (Pág 4)
> * *"Aunque el presente proyecto no se centró en el análisis de sonido..."* (Pág 14 y 15)
>
> **Sin embargo, en tu código fuente tienes archivos clave de audio** como `chatbot_voz_y_ruido.py` y `analizar_tipo_audio.py` que procesan señales físicas de sonido usando la transformada de Fourier (FFT) para diagnosticar fallas de motor por ruido.

### ¿Cómo defender esto ante el jurado? Te recomendamos dos enfoques:

#### Enfoque A (Recomendado - Mayor Valor Académico):
Presenta el procesamiento de sonido como un **Módulo Multimodal Acústico de Entrada**. En tu informe, modifica las frases restrictivas para indicar que el chatbot es de entrada multimodal:
> *"El sistema permite al usuario ingresar síntomas mediante texto o mediante una grabación de audio directa del ruido de su motor en WhatsApp. El sistema procesa el audio espectralmente para determinar si contiene voz o un patrón acústico de avería."*
* **Por qué ayuda**: Aumenta notablemente el nivel técnico de tu tesis de Ingeniería de Sistemas frente al jurado. Demuestra que no es solo un formulario web de texto, sino un sistema capaz de interactuar con datos analógicos de audio.

#### Enfoque B (Conservador - Alcance Limitado):
Declara el análisis acústico de ruido de motor como una **Funcionalidad Prototipo de Trabajo Futuro (Future Work)** implementada a nivel de servidor pero fuera del alcance de la validación estadística de la muestra actual de 60 casos.

---

## 2. Inventario y Descripción de Archivos del Proyecto

El proyecto está estructurado de la siguiente forma para mantener las buenas prácticas arquitectónicas:

### A. Módulos Principales de la Aplicación (`src/`)

* **[main.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/main.py)**:
  Punto de entrada principal. Configura FastAPI, importa las rutas de los webhooks y arranca el servidor web asíncrono con Uvicorn en el puerto 8000.
  
* **[src/interfaces/webhook.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/interfaces/webhook.py)**:
  Implementa los endpoints de la API. Expone el método `GET /webhook` (verificación de token de Meta) y `POST /webhook` (recepción de payloads JSON de WhatsApp). Se encarga de responder a Meta y enviar las respuestas HTTP.
  
* **[src/core/gestor_diagnostico.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/core/gestor_diagnostico.py)**:
  El cerebro del sistema (Orquestador). Coordina la lógica de negocio: recibe el mensaje del cliente, decide si es audio o texto, consulta el clasificador de Machine Learning, extrae el manual del RAG y genera la respuesta conversacional a través del LLM.
  
* **[src/core/audio_processor.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/core/audio_processor.py)**:
  Contiene las funciones matemáticas para procesamiento de audio. Normaliza la amplitud, calcula la energía RMS para detectar silencio y realiza la Transformada Rápida de Fourier (FFT) para identificar si la señal física es de rango agudo (chillido de frenos o alternador) o de rango vocal.
  
* **[src/infrastructure/modelo_ml.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/infrastructure/modelo_ml.py)**:
  Carga los modelos entrenados en memoria de forma segura. Utiliza `joblib` para cargar el vectorizador y el clasificador de texto, aislando la lógica de inferencia del resto de la aplicación.
  
* **[src/infrastructure/motor_rag.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/infrastructure/motor_rag.py)**:
  Indexa dinámicamente el manual técnico. Lee el archivo `manual_procedimientos.txt`, separa las secciones técnicas y realiza una búsqueda de similitud de coseno vectorial (RAG) para recuperar el párrafo técnico exacto a partir del síntoma.

---

### B. Módulos de Entrenamiento y Datos (`training/` y `data/`)

* **`generar_dataset.py`**:
  Crea sintéticamente la data estructurada de entrenamiento inicial escribiendo frases y síntomas comunes de usuarios de taller asociados a categorías de fallas mecánicas.
  
* **`entrenar_modelo.py`**:
  Toma la data sintetizada, entrena el modelo clasificador multiclase (generalmente usando un enfoque TF-IDF y un algoritmo supervisado) y guarda los binarios serializados (`modelo_diagnostico.pkl` y `vectorizador_tfidf.pkl`).
  
* **`analizar_resultados_tesis.py`**:
  Contiene el código estadístico y las utilidades para medir las métricas de exactitud, precisión, F1-score y generar las fichas de pre-test y post-test del diseño experimental.

---

## 3. Cómo Ejecutar el Proyecto Localmente

Para realizar pruebas locales y simular el comportamiento de WhatsApp:

1. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Entrenar el Modelo** (Si no tienes los archivos `.pkl` creados):
   ```bash
   python training/entrenar_modelo.py
   ```
3. **Configurar Claves de Entorno (Opcional)**:
   Si tienes una API Key de Gemini para respuestas conversacionales, configúrala en tu sistema:
   * **Windows (PowerShell)**: `$env:GEMINI_API_KEY="tu-clave-api-aqui"`
   * **Windows (CMD)**: `set GEMINI_API_KEY=tu-clave-api-aqui`
4. **Iniciar el Servidor**:
   ```bash
   python main.py
   ```
5. **Iniciar Ngrok** para hacerlo público:
   ```bash
   ngrok http 8000
   ```
6. Vincula la URL generada por Ngrok (`https://xxxx.ngrok-free.app/webhook`) en el panel de configuración de Meta for Developers.
