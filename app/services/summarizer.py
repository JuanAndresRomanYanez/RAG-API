import numpy as np
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from app.config import OPENAI_API_KEY
from app.lexical_filters import apply_lexical_filters

client = OpenAI(api_key=OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

TOPIC_THRESHOLD = 0.41
SHARED_KEYWORDS_THRESHOLD = 1  # Cuántas palabras clave deben coincidir para NO resetear

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def count_shared_keywords(text1: str, text2: str) -> int:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    return len(words1 & words2)

def detect_topic_change(summary: str, question: str) -> bool:
    filtered_summary = apply_lexical_filters(summary)
    filtered_question = apply_lexical_filters(question)

    if not summary:
        return False
    
    emb_sum = np.array(embeddings_model.embed_query(filtered_summary))
    emb_q = np.array(embeddings_model.embed_query(filtered_question))
    sim = cosine_sim(emb_sum, emb_q)

    shared_keywords = count_shared_keywords(filtered_summary, filtered_question)

    print(f"[SIMILARITY] Similitud entre resumen y pregunta: {sim:.4f}")
    print(f"[SHARED KEYWORDS] Palabras clave compartidas: {shared_keywords}")

    # Cambiar si similitud baja Y pocas palabras clave compartidas
    if sim < TOPIC_THRESHOLD and shared_keywords < SHARED_KEYWORDS_THRESHOLD:
        return True
    return False

def update_summary(old_summary: str, question: str, answer: str) -> str:
    prompt = (
        f"Resumen anterior:\n{old_summary}\n\n"
        f"Nuevo intercambio:\nUsuario: {question}\nAsistente: {answer}\n\n"
        # "Proporciona un resumen CONCISO de toda la conversación."
        "Actualiza el resumen para reflejar el nuevo intercambio, en UNA SOLA ORACIÓN clara y concisa (máximo 30 palabras)."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":"Eres un asistente que resume conversaciones."},
                  {"role":"user","content":prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
