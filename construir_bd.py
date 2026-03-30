import os
import shutil
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# --- CONFIGURACIÓN ---
PDF_PATH = "Leccion1.pdf"
FAISS_PATH = "./faiss_db"  # Nombre de la carpeta donde se guardará la "memoria"
MODELO_EMBEDDINGS = "nomic-embed-text"

def main():
    # 1. LIMPIEZA DEL ENTORNO
    # Si ya existe una base de datos antigua, la borramos para empezar de cero (limpio)
    if os.path.exists(FAISS_PATH):
        print(f"--- Borrando base de datos antigua en {FAISS_PATH} ---")
        shutil.rmtree(FAISS_PATH)

    # 2. CARGA Y LIMPIEZA DE DATOS (Lógica del Bloque A)
    print(f"--- Cargando {PDF_PATH} ---")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    
    print("--- Aplicando corrección de Pinyin y limpieza ---")
    for doc in docs:
        # Aplanar texto
        clean_text = doc.page_content.replace('\n', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # CORRECCIÓN DE PINYIN (La fórmula que validamos: n ǐ -> nǐ)
        clean_text = re.sub(r'([a-zA-Z])\s+([ǎǐǒǔàáèéìíòóùúāēīōūüǖǘǚǜ])', r'\1\2', clean_text)
        
        doc.page_content = clean_text.strip()

    # 3. FRAGMENTACIÓN (Chunking - Bloque A)
    print("--- Fragmentando el texto (Chunks: 1200 / Overlap: 200) ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["SECCIÓN:", "\n\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"-> Se generaron {len(chunks)} fragmentos.")

    # 4. VECTORIZACIÓN Y GUARDADO (Bloque B y C)
    print("--- Iniciando Vectorización y Guardado en FAISS ---")
    print("(Esto puede tardar un poco dependiendo de tu procesador...)")

    # Inicializamos el modelo de embeddings
    embedding_function = OllamaEmbeddings(model=MODELO_EMBEDDINGS)

    # Creamos la base de datos vectorial con FAISS y guardamos los chunks
    db = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_function
    )

    # Guardamos la base de datos en disco para persistencia
    db.save_local(FAISS_PATH)

    # 5. VERIFICACIÓN FINAL
    count = len(db.docstore._dict)
    print(f"\n--- ¡ÉXITO! Base de datos creada en '{FAISS_PATH}' ---")
    print(f"Total de fragmentos indexados: {count}")
    print("Ahora tu IA tiene memoria persistente.")

if __name__ == "__main__":
    main()