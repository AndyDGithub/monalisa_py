from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic.state import PortingGraphState
from agentic.tools import LegacyToolbox


@dataclass(slots=True)
class DocumentorAgent:
    toolbox: LegacyToolbox

    def record_cycle_event(self, state: PortingGraphState) -> dict[str, Any]:
        current = state.get("current_file", "")
        result = dict(state.get("last_repair_result", {}))
        verdict = str(result.get("reviewer_verdict", "needs_retry"))
        summary = f"{current} -> {verdict}"

        change_log = self.toolbox.log_root / "change_log.jsonl"
        if not bool(state.get("defer_change_log_write", False)):
            change_log = self.toolbox.document_change(
                file_path=current,
                summary=summary,
                details=result,
            )
        history = list(state.get("history", []))
        history.append(summary)
        return {
            "change_log_path": str(change_log),
            "history": history[-1000:],
        }

    def write_global_summary(self, state: PortingGraphState) -> dict[str, Any]:
        out_dir = self.toolbox.report_root
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "agentic_global_summary.json"
        payload = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "phase": state.get("phase", "done"),
            "stop_reason": state.get("stop_reason", ""),
            "approved_files": state.get("approved_files", []),
            "blocked_files": state.get("blocked_files", []),
            "pending_files": state.get("pending_files", []),
            "history_tail": list(state.get("history", []))[-50:],
        }
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        reports = dict(state.get("reports", {}))
        reports["global_summary"] = str(target)
        return {"reports": reports}
