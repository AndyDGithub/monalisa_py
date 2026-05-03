from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from porting.agentic.state import PortingGraphState
from porting.agentic.tools import LegacyToolbox


@dataclass(slots=True)
class PortingAgent:
    toolbox: LegacyToolbox

    @staticmethod
    def _extract_report_payload_from_command(command: list[str]) -> dict[str, Any]:
        if not command:
            return {}
        for idx, token in enumerate(command[:-1]):
            if token == "--output":
                candidate = Path(command[idx + 1]).expanduser()
                if candidate.exists():
                    try:
                        payload = json.loads(candidate.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        return {}
                    if isinstance(payload, dict):
                        return payload
        return {}

    @staticmethod
    def _extract_prior_detail_payload(state: PortingGraphState) -> dict[str, Any]:
        prior_result = dict(state.get("last_repair_result", {}) or {})
        detail_obj = prior_result.get("detail", {})
        payload: dict[str, Any] = {}
        if isinstance(detail_obj, dict):
            payload = detail_obj
        elif isinstance(detail_obj, str) and detail_obj.strip():
            try:
                parsed = ast.literal_eval(detail_obj.strip())
                if isinstance(parsed, dict):
                    payload = parsed
            except (SyntaxError, ValueError):
                payload = {}
        return payload

    @classmethod
    def _extract_quality_blockers_from_state(cls, state: PortingGraphState) -> list[str]:
        payload = cls._extract_prior_detail_payload(state)
        blockers = payload.get("quality_blockers", [])
        if not isinstance(blockers, list):
            return []
        out = [str(item).strip() for item in blockers if str(item).strip()]
        return out

    @classmethod
    def _build_retry_feedback(cls, state: PortingGraphState) -> str:
        prior_result = dict(state.get("last_repair_result", {}) or {})
        payload = cls._extract_prior_detail_payload(state)
        if not payload and not prior_result:
            return ""
        lines: list[str] = []
        if prior_result.get("repair_finished_reason"):
            lines.append(f"repair_finished_reason={prior_result.get('repair_finished_reason')}")
        repair_reasons = prior_result.get("repair_reasons", [])
        if isinstance(repair_reasons, list) and repair_reasons:
            lines.append(f"repair_reasons={','.join(str(x) for x in repair_reasons)}")
        elif prior_result.get("last_error"):
            lines.append(f"last_error={prior_result.get('last_error')}")
        quality_blockers = payload.get("quality_blockers", [])
        if isinstance(quality_blockers, list) and quality_blockers:
            lines.append(f"quality_blockers={','.join(str(x) for x in quality_blockers)}")
        if payload.get("test_scope"):
            lines.append(f"test_scope={payload.get('test_scope')}")
        if payload.get("test_returncode") is not None:
            lines.append(f"test_returncode={payload.get('test_returncode')}")
        if payload.get("forced_target_error"):
            lines.append(f"forced_target_error={payload.get('forced_target_error')}")
        tail = str(payload.get("test_stdout_tail", "")).strip()
        if tail:
            tail = tail[-800:]
            lines.append(f"test_stdout_tail={tail}")
        feedback = "\n".join(lines).strip()
        return feedback[:1500]

    def port_or_repair_current(self, state: PortingGraphState) -> dict[str, Any]:
        current_file = state.get("current_file", "")
        if not current_file:
            return {
                "last_repair_result": {
                    "current_file": "",
                    "detail": "no_current_file",
                }
            }

        roots = list(state.get("roots", []))
        repair_args = dict(state.get("repair_args", {}))
        repair_args["max_iterations"] = int(repair_args.get("max_iterations", 1))
        repair_args["max_files_per_iteration"] = int(repair_args.get("max_files_per_iteration", 1))
        prior_result = dict(state.get("last_repair_result", {}))
        prior_finished_reason = str(prior_result.get("repair_finished_reason", ""))
        quality_blockers = self._extract_quality_blockers_from_state(state)
        if quality_blockers:
            repair_args["force_quality_cleanup"] = True
            repair_args["quality_blockers"] = ",".join(sorted(set(quality_blockers)))
        retry_feedback = self._build_retry_feedback(state)
        if retry_feedback:
            repair_args["retry_feedback"] = retry_feedback
        if state.get("use_fallback_model") and repair_args.get("fallback_model"):
            repair_args["model"] = repair_args["fallback_model"]
        if state.get("force_next_retry"):
            repair_args["max_iterations"] = max(2, int(repair_args["max_iterations"]))
            # If the previous attempt was a no-op, disable strict prefilter on retry
            # so the LLM path can be attempted.
            repair_args["enable_strict_prefilter"] = False
        elif prior_finished_reason == "no_patch_applied":
            repair_args["enable_strict_prefilter"] = False

        result = self.toolbox.run_repair_cycle(
            roots=roots,
            repair_args=repair_args,
            target_file=current_file,
        )
        report = self._extract_report_payload_from_command(result.command)
        if not report:
            report = self.toolbox.read_latest_repair_report()
        iterations = report.get("iterations", []) if isinstance(report, dict) else []
        last_iteration = iterations[-1] if isinstance(iterations, list) and iterations else {}
        repair_results: list[dict[str, Any]] = []
        if isinstance(last_iteration, dict):
            raw_repairs = last_iteration.get("repairs", last_iteration.get("repair_results", []))
            if isinstance(raw_repairs, list):
                repair_results = [item for item in raw_repairs if isinstance(item, dict)]
        applied_count = 0
        applied_count = sum(1 for item in repair_results if item.get("applied"))
        repair_targets = [str(item.get("target", "")) for item in repair_results if str(item.get("target", ""))]
        repair_reasons = [str(item.get("reason", "")) for item in repair_results if str(item.get("reason", ""))]
        finished_reason = str(report.get("finished_reason", "")) if isinstance(report, dict) else ""
        forced_target_error = ""
        if isinstance(last_iteration, dict):
            forced_target_error = str(last_iteration.get("forced_target_error", ""))

        detail = {
            "repair_returncode": result.returncode,
            "repair_stdout_tail": result.stdout[-2500:],
            "repair_stderr_tail": result.stderr[-2500:],
            "repair_elapsed_seconds": result.elapsed_seconds,
            "repair_finished_reason": finished_reason,
            "repair_applied_count": applied_count,
            "repair_target_count": len(repair_targets),
            "repair_targets": repair_targets[:8],
            "repair_reasons": repair_reasons[:8],
            "forced_target_error": forced_target_error,
            "repair_backend": "legacy_script_subprocess",
        }
        return {
            "last_repair_result": {
                "current_file": current_file,
                "repair_returncode": result.returncode,
                "repair_finished_reason": finished_reason,
                "repair_applied_count": applied_count,
                "repair_target_count": len(repair_targets),
                "repair_targets": repair_targets[:8],
                "repair_reasons": repair_reasons[:8],
                "forced_target_error": forced_target_error,
                "repair_backend": "legacy_script_subprocess",
                "detail": str(detail),
            },
            "force_next_retry": False,
        }
