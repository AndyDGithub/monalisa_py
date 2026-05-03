from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from porting.agentic.state import CoordinatorDecision, PortingGraphState


@dataclass(slots=True)
class CoordinatorAgent:
    max_retries_per_file: int

    def initialize_queue(self, state: PortingGraphState) -> dict[str, Any]:
        order = list(state.get("porting_order", []))
        file_progress = dict(state.get("file_progress", {}))
        pending = [f for f in order if file_progress.get(f, {}).get("status", "pending") == "pending"]
        return {
            "pending_files": pending,
            "current_index": 0,
            "phase": "repair_cycle",
        }

    def pick_current_file(self, state: PortingGraphState) -> dict[str, Any]:
        pending = list(state.get("pending_files", []))
        if not pending:
            return {"last_decision": "stop_success", "current_file": "", "phase": "done"}
        current = pending[0]
        progress = dict(state.get("file_progress", {}))
        info = dict(progress.get(current, {}))
        info["status"] = "in_progress"
        progress[current] = info
        return {
            "current_file": current,
            "file_progress": progress,
            "last_decision": "retry_file",
        }

    def decide_local(self, state: PortingGraphState) -> dict[str, Any]:
        current = state.get("current_file", "")
        progress = dict(state.get("file_progress", {}))
        info = dict(progress.get(current, {}))
        last_repair = state.get("last_repair_result", {}) or {}
        verdict = last_repair.get("reviewer_verdict", "needs_retry")
        repair_finished_reason = str(last_repair.get("repair_finished_reason", ""))
        info["last_reviewer_verdict"] = str(verdict)
        info["last_error"] = repair_finished_reason

        if repair_finished_reason == "paused_on_applied_false":
            info["status"] = "blocked"
            progress[current] = info
            blocked = list(state.get("blocked_files", []))
            if current and current not in blocked:
                blocked.append(current)
            pending = [f for f in state.get("pending_files", []) if f != current]
            return {
                "file_progress": progress,
                "blocked_files": blocked,
                "pending_files": pending,
                "last_decision": "next_file",
                "stop_reason": "paused_on_applied_false",
            }

        hard_block_reasons = {
            "llm_disabled",
            "no_llm_runtime_available",
            "no_candidate_targets",
            "no_patch_applied",
        }
        if verdict != "approved" and repair_finished_reason in hard_block_reasons:
            info["status"] = "blocked"
            progress[current] = info
            blocked = list(state.get("blocked_files", []))
            if current and current not in blocked:
                blocked.append(current)
            pending = [f for f in state.get("pending_files", []) if f != current]
            return {
                "file_progress": progress,
                "blocked_files": blocked,
                "pending_files": pending,
                "last_decision": "next_file",
            }

        if verdict == "approved":
            info["status"] = "approved"
            progress[current] = info
            approved = list(state.get("approved_files", []))
            if current and current not in approved:
                approved.append(current)
            pending = [f for f in state.get("pending_files", []) if f != current]
            return {
                "file_progress": progress,
                "approved_files": approved,
                "pending_files": pending,
                "last_decision": "next_file",
            }

        retries = int(info.get("retries", 0)) + 1
        info["retries"] = retries
        if retries >= self.max_retries_per_file:
            info["status"] = "blocked"
            progress[current] = info
            blocked = list(state.get("blocked_files", []))
            if current and current not in blocked:
                blocked.append(current)
            pending = [f for f in state.get("pending_files", []) if f != current]
            return {
                "file_progress": progress,
                "blocked_files": blocked,
                "pending_files": pending,
                "last_decision": "next_file",
                "use_fallback_model": False,
            }

        # Escalate to fallback model on the last allowed retry.
        use_fallback = retries >= max(1, self.max_retries_per_file - 1)
        info["status"] = "rejected"
        progress[current] = info
        return {
            "file_progress": progress,
            "last_decision": "retry_file",
            "force_next_retry": True,
            "use_fallback_model": use_fallback,
        }

    def decide_global(self, state: PortingGraphState) -> dict[str, Any]:
        if str(state.get("stop_reason", "")) == "paused_on_applied_false":
            return {
                "last_decision": "stop_blocked",
                "stop_reason": "paused_on_applied_false",
                "phase": "blocked",
            }

        pending = list(state.get("pending_files", []))
        cycle_index = int(state.get("cycle_index", 0))
        max_cycles = int(state.get("max_cycles", 1))
        blocked = list(state.get("blocked_files", []))

        if pending:
            if cycle_index >= max_cycles:
                decision: CoordinatorDecision = "stop_blocked"
                reason = "max_cycles_reached_with_pending_files"
                phase = "blocked"
            else:
                decision = "next_file"
                reason = ""
                phase = "repair_cycle"
        else:
            if blocked:
                decision = "stop_blocked"
                reason = "all_candidates_processed_but_some_blocked"
                phase = "blocked"
            else:
                decision = "stop_success"
                reason = "all_files_approved"
                phase = "done"

        return {
            "last_decision": decision,
            "stop_reason": reason,
            "phase": phase,
        }
