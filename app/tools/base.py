"""Shared tool result types and timeout helper."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

T = TypeVar("T")

DEFAULT_TOOL_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class ToolError:
    """Structured failure from a tool (never raised into the LLM raw)."""

    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class ToolResult:
    """Typed tool outcome recorded on agent state."""

    tool: str
    ok: bool
    data: dict[str, Any] | None = None
    error: ToolError | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"tool": self.tool, "ok": self.ok}
        if self.data is not None:
            payload["data"] = self.data
        if self.error is not None:
            payload["error"] = self.error.to_dict()
        return payload


def run_with_timeout(
    fn: Callable[[], T],
    *,
    timeout_seconds: float = DEFAULT_TOOL_TIMEOUT_SECONDS,
) -> T:
    """Run ``fn`` in a worker thread and raise ``TimeoutError`` on overrun."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeout as exc:
            future.cancel()
            raise TimeoutError(
                f"Tool timed out after {timeout_seconds:.1f}s"
            ) from exc
