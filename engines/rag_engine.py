from operator import itemgetter

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings

from core.faiss_runtime import activar_gpu_si_disponible
from interfaces import MotorInferencia

FAISS_PATH = "./faiss_db"
MODELO_EMBEDDINGS = "nomic-embed-text"
MODELO_LLM = "qwen2.5:3b"
NUM_FRAGMENTOS = 5

TEMPLATE = """
Eres un profesor socrático de chino mandarín especializado en HSK 1. Tu objetivo es enseñar TODO sobre los saludos.

REGLAS DE INTERACCIÓN:
1. INICIO SOLO PRIMER TURNO: Si el historial está vacío, da un saludo cordial de 1-2 frases y pregunta qué aspecto específico de los saludos quiere aprender (ej. básicos, formales, despedidas). NO uses opciones A/B/C en este primer mensaje.
2. CONTINUIDAD OBLIGATORIA: Si hay historial, NO repitas bienvenida ni reinicies la clase; responde según la última intervención del estudiante.
3. MÉTODO SOCRÁTICO (DESDE EL SEGUNDO TURNO): No des la teoría directamente. Plantea un escenario breve y haz una pregunta de opción múltiple (A, B, C) para que el alumno deduzca la respuesta.
4. RETROALIMENTACIÓN: Cuando el alumno responda, corrige o felicita, explica brevemente el porqué usando el contexto, y lanza la siguiente pregunta de opción múltiple.
5. RESPUESTAS CORTAS: Si el alumno responde solo "A", "B" o "C", interprétalo usando la última pregunta del historial.
6. FORMATO: Usa siempre Español para las instrucciones/explicaciones y Hanzi + Pinyin para el mandarín.
7. LÍMITES: Si la pregunta sale del tema de los saludos o no está en el contexto, redirige amablemente la clase.

HISTORIAL PREVIO:
{historial}

CONTEXTO RECUPERADO:
{contexto}

PREGUNTA DEL ESTUDIANTE:
{pregunta}

RESPUESTA:
"""


def _formatear_documentos(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


class MotorRAG(MotorInferencia):
    def __init__(self) -> None:
        self._cadena_rag = self._crear_cadena()

    def _crear_cadena(self):
        print("--- Inicializando la base de datos y la cadena RAG ---")
        embedding_function = OllamaEmbeddings(model=MODELO_EMBEDDINGS)
        db = FAISS.load_local(
            FAISS_PATH,
            embeddings=embedding_function,
            allow_dangerous_deserialization=True,
        )
        db = activar_gpu_si_disponible(db)

        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": NUM_FRAGMENTOS},
        )
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        llm = ChatOllama(model=MODELO_LLM, temperature=0.3)

        cadena = (
            {
                "contexto": itemgetter("pregunta") | retriever | _formatear_documentos,
                "historial": itemgetter("historial"),
                "pregunta": itemgetter("pregunta"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        print("-> ¡Sistema RAG inicializado y listo para responder!")
        return cadena

    def generar_respuesta(self, pregunta: str, historial: str = "") -> str:
        return self._cadena_rag.invoke({"pregunta": pregunta, "historial": historial})
