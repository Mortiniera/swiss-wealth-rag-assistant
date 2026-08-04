"""Unit tests for structured ReAct turn decisions."""

from app.agent.turn_decision import (
    decision_from_fallback_tool,
    finish_decision,
    parse_turn_decision,
    search_policies_decision,
)


def test_parse_call_tool_decision():
    raw = (
        'Sure:\n'
        '{"action":"call_tool","tool":"get_client_profile","reason_code":"need_profile"}\n'
    )
    decision = parse_turn_decision(raw)
    assert decision is not None
    assert decision.action == "call_tool"
    assert decision.tool == "get_client_profile"
    assert decision.reason_code == "need_profile"
    assert decision.policy_query is None


def test_parse_search_policies_decision():
    decision = parse_turn_decision(
        '{"action":"search_policies","tool":null,'
        '"policy_query":"outbound transfer pending review SLA",'
        '"reason_code":"need_policy"}'
    )
    assert decision is not None
    assert decision.action == "search_policies"
    assert decision.tool is None
    assert decision.policy_query == "outbound transfer pending review SLA"
    assert decision.reason_code == "need_policy"


def test_parse_search_internal_policies_as_call_tool():
    from app.agent.tool_selection import POLICY_TOOL_NAME

    decision = parse_turn_decision(
        '{"action":"call_tool","tool":"search_internal_policies",'
        '"policy_query":"KYC refresh cadence SLA","reason_code":"need_policy"}'
    )
    assert decision is not None
    assert decision.action == "call_tool"
    assert decision.tool == POLICY_TOOL_NAME
    assert decision.policy_query == "KYC refresh cadence SLA"


def test_parse_finish_decision():
    decision = parse_turn_decision(
        '{"action":"finish","tool":null,"reason_code":"enough_evidence"}'
    )
    assert decision is not None
    assert decision.action == "finish"
    assert decision.tool is None
    assert decision.reason_code == "enough_evidence"


def test_parse_rejects_tool_batches():
    decision = parse_turn_decision(
        '{"action":"call_tool","tool":["get_client_profile","get_recent_transactions"],'
        '"reason_code":"need_profile"}'
    )
    assert decision is None


def test_parse_rejects_already_called_tool():
    decision = parse_turn_decision(
        '{"action":"call_tool","tool":"get_client_profile","reason_code":"need_profile"}',
        already_called=["get_client_profile"],
    )
    assert decision is None


def test_parse_rejects_duplicate_policy_query():
    decision = parse_turn_decision(
        '{"action":"search_policies","policy_query":"kyc refresh cadence",'
        '"reason_code":"need_policy"}',
        already_searched=["KYC refresh cadence"],
    )
    assert decision is None


def test_parse_rejects_short_policy_query():
    decision = parse_turn_decision(
        '{"action":"search_policies","policy_query":"ok","reason_code":"need_policy"}'
    )
    assert decision is None


def test_parse_rejects_unknown_tool():
    decision = parse_turn_decision(
        '{"action":"call_tool","tool":"delete_account","reason_code":"nope"}'
    )
    assert decision is None


def test_fallback_helpers():
    call = decision_from_fallback_tool("get_recent_transactions")
    assert call.action == "call_tool"
    assert call.tool == "get_recent_transactions"
    done = finish_decision("llm_fallback_finish")
    assert done.action == "finish"
    assert done.reason_code == "llm_fallback_finish"
    policy = search_policies_decision("transfer delay policy")
    assert policy.action == "search_policies"
    assert policy.policy_query == "transfer delay policy"
