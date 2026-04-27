#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _safe_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _parse_detail_blob(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip().startswith("{"):
        try:
            parsed = ast.literal_eval(value.strip())
        except (SyntaxError, ValueError):
            return {}
        if isinstance(parsed, dict):
            return parsed
    return {}


def build_report(*, change_log: Path, global_report: Path) -> dict[str, Any]:
    events = _safe_jsonl(change_log)
    verdicts = Counter()
    finished_reasons = Counter()
    repair_reasons = Counter()
    quality_blockers = Counter()
    by_file: dict[str, list[str]] = defaultdict(list)
    by_file_repair_reason: dict[str, list[str]] = defaultdict(list)

    for event in events:
        details = event.get("details", {}) if isinstance(event.get("details", {}), dict) else {}
        file_path = str(event.get("file", "")).strip()
        verdict = str(details.get("reviewer_verdict", "")).strip() or "<missing>"
        finished = str(details.get("repair_finished_reason", "")).strip() or "<missing>"
        verdicts[verdict] += 1
        finished_reasons[finished] += 1
        for reason in details.get("repair_reasons", []) or []:
            repair_reasons[str(reason)] += 1
            if file_path:
                by_file_repair_reason[file_path].append(str(reason))
        detail_blob = _parse_detail_blob(details.get("detail"))
        for blocker in detail_blob.get("quality_blockers", []) or []:
            quality_blockers[str(blocker)] += 1
        if file_path:
            by_file[file_path].append(verdict)

    stuck_files: list[dict[str, Any]] = []
    for file_path, seq in by_file.items():
        if len(seq) < 2:
            continue
        if all(item == seq[0] for item in seq):
            stuck_files.append(
                {
                    "file": file_path,
                    "attempts": len(seq),
                    "verdict": seq[0],
                    "repair_reasons": Counter(by_file_repair_reason.get(file_path, [])).most_common(3),
                }
            )
    stuck_files = sorted(stuck_files, key=lambda item: item["attempts"], reverse=True)

    global_payload: dict[str, Any] = {}
    if global_report.exists():
        try:
            raw = json.loads(global_report.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                global_payload = raw
        except json.JSONDecodeError:
            global_payload = {}

    return {
        "change_log_path": str(change_log),
        "global_report_path": str(global_report),
        "events": len(events),
        "verdicts": dict(verdicts),
        "repair_finished_reasons": dict(finished_reasons),
        "repair_reasons_top": repair_reasons.most_common(20),
        "quality_blockers_top": quality_blockers.most_common(20),
        "stuck_files_top": stuck_files[:50],
        "global_phase": global_payload.get("phase", ""),
        "global_stop_reason": global_payload.get("stop_reason", ""),
        "global_pending": len(global_payload.get("pending_files", []) or []),
        "global_blocked": len(global_payload.get("blocked_files", []) or []),
        "global_approved": len(global_payload.get("approved_files", []) or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit agentic workflow logs/reports.")
    parser.add_argument("--change-log", default="porting/logs/change_log.jsonl")
    parser.add_argument("--global-report", default="porting/reports/agentic_v2_global_report.json")
    parser.add_argument("--output", default="porting/reports/agentic_audit_report.json")
    args = parser.parse_args()

    report = build_report(
        change_log=Path(args.change_log).resolve(),
        global_report=Path(args.global_report).resolve(),
    )
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Audit report written to: {output}")
    print(
        json.dumps(
            {
                "events": report["events"],
                "verdicts": report["verdicts"],
                "top_repair_reason": report["repair_reasons_top"][:3],
                "top_quality_blockers": report["quality_blockers_top"][:3],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

