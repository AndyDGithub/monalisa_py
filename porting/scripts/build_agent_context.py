#!/usr/bin/env python3
"""Build compact agent context from deterministic pipeline reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _pick_top_blockers(report: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    analysis = report.get("generated_files_analysis", {})
    if isinstance(analysis, dict):
        summary = analysis.get("summary", {})
        todos = int(summary.get("matlab_todo_markers", 0) or 0)
        if todos > 0:
            out.append({"type": "matlab_todo_markers", "count": todos})

    parity = report.get("parity_snapshots", {})
    if isinstance(parity, dict):
        summary = parity.get("summary", {})
        failing = int(summary.get("failing_snapshot_dirs", 0) or 0)
        missing = int(summary.get("missing_snapshot_dirs", 0) or 0)
        if failing > 0 or missing > 0:
            out.append(
                {
                    "type": "parity_snapshot_mismatch",
                    "failing_snapshots": failing,
                    "missing_snapshots": missing,
                }
            )

    roots = report.get("roots", {})
    if isinstance(roots, dict):
        for root_tag, root_item in roots.items():
            if not isinstance(root_item, dict):
                continue
            failed_files = root_item.get("compile", {}).get("failed_files", [])
            failed_count = len(failed_files) if isinstance(failed_files, list) else 0
            if failed_count > 0:
                out.append(
                    {
                        "type": "compile_failures",
                        "root": root_tag,
                        "count": failed_count,
                    }
                )

    return out[: max(0, limit)]


def _render_prompt(context: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("Use deterministic tools first. Call LLM patching only for unresolved blockers.")
    lines.append(f"Roots: {', '.join(context.get('roots', [])) or 'none'}")
    lines.append(f"Total MATLAB files: {context.get('total_matlab_files', 0)}")
    lines.append(f"Total changed files: {context.get('total_changed_files', 0)}")
    lines.append(f"MATLAB TODO markers: {context.get('matlab_todo_markers', 0)}")
    parity = context.get("parity_snapshot_summary", {})
    if isinstance(parity, dict) and parity:
        lines.append(
            "Parity snapshots: "
            f"ref={parity.get('reference_snapshot_dirs', 0)}, "
            f"cand={parity.get('candidate_snapshot_dirs', 0)}, "
            f"failing={parity.get('failing_snapshot_dirs', 0)}, "
            f"missing={parity.get('missing_snapshot_dirs', 0)}"
        )
    blockers = context.get("top_blockers", [])
    if blockers:
        lines.append("Top blockers:")
        for b in blockers:
            lines.append(f"- {json.dumps(b, ensure_ascii=True)}")
    examples_text = str(context.get("translation_examples_text", "") or "").strip()
    if examples_text:
        lines.append("Reference MATLAB->Python examples available in context.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact context for agentic porting.")
    parser.add_argument("--reports-dir", default="../reports", help="Reports directory.")
    parser.add_argument(
        "--pipeline-report",
        default="pipeline_run_report.json",
        help="Pipeline report filename (inside reports dir).",
    )
    parser.add_argument(
        "--analysis-report",
        default="generated_files_analysis.json",
        help="Generated file analysis filename (inside reports dir).",
    )
    parser.add_argument(
        "--parity-snapshot-report",
        default="parity_snapshot_comparison.json",
        help="Parity snapshot report filename (inside reports dir).",
    )
    parser.add_argument("--max-blockers", type=int, default=20, help="Maximum blockers in compact context.")
    parser.add_argument(
        "--examples-prompt",
        default="../prompts/matlab_to_python_examples.md",
        help="Markdown file with curated MATLAB->Python examples.",
    )
    parser.add_argument(
        "--examples-max-chars",
        type=int,
        default=12000,
        help="Maximum number of example characters to store in compact context.",
    )
    parser.add_argument("--output", default="../state/agent_context_compact.json", help="Compact JSON output path.")
    parser.add_argument(
        "--prompt-output",
        default="../state/agent_context_compact.prompt.txt",
        help="Prompt text output path.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    reports_dir = (base / args.reports_dir).resolve()
    pipeline_report = _load_json(reports_dir / args.pipeline_report)
    analysis_report = _load_json(reports_dir / args.analysis_report)
    parity_snapshot_report = _load_json(reports_dir / args.parity_snapshot_report)
    examples_text = _read_text((base / args.examples_prompt).resolve()).strip()
    if args.examples_max_chars > 0 and len(examples_text) > args.examples_max_chars:
        examples_text = examples_text[: args.examples_max_chars]

    roots_report = pipeline_report.get("roots", {})
    roots = sorted(roots_report.keys()) if isinstance(roots_report, dict) else []
    total_matlab_files = int(pipeline_report.get("summary", {}).get("total_matlab_files", 0) or 0)
    total_changed_files = int(pipeline_report.get("summary", {}).get("total_changed_files", 0) or 0)
    matlab_todo_markers = int(analysis_report.get("summary", {}).get("matlab_todo_markers", 0) or 0)
    parity_summary = parity_snapshot_report.get("summary", {}) if isinstance(parity_snapshot_report, dict) else {}

    envelope = {
        "roots": roots,
        "total_matlab_files": total_matlab_files,
        "total_changed_files": total_changed_files,
        "matlab_todo_markers": matlab_todo_markers,
        "parity_snapshot_summary": parity_summary,
        "translation_examples_text": examples_text,
        "top_blockers": _pick_top_blockers(
            {
                "roots": roots_report,
                "generated_files_analysis": analysis_report,
                "parity_snapshots": parity_snapshot_report,
            },
            args.max_blockers,
        ),
    }

    output = (base / args.output).resolve()
    prompt_output = (base / args.prompt_output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    prompt_output.write_text(_render_prompt(envelope), encoding="utf-8")

    print(f"Agent context JSON written to: {output}")
    print(f"Agent context prompt written to: {prompt_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
