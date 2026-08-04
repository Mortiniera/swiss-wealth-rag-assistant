"""Unit tests for bounded agent routing and runner limits."""

from unittest.mock import MagicMock, patch

from app.agent.client_ref import extract_client_ref
from app.agent.intent import OUT_OF_SCOPE_MESSAGE
from app.agent.orchestrator import CONTROLLED_FAILURE, MAX_STEPS, handle_question
from app.agent.routing import (
    END,
    STEP_CLASSIFY,
    STEP_GENERATE,
    STEP_RESPOND_META,
    STEP_RESPOND_OOS,
    STEP_REWRITE,
    STEP_RUN_TOOLS,
    STEP_SELECT_TOOLS,
    next_step,
)
from app.agent.state import AgentState
from app.tools.base import ToolResult


def test_extract_client_ref_from_dock_prefix():
    q = "Regarding Helvetia client CLI-SCEN-01 (Helena Vogt): Why is the transfer delayed?"
    assert extract_client_ref(q) == "CLI-SCEN-01"


def test_extract_client_ref_absent():
    assert extract_client_ref("What is KYC refresh?") is None


def test_routing_starts_at_classify():
    state = AgentState(question="KYC refresh cadence?")
    assert next_step(state) == STEP_CLASSIFY


def test_routing_rag_path_without_client():
    state = AgentState(question="KYC?", intent="RAG_QUERY", step=STEP_CLASSIFY)
    assert next_step(state) == STEP_REWRITE
    state.step = STEP_REWRITE
    assert next_step(state) == STEP_GENERATE
    state.step = STEP_GENERATE
    state.status = "completed"
    assert next_step(state) == END


def test_routing_rag_path_with_client_loops_tools_until_stop():
    state = AgentState(
        question="Regarding CLI-SCEN-01: KYC?",
        intent="RAG_QUERY",
        client_ref="CLI-SCEN-01",
        step=STEP_CLASSIFY,
    )
    assert next_step(state) == STEP_SELECT_TOOLS

    state.step = STEP_SELECT_TOOLS
    state.selected_tools = ["get_client_profile"]
    assert next_step(state) == STEP_RUN_TOOLS

    state.step = STEP_RUN_TOOLS
    state.tool_round = 1
    assert next_step(state) == STEP_SELECT_TOOLS

    state.step = STEP_SELECT_TOOLS
    state.selected_tools = []
    assert next_step(state) == STEP_REWRITE


def test_routing_stops_tool_loop_at_max_rounds():
    state = AgentState(
        question="Regarding CLI-SCEN-01: KYC?",
        client_ref="CLI-SCEN-01",
        step=STEP_RUN_TOOLS,
        tool_round=5,
        max_tool_rounds=5,
    )
    assert next_step(state) == STEP_REWRITE


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
    assert MAX_STEPS == 16


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


def test_runner_selects_and_runs_tools_for_client_question():
    seen: list[str] = []

    def tracking_classify(state: AgentState) -> None:
        state.intent = "RAG_QUERY"
        seen.append(state.step or "")

    def tracking_select(state: AgentState) -> None:
        seen.append(state.step or "")
        if state.tool_round == 0:
            state.selected_tools = ["get_client_profile"]
        elif state.tool_round == 1:
            state.selected_tools = ["get_recent_transactions"]
        else:
            state.selected_tools = []
            state.stop_reason = "enough_evidence"

    def tracking_run(state: AgentState) -> None:
        seen.append(state.step or "")
        assert len(state.selected_tools) == 1
        tool = state.selected_tools[0]
        if tool == "get_client_profile":
            state.tool_results.append(
                ToolResult(
                    tool="get_client_profile",
                    ok=True,
                    data={
                        "client_code": "CLI-SCEN-01",
                        "full_name": "Helena Vogt",
                        "kyc_status": "expired",
                        "kyc_document_expiry": "2024-01-01",
                    },
                ).to_dict()
            )
        else:
            state.tool_results.append(
                ToolResult(
                    tool="get_recent_transactions",
                    ok=True,
                    data={
                        "transaction_count": 1,
                        "pending_or_unusual_count": 1,
                        "pending_or_unusual": [
                            {
                                "transaction_code": "TXN-SCEN-01",
                                "account_code": "ACC-SCEN-01",
                                "txn_type": "transfer_out",
                                "amount": "250000.00",
                                "currency": "CHF",
                                "status": "pending",
                                "delay_reason_code": "kyc_expired",
                                "is_unusual": False,
                            }
                        ],
                    },
                ).to_dict()
            )
        state.tools_called.append(tool)
        state.tool_round += 1
        state.round_trace.append(
            {
                "round": state.tool_round,
                "selected": [tool],
                "tools": [tool],
                "ok": [True],
            }
        )

    def tracking_rewrite(state: AgentState) -> None:
        seen.append(state.step or "")
        state.rewritten_query = "transfer delay CLI-SCEN-01"

    def tracking_generate(state: AgentState) -> None:
        seen.append(state.step or "")
        assert len(state.tool_results) == 2
        assert state.round_trace == [
            {
                "round": 1,
                "selected": ["get_client_profile"],
                "tools": ["get_client_profile"],
                "ok": [True],
            },
            {
                "round": 2,
                "selected": ["get_recent_transactions"],
                "tools": ["get_recent_transactions"],
                "ok": [True],
            },
        ]
        state.answer = "ok"
        state.sources = []
        state.status = "completed"

    with patch(
        "app.agent.orchestrator.NODES",
        {
            STEP_CLASSIFY: tracking_classify,
            STEP_SELECT_TOOLS: tracking_select,
            STEP_RUN_TOOLS: tracking_run,
            STEP_REWRITE: tracking_rewrite,
            STEP_GENERATE: tracking_generate,
        },
    ):
        result = handle_question(
            "Regarding Helvetia client CLI-SCEN-01 (Helena Vogt): Why delayed?"
        )

    assert result["answer"] == "ok"
    assert seen == [
        STEP_CLASSIFY,
        STEP_SELECT_TOOLS,
        STEP_RUN_TOOLS,
        STEP_SELECT_TOOLS,
        STEP_RUN_TOOLS,
        STEP_SELECT_TOOLS,
        STEP_REWRITE,
        STEP_GENERATE,
    ]
    assert any(item["label"] == "Pending txn" for item in result["evidence"])


def test_run_tools_node_dispatches_selected_only():
    from app.agent.nodes.run_tools import run as run_tools

    state = AgentState(
        question="pending transfer?",
        client_ref="CLI-SCEN-01",
        selected_tools=["get_recent_transactions"],
    )
    with patch("app.agent.nodes.run_tools.fetch_transactions.run") as mock_txn, patch(
        "app.agent.nodes.run_tools.fetch_profile.run"
    ) as mock_profile, patch(
        "app.agent.nodes.run_tools.fetch_account_summary.run"
    ) as mock_summary:
        run_tools(state)

    mock_txn.assert_called_once_with(state)
    mock_profile.assert_not_called()
    mock_summary.assert_not_called()


def test_run_tools_node_dispatches_account_summary():
    from app.agent.nodes.run_tools import run as run_tools

    state = AgentState(
        question="portfolio holdings?",
        client_ref="CLI-SCEN-10",
        selected_tools=["get_account_summary"],
    )
    with patch(
        "app.agent.nodes.run_tools.fetch_account_summary.run"
    ) as mock_summary, patch(
        "app.agent.nodes.run_tools.fetch_profile.run"
    ) as mock_profile:
        run_tools(state)

    mock_summary.assert_called_once_with(state)
    mock_profile.assert_not_called()


def test_run_tools_node_records_round_trace_and_advances():
    from app.agent.nodes.run_tools import run as run_tools

    state = AgentState(
        question="pending transfer?",
        client_ref="CLI-SCEN-01",
        selected_tools=["get_recent_transactions"],
        max_tool_rounds=5,
    )

    def fake_txn(s: AgentState) -> None:
        s.tool_results.append(
            ToolResult(
                tool="get_recent_transactions",
                ok=True,
                data={"transaction_count": 0, "pending_or_unusual_count": 0},
            ).to_dict()
        )

    with patch("app.agent.nodes.run_tools.fetch_transactions.run", side_effect=fake_txn):
        run_tools(state)

    assert state.tool_round == 1
    assert state.tools_called == ["get_recent_transactions"]
    assert state.round_trace == [
        {
            "round": 1,
            "selected": ["get_recent_transactions"],
            "tools": ["get_recent_transactions"],
            "ok": [True],
        }
    ]
    assert state.stop_reason is None


def test_run_tools_sets_max_rounds_stop_reason():
    from app.agent.nodes.run_tools import run as run_tools

    state = AgentState(
        question="kyc?",
        client_ref="CLI-SCEN-01",
        selected_tools=["get_client_profile"],
        tool_round=4,
        max_tool_rounds=5,
    )
    with patch("app.agent.nodes.run_tools.fetch_profile.run"):
        run_tools(state)

    assert state.tool_round == 5
    assert state.stop_reason == "max_tool_rounds"
