"""Fetch recent transactions tool node."""

from __future__ import annotations

import logging

from app.agent.state import AgentState
from app.database.session import SessionLocal
from app.tools.get_recent_transactions import (
    GetRecentTransactionsInput,
    get_recent_transactions,
)

logger = logging.getLogger(__name__)


def run(state: AgentState) -> None:
    """Call ``get_recent_transactions`` when ``client_ref`` is set; record the result."""
    if not state.client_ref:
        return

    session = SessionLocal()
    try:
        result = get_recent_transactions(
            session,
            GetRecentTransactionsInput(
                client_ref=state.client_ref,
                actor_employee_code=state.actor_employee_code,
            ),
        )
    finally:
        session.close()

    state.tool_results.append(result.to_dict())
    logger.info(
        "Tool get_recent_transactions: client_ref=%s ok=%s",
        state.client_ref,
        result.ok,
    )
