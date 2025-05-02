from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import OPENAI_API_KEY
from app.lexical_filters import apply_lexical_filters
from app.schemas import Message

# Configuración
CHROMA_PATH = r"data/chroma_db"

client = OpenAI(api_key=OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

vectorstore = Chroma(
    collection_name="CodigoTransito",
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings_model
)

SYSTEM_PROMPT = """
    Eres un asistente legal especializado en leyes de tránsito qué responde 
    basandose en el conocimiento que se te proporciona.
    Basas tu respuesta únicamente en la sección "Conocimiento"
    Si la pregunta no se puede responder con la información proporcionada, responde 'No sé la respuesta'.
    No inventes información ni especules sobre la respuesta.
    Si la pregunta es general y tiene respuesta para varios escenarios legales,
    proporciona una respuesta general y menciona esos escenarios legales aplicables.
    Si se sabe información cómo el Título, Capítulo, Artículo asi cómo si es de una Ley o Decreto, inclúyelo en la respuesta.
    Por ejemplo: 'Respuesta basada en el código de tránsito de la "ley o decreto N°" X, título Y, capítulo Z, artículo W. 
    pero no coloques por colocar ley X, titulo Y, capitulo Z, articulo W'.
    No menciones nada al usuario sobre que proporcionas la información del conocimiento proporcionado.
    Debes tener en cuenta la conversaciones previas para interpretar adecuadamente preguntas como "¿cuánto es la multa?" o "¿y qué pasa después? o ¿cuál sería la sanción?".
    Siempre que la conversación lo permita, infiere el contexto de los intercambios anteriores para dar una respuesta coherente.
"""

def query_answer(question: str, history: list[Message]) -> dict:
    
    # 0) Aplicar filtros léxicos 
    question_filtered = apply_lexical_filters(question)

     # 1) Construir contexto para búsqueda (historial de preguntas + la nueva)
    history_questions = " ".join([
        msg.content for msg in history if msg.role == "user"
    ])

    # Mezclar conversación previa + pregunta actual
    context_query = f"{history_questions} {question_filtered}".strip()

    # 2) Búsqueda por similitud de los k chunks más relevantes estaba en 20
    docs = vectorstore.similarity_search(context_query, k=15)
    contextos = [doc.page_content for doc in docs]
    fuentes = [doc.metadata.get("source", "desconocido") for doc in docs]
    conocimiento = "\n\n".join(contextos)

    # 3) Preparar el prompt para el modelo (incluir conversación previa)
    history_text = "\n".join([
        f"{msg.role.capitalize()}: {msg.content}" for msg in history
    ])

    user_prompt = f"Conversación previa:\n{history_text}\n\nPregunta actual: {question_filtered}\n\nConocimiento:\n{conocimiento}"

    # 3) componer mensajes: system + history + nuevo user,
    # convirtiendo cada Message en dict   
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        # msg es una instancia de Message(BaseModel) —> la pasamos como dict
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role":"user", "content": user_prompt})

    # 4) Llamada a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    answer = response.choices[0].message.content

    return {
        "answer": answer.strip(),
        "sources": sorted(set(fuentes))
    }
