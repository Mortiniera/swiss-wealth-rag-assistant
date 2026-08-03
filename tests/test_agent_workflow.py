"""Unit tests for bounded agent routing and runner limits."""

from unittest.mock import patch

from app.agent.intent import OUT_OF_SCOPE_MESSAGE
from app.agent.orchestrator import CONTROLLED_FAILURE, MAX_STEPS, handle_question
from app.agent.routing import (
    END,
    STEP_CLASSIFY,
    STEP_GENERATE,
    STEP_RESPOND_META,
    STEP_RESPOND_OOS,
    STEP_REWRITE,
    next_step,
)
from app.agent.state import AgentState


def test_routing_starts_at_classify():
    state = AgentState(question="KYC refresh cadence?")
    assert next_step(state) == STEP_CLASSIFY


def test_routing_rag_path():
    state = AgentState(question="KYC?", intent="RAG_QUERY", step=STEP_CLASSIFY)
    assert next_step(state) == STEP_REWRITE
    state.step = STEP_REWRITE
    assert next_step(state) == STEP_GENERATE
    state.step = STEP_GENERATE
    state.status = "completed"
    assert next_step(state) == END


def test_routing_out_of_scope_path():
    state = AgentState(question="protein?", intent="OUT_OF_SCOPE", step=STEP_CLASSIFY)
    assert next_step(state) == STEP_RESPOND_OOS
    state.step = STEP_RESPOND_OOS
    state.status = "completed"
    assert next_step(state) == END


def test_routing_meta_path():
    state = AgentState(
        question="what can you do?",
        intent="ASSISTANT_META",
        step=STEP_CLASSIFY,
    )
    assert next_step(state) == STEP_RESPOND_META
    state.step = STEP_RESPOND_META
    state.status = "completed"
    assert next_step(state) == END


def test_runner_respects_max_steps():
    """A non-terminating route must stop at MAX_STEPS with a controlled failure."""
    with patch("app.agent.orchestrator.next_step", return_value=STEP_CLASSIFY), patch(
        "app.agent.orchestrator.NODES",
        {STEP_CLASSIFY: lambda state: None},
    ):
        result = handle_question("never ends")

    assert result == CONTROLLED_FAILURE
    assert MAX_STEPS == 8


def test_runner_oos_uses_classify_then_respond():
    seen: list[str] = []

    def tracking_classify(state: AgentState) -> None:
        state.intent = "OUT_OF_SCOPE"
        seen.append(state.step or "")

    def tracking_oos(state: AgentState) -> None:
        seen.append(state.step or "")
        state.answer = OUT_OF_SCOPE_MESSAGE
        state.sources = []
        state.status = "completed"

    with patch(
        "app.agent.orchestrator.NODES",
        {
            STEP_CLASSIFY: tracking_classify,
            STEP_RESPOND_OOS: tracking_oos,
        },
    ):
        result = handle_question("What is a protein?")

    assert result["answer"] == OUT_OF_SCOPE_MESSAGE
    assert result["sources"] == []
    assert seen == [STEP_CLASSIFY, STEP_RESPOND_OOS]
