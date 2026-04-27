#!/usr/bin/env python3
"""Build a ready-to-paste agent prompt with compact project context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _mode_instruction(mode: str) -> str:
    if mode == "deterministic":
        return (
            "Run deterministic workflow only. Do not call LLM repair. "
            "Produce blocker summary and next deterministic command."
        )
    if mode == "repair":
        return (
            "Run deterministic workflow first, then run bounded repair cycle "
            "if TODO markers or parity blockers remain."
        )
    return "Run full workflow with deterministic-first policy and bounded repair when needed."


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compact prompt for agentic porting.")
    parser.add_argument(
        "--system-prompt",
        default="../prompts/system_agentic_orchestrator_full.md",
        help="System prompt file.",
    )
    parser.add_argument(
        "--compact-context-json",
        default="../state/agent_context_compact.json",
        help="Compact context JSON file.",
    )
    parser.add_argument(
        "--compact-context-text",
        default="../state/agent_context_compact.prompt.txt",
        help="Compact context text file.",
    )
    parser.add_argument(
        "--mode",
        choices=["deterministic", "repair", "full"],
        default="full",
        help="Prompt execution mode.",
    )
    parser.add_argument(
        "--roots",
        default="src,demo,tests,third_part",
        help="Roots to pass to the workflow.",
    )
    parser.add_argument(
        "--output",
        default="../state/porting_agent_prompt.txt",
        help="Output prompt file.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    system_prompt = _read_text((base / args.system_prompt).resolve())
    compact_context_json = _read_json((base / args.compact_context_json).resolve())
    compact_context_text = _read_text((base / args.compact_context_text).resolve())
    output = (base / args.output).resolve()

    context_summary = {
        "roots": compact_context_json.get("roots", []),
        "total_matlab_files": compact_context_json.get("total_matlab_files", 0),
        "total_changed_files": compact_context_json.get("total_changed_files", 0),
        "matlab_todo_markers": compact_context_json.get("matlab_todo_markers", 0),
        "parity_snapshot_summary": compact_context_json.get("parity_snapshot_summary", {}),
        "top_blockers": compact_context_json.get("top_blockers", [])[:15],
    }
    translation_examples_text = str(compact_context_json.get("translation_examples_text", "") or "").strip()

    task_block = "\n".join(
        [
            "Task:",
            _mode_instruction(args.mode),
            f"Use roots: {args.roots}",
            "Primary command:",
            (
                "python porting/scripts/run_agentic_porting_workflow.py "
                f"--roots {args.roots} --model gpt-oss:20b --max-cycles 12 "
                "--enable-strict-prefilter"
            ),
            "If deterministic-only mode is requested, use: --engine legacy --disable-llm --skip-tests",
            "If you need manual intervention on first failed apply=False, add: --pause-on-applied-false",
            "To resume safely after pause, use: --engine legacy --resume-from-report <report.json> --skip-pipeline",
            "Return concise execution summary and next command.",
        ]
    )

    payload = "\n\n".join(
        part
        for part in [
            system_prompt,
            (
                "Reference MATLAB->Python examples:\n" + translation_examples_text
                if translation_examples_text
                else ""
            ),
            "Compact context (text):\n" + compact_context_text if compact_context_text else "",
            "Compact context (JSON):\n" + json.dumps(context_summary, indent=2),
            task_block,
        ]
        if part
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")
    print(f"Prompt written to: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

