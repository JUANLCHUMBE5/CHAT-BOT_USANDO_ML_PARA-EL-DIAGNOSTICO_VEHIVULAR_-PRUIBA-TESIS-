import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Cargar el manual de procedimientos (Base de Conocimiento)
file_path = "manuales_taller/manual_procedimientos.txt"
if not os.path.exists(file_path):
    print("Error: No se encontró el manual de procedimientos.")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    contenido = f.read()

# Dividir el manual por secciones/procedimientos
secciones = [sec.strip() for sec in contenido.split("===") if sec.strip()]

# Limpiar las secciones y quedarnos con el texto completo
documentos = []
titulos = []
for sec in secciones:
    lineas = sec.split("\n")
    titulo = lineas[0] if lineas else "Procedimiento"
    cuerpo = "\n".join(lineas[1:])
    titulos.append(titulo)
    documentos.append(cuerpo)

# 2. Vectorizar los documentos para búsqueda semántica (Búsqueda Vectorial)
vectorizador = TfidfVectorizer(lowercase=True, strip_accents='unicode')
documentos_vectorizados = vectorizador.fit_transform(documentos)

print("=" * 70)
print("DEMOSTRACIÓN DE RAG (RETRIEVAL-AUGMENTED GENERATION) PARA MECÁNICA")
print(f"Base de conocimientos indexada: {len(documentos)} procedimientos técnicos.")
print("=" * 70)

while True:
    pregunta_usuario = input("\nPregúntale al chatbot (ej: '¿cómo purgo los frenos?' o 'bujias'): ")
    if pregunta_usuario.lower() == 'salir':
        break

    # --- PASO 1: RETRIEVAL (Recuperación) ---
    # Convertimos la pregunta del usuario al mismo espacio vectorial
    pregunta_vec = vectorizador.transform([pregunta_usuario])
    
    # Calculamos la similitud de coseno entre la pregunta y cada sección del manual
    similitudes = cosine_similarity(pregunta_vec, documentos_vectorizados)[0]
    
    # Obtener el índice del documento más similar
    indice_mejor_coincidencia = similitudes.argsort()[-1]
    mejor_similitud = similitudes[indice_mejor_coincidencia]

    print(f"\n[1. RETRIEVAL] Buscando en los manuales de taller...")
    print(f"-> Procedimiento más relevante encontrado: {titulos[indice_mejor_coincidencia]}")
    print(f"-> Nivel de coincidencia semántica: {mejor_similitud * 100:.2f}%")

    texto_recuperado = documentos[indice_mejor_coincidencia]

    # --- PASO 2: AUGMENTATION (Aumentar el Prompt para la IA) ---
    # Así se construye el prompt final que se le enviaría al LLM (GPT o Gemini)
    prompt_completo = f"""
    [INSTRUCCIONES PARA LA IA]
    Eres 'CarBot', un asistente mecánico del taller en Carabayllo.
    Responde la duda del cliente de forma amigable y concisa basándote ÚNICAMENTE en la siguiente información técnica del manual:
    
    === INFORMACIÓN DEL MANUAL ===
    {texto_recuperado}
    ==============================
    
    Pregunta del cliente: "{pregunta_usuario}"
    Respuesta del mecánico:
    """

    print("\n[2. AUGMENTATION] Prompt construido para enviar al LLM (GPT / Gemini):")
    print("-" * 75)
    print(prompt_completo.strip())
    print("-" * 75)

    # --- PASO 3: GENERATION (Generación simulada / llamada a la API) ---
    # En el chatbot real de WhatsApp, aquí harías la llamada a la API de OpenAI o Gemini pasándole el 'prompt_completo'
    print("\n[3. GENERATION] Respuesta final que se enviaría a WhatsApp:")
    print("*" * 75)
    print(f"Hola, de acuerdo con el manual técnico de nuestro taller para {titulos[indice_mejor_coincidencia].lower()}:")
    # Para la demo, mostramos los pasos directamente ya que provienen del manual oficial
    print(texto_recuperado)
    print("*" * 75)
    print("\n(Nota: Si conectamos tu clave de API de OpenAI o Gemini, el paso 3 se redactará automáticamente de forma conversacional según el prompt generado en el paso 2).")

print("\n¡Demo RAG finalizada!")
