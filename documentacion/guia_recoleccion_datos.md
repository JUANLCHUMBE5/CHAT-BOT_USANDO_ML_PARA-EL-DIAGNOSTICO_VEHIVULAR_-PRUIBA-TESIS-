# Guía de Recolección de Datos para Entrenamiento del Chatbot
## Tesis: Chatbot para Diagnóstico Vehicular Híbrido en Carabayllo

Para que el modelo de Machine Learning (`RandomForestClassifier`) y el motor de búsqueda semántica (`RAG`) funcionen con precisión profesional en la sustentación de tu tesis, necesitas un dataset estructurado. Aquí te explicamos las **4 fuentes principales** de donde puedes obtener estos datos y cómo estructurarlos.

---

## 1. Fuentes de Datos Recomendadas

### Fuente A: Órdenes de Trabajo del Taller (Datos Reales de Campo)
*Esta es la fuente con mayor peso académico para tu jurado de tesis de la UCV.*
* **Cómo obtenerlos**: Solicita al taller mecánico de Carabayllo el histórico de sus **órdenes de servicio, facturas o cuadernos de registro** de los últimos meses.
* **Qué extraer**:
  * **Síntoma (Entrada)**: Cómo describió el cliente el problema al dejar el auto (ej: *"El carro se me apaga en los rompemuelles"*).
  * **Falla Real (Etiqueta/Clasificación)**: Qué diagnóstico final determinó el mecánico en la orden de trabajo (ej: *"Válvula IAC sucia"*).

### Fuente B: Datasets Públicos de Ciencia de Datos (Kaggle y UCI Repository)
Si quieres bases de datos más grandes para entrenar modelos complejos:
* **Kaggle**: Busca términos como *"car maintenance dataset"*, *"vehicle diagnostic codes"*, o *"OBD-II sensor logs"*.
* **UCI Machine Learning Repository**: Cuenta con el *Car Evaluation Dataset* y registros de fallas de motores por vibración/temperatura.
* **Repositorios de Códigos DTC (OBD-II)**: Puedes descargar tablas de códigos estándar de fallas (OBD2 Diagnostic Trouble Codes) donde cada código (ej: `P0301`) tiene su descripción de síntomas (ej: *"Fallo de encendido en cilindro 1"*) y causa probable (ej: *"Bujía o bobina defectuosa"*).

### Fuente C: Aumentación de Datos Mediante IA (Linguística)
Dado que los clientes en Lima Norte usan jergas o modismos coloquiales para describir fallas (ej: *"mi caña cascabelea"*, *"siento que el carro se chupa"*), puedes usar un LLM (como Gemini) para multiplicar tus datos:
1. Tomas una falla real (ej: *"Amortiguadores reventados"*).
2. Le pides a la IA: *"Genera 20 formas diferentes en las que un conductor peruano de Carabayllo describiría que sus amortiguadores están fallando al pasar un bache"*.
3. Agregas esas variantes a tu archivo `dataset_sintomas.csv`.

### Fuente D: Manuales de Reparación Automotriz (Para el RAG)
* **Manuales Haynes / Chilton**: Son manuales comerciales que detallan el paso a paso de solución para cada síntoma.
* **Manuales de Taller de Marcas Comunes** (Toyota Yaris, Hyundai Accent, Kia Rio): Extrae secciones específicas de fallas de suspensión, frenos y motor y pégalas separadas por `===` en tu archivo `manuales_taller/manual_procedimientos.txt`.

---

## 2. Plantilla de Estructura del Dataset (`dataset_sintomas.csv`)

Tu modelo supervisado aprende relacionando un **Texto de Entrada** con una **Clase o Categoría de Falla**. La estructura en [data/dataset_sintomas.csv](file:///C:/Users/Juan/.gemini/antigravity-ide/scratch/chatbot-diagnostico-vehicular/data/dataset_sintomas.csv) debe seguir este formato exacto:

| sintoma (Texto de Entrada) | falla (Categoría / Target) |
| :--- | :--- |
| siento que el carro se va para la derecha cuando suelto el timon | Falta de alineación y balanceo |
| chilla feo la llanta delantera cuando piso el pedal de freno | Pastillas de freno desgastadas |
| el motor tiembla bastante cuando estoy detenido en el semáforo | Soportes de motor defectuosos |
| bota humo azul espeso por el tubo de escape cuando acelero | Desgaste de anillos de pistón (quema de aceite) |

---

## 3. Plan de Acción para tu Tesis (Paso a Paso)

1. **Recolección Inicial**: Recopila entre **50 y 100 casos reales** del taller de Carabayllo usando la plantilla de Excel (Síntoma vs Falla).
2. **Aumentación Linguística**: Expande esos casos a **300 o 500 registros** usando variaciones en lenguaje coloquial (para que el modelo sea robusto ante palabras mal escritas o sinónimos).
3. **Guardar en el Proyecto**: Guarda tu archivo final en [data/dataset_sintomas.csv](file:///C:/Users/Juan/.gemini/antigravity-ide/scratch/chatbot-diagnostico-vehicular/data/dataset_sintomas.csv).
4. **Re-entrenar**: Ejecuta desde la terminal:
   ```bash
   python training/entrenar_modelo.py
   ```
   El script leerá tus nuevos datos, entrenará el clasificador Random Forest y exportará los nuevos archivos binarios actualizados en `models/`.
