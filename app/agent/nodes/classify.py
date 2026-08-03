"""Classify intent node."""

from __future__ import annotations

from app.agent.intent import classify_intent
from app.agent.state import AgentState


def run(state: AgentState) -> None:
    """Classify the latest user message into an intent label."""
    state.intent = classify_intent(state.question, state.history)
