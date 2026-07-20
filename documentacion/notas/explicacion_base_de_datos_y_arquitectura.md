# Explicación de Base de Datos y Arquitectura de Software
## Tesis: Chatbot de Diagnóstico Vehicular Híbrido

Para la sustentación de la tesis, es muy probable que el jurado haga preguntas específicas sobre la **Base de Datos** (dónde se guardan los datos) y la **Arquitectura** (cómo está estructurado el sistema).

---

## 1. ¿Qué Base de Datos se está utilizando?

Este sistema utiliza un enfoque de **Base de Datos Plana (Flat-File Database)** y **Base de Datos Documental Ligera**. No requiere de un motor relacional pesado (como MySQL o SQL Server) debido a la ligereza y al diseño de la Inteligencia Artificial:

1. **Base de Datos de Entrenamiento (ML)**: 
   * Archivo: [data/dataset_sintomas.csv](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/data/dataset_sintomas.csv) (Formato CSV estructurado con columnas `sintoma` y `falla`).
2. **Base de Datos de Conocimiento (RAG)**: 
   * Archivo: [manuales_taller/manual_procedimientos.txt](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/manuales_taller/manual_procedimientos.txt) (Base de datos documental plana estructurada con delimitadores `===` donde se almacenan las secciones de los manuales de taller).
3. **Base de Datos del Historial/Experimento**: 
   * Archivo: [data/tracker_diagnosticos.csv](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/data/tracker_diagnosticos.csv) (Guarda el registro de vehículos evaluados en las fases del experimento).

### Justificación de Defensa ante el Jurado (Por qué no usaste SQL):
> *"Para este prototipo, optamos por una arquitectura de **Bases de Datos de Archivos Planos (Flat-Files)** y **Documentales Planas**. Esto garantiza una lectura directa en memoria RAM con latencia cero (en milisegundos) y simplifica el despliegue del software en talleres locales sin depender de servidores de bases de datos externos. Asimismo, facilita la integración con el motor RAG para realizar búsquedas semánticas de texto en milisegundos. Para una fase posterior en producción a gran escala, la arquitectura está preparada para conectarse con una Base de Datos Vectorial (como ChromaDB o Pinecone) y una base de datos relacional para el registro de clientes."*

---

## 2. ¿Qué Arquitectura de Software se está usando?

El proyecto implementa una **Arquitectura Híbrida Inteligente** y está organizado bajo principios de **Clean Architecture (Arquitectura Limpia / Capas Modulares)**.

### A. Estructura de Capas del Software (Código Limpio)
El código está separado en tres capas físicas bien definidas para facilitar su mantenimiento y escalabilidad:
1. **Capa de Interfaces (`src/interfaces/`)**: Contiene los endpoints web (FastAPI Webhook) encargados de la entrada y salida de datos (recibir el mensaje HTTP de WhatsApp y enviar la respuesta).
2. **Capa del Core o Negocio (`src/core/`)**: El orquestador principal (`gestor_diagnostico.py`) que decide cómo se procesa la consulta (recibe el síntoma, lo envía al ML, busca en el RAG y genera la respuesta conversacional).
3. **Capa de Infraestructura (`src/infrastructure/`)**: Contiene la lógica de los motores de IA y algoritmos (`modelo_ml.py` para Random Forest y `motor_rag.py` para la búsqueda en manuales).

### B. Arquitectura Híbrida del Chatbot (Flujo de la IA)
La arquitectura del flujo de información sigue tres capas lógicas de procesamiento:

```
[Mensaje de WhatsApp del Mecánico]
                │
                ▼
  [Capa 1: Machine Learning]  ──► Clasifica el síntoma en una categoría/falla
                │
                ▼
      [Capa 2: Motor RAG]     ──► Busca y recupera los pasos exactos del manual
                │
                ▼
  [Capa 3: LLM (Gemini/Local)] ──► Redacta la respuesta técnica y amigable
                │
                ▼
     [Respuesta en WhatsApp]
```

---

## 3. Guía de Defensa ante el Jurado

Si te preguntan **"¿Qué arquitectura tiene su sistema y qué base de datos usó?"**, responde así:

> *"El sistema implementa una **Arquitectura Limpia organizada en Capas Modulares** (Interfaces, Core de Negocio e Infraestructura) que separa la lógica de comunicación de WhatsApp de los algoritmos de Inteligencia Artificial. 
> 
> Asimismo, el motor de diagnóstico cuenta con una **Arquitectura Híbrida** en tres niveles: Clasificación de intenciones por Machine Learning, Recuperación Semántica de Información técnica mediante RAG, y Generación de lenguaje natural con un LLM. 
> 
> En cuanto a la persistencia de datos, implementamos una arquitectura de **Bases de Datos de Archivos Planos y Documentales en formato CSV y TXT**. Esto optimiza el procesamiento en memoria y reduce la complejidad de infraestructura en talleres locales, manteniendo la portabilidad del sistema."*
