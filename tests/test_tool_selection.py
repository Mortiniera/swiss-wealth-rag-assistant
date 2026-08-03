"""Unit tests for bounded tool selection helpers."""

from app.agent.tool_selection import (
    heuristic_tools,
    merge_tool_choices,
    normalize_selected_tools,
    parse_tool_names,
)


def test_parse_tool_names_json_array():
    raw = 'Here you go:\n["get_recent_transactions", "get_client_profile"]\n'
    assert parse_tool_names(raw) == [
        "get_recent_transactions",
        "get_client_profile",
    ]


def test_normalize_drops_unknown_and_caps():
    selected = normalize_selected_tools(
        [
            "get_recent_transactions",
            "nope",
            "get_account_restrictions",
            "get_open_service_requests",
            "get_client_profile",
        ],
        max_tools=3,
        fallback_if_empty=False,
    )
    assert selected == [
        "get_client_profile",
        "get_account_restrictions",
        "get_recent_transactions",
    ]
    assert "get_open_service_requests" not in selected


def test_normalize_adds_profile_when_other_tools_chosen():
    selected = normalize_selected_tools(
        ["get_recent_transactions"],
        max_tools=3,
        fallback_if_empty=False,
    )
    assert selected[0] == "get_client_profile"
    assert "get_recent_transactions" in selected


def test_heuristic_pending_transfer():
    picks = heuristic_tools(
        "Why is this client's outbound transfer still in pending review?"
    )
    assert "get_recent_transactions" in picks


def test_heuristic_portfolio_holdings():
    picks = heuristic_tools(
        "Why does the client's portfolio look weaker — what holdings are on file?"
    )
    assert "get_account_summary" in picks
    assert "get_account_restrictions" not in picks


def test_heuristic_awaiting_reply():
    picks = heuristic_tools(
        "The client emailed in and nobody replied — what's on the thread?"
    )
    assert "get_interaction_history" in picks


def test_merge_empty_without_fallback_stays_empty():
    assert merge_tool_choices([], [], fallback_if_empty=False) == []


def test_merge_empty_with_fallback_uses_profile():
    assert merge_tool_choices([], [], fallback_if_empty=True) == [
        "get_client_profile"
    ]
