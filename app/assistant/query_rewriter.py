from llama_index.core import Settings as LlamaSettings

from app.models.schemas import ChatMessage
from app.rag.common import configure_llm
from app.rag.generator import _format_history

import logging

logger = logging.getLogger(__name__)


def _build_rewrite_prompt(question: str, history: list[ChatMessage]) -> str:
    return f"""You rewrite follow-up questions into standalone search queries.

Given conversation history and the latest user question, produce ONE retrieval-friendly
question that can be understood without the history.

Rules:
- Preserve intent and entities (bank names, topics, ...)
- Resolve pronouns and references ("it", "they", "compared to X", "that", ...)
- Do not answer the question
- Output only the rewritten question, nothing else

Conversation history:
{_format_history(history)}

Latest question: {question}

Standalone retrieval query:"""


def rewrite_query(question: str, history: list[ChatMessage] | None = None) -> str:
    history = history or []
    # No need to rewrite when it is the very first question for now 
    if not history:
        return question

    configure_llm()
    prompt = _build_rewrite_prompt(question, history)
    response = LlamaSettings.llm.complete(prompt)
    rewritten = response.text.strip()

    logger.info(
        "Query rewritten: original=%r rewritten=%r",
        question,
        rewritten,
    )
    return rewritten or question