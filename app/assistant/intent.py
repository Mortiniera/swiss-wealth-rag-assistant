from typing import Literal

from llama_index.core import Settings as LlamaSettings
from app.models.schemas import ChatMessage
from app.rag.common import configure_llm
from app.rag.generator import _format_history

import logging

logger = logging.getLogger(__name__)

Intent = Literal["RAG_QUERY", "ASSISTANT_META", "OUT_OF_SCOPE"]

VALID_INTENTS = {"RAG_QUERY", "ASSISTANT_META", "OUT_OF_SCOPE"}

OUT_OF_SCOPE_MESSAGE = (
    "I can only answer questions about Swiss private banking and wealth management "
    "based on the indexed documents. Please ask about topics such as sustainable investing, "
    "family governance or the approaches of UBS, Pictet, Lombard Odier or Julius Baer."
)

ASSISTANT_META_MESSAGE = (
    "I am a Swiss Wealth RAG Assistant. I answer questions using indexed public-style "
    "documents about Lombard Odier, UBS, Picte and Julius Baer, covering topics like "
    "sustainable investing, family governance, digital banking and private markets. "
    "I ground every answer in retrieved sources and show institution, document and relevance scores. "
    "I cannot browse the web or answer questions outside those topics."
)


def _build_intent_prompt(question: str, history: list[ChatMessage]) -> str:
    return f"""Classify the user's latest message into exactly one intent.
Intents:
- RAG_QUERY: questions about Swiss private banking, wealth management or indexed institutions (UBS, Pictet, Lombard Odier, Julius Baer), including comparisons and follow-ups.
- ASSISTANT_META: questions about the assistant itself, its capabilities, limitations or which sources/documents it uses.
- OUT_OF_SCOPE: unrelated topics (sports, weather, general questions, coding help, etc.).

Rules:
- If the user asks about a bank or wealth topic, choose RAG_QUERY even if phrased casually.
- Use conversation history to resolve ambiguous follow-ups or to have additional context.
- Output only one label: RAG_QUERY, ASSISTANT_META or OUT_OF_SCOPE.

Conversation history:
{_format_history(history)}

Latest message: {question}

Intent:"""


def classify_intent(question: str, history: list[ChatMessage] | None = None) -> Intent:
    history = history or []
    configure_llm()
    prompt = _build_intent_prompt(question, history)
    response = LlamaSettings.llm.complete(prompt)
    label = response.text.strip().upper()

    if label not in VALID_INTENTS:
        for candidate in VALID_INTENTS:
            if candidate in label:
                label = candidate
                break
        else:
            logger.warning("Unknown intent %r, defaulting to RAG_QUERY", label)
            label = "RAG_QUERY"
    
    logger.info("Intent classified: question=%r intent=%s", question, label)
    return label


def build_meta_response(question: str, history: list[ChatMessage] | None = None) -> dict:
    return {"answer": ASSISTANT_META_MESSAGE, "sources": []}


def build_out_of_scope_response() -> dict:
    return {"answer": OUT_OF_SCOPE_MESSAGE, "sources": []}