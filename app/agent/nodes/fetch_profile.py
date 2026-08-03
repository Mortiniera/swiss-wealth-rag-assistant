"""Fetch client profile tool node."""

from __future__ import annotations

import logging

from app.agent.state import AgentState
from app.database.session import SessionLocal
from app.tools.get_client_profile import GetClientProfileInput, get_client_profile

logger = logging.getLogger(__name__)


def run(state: AgentState) -> None:
    """Call ``get_client_profile`` when ``client_ref`` is set; record the result."""
    if not state.client_ref:
        return

    session = SessionLocal()
    try:
        result = get_client_profile(
            session,
            GetClientProfileInput(
                client_ref=state.client_ref,
                actor_employee_code=state.actor_employee_code,
            ),
        )
    finally:
        session.close()

    state.tool_results.append(result.to_dict())
    logger.info(
        "Tool get_client_profile: client_ref=%s ok=%s",
        state.client_ref,
        result.ok,
    )
