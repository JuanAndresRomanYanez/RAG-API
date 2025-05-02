from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.lexical_filters import apply_lexical_filters
from app.services.rag import get_relevant_chunks
from app.services.summarizer import detect_topic_change, update_summary
from app.schemas import Message

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
    Eres un asistente legal especializado en leyes de tránsito qué responde 
    basandose en el conocimiento que se te proporciona.
    Basas tu respuesta únicamente en la sección "Conocimiento relevante"
    Si la pregunta no se puede responder con la información proporcionada, responde 'No sé la respuesta'.
    No inventes información ni especules sobre la respuesta.
    Si la pregunta es general y tiene respuesta para varios escenarios legales,
    proporciona una respuesta general y menciona esos escenarios legales aplicables.
    Si se sabe información cómo el Título, Capítulo, Artículo asi cómo si es de una Ley o Decreto, inclúyelo en la respuesta.
    Por ejemplo: 'Respuesta basada en el código de tránsito de la "ley o decreto N°" X, título Y, capítulo Z, artículo W. 
    pero no coloques por colocar ley X, titulo Y, capitulo Z, articulo W'.
    No menciones nada al usuario sobre que proporcionas la información del conocimiento proporcionado.
    Debes tener en cuenta la conversaciones previas para interpretar adecuadamente preguntas como: 
    "¿cuánto es la multa?" o "¿y qué pasa después? o ¿cuál sería la sanción?".
    Siempre que la conversación lo permita, infiere el contexto de los intercambios anteriores para dar una respuesta coherente.
"""

def filter_docs_by_keywords(docs, query, min_hits=1):
    """
    Filtra los documentos recuperados para mantener solo los que tengan coincidencias de palabras clave.
    Si ninguno matchea, se devuelven todos los documentos originales.
    """
    keywords = query.lower().split()
    filtered = []
    
    for doc in docs:
        hits = sum(1 for word in keywords if word in doc.page_content.lower())
        if hits >= min_hits:
            filtered.append(doc)
    
    return filtered if filtered else docs

def query_answer(question: str, history: list[Message], summary: str = "") -> dict:
    print(f"[DEBUG] Resumen actual: {summary}")
    # Detectar cambio de tema
    if detect_topic_change(summary, question):
        print("[CONTEXT CHANGE] Cambio detectado → Se limpia el resumen.")
        summary = ""
    else:
        print("[CONTEXT CHANGE] No se detectó cambio de tema → Se mantiene el resumen.")
    
    # Normalizar la pregunta
    qf = apply_lexical_filters(question)
    
    # Normalizar el summary
    filtered_summary = apply_lexical_filters(summary)

    # Tomar últimos N turnos solo USER
    N = 6
    recent_user_messages = [m.content for m in history if m.role == "user"][-N:]
    recent_history_text = "\n".join(apply_lexical_filters(m) for m in recent_user_messages)

    # Preparar contexto para la búsqueda (enriquecer context_query)
    context_for_search = f"{filtered_summary} {recent_history_text} {qf}".strip()

    # Elegir k dinámicamente
    k = 15
    # k = 15 if not detect_topic_change(summary, question) else 5

    # Recuperar chunks
    docs = get_relevant_chunks(context_for_search, k=k)

    # Mostrar cantidad de chunks recuperados
    print(f"[DEBUG] Chunks recuperados antes del filtro: {len(docs)}")

    # Filtrar chunks para priorizar los relevantes
    docs = filter_docs_by_keywords(docs, qf)
    
    # Mostrar cantidad de chunks después del filtro
    print(f"[DEBUG] Chunks después del filtro: {len(docs)}")

    # Preparar conocimiento
    know = "\n\n".join(d.page_content for d in docs)
    sources = sorted({d.metadata.get("source", "desconocido") for d in docs})

    # Preparar user prompt para el modelo
    user_prompt = (
        f"Resumen previo:\n{filtered_summary}\n\n"
        f"Interacciones recientes:\n{recent_history_text}\n\n"
        f"Pregunta actual:\n{qf}\n\n"
        f"Conocimiento relevante:\n{know}"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": user_prompt})

    # Llamada al modelo
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=600
    )
    answer = resp.choices[0].message.content.strip()

    # Actualizar resumen
    new_summary = update_summary(summary, qf, answer)

    return {
        "answer": answer,
        "sources": sources,
        "summary": new_summary
    }