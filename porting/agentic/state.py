from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


WorkflowPhase = Literal[
    "bootstrap",
    "analysis",
    "repair_cycle",
    "validation",
    "done",
    "blocked",
]
FileStatus = Literal["pending", "in_progress", "approved", "rejected", "blocked", "skipped"]
ReviewerVerdict = Literal["approved", "rejected", "needs_retry"]
CoordinatorDecision = Literal["retry_file", "next_file", "stop_success", "stop_blocked"]


class FileProgress(TypedDict, total=False):
    status: FileStatus
    retries: int
    last_error: str
    last_reviewer_verdict: ReviewerVerdict
    last_action: str
    last_change_summary: str


class RepairCycleResult(TypedDict, total=False):
    current_file: str
    reviewer_verdict: ReviewerVerdict
    coordinator_decision: CoordinatorDecision
    test_returncode: int
    parity_returncode: int
    detail: str


class PortingGraphState(TypedDict, total=False):
    request_id: str
    user_request: str
    repo_root: str
    roots: list[str]

    phase: WorkflowPhase
    cycle_index: int
    max_cycles: int
    max_retries_per_file: int

    matlab_files: list[str]
    call_graph_path: str
    porting_order: list[str]
    file_layer_map: dict[str, int]
    pending_files: list[str]
    current_file: str
    current_index: int

    file_progress: dict[str, FileProgress]
    approved_files: list[str]
    blocked_files: list[str]

    reports: dict[str, str]
    last_repair_result: RepairCycleResult
    last_decision: CoordinatorDecision
    stop_reason: str

    change_log_path: str
    history: list[str]

    # Operational knobs that can be tuned across cycles.
    repair_args: dict[str, str | int | bool]
    force_next_retry: NotRequired[bool]
    defer_change_log_write: NotRequired[bool]
    use_fallback_model: NotRequired[bool]
