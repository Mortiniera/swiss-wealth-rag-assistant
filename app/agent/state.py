"""Typed workflow state for the bounded agent runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.models.schemas import ChatMessage

AgentStatus = Literal["running", "completed", "failed"]


@dataclass
class AgentState:
    """Mutable state passed through agent nodes for one /ask run."""

    question: str
    history: list[ChatMessage] = field(default_factory=list)
    role: str | None = None
    intent: str | None = None
    rewritten_query: str | None = None
    answer: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    status: AgentStatus = "running"
    step: str | None = None
    transitions: list[str] = field(default_factory=list)
    error: str | None = None
