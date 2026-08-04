"""Typed workflow state for the bounded agent runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.models.schemas import ChatMessage

AgentStatus = Literal["running", "completed", "failed"]

# Hard bound on select→run iterations within one /ask (overall MAX_STEPS is separate).
DEFAULT_MAX_TOOL_ROUNDS = 5


@dataclass
class AgentState:
    """Mutable state passed through agent nodes for one /ask run."""

    question: str
    history: list[ChatMessage] = field(default_factory=list)
    role: str | None = None
    actor_employee_code: str | None = None
    client_ref: str | None = None
    intent: str | None = None
    selected_tools: list[str] = field(default_factory=list)
    rewritten_query: str | None = None
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)
    tool_round: int = 0
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS
    stop_reason: str | None = None
    round_trace: list[dict[str, Any]] = field(default_factory=list)
    answer: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    status: AgentStatus = "running"
    step: str | None = None
    transitions: list[str] = field(default_factory=list)
    error: str | None = None
