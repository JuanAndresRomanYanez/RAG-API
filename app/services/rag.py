from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

vectorstore = Chroma(
    collection_name="CodigoTransito",
    persist_directory="data/chroma_db",
    embedding_function=embeddings_model
)

def get_relevant_chunks(query: str, k: int = 5):
    return vectorstore.similarity_search(query, k=k)