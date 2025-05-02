import uuid
import string
import openai
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import OPENAI_API_KEY

# Configuración
DATA_PATH = r"data/raw_docs"
CHROMA_PATH = r"data/chroma_db"

openai.api_key = OPENAI_API_KEY
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Inicializar (o cargar) el vectorstore
vectorstore = Chroma(
    collection_name="CodigoTransito",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH
)

def build_separators(max_letter="z", max_number=50):
    base = [
        "TÍTULO", "Título",
        "CAPÍTULO", "Capítulo",
        "ARTÍCULO", "Artículo", "Art.",
    ]
    letters = []
    for c in string.ascii_lowercase:
        if c > max_letter:
            break
        for suffix in (".", ")"):
            letters.append(f"{c}{suffix}")
            letters.append(f"{c.upper()}{suffix}")

    numbers = []
    for i in range(1, max_number + 1):
        for suffix in (".", ")"):
            numbers.append(f"{i}{suffix}")

    # Ahora prefijamos un salto de línea a cada uno de estos
    nl_seps = [f"\n{sep}" for sep in (base + letters + numbers)]
    # Fallbacks al final
    fallbacks = ["\n\n", "\n", "\n- "]
    # Ordenamos por longitud para que matchee primero los más largos
    all_seps = sorted(set(nl_seps + fallbacks), key=lambda s: len(s), reverse=True)
    return all_seps

# Configurar el splitter usando los separadores generados
separadores = build_separators(max_letter="z", max_number=50)

# Configurar el text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=200,
    length_function=len,
    separators=separadores
)

def load_initial_documents():
    # 1) Cargar y normalizar
    loader = DirectoryLoader(
        DATA_PATH,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()

    # 2) Dividir en chunks
    docs_chunks = text_splitter.split_documents(documents)

    # 3) Asignar metadatos enriquecidos (ID, origen y posición)
    for i, chunk in enumerate(docs_chunks):
        # El loader normalmente pone 'source' en metadata; si no, usamos la ruta
        source = chunk.metadata.get("source") or f"{DATA_PATH}/{chunk.metadata.get('source', 'desconocido')}"
        chunk.metadata.update({
            "chunk_id": str(uuid.uuid4()),
            "source": source,
            "chunk_index": i,
        })

    # 4) Insertar en Chroma en batches de 166
    if docs_chunks:
        batch_size = 166
        for i in range(0, len(docs_chunks), batch_size):
            batch = docs_chunks[i:i+batch_size]
            vectorstore.add_documents(batch)
        print(f"Se han cargado {len(docs_chunks)} chunks desde '{DATA_PATH}'.")
    
if __name__ == "__main__":
    load_initial_documents()