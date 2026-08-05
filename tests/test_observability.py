"""Observability facade: opt-in Langfuse init, no-op without keys."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.observability import (
    dev_trace_url,
    extract_usage_details,
    finish_generation,
    flush_observability,
    get_client,
    init_observability,
    is_enabled,
    observe,
    observe_generation,
    reset_observability,
)
from app.observability import langfuse_client as lf_mod


@pytest.fixture(autouse=True)
def _reset_observability_state():
    reset_observability()
    yield
    reset_observability()


def test_init_noop_without_keys(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "")
    monkeypatch.setattr(settings, "langfuse_secret_key", "")
    monkeypatch.setattr(settings, "langfuse_base_url", "")

    assert init_observability() is False
    assert is_enabled() is False
    assert get_client() is None


def test_init_noop_with_placeholder_keys(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "YOUR_LANGFUSE_PUBLIC_KEY")
    monkeypatch.setattr(settings, "langfuse_secret_key", "YOUR_LANGFUSE_SECRET_KEY")

    assert init_observability() is False
    assert is_enabled() is False
    assert get_client() is None


def test_init_enabled_with_mocked_client(monkeypatch):
    mock_client = MagicMock(name="LangfuseClient")
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")
    monkeypatch.setattr(settings, "langfuse_base_url", "https://cloud.langfuse.com")

    with patch(
        "langfuse.Langfuse",
        return_value=mock_client,
    ) as mock_ctor:
        assert init_observability() is True

    mock_ctor.assert_called_once_with(
        public_key="pk-lf-test",
        secret_key="sk-lf-test",
        base_url="https://cloud.langfuse.com",
    )
    assert is_enabled() is True
    assert get_client() is mock_client


def test_init_enabled_without_base_url_omits_arg(monkeypatch):
    mock_client = MagicMock(name="LangfuseClient")
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")
    monkeypatch.setattr(settings, "langfuse_base_url", "")

    with patch("langfuse.Langfuse", return_value=mock_client) as mock_ctor:
        assert init_observability() is True

    mock_ctor.assert_called_once_with(
        public_key="pk-lf-test",
        secret_key="sk-lf-test",
    )
    assert is_enabled() is True


def test_init_failure_stays_disabled(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")

    with patch("langfuse.Langfuse", side_effect=RuntimeError("boom")):
        assert init_observability() is False

    assert is_enabled() is False
    assert get_client() is None


def test_observe_noop_when_disabled():
    with observe("ask", metadata={"role": "rm"}) as span:
        assert span is None


def test_observe_opens_span_when_enabled():
    mock_span = MagicMock(name="span")

    @contextmanager
    def _cm(**_kwargs):
        yield mock_span

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    lf_mod._client = mock_client
    lf_mod._enabled = True

    with observe("classify", metadata={"step": "classify"}) as span:
        assert span is mock_span

    mock_client.start_as_current_observation.assert_called_once_with(
        name="classify",
        as_type="span",
        metadata={"step": "classify"},
    )


def test_observe_ask_uses_chain_type():
    mock_span = MagicMock(name="span")

    @contextmanager
    def _cm(**_kwargs):
        yield mock_span

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    lf_mod._client = mock_client
    lf_mod._enabled = True

    with observe("ask") as span:
        assert span is mock_span

    assert mock_client.start_as_current_observation.call_args.kwargs["as_type"] == "chain"


def test_flush_noop_when_disabled():
    flush_observability()  # must not raise


def test_flush_calls_client_when_enabled():
    mock_client = MagicMock()
    lf_mod._client = mock_client
    lf_mod._enabled = True
    flush_observability()
    mock_client.flush.assert_called_once_with()


def test_handle_question_emits_ask_and_step_spans():
    from app.agent.orchestrator import handle_question

    spans: dict[str, MagicMock] = {}

    @contextmanager
    def _cm(**kwargs):
        name = kwargs["name"]
        span = MagicMock(name=f"span-{name}")
        spans[name] = span
        yield span

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    mock_client.get_current_trace_id.return_value = "trace-test-1"
    lf_mod._client = mock_client
    lf_mod._enabled = True

    def _fake_classify(state):
        state.intent = "ASSISTANT_META"

    def _fake_respond_meta(state):
        state.answer = "I am Helvetia ops assistant."
        state.sources = []
        state.status = "completed"

    with patch.dict(
        "app.agent.orchestrator.NODES",
        {
            "classify": _fake_classify,
            "respond_meta": _fake_respond_meta,
        },
    ):
        result = handle_question(
            "What can you do?",
            role="relationship_manager",
            actor_employee_code="EMP-RM-01",
        )

    assert result["answer"]
    names = [
        c.kwargs["name"] for c in mock_client.start_as_current_observation.call_args_list
    ]
    assert names[0] == "ask"
    assert "classify" in names
    assert "respond_meta" in names
    mock_client.flush.assert_called_once_with()
    spans["ask"].update.assert_called()
    # PII hygiene: root metadata must not include the raw question text
    ask_call = mock_client.start_as_current_observation.call_args_list[0]
    root_meta = ask_call.kwargs["metadata"]
    assert "question" not in root_meta
    assert root_meta["actor_employee_code"] == "EMP-RM-01"
    assert root_meta["role"] == "relationship_manager"


def test_dev_trace_url_none_in_prod(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "prod")
    mock_client = MagicMock()
    mock_client.get_trace_url.return_value = "https://cloud.langfuse.com/project/x/traces/y"
    lf_mod._client = mock_client
    lf_mod._enabled = True

    assert dev_trace_url("trace-123") is None
    mock_client.get_trace_url.assert_not_called()


def test_dev_trace_url_returns_url_in_dev(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "dev")
    mock_client = MagicMock()
    mock_client.get_trace_url.return_value = "https://cloud.langfuse.com/project/x/traces/y"
    lf_mod._client = mock_client
    lf_mod._enabled = True

    assert dev_trace_url("trace-123") == "https://cloud.langfuse.com/project/x/traces/y"
    mock_client.get_trace_url.assert_called_once_with(trace_id="trace-123")


def test_handle_question_includes_trace_url_in_dev(monkeypatch):
    from app.agent.orchestrator import handle_question

    monkeypatch.setattr(settings, "app_env", "dev")

    @contextmanager
    def _cm(**kwargs):
        yield MagicMock()

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    mock_client.get_current_trace_id.return_value = "trace-dev-1"
    mock_client.get_trace_url.return_value = "https://cloud.langfuse.com/project/x/traces/trace-dev-1"
    lf_mod._client = mock_client
    lf_mod._enabled = True

    def _fake_classify(state):
        state.intent = "ASSISTANT_META"

    def _fake_respond_meta(state):
        state.answer = "I am Helvetia ops assistant."
        state.sources = []
        state.status = "completed"

    with patch.dict(
        "app.agent.orchestrator.NODES",
        {"classify": _fake_classify, "respond_meta": _fake_respond_meta},
    ):
        result = handle_question("What can you do?")

    assert result.get("trace_url") == "https://cloud.langfuse.com/project/x/traces/trace-dev-1"


def test_handle_question_omits_trace_url_in_prod(monkeypatch):
    from app.agent.orchestrator import handle_question

    monkeypatch.setattr(settings, "app_env", "prod")

    @contextmanager
    def _cm(**kwargs):
        yield MagicMock()

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    mock_client.get_current_trace_id.return_value = "trace-prod-1"
    mock_client.get_trace_url.return_value = "https://cloud.langfuse.com/project/x/traces/trace-prod-1"
    lf_mod._client = mock_client
    lf_mod._enabled = True

    def _fake_classify(state):
        state.intent = "ASSISTANT_META"

    def _fake_respond_meta(state):
        state.answer = "I am Helvetia ops assistant."
        state.sources = []
        state.status = "completed"

    with patch.dict(
        "app.agent.orchestrator.NODES",
        {"classify": _fake_classify, "respond_meta": _fake_respond_meta},
    ):
        result = handle_question("What can you do?")

    assert "trace_url" not in result


def test_extract_usage_details_from_dict_raw():
    response = MagicMock()
    response.raw = {"usage": {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16}}
    assert extract_usage_details(response) == {"input": 12, "output": 4, "total": 16}


def test_extract_usage_details_missing_returns_none():
    response = MagicMock()
    response.raw = None
    response.additional_kwargs = {}
    assert extract_usage_details(response) is None


def test_observe_generation_uses_generation_type():
    mock_span = MagicMock(name="gen")

    @contextmanager
    def _cm(**_kwargs):
        yield mock_span

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    lf_mod._client = mock_client
    lf_mod._enabled = True

    with observe_generation("intent_llm", prompt_length=100) as span:
        assert span is mock_span

    assert (
        mock_client.start_as_current_observation.call_args.kwargs["as_type"]
        == "generation"
    )


def test_finish_generation_records_usage_and_output():
    mock_span = MagicMock()
    response = MagicMock()
    response.text = "RAG_QUERY"
    response.raw = {"usage": {"prompt_tokens": 50, "completion_tokens": 2}}

    finish_generation(
        mock_span,
        response,
        elapsed_s=1.234,
        prompt_length=500,
        output_max_len=32,
    )

    mock_span.update.assert_called()
    kwargs = mock_span.update.call_args.kwargs
    assert kwargs["usage_details"] == {"input": 50, "output": 2}
    assert kwargs["output"] == "RAG_QUERY"
    assert kwargs["metadata"]["prompt_length"] == 500


def test_run_tools_emits_per_tool_spans():
    from app.agent.nodes.run_tools import run as run_tools_node
    from app.agent.state import AgentState

    mock_span = MagicMock()

    @contextmanager
    def _cm(**kwargs):
        yield mock_span

    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = (
        lambda **kwargs: _cm(**kwargs)
    )
    lf_mod._client = mock_client
    lf_mod._enabled = True

    state = AgentState(
        question="Regarding CLI-SCEN-01: status?",
        client_ref="CLI-SCEN-01",
        selected_tools=["get_client_profile"],
    )

    def _fake_profile(state):
        state.tool_results.append(
            {"tool": "get_client_profile", "ok": True, "data": {"client_ref": "CLI-SCEN-01"}}
        )

    with patch.dict(
        "app.agent.nodes.run_tools._TOOL_MODULES",
        {"get_client_profile": MagicMock(run=_fake_profile)},
    ):
        run_tools_node(state)

    tool_call = mock_client.start_as_current_observation.call_args
    assert tool_call.kwargs["name"] == "get_client_profile"
    assert tool_call.kwargs["as_type"] == "tool"
    assert tool_call.kwargs["metadata"]["client_ref"] == "CLI-SCEN-01"
    mock_span.update.assert_called()
    assert mock_span.update.call_args.kwargs["metadata"]["ok"] is True
