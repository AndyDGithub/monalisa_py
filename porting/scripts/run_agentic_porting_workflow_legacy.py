#!/usr/bin/env python3
"""One-command deterministic + agentic porting workflow with progress logs."""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
LOGGER = logging.getLogger("agentic_porting_workflow")


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    LOGGER.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    LOGGER.handlers.clear()
    LOGGER.addHandler(handler)


def _run(
    script_name: str,
    args: list[str],
    cwd: Path,
    *,
    step_name: str,
    stream_output: bool,
    verbose: bool,
) -> dict[str, Any]:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    LOGGER.info("START %s", step_name)
    LOGGER.info("CMD   %s", " ".join(cmd))
    t0 = time.perf_counter()

    if stream_output:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        merged_out: list[str] = []
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip("\n")
            merged_out.append(line)
            LOGGER.info("[%s] %s", step_name, line)
        returncode = proc.wait()
        stdout_text = ("\n".join(merged_out) + ("\n" if merged_out else ""))
        stderr_text = ""
    else:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            env=env,
        )
        returncode = proc.returncode
        stdout_text = proc.stdout
        stderr_text = proc.stderr
        if verbose and stdout_text.strip():
            LOGGER.debug("[%s stdout]\n%s", step_name, stdout_text.strip())
        if verbose and stderr_text.strip():
            LOGGER.debug("[%s stderr]\n%s", step_name, stderr_text.strip())

    elapsed_s = round(time.perf_counter() - t0, 2)
    if returncode == 0:
        LOGGER.info("DONE  %s (%.2fs)", step_name, elapsed_s)
    else:
        LOGGER.error("FAIL  %s (%.2fs) rc=%s", step_name, elapsed_s, returncode)

    return {
        "command": cmd,
        "returncode": returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
        "elapsed_seconds": elapsed_s,
    }


def _run_repair_cycle_with_compat(
    *,
    repo_root: Path,
    repair_args: list[str],
    stream_repair_logs: bool,
    verbose: bool,
) -> dict[str, Any]:
    result = _run(
        "run_agentic_repair_cycle.py",
        repair_args,
        repo_root,
        step_name="agentic_repair_cycle",
        stream_output=stream_repair_logs,
        verbose=verbose,
    )

    err_blob = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
    if result.get("returncode") == 2 and "unrecognized arguments" in err_blob:
        LOGGER.warning(
            "Repair cycle argument mismatch detected. Retrying without stream/heartbeat compatibility flags."
        )
        fallback_args: list[str] = []
        i = 0
        while i < len(repair_args):
            token = repair_args[i]
            if token == "--stream-subprocess-logs":
                i += 1
                continue
            if token == "--heartbeat-seconds":
                i += 2
                continue
            fallback_args.append(token)
            i += 1
        retry = _run(
            "run_agentic_repair_cycle.py",
            fallback_args,
            repo_root,
            step_name="agentic_repair_cycle_retry_compat",
            stream_output=stream_repair_logs,
            verbose=verbose,
        )
        return {
            "initial_attempt": result,
            "compat_retry": retry,
            "returncode": retry.get("returncode"),
        }
    return result


def _load_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full deterministic + agentic porting workflow.")
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--roots", default="src,demo,tests,third_part", help="Comma-separated roots.")
    parser.add_argument("--force", action="store_true", help="Force regeneration.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip compile-time pytest in pipeline.")
    parser.add_argument("--overwrite-manual", action="store_true", help="Allow overwrite of manual Python files.")
    parser.add_argument(
        "--repair-force-pipeline",
        action="store_true",
        help="Also force regeneration inside each repair iteration (disabled by default).",
    )
    parser.add_argument(
        "--repair-overwrite-manual",
        action="store_true",
        help="Also allow overwrite-manual inside each repair iteration (disabled by default).",
    )
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model.")
    parser.add_argument(
        "--fallback-model",
        default="gpt-oss:20b",
        help="Fallback Ollama model if --model is unavailable.",
    )
    parser.add_argument(
        "--auto-pull-model",
        dest="auto_pull_model",
        action="store_true",
        default=True,
        help="Auto-pull missing Ollama model(s) during repair cycle.",
    )
    parser.add_argument(
        "--no-auto-pull-model",
        dest="auto_pull_model",
        action="store_false",
        help="Disable model auto-pull and use only locally installed models.",
    )
    parser.add_argument("--max-iterations", type=int, default=2, help="Repair iterations.")
    parser.add_argument("--max-files-per-iteration", type=int, default=5, help="Repair file cap per iteration.")
    parser.add_argument(
        "--repair-all-candidates",
        action="store_true",
        help="Attempt to repair all detected candidate files each iteration.",
    )
    parser.add_argument(
        "--run-all-generated-tests",
        action="store_true",
        help="Run all generated tests in each repair iteration.",
    )
    parser.add_argument(
        "--run-all-contract-tests",
        action="store_true",
        help="Run all contract tests in each repair iteration.",
    )
    parser.add_argument(
        "--allow-matlab-todos",
        action="store_true",
        help="Allow workflow to finish even if TODO(matlab-*) markers remain.",
    )
    parser.add_argument(
        "--one-shot-full",
        action="store_true",
        help=(
            "Preset for full translation in one run: enables repair-all-candidates, "
            "run-all-generated-tests, run-all-contract-tests, and raises max-iterations to at least 8."
        ),
    )
    parser.add_argument(
        "--generated-tests-per-iteration",
        type=int,
        default=120,
        help="Number of generated tests to run in each repair iteration.",
    )
    parser.add_argument(
        "--contracts-per-iteration",
        type=int,
        default=30,
        help="Number of contract tests to run in each repair iteration.",
    )
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=6000,
        help="Maximum characters used per context block in repair prompts.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    parser.add_argument(
        "--stream-repair-logs",
        action="store_true",
        help="Stream run_agentic_repair_cycle logs live to console (recommended).",
    )
    parser.add_argument(
        "--repair-heartbeat-seconds",
        type=int,
        default=15,
        help="Heartbeat interval forwarded to run_agentic_repair_cycle.",
    )
    parser.add_argument(
        "--llm-timeout-seconds",
        type=int,
        default=180,
        help="Timeout per LLM repair call in run_agentic_repair_cycle.",
    )
    parser.add_argument(
        "--dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_true",
        default=True,
        help="Enable dynamic LLM timeout in repair cycle.",
    )
    parser.add_argument(
        "--no-dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_false",
        help="Disable dynamic LLM timeout in repair cycle.",
    )
    parser.add_argument(
        "--dynamic-timeout-base-seconds",
        type=int,
        default=45,
        help="Dynamic timeout base seconds (base + per_line * lines).",
    )
    parser.add_argument(
        "--dynamic-timeout-per-line-seconds",
        type=int,
        default=3,
        help="Dynamic timeout per file line.",
    )
    parser.add_argument(
        "--dynamic-timeout-min-seconds",
        type=int,
        default=60,
        help="Dynamic timeout minimum after clamp.",
    )
    parser.add_argument(
        "--dynamic-timeout-max-seconds",
        type=int,
        default=900,
        help="Dynamic timeout maximum after clamp.",
    )
    parser.add_argument(
        "--failure-context-max-lines",
        type=int,
        default=160,
        help="Maximum number of pytest log lines sent to LLM for each repair.",
    )
    parser.add_argument(
        "--enable-matlab-help",
        action="store_true",
        help='Enable MATLAB help enrichment (matlab -batch "help <fn>") in repair prompts.',
    )
    parser.add_argument(
        "--matlab-help-max-functions",
        type=int,
        default=1,
        help="Maximum MATLAB functions queried per repaired target file.",
    )
    parser.add_argument(
        "--matlab-help-timeout-seconds",
        type=int,
        default=25,
        help="Timeout for each MATLAB help query.",
    )
    parser.add_argument(
        "--parity-candidate-root",
        default=None,
        help="Candidate parity snapshot root produced by python side (optional).",
    )
    parser.add_argument("--disable-llm", action="store_true", help="Never call LLM in repair cycle.")
    parser.add_argument(
        "--output",
        default="../reports/agentic_porting_workflow_report.json",
        help="Output report JSON.",
    )
    args = parser.parse_args()

    if args.one_shot_full:
        args.repair_all_candidates = True
        args.run_all_generated_tests = True
        args.run_all_contract_tests = True
        if args.max_iterations < 8:
            args.max_iterations = 8

    _configure_logging(args.verbose)

    base = Path(__file__).resolve().parent
    repo_root = (base / args.repo_root).resolve()
    output = (base / args.output).resolve()
    reports_dir = (base / "../reports").resolve()

    LOGGER.info("Workflow roots: %s", args.roots)
    LOGGER.info("LLM enabled: %s", not args.disable_llm)
    LOGGER.info("Repair log streaming: %s", args.stream_repair_logs)
    LOGGER.info(
        "Dynamic timeout: %s (base=%s per_line=%s min=%s max=%s)",
        args.dynamic_llm_timeout,
        args.dynamic_timeout_base_seconds,
        args.dynamic_timeout_per_line_seconds,
        args.dynamic_timeout_min_seconds,
        args.dynamic_timeout_max_seconds,
    )
    LOGGER.info(
        "Repair iteration regeneration: force_pipeline=%s overwrite_manual=%s",
        args.repair_force_pipeline,
        args.repair_overwrite_manual,
    )
    if args.one_shot_full:
        LOGGER.info(
            "One-shot full mode enabled: repair_all_candidates=%s run_all_generated_tests=%s run_all_contract_tests=%s max_iterations=%s",
            args.repair_all_candidates,
            args.run_all_generated_tests,
            args.run_all_contract_tests,
            args.max_iterations,
        )

    workflow: dict[str, Any] = {"roots": args.roots}

    pipeline_args = ["--roots", args.roots, "--generate-contract-tests", "--compare-parity-snapshots"]
    if args.force:
        pipeline_args.append("--force")
    if args.skip_tests:
        pipeline_args.append("--skip-tests")
    if args.overwrite_manual:
        pipeline_args.append("--overwrite-manual")
    if args.parity_candidate_root:
        pipeline_args.extend(["--parity-candidate-root", args.parity_candidate_root])
    workflow["pipeline"] = _run(
        "run_porting_pipeline.py",
        pipeline_args,
        repo_root,
        step_name="pipeline",
        stream_output=False,
        verbose=args.verbose,
    )

    roots_for_scripts = ",".join(f"../../{token.strip()}" for token in args.roots.split(",") if token.strip())
    workflow["auto_fix_missing_imports"] = _run(
        "auto_fix_missing_imports.py",
        ["--roots", roots_for_scripts, "--apply", "--summary-only"],
        repo_root,
        step_name="auto_fix_missing_imports",
        stream_output=False,
        verbose=args.verbose,
    )
    workflow["analyze_generated_files"] = _run(
        "analyze_generated_files.py",
        ["--roots", roots_for_scripts],
        repo_root,
        step_name="analyze_generated_files",
        stream_output=False,
        verbose=args.verbose,
    )
    workflow["build_agent_context"] = _run(
        "build_agent_context.py",
        [],
        repo_root,
        step_name="build_agent_context",
        stream_output=False,
        verbose=args.verbose,
    )

    analysis_report = _load_report(reports_dir / "generated_files_analysis.json")
    parity_snapshot_report = _load_report(reports_dir / "parity_snapshot_comparison.json")
    todo_count = int(analysis_report.get("summary", {}).get("matlab_todo_markers", 0) or 0)
    parity_ok = bool(parity_snapshot_report.get("summary", {}).get("ok", False))
    needs_repair = todo_count > 0 or not parity_ok

    workflow["decision"] = {
        "matlab_todo_markers": todo_count,
        "parity_snapshots_ok": parity_ok,
        "needs_repair_cycle": needs_repair,
    }
    LOGGER.info(
        "Decision: TODO markers=%s | parity_ok=%s | needs_repair=%s",
        todo_count,
        parity_ok,
        needs_repair,
    )

    if needs_repair:
        repair_args = [
            "--roots",
            args.roots,
            "--model",
            args.model,
            "--fallback-model",
            args.fallback_model,
            "--max-iterations",
            str(args.max_iterations),
            "--max-files-per-iteration",
            str(args.max_files_per_iteration),
            "--generated-tests-per-iteration",
            str(args.generated_tests_per_iteration),
            "--contracts-per-iteration",
            str(args.contracts_per_iteration),
            "--max-context-chars",
            str(args.max_context_chars),
            "--llm-timeout-seconds",
            str(args.llm_timeout_seconds),
            "--dynamic-timeout-base-seconds",
            str(args.dynamic_timeout_base_seconds),
            "--dynamic-timeout-per-line-seconds",
            str(args.dynamic_timeout_per_line_seconds),
            "--dynamic-timeout-min-seconds",
            str(args.dynamic_timeout_min_seconds),
            "--dynamic-timeout-max-seconds",
            str(args.dynamic_timeout_max_seconds),
            "--failure-context-max-lines",
            str(args.failure_context_max_lines),
            "--matlab-help-max-functions",
            str(args.matlab_help_max_functions),
            "--matlab-help-timeout-seconds",
            str(args.matlab_help_timeout_seconds),
        ]
        if args.dynamic_llm_timeout:
            repair_args.append("--dynamic-llm-timeout")
        else:
            repair_args.append("--no-dynamic-llm-timeout")
        if args.enable_matlab_help:
            repair_args.append("--enable-matlab-help")
        if args.auto_pull_model:
            repair_args.append("--auto-pull-model")
        else:
            repair_args.append("--no-auto-pull-model")
        if args.repair_force_pipeline:
            repair_args.append("--force-pipeline")
        if args.repair_overwrite_manual:
            repair_args.append("--overwrite-manual")
        if args.repair_all_candidates:
            repair_args.append("--repair-all-candidates")
        if args.run_all_generated_tests:
            repair_args.append("--run-all-generated-tests")
        if args.run_all_contract_tests:
            repair_args.append("--run-all-contract-tests")
        if args.allow_matlab_todos:
            repair_args.append("--allow-matlab-todos")
        if args.disable_llm:
            repair_args.append("--disable-llm")
        if args.stream_repair_logs:
            repair_args.append("--stream-subprocess-logs")
            repair_args.extend(["--heartbeat-seconds", str(args.repair_heartbeat_seconds)])

        workflow["agentic_repair_cycle"] = _run_repair_cycle_with_compat(
            repo_root=repo_root,
            repair_args=repair_args,
            stream_repair_logs=args.stream_repair_logs,
            verbose=args.verbose,
        )
    else:
        workflow["agentic_repair_cycle"] = {"status": "skipped_not_needed"}
        LOGGER.info("Skip agentic_repair_cycle: no blockers detected.")

    failing_steps: list[str] = []
    for step_name in ("pipeline", "auto_fix_missing_imports", "analyze_generated_files", "build_agent_context"):
        step = workflow.get(step_name, {})
        if isinstance(step, dict) and int(step.get("returncode", 0) or 0) != 0:
            failing_steps.append(step_name)
    repair_step = workflow.get("agentic_repair_cycle", {})
    if isinstance(repair_step, dict):
        repair_rc = repair_step.get("returncode")
        if isinstance(repair_rc, int) and repair_rc != 0:
            failing_steps.append("agentic_repair_cycle")
    workflow["status"] = {
        "ok": len(failing_steps) == 0,
        "failing_steps": failing_steps,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    LOGGER.info("Workflow report written: %s", output)
    print(json.dumps(workflow["decision"], indent=2))
    if failing_steps:
        LOGGER.error("Workflow failed; failing steps: %s", ", ".join(failing_steps))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

