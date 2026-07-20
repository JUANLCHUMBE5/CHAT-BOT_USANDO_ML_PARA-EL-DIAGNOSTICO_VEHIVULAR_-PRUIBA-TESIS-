# Banco de Preguntas del Jurado - Tesis I (Enfoque en Diseño y Metodología)
## Proyecto: Chatbot de Diagnóstico Vehicular con Machine Learning (9no Ciclo)

En **Tesis I (9no Ciclo)** el jurado evalúa el **perfil del proyecto, su diseño, la metodología de desarrollo y cómo planeas medir las variables**. No evalúan los resultados finales (eso corresponde a Tesis II). 

A partir de tus diapositivas y el diseño experimental planteado, he estructurado las preguntas que te hará el jurado organizadas por cada punto clave de tu exposición:

---

## 1. El Problema y Justificación (Slide 3)

### *¿Por qué delimitar la investigación a talleres mecánicos en el distrito de Carabayllo?*
* **Respuesta del Tesista**:
  > *"Según los datos del V Censo Nacional Económico del INEI, en Carabayllo existen 363 establecimientos dedicados al mantenimiento vehicular. Identificamos en nuestro diagnóstico exploratorio que la mayoría realiza el diagnóstico y registro de fallas de forma manual en hojas o cuadernos físicos. Esto genera pérdida de registros históricos, demoras y falta de claridad al informar al cliente. Por lo tanto, el distrito presenta una alta concentración de talleres con una necesidad real de digitalización y automatización de procesos."*

### *¿Por qué un Chatbot por WhatsApp y no una aplicación móvil nativa o una página web?*
* **Respuesta del Tesista**:
  > *"WhatsApp es la herramienta de comunicación que los mecánicos ya utilizan en su día a día. Desarrollar una aplicación web o móvil nativa requeriría que el mecánico aprenda a usar una nueva interfaz, consuma espacio en su celular y detenga su trabajo para iniciar sesión. Al integrar el chatbot en WhatsApp, aprovechamos una curva de aprendizaje de cero y permitimos que el mecánico consulte el manual y registre los síntomas de manera natural e inmediata."*

---

## 2. Antecedentes y Soporte Teórico (Slide 5)

### *¿De qué manera fundamenta su investigación en el antecedente de Lin y Miao (2025)?*
* **Respuesta del Tesista**:
  > *"El estudio de Lin y Miao (2025) sustenta la viabilidad de utilizar interfaces conversacionales (chatbots) para interpretar descripciones de síntomas hechas en lenguaje natural por los usuarios y generar recomendaciones precisas mediante el cruce de datos. Esto respalda directamente nuestra variable independiente de usar un chatbot basado en Machine Learning para guiar el diagnóstico de manera ordenada."*

---

## 3. Metodología Tecnológica: Integración SCRUM y CRISP-DM (Slide 10)

### *¿Cómo integra una metodología ágil como Scrum con una metodología de ciencia de datos como CRISP-DM?*
* **Respuesta del Tesista**:
  > *"Scrum gestiona el desarrollo del software mediante Sprints (ciclos de desarrollo rápidos), mientras que CRISP-DM estructura el modelado de datos de la Inteligencia Artificial. Los integramos alineando las fases:
  > * En los primeros Sprints de Scrum definimos requerimientos y realizamos la **Comprensión y Preparación de Datos** (Fases 1, 2 y 3 de CRISP-DM).
  > * En los Sprints intermedios desarrollamos el **Modelado de Machine Learning** y la API en FastAPI (Fase 4 de CRISP-DM).
  > * En los Sprints finales realizamos la **Evaluación del sistema e Integración con WhatsApp** mediante el Webhook (Fases 5 y 6 de CRISP-DM)."*

### *¿Qué algoritmo de Machine Learning planea utilizar para el modelado y por qué?*
* **Respuesta del Tesista**:
  > *"Para el clasificador predictivo diseñamos el uso del algoritmo **Random Forest Classifier** con representación de texto **TF-IDF**. Se eligió este algoritmo porque es altamente eficiente para clasificar texto corto (síntomas), tiene un tiempo de entrenamiento de pocos segundos en CPU y evita el sobreajuste (overfitting), lo cual es ideal para entornos de computación local en talleres automotrices."*

---

## 4. Diseño y Enfoque de la Investigación (Slide 6)

### *¿Por qué el diseño de su investigación es Preexperimental ($O_1 - X - O_2$) y cómo se ejecutará?*
* **Respuesta del Tesista**:
  > *"Es preexperimental porque trabajaremos con un único grupo de evaluación (los mecánicos seleccionados de los talleres asociados). La ejecución consta de tres pasos:
  > 1. **Medición Inicial ($O_1$ - Pre-test)**: Evaluamos el diagnóstico de 30 vehículos sin usar el chatbot, registrando tiempos, precisión del diagnóstico y completitud de datos de forma manual.
  > 2. **Estímulo ($X$)**: Implementamos el chatbot utilizando Machine Learning en el taller.
  > 3. **Medición Final ($O_2$ - Post-test)**: Medimos el diagnóstico de otros 30 vehículos utilizando el chatbot y comparamos los indicadores para evaluar la influencia del sistema."*

### *¿Por qué su investigación tiene un alcance explicativo?*
* **Respuesta del Tesista**:
  > *"Tiene un alcance explicativo porque no solo busca describir si el chatbot funciona, sino que busca **explicar la relación de causalidad**: cómo la introducción de un chatbot con Machine Learning (variable independiente) influye y causa la optimización de los tiempos y la precisión del diagnóstico vehicular (variable dependiente) en los talleres."*

---

## 5. Operacionalización de Variables e Indicadores (Slides 7 y 8)

### *¿Cómo medirá técnicamente el indicador "Exactitud del modelo de machine learning" en su Tesis?*
* **Respuesta del Tesista**:
  > *"La exactitud (Accuracy) se medirá a nivel de código durante la validación del modelo usando la métrica `accuracy_score` de Scikit-Learn. Compara el total de predicciones de fallas correctas del clasificador Random Forest contra el total de diagnósticos reales etiquetados en nuestro dataset de pruebas."*

### *¿Cómo medirá y registrará los indicadores "Porcentaje de registros diagnósticos completos" y "Tiempo promedio de respuesta"?*
* **Respuesta del Tesista**:
  > *"Para el **Pre-test**, registramos el tiempo de forma manual con cronómetro y revisamos las hojas físicas para ver si el mecánico llenó los 8 campos obligatorios de la ficha de diagnóstico. 
  > Para el **Post-test**, el sistema FastAPI está diseñado para registrar automáticamente en la base de datos plana (`tracker_diagnosticos.csv`): la marca, placa, síntoma detectado, diagnóstico y la estampa de tiempo exacta (timestamp) de inicio y fin de la consulta, permitiendo calcular el tiempo y la completitud del registro sin errores humanos."*

### *En su metodología (Pág. 27 del PDF) menciona el uso de la prueba t de Student para muestras relacionadas. ¿Por qué es adecuada para su diseño?*
* **Respuesta del Tesista**:
  > *"Es la prueba estadística paramétrica adecuada porque comparamos dos medias del mismo grupo de estudio en condiciones diferentes (el tiempo promedio de diagnóstico antes y después de aplicar el estímulo del chatbot). Al procesar los datos correlacionados del Pre-test y Post-test, la prueba T-Student confirmará si la reducción de los tiempos es estadísticamente significativa con un nivel de confianza del 95% ($p < 0.05$)."*

---

## 6. Aspectos Éticos (Turnitin y Datos)

### *Su reporte de Turnitin marca 14%. ¿Cómo garantiza la originalidad de su trabajo?*
* **Respuesta del Tesista**:
  > *"El 14% de similitud demuestra un alto nivel de originalidad. Los porcentajes de coincidencia corresponden únicamente a términos técnicos invariables (como nombres de librerías, algoritmos, y nombres de los antecedentes de Scopus). El marco metodológico, el diseño del software y el código fuente han sido desarrollados íntegramente por los autores."*
