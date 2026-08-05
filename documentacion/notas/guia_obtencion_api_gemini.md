# Guía para la Obtención y Configuración de la API de Gemini
## Tesis: Chatbot de Diagnóstico Vehicular Híbrido en Carabayllo

Esta guía explica paso a paso cómo obtener la clave API (API Key) gratuita de Google AI Studio, qué modelos son compatibles y cómo configurar el entorno del proyecto.

---

## 1. ¿De dónde se obtiene la API Key?

La clave de API se obtiene de forma **100% gratuita** desde el portal oficial **Google AI Studio**:

1. **Ingresar a la plataforma**:
   Navega a [https://aistudio.google.com/](https://aistudio.google.com/)

2. **Iniciar sesión**:
   Inicia sesión con tu cuenta de Google / Gmail personal o institucional.

3. **Generar la clave de API**:
   - En la barra lateral izquierda, haz clic en el botón **"Get API key"** (Obtener clave de API).
   - Haz clic en **"Create API key"** -> *"Create API key in new project"*.
   - Copia la clave generada (comienza con el prefijo `AIzaSy...`).

4. **Configurar en el proyecto**:
   Abre el archivo `.env` en la raíz de tu proyecto ([.env](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/.env)) y pega la clave:

   ```env
   GEMINI_API_KEY="AIzaSy...tu_clave_copiada_aqui..."
   ```

---

## 2. Modelos Compatibles y Comparativa de Versiones

El proyecto utiliza por defecto el modelo **`gemini-1.5-flash`** a través de la API REST v1beta de Google.

| Modelo | Latencia (Respuesta) | Ventana de Contexto RAG | Uso Gratuito (AI Studio) | Recomendación para Tesis |
| :--- | :--- | :--- | :--- | :--- |
| **`gemini-1.5-flash`** | ⚡ Ultra Rápido (~1.0s) | 1,000,000 tokens | 15 RPM (Gratis) | **RECOMENDADO NATIVO**: Ideal para respuestas fluidas en WhatsApp. |
| **`gemini-1.5-pro`** | 🐢 Moderado (~2.5s) | 2,000,000 tokens | 2 RPM (Gratis) | Útil si se requiere razonamiento técnico de muy alta complejidad. |
| **`gemini-2.0-flash-exp`** | ⚡⚡ Rápido (~0.8s) | 1,000,000 tokens | Exp. Limitado | Excelente opción para pruebas de vanguardia. |

---

## 3. ¿Pueden usarse otros LLMs? (OpenAI / Ollama / Llama3)

**Sí, absolutamente.** Gracias a la **Arquitectura Modular por Capas** implementada en tu proyecto:

- La llamada al LLM está desacoplada dentro de la clase `GestorDiagnostico` en el archivo [gestor_diagnostico.py](file:///c:/Users/leonc/OneDrive/Desktop/CHAT_BOT_MACHINLEARNING/src/core/gestor_diagnostico.py).
- Si en el futuro deseas cambiar a **OpenAI (GPT-4o)** o a **Ollama (Llama-3 local en la computadora)**, solo debes modificar la URL y el payload HTTP en la función `generar_respuesta_conversacional`, **sin alterar la interfaz de WhatsApp ni los modelos ML ni el RAG**.
