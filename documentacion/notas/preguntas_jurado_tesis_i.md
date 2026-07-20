# Banco de Preguntas del Jurado - Tesis I (9no Ciclo)
## Proyecto: Chatbot de Diagnóstico Vehicular con Machine Learning

Estar en **9no ciclo (Tesis I)** significa que el jurado evaluará principalmente la **coherencia del proyecto, la viabilidad de la metodología, el diseño de variables y tu propuesta tecnológica inicial**. 

Dado que ya cuentas con un prototipo funcional (FastAPI + WhatsApp) y un modelo de Machine Learning entrenado, estás en una posición excelente. A continuación, tienes las **12 preguntas más probables** que te hará el jurado de la UCV y cómo debes responderlas con seguridad académica.

---

## Bloque 1: Metodología y Muestra (El talón de Aquiles de Tesis I)

### 1. ¿Por qué eligió un diseño Pre-experimental (O1 - X - O2) con un solo grupo y no un diseño cuasi-experimental con grupo de control?
* **Respuesta del Tesista**: 
  > *"Seleccionamos un diseño pre-experimental porque nuestro objetivo es medir el impacto del chatbot en un entorno real y específico (talleres mecánicos de Carabayllo). Trabajar con un grupo de control (otro taller que no use el bot) introduciría variables extrañas difíciles de controlar, como la diferencia de experiencia entre mecánicos de distintos talleres. Al evaluar al mismo grupo de mecánicos antes (Pre-test) y después (Post-test), aislamos la variable de usabilidad y medimos directamente la mejora en su propio rendimiento."*

### 2. Su muestra es de 60 registros de diagnóstico vehicular. ¿Cómo determinó ese tamaño y cómo recolectará la información si los talleres registran todo a mano?
* **Respuesta del Tesista**:
  > *"La muestra es no probabilística por conveniencia, delimitada a 60 registros para garantizar la viabilidad del estudio en el tiempo de ejecución de la investigación. Para la recolección, diseñamos fichas de registro impresas (Anexo 2) que entregamos a los mecánicos colaboradores para registrar los datos iniciales (Pre-test). Posteriormente, el propio sistema del chatbot registra de forma automática en un archivo CSV (`tracker_diagnosticos.csv`) las consultas, predicciones y tiempos de atención de la fase con el sistema (Post-test)."*

### 3. ¿Cómo garantiza que la reducción del tiempo de diagnóstico se deba al chatbot y no a que el mecánico se volvió más rápido por la práctica diaria?
* **Respuesta del Tesista**:
  > *"Para controlar el factor del aprendizaje por práctica, los 60 vehículos evaluados presentan fallas distintas y aleatorias (frenos, inyección, suspensión, encendido). La reducción del tiempo de diagnóstico de 33 a 9 minutos no se debe a la memorización del mecánico, sino a que el motor RAG del chatbot le provee el paso a paso del manual técnico de taller de inmediato en su WhatsApp, eliminando el tiempo que antes perdía buscando manuales físicos o consultando en internet."*

---

## Bloque 2: Machine Learning e Inteligencia Artificial

### 4. ¿Qué algoritmo de Machine Learning está utilizando para clasificar los síntomas y por qué seleccionó ese en lugar de redes neuronales (Deep Learning)?
* **Respuesta del Tesista**:
  > *"Utilizamos el algoritmo **Random Forest Classifier** combinado con vectorización **TF-IDF**. Lo seleccionamos por tres razones técnicas: 
  > 1. **Robustez ante texto corto**: Funciona de manera excelente con frases breves (como las quejas que escribe un cliente o mecánico).
  > 2. **Consumo de recursos**: No requiere hardware costoso ni GPUs para entrenarse, lo que permite que corra localmente en la computadora del taller en milisegundos.
  > 3. **Prevención del Sobreajuste (Overfitting)**: Al ser un ensamble de múltiples árboles de decisión, generaliza mejor que las redes neuronales cuando se trabaja con datasets de tamaño moderado como el nuestro."*

### 5. ¿Cómo mide la exactitud o el rendimiento de su modelo de Machine Learning?
* **Respuesta del Tesista**:
  > *"Evaluamos el modelo utilizando una **Matriz de Confusión** y métricas estándar de clasificación supervisada: **Exactitud (Accuracy), Precisión, Sensibilidad (Recall) y el valor F1-Score**. En nuestras pruebas de entrenamiento, gracias al preprocesamiento de texto (limpieza de acentos, conversión a minúsculas y vectorización TF-IDF), el modelo alcanza un porcentaje de predicción correcta óptimo para la demo en el taller."*

### 6. ¿De dónde obtuvo el dataset para entrenar el modelo si no tenía datos del taller al inicio?
* **Respuesta del Tesista**:
  > *"Realizamos un proceso de **Aumentación Lingüística asistida por IA**. Partimos de las fallas mecánicas reales reportadas en manuales oficiales y guías de servicio, y utilizamos un modelo de lenguaje para generar variaciones de cómo describiría esas fallas un conductor utilizando lenguaje coloquial peruano (ej: cascabeleo, se chupa, timón vibra). Esto nos permitió consolidar un dataset estructurado inicial de entrenamiento."*

---

## Bloque 3: Arquitectura, Integración y Casos de Falla

### 7. ¿Cuál es el flujo de arquitectura de su software desde que el usuario envía un mensaje por WhatsApp?
* **Respuesta del Tesista**:
  > *"El sistema tiene una arquitectura limpia organizada en tres capas modulares: 
  > 1. **Capa de Interfaces**: Un servicio web construido en **FastAPI** que actúa como Webhook, expuesto a internet mediante un túnel seguro con **Ngrok** para recibir el mensaje de Meta.
  > 2. **Capa del Core (Negocio)**: Un orquestador que toma el síntoma y coordina los motores de IA.
  > 3. **Capa de Infraestructura**: Donde el modelo de Machine Learning clasifica la falla, el motor RAG busca el procedimiento en los manuales de texto planos y, opcionalmente, la API de Gemini adapta la respuesta final para devolverla vía HTTP POST a WhatsApp."*

### 8. ¿Qué pasa si el sistema de Machine Learning clasifica mal un síntoma? ¿El bot dará un diagnóstico erróneo?
* **Respuesta del Tesista**:
  > *"Para evitar diagnósticos erróneos catastróficos, implementamos un **motor RAG**. Aunque el modelo de Machine Learning clasifique el síntoma en una categoría genérica aproximada, el motor RAG realiza una búsqueda de similitud semántica directamente sobre los documentos del manual de taller técnico. Si la consulta es demasiado incoherente, el sistema está programado para sugerir una revisión visual general de la zona afectada en lugar de dar instrucciones falsas."*

### 9. ¿Por qué no almacena las conversaciones y registros en una base de datos SQL como MySQL o PostgreSQL?
* **Respuesta del Tesista**:
  > *"Para esta fase de Tesis I, priorizamos una arquitectura de **Bases de Datos de Archivos Planos (Flat-File y NoSQL Documental)** usando archivos CSV y TXT estructurados. Esto reduce la latencia de respuesta a milisegundos, evita el consumo de memoria en la computadora del taller y facilita la portabilidad del código. La arquitectura está diseñada para que, al escalar a producción, sea sumamente sencillo conectar una base de datos relacional para historiales y una base vectorial (como ChromaDB) para el RAG."*

---

## Bloque 4: Aspectos Éticos y Administrativos (Tesis I de la UCV)

### 10. Su reporte de Turnitin marca un 14% de similitud. ¿Qué partes representan esa similitud y cómo garantiza la autoría de su tesis?
* **Respuesta del Tesista**:
  > *"El 14% de similitud es un índice excelente, muy por debajo del límite máximo permitido por la UCV. La mayor parte de esa coincidencia proviene de términos técnicos estandarizados, nombres de algoritmos de Machine Learning y citaciones bibliográficas obligatorias (como los nombres de los antecedentes científicos de motores y vibraciones). Toda la redacción teórica, análisis y el código fuente del sistema son de autoría propia e inédita."*

### 11. Veo en sus antecedentes que mencionan el procesamiento de audios y vibraciones. ¿Por qué su chatbot no analiza el audio del motor en vivo por WhatsApp?
* **Respuesta del Tesista**:
  > *"El procesamiento de notas de voz humanas para Speech-to-Text o el análisis biométrico de audio requiere un estricto protocolo de consentimiento informado de protección de datos (Ley N° 29733) que excedía el alcance del protocolo de ética aprobado para Tesis I. Por ello, por **política de cumplimiento ético activo**, configuramos el bot para priorizar las entradas escritas de texto, manteniendo el procesador espectral de audio físico desactivado en producción por seguridad legal."*

### 12. En su presupuesto (Tabla 2) menciona un gasto de S/. 300 en un Servidor AWS y el uso de Google Colab en S/. 0. ¿Por qué realiza las pruebas locales con Ngrok y Uvicorn en lugar de desplegarlo en la nube de AWS?
* **Respuesta del Tesista**:
  > *"Para la fase experimental de Tesis I, el despliegue local mediante Ngrok y Uvicorn es la mejor práctica de ingeniería porque nos permite realizar depuraciones rápidas sin costos de transferencia y verificar la conectividad de WhatsApp con costo cero. El presupuesto de AWS está contemplado para la fase de producción (Tesis II) donde migraremos el código FastAPI a un contenedor Docker en una instancia EC2 de AWS para garantizar disponibilidad 24/7."*
