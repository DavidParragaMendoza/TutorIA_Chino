import sys
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from faiss_runtime import activar_gpu_si_disponible

# --- CONFIGURACIÓN ---
FAISS_PATH = "./faiss_db"
MODELO_EMBEDDINGS = "nomic-embed-text"       # Mismo modelo que en construir_bd.py
MODELO_LLM = "qwen2.5:3b"                   # Modelo LLM instalado en Ollama
NUM_FRAGMENTOS = 5                           # Vecinos más cercanos a recuperar

# --- PLANTILLA DEL PROMPT AUMENTADO (Bloque C) ---
TEMPLATE = """Eres un profesor experto en chino mandarín. Tu tarea es responder 
la pregunta del estudiante usando ÚNICAMENTE la información proporcionada en el contexto.

Si la respuesta no se encuentra en el contexto, responde: 
"No tengo información suficiente en mis materiales para responder eso."

No inventes información. Sé claro, didáctico y utiliza ejemplos del contexto cuando sea posible.

CONTEXTO RECUPERADO:
{contexto}

PREGUNTA DEL ESTUDIANTE:
{pregunta}

RESPUESTA:"""


def formatear_documentos(docs):
    """Une los fragmentos recuperados en un solo bloque de texto."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def main():
    # ===========================================================
    # BLOQUE A: Vectorización de la Consulta (Query Embedding)
    # ===========================================================
    # Cargamos el mismo modelo de embeddings usado en construir_bd.py
    # para que la pregunta del usuario quede en el mismo espacio
    # matemático que los fragmentos del PDF.
    print("--- Cargando modelo de embeddings y base de datos FAISS ---")
    embedding_function = OllamaEmbeddings(model=MODELO_EMBEDDINGS)

    # Cargamos la base de datos vectorial creada en la Fase 2
    db = FAISS.load_local(
        FAISS_PATH,
        embeddings=embedding_function,
        allow_dangerous_deserialization=True
    )
    db = activar_gpu_si_disponible(db)
    print(f"-> Base de datos cargada desde '{FAISS_PATH}'")

    # ===========================================================
    # BLOQUE B: Búsqueda Semántica (Retrieval)
    # ===========================================================
    # Convertimos la BD en un "retriever" que, dado un vector de
    # pregunta, devuelve los k fragmentos más cercanos (similitud).
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": NUM_FRAGMENTOS}
    )

    # ===========================================================
    # BLOQUE C: Construcción del Prompt Aumentado (Augmentation)
    # ===========================================================
    # Se arma el prompt con el TEMPLATE, inyectando los fragmentos
    # recuperados y la pregunta del usuario, y se envía a Qwen.
    prompt = ChatPromptTemplate.from_template(TEMPLATE)

    # Inicializamos el modelo LLM (Qwen 2.5 3B corriendo en Ollama)
    llm = ChatOllama(model=MODELO_LLM, temperature=0.3)

    # Cadena RAG completa: retriever -> prompt -> LLM -> texto
    cadena_rag = (
        {
            "contexto": retriever | formatear_documentos,
            "pregunta": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # ===========================================================
    # BUCLE DE CONVERSACIÓN
    # ===========================================================
    print("\n========================================")
    print("  Tutor de Chino Mandarín (RAG)")
    print("  Modelo LLM: " + MODELO_LLM)
    print("  Escribe 'salir' para terminar.")
    print("========================================\n")

    while True:
        pregunta = input("Tu pregunta: ").strip()

        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego! 再见 (zàijiàn)")
            break

        print("\nBuscando en los materiales y generando respuesta...\n")

        # Ejecutar la cadena RAG (Bloques A + B + C en secuencia)
        respuesta = cadena_rag.invoke(pregunta)

        print(f"Respuesta:\n{respuesta}\n")
        print("-" * 50 + "\n")


if __name__ == "__main__":
    main()
