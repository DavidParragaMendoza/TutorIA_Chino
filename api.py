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
