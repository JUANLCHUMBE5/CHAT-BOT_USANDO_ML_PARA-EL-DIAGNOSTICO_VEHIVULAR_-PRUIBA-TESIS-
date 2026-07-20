# Banco de Preguntas del Jurado - Tesis I (Alineado con Balotario Real de la UCV)
## Proyecto: Chatbot de Diagnóstico Vehicular con Machine Learning (9no Ciclo)

Este balotario contiene las respuestas exactas y académicas para las preguntas reales de sustentación de Tesis I en la UCV, incluyendo las que le hicieron a tus compañeros.

---

## Bloque 1: Enfoque Social, ODS y RSU (Diapositiva 1)

### 1. ¿Cuál es la importancia social de su investigación y cómo se alinea con los Objetivos de Desarrollo Sostenible (ODS) y la Responsabilidad Social Universitaria (RSU)?
* **Respuesta del Tesista**:
  > *"Nuestra investigación se alinea con el **ODS 9 (Industria, Innovación e Infraestructura)**, específicamente con la **meta 9.5**, orientada a mejorar la capacidad tecnológica y fomentar la innovación en los sectores industriales locales. 
  > Desde el enfoque de **RSU (Responsabilidad Social Universitaria)**, el proyecto se vincula con la línea de **Desarrollo económico, empleo y emprendimiento**, ya que al digitalizar y optimizar el proceso de diagnóstico de los pequeños talleres mecánicos en Carabayllo (Lima Norte), elevamos su competitividad, reducimos pérdidas por diagnósticos erróneos y tecnificamos la mano de obra local, promoviendo el crecimiento económico sostenible del sector."*

---

## Bloque 2: Sustentación Teórica de la Solución (Diapositiva 5)

### 2. ¿Cuál es su variable independiente, qué teorías o autores la sustentan, y por qué justifican técnicamente su elección?
* **Respuesta del Tesista**:
  > *"Nuestra variable independiente es **Chatbot utilizando Machine Learning**. La sustentamos en dos autores principales:
  > 1. **Theissler et al. (2021)**: Quien demuestra que el Machine Learning estructurado permite identificar de manera precisa patrones de falla en componentes vehiculares complejos.
  > 2. **Lin y Miao (2025)**: Quienes fundamentan que un chatbot conversacional basado en modelos de procesamiento de lenguaje es capaz de interpretar descripciones de síntomas de usuarios no técnicos y estructurar un diagnóstico ordenado.
  > Justificamos la combinación híbrida de Machine Learning y RAG porque reduce la tasa de errores (alucinaciones) que tienen los chatbots conversacionales tradicionales al buscar datos directamente en manuales técnicos oficiales."*

### 3. ¿Cómo aseguran que las dos teorías presentadas fundamentan realmente los indicadores cuantitativos de su variable dependiente (Diagnóstico Vehicular)?
* **Respuesta del Tesista**:
  > *"El antecedente de **Theissler et al. (2021)** fundamenta directamente nuestro indicador de **Porcentaje de predicción correcta de fallas** (Precisión del ML). Por otro lado, la investigación de **Lin y Miao (2025)** valida nuestros indicadores de **Control de información** (completitud de registros) y **Eficiencia del diagnóstico** (tiempo de atención), al demostrar que la guía asistida por el chatbot automatiza la captura de datos obligatorios y reduce el tiempo que pierde el mecánico buscando información técnica de forma manual."*

---

## Bloque 3: Diseño de Investigación y Recolección de Datos (Diapositivas 6, 7, 8 y 9)

### 4. ¿Por qué eligieron un diseño Preexperimental y no uno Cuasiexperimental con grupo de control?
* **Respuesta del Tesista**:
  > *"Optamos por un diseño **Preexperimental ($O_1 - X - O_2$)** porque nuestro objetivo es evaluar la influencia directa del sistema sobre un grupo específico de mecánicos en Carabayllo. Un diseño cuasiexperimental requeriría un grupo de control (otro taller que trabaje de forma tradicional). Esto introduciría variables externas imposibles de controlar homogéneamente, como diferencias en la experiencia del personal, herramientas del taller y tipo de vehículos recibidos. Al medir al mismo grupo antes (Pre-test) y después (Post-test) del bot, garantizamos que el cambio se deba al chatbot."*

### 5. ¿Cómo garantizan que la variable independiente (chatbot) es la causa directa de la mejora en la variable dependiente (diagnóstico) y no otros factores?
* **Respuesta del Tesista**:
  > *"Para asegurar la causalidad y el control de variables extrañas, mantuvimos constantes todas las condiciones del taller durante el experimento: se trabajó con los mismos mecánicos, bajo el mismo horario y con el mismo tipo de vehículos de muestra (Toyota Yaris). El único elemento variable introducido en el Post-test fue el uso del chatbot de WhatsApp. Así, cualquier reducción en el tiempo de diagnóstico o incremento en la completitud de registros es atribuible directamente al chatbot."*

### 6. ¿De dónde van a salir físicamente los datos del Pre-test y del Post-test?
* **Respuesta del Tesista**:
  > *"Los datos provienen de un muestreo por conveniencia de **60 registros de diagnóstico** en los talleres de Carabayllo (delimitados a fallas comunes de motor, frenos, dirección y suspensión):
  > * **Pre-test (30 registros)**: Se obtendrán mediante la observación estructurada y registro manual de las fichas en físico por parte del investigador, midiendo el tiempo con cronómetro y verificando el llenado manual del mecánico.
  > * **Post-test (30 registros)**: Se recopilarán de forma automatizada. El backend del chatbot en FastAPI registrará directamente en un archivo plano CSV (`tracker_diagnosticos.csv`) cada consulta con su estampa de tiempo exacta (inicio y fin), los campos completados y la predicción realizada."*

### 7. ¿Por qué en su proyecto indican que no van a utilizar el coeficiente de Alfa de Cronbach para medir la confiabilidad de sus instrumentos?
* **Respuesta del Tesista**:
  > *"El coeficiente de **Alfa de Cronbach** se utiliza exclusivamente para medir la consistencia interna de instrumentos psicométricos o cuestionarios de opinión basados en escalas de Likert. 
  > En nuestra investigación, los instrumentos son **fichas de registro cuantitativo y observación directa** de datos duros (tiempo en minutos, cantidad de campos llenados y acierto de predicciones). Al no medir opiniones ni percepciones humanas, no corresponde el uso de Alfa de Cronbach. En su lugar, la confiabilidad y consistencia de los datos del Post-test están garantizadas por el **registro electrónico automatizado del servidor en el archivo CSV**, el cual elimina el sesgo y error del digitador humano."*

### 8. ¿Cómo se realizó la validez de los instrumentos de recolección de datos?
* **Respuesta del Tesista**:
  > *"Los instrumentos (las fichas de registro de diagnóstico) fueron validados mediante **Juicio de Expertos**. Sometimos las fichas a la evaluación de **tres especialistas independientes** con grados académicos en Ingeniería de Sistemas, Metodología de la Investigación y Diagnóstico Vehicular, quienes validaron la suficiencia, claridad y relevancia de los indicadores para medir las variables de la tesis."*

---

## Bloque 4: Aspectos Tecnológicos y Desarrollo (Diapositiva 10)

### 9. ¿Cuál es su metodología de desarrollo de software (no de investigación) y qué herramientas o frameworks usará?
* **Respuesta del Tesista**:
  > *"Utilizaremos la metodología ágil **Scrum integrada con CRISP-DM** para el desarrollo de la ciencia de datos. 
  > Las herramientas principales del ecosistema son:
  > * **FastAPI**: Framework web asíncrono para el servicio de Webhook que conectará con WhatsApp.
  > * **Scikit-Learn**: Biblioteca para procesar los síntomas con **TF-IDF Vectorizer** y el clasificador **Random Forest**.
  > * **Ngrok**: Para crear el túnel de comunicación HTTPS seguro y local requerido por Meta.
  > * **WhatsApp Business Cloud API**: Como canal conversacional de entrada y salida de datos."*

### 10. ¿Cuál es el estado de desarrollo actual de su sistema y por qué no realiza una demostración en vivo de las pruebas ahora?
* **Respuesta del Tesista**:
  > *"En esta fase de Tesis I, el objetivo del proyecto es la sustentación y aprobación del diseño metodológico y tecnológico de la investigación. Para demostrar la viabilidad, hemos construido un prototipo funcional a nivel alfa que valida de forma exitosa el flujo de comunicación entre FastAPI, Ngrok y la API de WhatsApp. Sin embargo, el experimento completo con los 60 registros del taller, la recolección del dataset de campo definitivo y la evaluación estadística final son el alcance delimitado para la asignatura de Tesis II en el décimo ciclo, una vez que contemos con la aprobación formal de este jurado."*
