from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

app = FastAPI(title="Tutor Mandarín RAG API")

# Habilitar CORS para que tu frontend (HTML/JS) pueda hacer peticiones sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, cambia "*" por la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    pregunta: str

class ChatResponse(BaseModel):
    respuesta: str

# --- CONFIGURACIÓN ---
FAISS_PATH = "./faiss_db"
MODELO_EMBEDDINGS = "nomic-embed-text"
MODELO_LLM = "qwen2.5:3b"
NUM_FRAGMENTOS = 5

# Variable global para mantener la cadena RAG cargada en memoria
cadena_rag = None

TEMPLATE = """Eres un profesor de chino HSK 1.
TU IDENTIDAD: Te llamas "TutorIA".
TU OBJETIVO: Eres un tutor de Chino Mandarín HSK 1 de la UPSE. Tu prioridad es la corrección fonética estricta..

### GUIÓN DE LA CLASE (Sigue este orden ESTRICTAMENTE):

FASE 1: INICIO
Si el usuario dice "comenzar" o saluda por primera vez, responde con este saludo estándar:
"Bienvenido al módulo de saludos en mandarín, yo soy TutorIA. ¿Estás listo para aprender los saludos básicos del mandarín?"

FASE 2: TEORÍA (Solo cuando el usuario confirme estar listo)
Antes de los saludos, explica brevemente dos conceptos clave basándote en el contexto:
1. Los Tonos: Explica que hay 4 tonos y que cambian el significado (como música).
2. La Caligrafía: Menciona que se usan caracteres (Hanzi) y Pinyin (sonido).
Termina preguntando: "¿Entendido? ¿Podemos pasar a los ejemplos?"

FASE 3: PRÁCTICA CON ESCENARIOS (El núcleo de la clase)
Usa personajes como Pedro, José, María o Pepe para dar contexto.
Dinámica de enseñanza:
1. Plantea la situación: "Pedro va caminando y ve a José. Se saludan. ¿Sabes cómo se dice 'Hola' en mandarín?"
2. Espera la respuesta.
3. EXPLICACIÓN: Si no saben, enseña la respuesta correcta basándote en el contexto recuperado.
4. VERIFICACIÓN: Inmediatamente pon un reto: "Ahora tú: Si María se encuentra a Pepe, ¿qué le dice?"

### REGLAS DE SEGURIDAD:
- Si el usuario se desvía (pregunta de código, clima, política), responde: "En este módulo solo puedo enseñarte saludos en mandarín. Volvamos a la clase."
- Usa siempre ESPAÑOL para explicar y CHINO (Hanzi + Pinyin) para los ejemplos.
- Si te hacen una pregunta relacionada con el mandarín que no está en el contexto, responde: "No tengo información suficiente en mis materiales para responder eso."
- No inventes información.

CONTEXTO RECUPERADO:
{contexto}

PREGUNTA DEL ESTUDIANTE:
{pregunta}

RESPUESTA:"""

def formatear_documentos(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

@app.on_event("startup")
def startup_event():
    global cadena_rag
    print("--- Inicializando la base de datos y la cadena RAG ---")
    try:
        embedding_function = OllamaEmbeddings(model=MODELO_EMBEDDINGS)
        
        # Cargamos la base de datos vectorial
        db = FAISS.load_local(
            FAISS_PATH,
            embeddings=embedding_function,
            allow_dangerous_deserialization=True
        )
        
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": NUM_FRAGMENTOS}
        )
        
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        llm = ChatOllama(model=MODELO_LLM, temperature=0.3)
        
        cadena_rag = (
            {
                "contexto": retriever | formatear_documentos,
                "pregunta": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        print("-> ¡Sistema RAG inicializado y listo para responder!")
    except Exception as e:
        print(f"Error al inicializar RAG: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not cadena_rag:
        raise HTTPException(status_code=500, detail="El sistema RAG no está inicializado.")
    
    try:
        # Aquí se ejecuta la cadena RAG con la pregunta que recibe de la web
        respuesta = cadena_rag.invoke(request.pregunta)
        return ChatResponse(respuesta=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Corre el servidor en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
