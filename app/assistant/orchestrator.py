from app.models.schemas import ChatMessage
from app.rag.generator import generate_answer

MAX_HISTORY_TURNS = 10

def handle_question(question: str, history: list[ChatMessage] | None = None) -> dict: 
    """
    Coordinate the assistant pipeline by passing history through generation
    """

    trimmed_history = (history or [])[-MAX_HISTORY_TURNS:]

    return generate_answer(question, history=trimmed_history)