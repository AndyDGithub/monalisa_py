#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic.config import WorkflowConfig
from agentic.state import PortingGraphState
from agentic.tools import LegacyToolbox
from agentic.workflows.repair_graph import build_repair_cycle_workflow


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LangGraph local repair workflow (v2).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--roots", default="src,demo,tests,third_part", help="Comma-separated roots.")
    parser.add_argument("--current-file", default="", help="Current file to process.")
    parser.add_argument("--target-file", default="", help="Compatibility alias for --current-file.")
    parser.add_argument("--max-retries-per-file", type=int, default=3, help="Max local retries.")
    parser.add_argument("--max-iterations", type=int, default=None, help="Compatibility alias for retries.")
    parser.add_argument("--max-files-per-iteration", type=int, default=1, help="Compatibility arg.")
    parser.add_argument("--model", default="gpt-oss:20b", help="Primary LLM model.")
    parser.add_argument("--fallback-model", default="gpt-oss:20b", help="Fallback LLM model.")
    parser.add_argument("--disable-llm", action="store_true", help="Compatibility flag.")
    parser.add_argument("--skip-tests", action="store_true", help="Compatibility flag.")
    parser.add_argument(
        "--enforce-comment-parity",
        dest="enforce_comment_parity",
        action="store_true",
        default=True,
        help="Treat missing Python comments vs MATLAB comments as a blocking reviewer gate.",
    )
    parser.add_argument(
        "--no-enforce-comment-parity",
        dest="enforce_comment_parity",
        action="store_false",
        help="Disable reviewer gate on comment parity.",
    )
    parser.add_argument(
        "--enforce-matlab-todo-gate",
        dest="enforce_matlab_todo_gate",
        action="store_true",
        default=True,
        help="Treat TODO(matlab-*) markers as a blocking reviewer gate.",
    )
    parser.add_argument(
        "--no-enforce-matlab-todo-gate",
        dest="enforce_matlab_todo_gate",
        action="store_false",
        help="Disable reviewer gate on TODO(matlab-*) markers.",
    )
    parser.add_argument(
        "--enforce-fallback-stub-gate",
        dest="enforce_fallback_stub_gate",
        action="store_true",
        default=True,
        help="Treat fallback stubs as blocking reviewer gate.",
    )
    parser.add_argument(
        "--no-enforce-fallback-stub-gate",
        dest="enforce_fallback_stub_gate",
        action="store_false",
        help="Do not block reviewer approval on fallback-stub markers.",
    )
    parser.add_argument(
        "--enforce-untranslated-placeholder-gate",
        dest="enforce_untranslated_placeholder_gate",
        action="store_true",
        default=True,
        help="Block approval when untranslated placeholders/stubs are detected.",
    )
    parser.add_argument(
        "--no-enforce-untranslated-placeholder-gate",
        dest="enforce_untranslated_placeholder_gate",
        action="store_false",
        help="Disable untranslated-placeholder reviewer gate.",
    )
    parser.add_argument(
        "--enforce-test-scope-gate",
        dest="enforce_test_scope_gate",
        action="store_true",
        default=True,
        help="Require at least one mapped target test for approval (except special-case invalid unreferenced MATLAB).",
    )
    parser.add_argument(
        "--no-enforce-test-scope-gate",
        dest="enforce_test_scope_gate",
        action="store_false",
        help="Allow approval even when no target tests are mapped.",
    )
    parser.add_argument(
        "--enforce-runtime-metadata-gate",
        dest="enforce_runtime_metadata_gate",
        action="store_true",
        default=True,
        help="Require helper-based handling when MATLAB uses inputname/assignin/evalin.",
    )
    parser.add_argument(
        "--no-enforce-runtime-metadata-gate",
        dest="enforce_runtime_metadata_gate",
        action="store_false",
        help="Disable runtime metadata reviewer gate.",
    )
    parser.add_argument(
        "--enable-strict-prefilter",
        dest="enable_strict_prefilter",
        action="store_true",
        default=True,
        help="Run deterministic strict baseline prefilter before LLM repair.",
    )
    parser.add_argument(
        "--disable-strict-prefilter",
        dest="enable_strict_prefilter",
        action="store_false",
        help="Disable strict baseline prefilter.",
    )
    parser.add_argument(
        "--pause-on-applied-false",
        action="store_true",
        help="Pause local repair when a candidate returns applied=False (except benign skip reasons).",
    )
    parser.add_argument(
        "--skip-pipeline",
        action="store_true",
        help="Skip deterministic pipeline regeneration in local repair calls.",
    )
    parser.add_argument(
        "--sync-env",
        action="store_true",
        help="Generate deterministic requirements and install them before test runs.",
    )
    parser.add_argument(
        "--requirements-output",
        default="porting/reports/requirements.generated.txt",
        help="Requirements file path generated by deterministic sync step.",
    )
    parser.add_argument("--output", default="porting/reports/agentic_v2_repair_report.json", help="Output path.")
    args = parser.parse_args()

    current_file = args.current_file or args.target_file
    if not current_file:
        raise SystemExit("Missing required target: use --current-file or --target-file.")
    max_retries = args.max_iterations if args.max_iterations is not None else args.max_retries_per_file

    repo_root = Path(args.repo_root).resolve()
    roots = [x.strip() for x in args.roots.split(",") if x.strip()]
    cfg = WorkflowConfig(
        repo_root=repo_root,
        roots=roots,
        max_retries_per_file=max_retries,
        llm_model=args.model,
        fallback_model=args.fallback_model,
        enable_strict_prefilter=bool(args.enable_strict_prefilter),
        pause_on_applied_false=bool(args.pause_on_applied_false),
    )
    toolbox = LegacyToolbox(repo_root=repo_root)
    app = build_repair_cycle_workflow(toolbox=toolbox, max_retries_per_file=cfg.max_retries_per_file)

    state: PortingGraphState = {
        "repo_root": str(repo_root),
        "roots": roots,
        "pending_files": [current_file],
        "current_file": current_file,
        "max_retries_per_file": cfg.max_retries_per_file,
        "repair_args": {
            "model": cfg.llm_model,
            "fallback_model": cfg.fallback_model,
            "max_iterations": max(1, int(args.max_files_per_iteration)),
            "max_files_per_iteration": max(1, int(args.max_files_per_iteration)),
            "generated_tests_per_iteration": cfg.generated_tests_per_iteration,
            "contracts_per_iteration": cfg.contracts_per_iteration,
            "llm_timeout_seconds": cfg.llm_timeout_seconds,
            "dynamic_llm_timeout": cfg.dynamic_llm_timeout,
            "enable_matlab_help": cfg.enable_matlab_help,
            "matlab_help_max_functions": cfg.matlab_help_max_functions,
            "matlab_help_timeout_seconds": cfg.matlab_help_timeout_seconds,
            "stream_subprocess_logs": cfg.stream_subprocess_logs,
            "disable_llm": bool(args.disable_llm),
            "skip_tests": bool(args.skip_tests),
            "enable_strict_prefilter": cfg.enable_strict_prefilter,
            "pause_on_applied_false": cfg.pause_on_applied_false,
            "skip_pipeline": bool(args.skip_pipeline),
            "sync_env": bool(args.sync_env),
            "requirements_output": str(args.requirements_output),
            "enforce_comment_parity": bool(args.enforce_comment_parity),
            "enforce_matlab_todo_gate": bool(args.enforce_matlab_todo_gate),
            "enforce_fallback_stub_gate": bool(args.enforce_fallback_stub_gate),
            "enforce_untranslated_placeholder_gate": bool(args.enforce_untranslated_placeholder_gate),
            "enforce_test_scope_gate": bool(args.enforce_test_scope_gate),
            "enforce_runtime_metadata_gate": bool(args.enforce_runtime_metadata_gate),
        },
    }
    result = app.invoke(state)

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"LangGraph v2 repair report written to: {output}")
    print(
        json.dumps(
            {
                "current_file": result.get("current_file", ""),
                "decision": result.get("last_decision", ""),
                "review": (result.get("last_repair_result", {}) or {}).get("reviewer_verdict", ""),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
