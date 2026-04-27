"""MATLAB runtime metadata helpers for inputname/assignin/evalin semantics.

These helpers provide deterministic, explicit behavior for MATLAB runtime
constructs that depend on the caller workspace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any


@dataclass(slots=True)
class MatlabRuntimeMetadata:
    """Best-effort runtime context to emulate MATLAB workspace behavior."""

    workspace: dict[str, Any] = field(default_factory=dict)
    caller_locals: dict[str, Any] = field(default_factory=dict)
    caller_globals: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_caller(cls, *, frame_depth: int = 2) -> "MatlabRuntimeMetadata":
        frame = inspect.currentframe()
        for _ in range(max(frame_depth, 0)):
            if frame is None:
                break
            frame = frame.f_back
        if frame is None:
            return cls()
        return cls(
            workspace={},
            caller_locals=dict(frame.f_locals),
            caller_globals=dict(frame.f_globals),
        )


def ensure_runtime_metadata(
    metadata: MatlabRuntimeMetadata | None = None,
    *,
    frame_depth: int = 2,
) -> MatlabRuntimeMetadata:
    if metadata is not None:
        return metadata
    return MatlabRuntimeMetadata.from_caller(frame_depth=frame_depth)


def _find_name_for_value(scope: dict[str, Any], value: Any) -> str | None:
    for name, candidate in scope.items():
        if candidate is value:
            return name
    return None


def resolve_inputname(
    position: int,
    *,
    args: tuple[Any, ...] | list[Any] | None = None,
    explicit_name: str | None = None,
    fallback_name: str = "",
    frame_depth: int = 2,
) -> str:
    """Best-effort replacement for MATLAB inputname(position).

    Preferred usage in ported code:
    - pass `explicit_name` when available for deterministic behavior.
    - otherwise pass `args=(...)` from the current function.
    """
    if explicit_name:
        return str(explicit_name)

    pos = int(position) - 1
    if pos < 0:
        return fallback_name or ""

    values: tuple[Any, ...] = tuple(args or ())
    if not values:
        frame = inspect.currentframe()
        target_frame = frame
        for _ in range(max(frame_depth, 0)):
            if target_frame is None:
                break
            target_frame = target_frame.f_back
        if target_frame is not None:
            arg_info = inspect.getargvalues(target_frame)
            ordered_names = list(arg_info.args)
            if arg_info.varargs:
                ordered_names.append(arg_info.varargs)
            values = tuple(target_frame.f_locals.get(name) for name in ordered_names)
        else:
            values = tuple()

    if pos >= len(values):
        return fallback_name or ""
    value = values[pos]

    frame = inspect.currentframe()
    caller_frame = frame
    for _ in range(max(frame_depth + 1, 0)):
        if caller_frame is None:
            break
        caller_frame = caller_frame.f_back
    if caller_frame is not None:
        local_name = _find_name_for_value(dict(caller_frame.f_locals), value)
        if local_name:
            return local_name
        global_name = _find_name_for_value(dict(caller_frame.f_globals), value)
        if global_name:
            return global_name

    return fallback_name or f"arg_{position}"


def assignin_runtime(
    scope: str,
    name: str,
    value: Any,
    *,
    metadata: MatlabRuntimeMetadata | None = None,
) -> MatlabRuntimeMetadata:
    """Best-effort replacement for MATLAB assignin(scope, name, value)."""
    ctx = ensure_runtime_metadata(metadata, frame_depth=3)
    normalized = str(scope or "").lower()
    key = str(name)

    # Python cannot reliably mutate another function's local scope at runtime.
    # We store values in explicit runtime metadata workspace instead.
    if normalized in {"caller", "base", "workspace"}:
        ctx.workspace[key] = value
        return ctx
    if normalized in {"global"}:
        ctx.caller_globals[key] = value
        return ctx

    # Fallback: keep deterministic behavior in metadata workspace.
    ctx.workspace[key] = value
    return ctx


def evalin_runtime(
    scope: str,
    expression: str,
    *,
    metadata: MatlabRuntimeMetadata | None = None,
    default: Any = None,
) -> Any:
    """Best-effort replacement for MATLAB evalin(scope, expression)."""
    ctx = ensure_runtime_metadata(metadata, frame_depth=3)
    normalized = str(scope or "").lower()
    expr = str(expression or "").strip()
    if not expr:
        return default

    env: dict[str, Any] = {}
    if normalized in {"caller", "base", "workspace"}:
        env.update(ctx.caller_globals)
        env.update(ctx.caller_locals)
        env.update(ctx.workspace)
    elif normalized in {"global"}:
        env.update(ctx.caller_globals)
    else:
        env.update(ctx.workspace)

    try:
        return eval(expr, {"__builtins__": {}}, env)
    except Exception:  # noqa: BLE001
        return default


__all__ = [
    "MatlabRuntimeMetadata",
    "ensure_runtime_metadata",
    "resolve_inputname",
    "assignin_runtime",
    "evalin_runtime",
]

