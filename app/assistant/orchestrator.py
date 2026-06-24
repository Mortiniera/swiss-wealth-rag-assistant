from app.models.schemas import ChatMessage
from app.rag.generator import generate_answer
from app.assistant.query_rewriter import rewrite_query

MAX_HISTORY_TURNS = 10

def handle_question(question: str, history: list[ChatMessage] | None = None) -> dict: 
    """
    Coordinate the assistant pipeline by passing history through generation
    """

    trimmed_history = (history or [])[-MAX_HISTORY_TURNS:]
    rewritten_query = rewrite_query(question, trimmed_history)

    return generate_answer(question, history=trimmed_history, rewritten_query=rewritten_query)