#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from porting.agentic.config import WorkflowConfig
from porting.agentic.state import PortingGraphState
from porting.agentic.workflows.global_graph import build_global_porting_workflow


def _configure_logging(*, verbose: bool, log_file: str | None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter)
    root.addHandler(sh)
    if log_file:
        path = Path(log_file).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(path, mode="a", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        root.addHandler(fh)
    logging.getLogger("porting.agentic.cli.v2").info("Logging initialized (level=%s)", logging.getLevelName(level))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LangGraph global workflow (v2).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--roots", default="src,demo,tests,third_part", help="Comma-separated roots.")
    parser.add_argument("--max-cycles", type=int, default=60, help="Max global cycles.")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Compatibility alias for --max-cycles.",
    )
    parser.add_argument("--max-retries-per-file", type=int, default=3, help="Max retries per file.")
    parser.add_argument(
        "--max-files-per-iteration",
        type=int,
        default=1,
        help="Max files per local repair invocation (kept for compatibility).",
    )
    parser.add_argument(
        "--repair-iterations-per-file",
        type=int,
        default=1,
        help="Max iterations passed to the local repair engine for each selected file.",
    )
    parser.add_argument("--model", default="qwen2.5-coder:7b", help="Primary LLM model.")
    parser.add_argument("--fallback-model", default="gpt-oss:20b", help="Fallback LLM model.")
    parser.add_argument("--ollama-host", default="", help="Optional Ollama host.")
    parser.add_argument("--ollama-num-parallel", type=int, default=0, help="Optional Ollama parallel requests cap.")
    parser.add_argument(
        "--ollama-max-loaded-models",
        type=int,
        default=0,
        help="Optional Ollama max loaded models override.",
    )
    parser.add_argument("--ollama-max-queue", type=int, default=0, help="Optional Ollama max queue override.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    parser.add_argument(
        "--log-file",
        default="porting/logs/agentic_v2_global.log",
        help="Optional log file path.",
    )
    parser.add_argument(
        "--stream-repair-logs",
        dest="stream_repair_logs",
        action="store_true",
        default=True,
        help="Stream logs from subprocesses in local repair cycle.",
    )
    parser.add_argument(
        "--no-stream-repair-logs",
        dest="stream_repair_logs",
        action="store_false",
        help="Disable streaming logs from repair subprocesses.",
    )
    parser.add_argument("--allow-matlab-todos", action="store_true", help="Allow stopping with TODO markers.")
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
    parser.add_argument("--disable-llm", action="store_true", help="Compatibility flag. Keeps deterministic mode.")
    parser.add_argument("--skip-tests", action="store_true", help="Compatibility flag (currently informational).")
    parser.add_argument(
        "--parallel-files-per-cycle",
        type=int,
        default=1,
        help="Number of files from the same dependency layer to process per global cycle.",
    )
    parser.add_argument(
        "--enable-parallel-repair",
        action="store_true",
        help="Enable threaded local repair dispatch for same-layer batch (recommended with --skip-pipeline).",
    )
    parser.add_argument(
        "--parallel-repair-max-workers",
        type=int,
        default=8,
        help="Upper bound of concurrent local repair subprocesses when parallel repair is enabled.",
    )
    parser.add_argument(
        "--generated-tests-per-iteration",
        type=int,
        default=120,
        help="Compatibility value forwarded to repair args.",
    )
    parser.add_argument(
        "--contracts-per-iteration",
        type=int,
        default=30,
        help="Compatibility value forwarded to repair args.",
    )
    parser.add_argument("--llm-timeout-seconds", type=int, default=180, help="LLM timeout in seconds.")
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=30000,
        help="Max context chars forwarded to local repair prompt builder.",
    )
    parser.add_argument(
        "--max-context-hard-cap",
        type=int,
        default=180000,
        help="Upper bound for adaptive context expansion on very large files.",
    )
    parser.add_argument(
        "--disable-llm-timeout",
        action="store_true",
        help="Disable timeout for each LLM repair invocation.",
    )
    parser.add_argument(
        "--dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_true",
        default=True,
        help="Enable dynamic LLM timeout based on file length.",
    )
    parser.add_argument(
        "--no-dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_false",
        help="Disable dynamic timeout and use fixed --llm-timeout-seconds.",
    )
    parser.add_argument("--dynamic-timeout-base-seconds", type=int, default=45)
    parser.add_argument("--dynamic-timeout-per-line-seconds", type=int, default=3)
    parser.add_argument("--dynamic-timeout-min-seconds", type=int, default=60)
    parser.add_argument("--dynamic-timeout-max-seconds", type=int, default=900)
    parser.add_argument("--enable-matlab-help", action="store_true", default=True)
    parser.add_argument("--matlab-help-max-functions", type=int, default=1)
    parser.add_argument("--matlab-help-timeout-seconds", type=int, default=20)
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
    parser.add_argument(
        "--sync-env-timeout-seconds",
        type=int,
        default=180,
        help="Hard timeout for the sync-env pip install step in local repair.",
    )
    parser.add_argument(
        "--per-file-pytest-timeout-seconds",
        type=int,
        default=180,
        help="Hard timeout for targeted per-file pytest probes in local repair.",
    )
    parser.add_argument(
        "--repair-subprocess-timeout-seconds",
        type=int,
        default=1800,
        help="Hard timeout for each local legacy repair subprocess.",
    )
    parser.add_argument("--output", default="porting/reports/agentic_v2_global_report.json", help="Output path.")
    args = parser.parse_args()
    _configure_logging(verbose=bool(args.verbose), log_file=args.log_file)

    max_cycles = args.max_iterations if args.max_iterations is not None else args.max_cycles
    repo_root = Path(args.repo_root).resolve()
    roots = [x.strip() for x in args.roots.split(",") if x.strip()]
    cfg = WorkflowConfig(
        repo_root=repo_root,
        roots=roots,
        max_cycles=max_cycles,
        max_retries_per_file=args.max_retries_per_file,
        generated_tests_per_iteration=args.generated_tests_per_iteration,
        contracts_per_iteration=args.contracts_per_iteration,
        llm_model=args.model,
        fallback_model=args.fallback_model,
        llm_timeout_seconds=args.llm_timeout_seconds,
        dynamic_llm_timeout=bool(args.dynamic_llm_timeout),
        dynamic_timeout_base_seconds=args.dynamic_timeout_base_seconds,
        dynamic_timeout_per_line_seconds=args.dynamic_timeout_per_line_seconds,
        dynamic_timeout_min_seconds=args.dynamic_timeout_min_seconds,
        dynamic_timeout_max_seconds=args.dynamic_timeout_max_seconds,
        enable_matlab_help=bool(args.enable_matlab_help),
        matlab_help_max_functions=args.matlab_help_max_functions,
        matlab_help_timeout_seconds=args.matlab_help_timeout_seconds,
        stream_subprocess_logs=bool(args.stream_repair_logs),
        allow_matlab_todos=args.allow_matlab_todos,
        enable_strict_prefilter=bool(args.enable_strict_prefilter),
        pause_on_applied_false=bool(args.pause_on_applied_false),
        sync_env=bool(args.sync_env),
        requirements_output=str(args.requirements_output),
    )
    logging.getLogger("porting.agentic.cli.v2").info(
        "Local repair backend currently uses legacy subprocess engine: run_agentic_repair_cycle_legacy.py"
    )
    app = build_global_porting_workflow(cfg)
    initial_state: PortingGraphState = {
        "repo_root": str(repo_root),
        "roots": roots,
        "max_cycles": cfg.max_cycles,
        "max_retries_per_file": cfg.max_retries_per_file,
        "repair_args": {
            "model": cfg.llm_model,
            "fallback_model": cfg.fallback_model,
            "ollama_host": str(args.ollama_host or ""),
            "ollama_num_parallel": max(0, int(args.ollama_num_parallel)),
            "ollama_max_loaded_models": max(0, int(args.ollama_max_loaded_models)),
            "ollama_max_queue": max(0, int(args.ollama_max_queue)),
            "auto_pull_model": False,
            "max_iterations": max(1, int(args.repair_iterations_per_file)),
            "max_files_per_iteration": max(1, int(args.max_files_per_iteration)),
            "generated_tests_per_iteration": cfg.generated_tests_per_iteration,
            "contracts_per_iteration": cfg.contracts_per_iteration,
            "llm_timeout_seconds": cfg.llm_timeout_seconds,
            "max_context_chars": max(4000, int(args.max_context_chars)),
            "max_context_hard_cap": max(8000, int(args.max_context_hard_cap)),
            "disable_llm_timeout": bool(args.disable_llm_timeout),
            "dynamic_llm_timeout": cfg.dynamic_llm_timeout,
            "dynamic_timeout_base_seconds": cfg.dynamic_timeout_base_seconds,
            "dynamic_timeout_per_line_seconds": cfg.dynamic_timeout_per_line_seconds,
            "dynamic_timeout_min_seconds": cfg.dynamic_timeout_min_seconds,
            "dynamic_timeout_max_seconds": cfg.dynamic_timeout_max_seconds,
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
            "sync_env_timeout_seconds": max(60, int(args.sync_env_timeout_seconds)),
            "enforce_comment_parity": bool(args.enforce_comment_parity),
            "enforce_matlab_todo_gate": bool(args.enforce_matlab_todo_gate),
            "enforce_fallback_stub_gate": bool(args.enforce_fallback_stub_gate),
            "enforce_untranslated_placeholder_gate": bool(args.enforce_untranslated_placeholder_gate),
            "enforce_test_scope_gate": bool(args.enforce_test_scope_gate),
            "enforce_runtime_metadata_gate": bool(args.enforce_runtime_metadata_gate),
            "parallel_files_per_cycle": max(1, int(args.parallel_files_per_cycle)),
            "enable_parallel_repair": bool(args.enable_parallel_repair),
            "parallel_repair_max_workers": max(1, int(args.parallel_repair_max_workers)),
            "per_file_pytest_timeout_seconds": max(30, int(args.per_file_pytest_timeout_seconds)),
            "repair_subprocess_timeout_seconds": (
                0 if bool(args.disable_llm_timeout) else max(120, int(args.repair_subprocess_timeout_seconds))
            ),
        },
    }

    # Invoke the workflow and get the final state/result after completion
    result = app.invoke(initial_state)

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"LangGraph v2 global report written to: {output}")
    print(
        json.dumps(
            {
                "phase": result.get("phase", ""),
                "stop_reason": result.get("stop_reason", ""),
                "approved_files": len(result.get("approved_files", [])),
                "blocked_files": len(result.get("blocked_files", [])),
                "pending_files": len(result.get("pending_files", [])),
                "cycles": result.get("cycle_index", 0),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
