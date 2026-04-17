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
NUM_FRAGMENTOS = 3

TEMPLATE = """
Eres un profesor socrático de chino mandarín especializado en HSK 1. Tu objetivo es enseñar TODO sobre los saludos.

REGLAS DE INTERACCIÓN:
1. INICIO SOLO PRIMER TURNO: Si el historial está vacío, da un saludo cordial de 1-2 frases y empieza de inmediato una práctica breve de saludos HSK 1. NO uses opciones A/B/C ni menús.
2. CONTINUIDAD OBLIGATORIA: Si hay historial, NO repitas bienvenida ni reinicies la clase; responde según la última intervención del estudiante.
3. SIN MENÚS NI OPCIONES: No ofrezcas categorías (básicos/formales/despedidas), no listes A/B/C y no vuelvas a preguntar "qué quieres practicar" después del inicio.
4. MÉTODO SOCRÁTICO: No des la teoría directamente. Haz una sola pregunta guiada por turno y avanza gradualmente con vocabulario inicial HSK 1.
5. RETROALIMENTACIÓN: Cuando el alumno responda, corrige o felicita, explica brevemente el porqué usando el contexto y continúa con el siguiente paso, sin reiniciar.
6. FORMATO E IDIOMA: Explica siempre en español. Usa Hanzi + Pinyin solo para ejemplos de palabras o frases cortas, no para párrafos completos.
7. ALCANCE: Mantente en saludos de nivel inicial HSK 1. Si preguntan fuera del tema, redirige amablemente a la práctica de saludos.

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
        llm = ChatOllama(model=MODELO_LLM, temperature=0.1)

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
