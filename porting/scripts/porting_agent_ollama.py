#!/usr/bin/env python3
"""Local Ollama agent orchestrator for the deterministic porting pipeline."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama import ChatOllama


SCRIPT_DIR = Path(__file__).resolve().parent


def _run_python_script(script_name: str, args: list[str]) -> str:
    script = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    payload = {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    return json.dumps(payload, indent=2)


def _load_prompt_file(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return ""


def _run_matlab_help(function_name: str, timeout_seconds: int = 25) -> str:
    cmd = ["matlab", "-batch", f"help {function_name}"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=max(1, timeout_seconds),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return json.dumps(
            {"command": cmd, "returncode": -1, "stdout": "", "stderr": str(exc)},
            indent=2,
        )
    return json.dumps(
        {"command": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr},
        indent=2,
    )


@tool
def search_matlab_files_tool() -> str:
    """List MATLAB files and update hash manifest diff."""
    return _run_python_script(
        "search_matlab.py",
        [
            "--directory",
            "../../src",
            "--hash-manifest",
            "../state/matlab_hashes.json",
            "--write-hashes",
            "../state/matlab_hashes.json",
            "--json",
        ],
    )


@tool
def build_dependency_graph_tool() -> str:
    """Build MATLAB function dependency graph JSON."""
    return _run_python_script(
        "get_function_call_graph.py",
        ["--root", "../../src", "--output", "../../script_outputs/all_files_function_call_graph.json"],
    )


@tool
def select_file_order_tool() -> str:
    """Compute deterministic layered porting order from dependency graph."""
    return _run_python_script(
        "select_file_order.py",
        [
            "--input",
            "../../script_outputs/all_files_function_call_graph.json",
            "--output",
            "../../script_outputs/porting_order.json",
        ],
    )


@tool
def run_porting_compiler(max_files: int = 3) -> str:
    """Run MATLAB->Python incremental compiler.

    Args:
        max_files: Maximum number of changed files to process in this run.
    """
    return _run_python_script("porting_compiler.py", ["--max-files", str(max_files), "--skip-tests"])


@tool
def run_full_porting_pipeline(
    roots: str = "src,demo,tests,third_part",
    max_files: int = 0,
    force: bool = True,
    skip_tests: bool = True,
    generate_contract_tests: bool = True,
    compare_parity_snapshots: bool = True,
    parity_candidate_root: str = "",
) -> str:
    """Run deterministic end-to-end pipeline across selected roots.

    Args:
        roots: Comma-separated roots to process (e.g. "src,demo,tests,third_part").
        max_files: Optional max changed files per root (0 means no limit).
        force: Force regeneration.
        skip_tests: Skip generated pytest during compile phase.
        generate_contract_tests: Generate structural contract tests.
        compare_parity_snapshots: Compare parity snapshots in parity directory.
        parity_candidate_root: Candidate parity snapshot root (optional).
    """
    args = ["--roots", roots]
    if max_files > 0:
        args.extend(["--max-files", str(max_files)])
    if force:
        args.append("--force")
    if skip_tests:
        args.append("--skip-tests")
    if generate_contract_tests:
        args.append("--generate-contract-tests")
    if compare_parity_snapshots:
        args.append("--compare-parity-snapshots")
    if parity_candidate_root.strip():
        args.extend(["--parity-candidate-root", parity_candidate_root.strip()])
    return _run_python_script("run_porting_pipeline.py", args)


@tool
def extract_logic_report(include_python: bool = True) -> str:
    """Extract MATLAB/Python logic blocks into JSON report."""
    args = ["--output", "../reports/extracted_logic.json"]
    if include_python:
        args.append("--include-python")
    return _run_python_script("extract_logic.py", args)


@tool
def compare_logic_report(extracted_logic_path: str = "../reports/extracted_logic.json") -> str:
    """Compare MATLAB and Python logic snapshots.

    Args:
        extracted_logic_path: Path to extracted logic json.
    """
    return _run_python_script("compare_matlab_python_logic.py", [extracted_logic_path])


@tool
def run_parity_report(cases_json: str = "../reports/parity_cases.json") -> str:
    """Run parity metrics on prepared cases and write a JSON report."""
    return _run_python_script(
        "run_parity_case.py",
        ["--cases-json", cases_json, "--output", "../reports/parity_report.json"],
    )


@tool
def compare_parity_snapshots_report(candidate_root: str = "") -> str:
    """Compare parity fingerprints against reference parity snapshots.

    Args:
        candidate_root: Candidate parity root (optional).
    """
    args = ["--reference-root", "../../parity", "--output", "../reports/parity_snapshot_comparison.json"]
    if candidate_root.strip():
        args.extend(["--candidate-root", candidate_root.strip()])
    return _run_python_script("compare_parity_snapshots.py", args)


@tool
def generate_contract_tests_report() -> str:
    """Generate structural contract tests for translated files and report summary."""
    return _run_python_script("generate_contract_tests.py", ["--summary-only"])


@tool
def run_agentic_repair_cycle(
    model: str = "gpt-oss:20b",
    max_iterations: int = 3,
    max_files_per_iteration: int = 5,
    llm_timeout_seconds: int = 180,
    dynamic_llm_timeout: bool = True,
    dynamic_timeout_base_seconds: int = 45,
    dynamic_timeout_per_line_seconds: int = 3,
    dynamic_timeout_min_seconds: int = 60,
    dynamic_timeout_max_seconds: int = 900,
    failure_context_max_lines: int = 160,
    enable_matlab_help: bool = False,
    matlab_help_max_functions: int = 1,
) -> str:
    """Run iterative agentic repair loop: pipeline -> tests -> repair -> retry.

    Args:
        model: Ollama model name.
        max_iterations: Max repair iterations.
        max_files_per_iteration: Max files patched per iteration.
        llm_timeout_seconds: Hard timeout for each LLM repair call.
        failure_context_max_lines: Max pytest lines included in each LLM prompt.
        enable_matlab_help: Enrich repair prompts with matlab help snippets.
        matlab_help_max_functions: Max MATLAB functions queried per target.
    """
    args = [
        "--model",
        model,
        "--max-iterations",
        str(max_iterations),
        "--max-files-per-iteration",
        str(max_files_per_iteration),
        "--llm-timeout-seconds",
        str(llm_timeout_seconds),
        "--dynamic-timeout-base-seconds",
        str(dynamic_timeout_base_seconds),
        "--dynamic-timeout-per-line-seconds",
        str(dynamic_timeout_per_line_seconds),
        "--dynamic-timeout-min-seconds",
        str(dynamic_timeout_min_seconds),
        "--dynamic-timeout-max-seconds",
        str(dynamic_timeout_max_seconds),
        "--failure-context-max-lines",
        str(failure_context_max_lines),
        "--matlab-help-max-functions",
        str(matlab_help_max_functions),
    ]
    if dynamic_llm_timeout:
        args.append("--dynamic-llm-timeout")
    else:
        args.append("--no-dynamic-llm-timeout")
    if enable_matlab_help:
        args.append("--enable-matlab-help")
    args = ["--engine", "legacy", *args]
    return _run_python_script("run_agentic_repair_cycle.py", args)


@tool
def matlab_help_tool(function_name: str, timeout_seconds: int = 25) -> str:
    """Get official MATLAB CLI help text for a function.

    Args:
        function_name: MATLAB function name (e.g. roipoly, padarray).
        timeout_seconds: Timeout for the MATLAB call.
    """
    return _run_matlab_help(function_name=function_name, timeout_seconds=timeout_seconds)


@tool
def cleanup_pipeline_artifacts(
    apply: bool = False,
    clean_cache: bool = True,
    prune_stale_tests: bool = True,
    remove_empty_dirs: bool = True,
) -> str:
    """Cleanup stale pipeline artifacts.

    Args:
        apply: Apply changes, otherwise dry-run.
        clean_cache: Remove __pycache__ and .pytest_cache.
        prune_stale_tests: Remove generated tests pointing to missing target files.
        remove_empty_dirs: Remove empty test directories.
    """
    args: list[str] = []
    if clean_cache:
        args.append("--clean-cache")
    if prune_stale_tests:
        args.append("--prune-stale-tests")
    if remove_empty_dirs:
        args.append("--remove-empty-dirs")
    if apply:
        args.append("--apply")
    args.append("--json")
    return _run_python_script("cleanup_pipeline_artifacts.py", args)


@tool
def ensure_module_entrypoints(
    roots: str = "../../src,../../demo,../../tests,../../third_part",
    apply: bool = True,
) -> str:
    """Add deterministic filename->function export aliases when missing.

    Args:
        roots: Comma-separated roots to scan.
        apply: Apply alias changes.
    """
    args = ["--roots", roots, "--summary-only"]
    if apply:
        args.append("--apply")
    return _run_python_script("ensure_module_entrypoints.py", args)


@tool
def sanitize_optional_imports(
    roots: str = "../../src,../../demo,../../tests,../../third_part",
    apply: bool = True,
) -> str:
    """Rewrite optional imports (e.g. pydicom) to try/except guards.

    Args:
        roots: Comma-separated roots to scan.
        apply: Apply rewrites.
    """
    args = ["--roots", roots, "--summary-only"]
    if apply:
        args.append("--apply")
    return _run_python_script("sanitize_optional_imports.py", args)


@tool
def generate_matlab_native_compat(
    roots: str = "src,demo,tests,third_part",
    apply: bool = True,
) -> str:
    """Generate/update third_part MATLAB native compatibility helpers.

    Args:
        roots: Comma-separated roots scanned for TODO(matlab-*) markers.
        apply: Write compatibility module when True, otherwise dry-run.
    """
    args = ["--roots", roots, "--summary-only"]
    if apply:
        args.append("--apply")
    return _run_python_script("generate_matlab_native_compat.py", args)


@tool
def build_agent_context_report() -> str:
    """Build compact JSON + prompt context from current reports."""
    return _run_python_script("build_agent_context.py", [])


@tool
def generate_porting_prompt(mode: str = "full") -> str:
    """Generate ready-to-paste external agent prompt with compact context.

    Args:
        mode: deterministic | repair | full
    """
    safe_mode = mode if mode in {"deterministic", "repair", "full"} else "full"
    return _run_python_script("get_prompt_for_porting.py", ["--mode", safe_mode])


@tool
def run_agentic_porting_workflow(
    roots: str = "src,demo,tests,third_part",
    model: str = "gpt-oss:20b",
    max_iterations: int = 2,
    max_files_per_iteration: int = 5,
    generated_tests_per_iteration: int = 120,
    contracts_per_iteration: int = 30,
    max_context_chars: int = 6000,
    llm_timeout_seconds: int = 180,
    dynamic_llm_timeout: bool = True,
    dynamic_timeout_base_seconds: int = 45,
    dynamic_timeout_per_line_seconds: int = 3,
    dynamic_timeout_min_seconds: int = 60,
    dynamic_timeout_max_seconds: int = 900,
    failure_context_max_lines: int = 160,
    enable_matlab_help: bool = False,
    matlab_help_max_functions: int = 1,
    disable_llm: bool = False,
) -> str:
    """Run one-command deterministic+agentic workflow.

    Args:
        roots: Comma-separated roots.
        model: Ollama model name.
        max_iterations: Repair cycle max iterations.
        max_files_per_iteration: Repair cycle max file count per iteration.
        generated_tests_per_iteration: Generated tests executed per iteration.
        contracts_per_iteration: Contract tests executed per iteration.
        max_context_chars: Max chars used per context block in repair prompts.
        llm_timeout_seconds: Hard timeout for each LLM repair call.
        failure_context_max_lines: Max pytest lines included in each LLM prompt.
        enable_matlab_help: Enrich repair prompts with matlab help snippets.
        matlab_help_max_functions: Max MATLAB functions queried per target.
        disable_llm: Run deterministic-only workflow.
    """
    args = [
        "--roots",
        roots,
        "--model",
        model,
        "--max-iterations",
        str(max_iterations),
        "--max-files-per-iteration",
        str(max_files_per_iteration),
        "--generated-tests-per-iteration",
        str(generated_tests_per_iteration),
        "--contracts-per-iteration",
        str(contracts_per_iteration),
        "--max-context-chars",
        str(max_context_chars),
        "--llm-timeout-seconds",
        str(llm_timeout_seconds),
        "--dynamic-timeout-base-seconds",
        str(dynamic_timeout_base_seconds),
        "--dynamic-timeout-per-line-seconds",
        str(dynamic_timeout_per_line_seconds),
        "--dynamic-timeout-min-seconds",
        str(dynamic_timeout_min_seconds),
        "--dynamic-timeout-max-seconds",
        str(dynamic_timeout_max_seconds),
        "--failure-context-max-lines",
        str(failure_context_max_lines),
        "--matlab-help-max-functions",
        str(matlab_help_max_functions),
        "--skip-tests",
    ]
    if enable_matlab_help:
        args.append("--enable-matlab-help")
    if dynamic_llm_timeout:
        args.append("--dynamic-llm-timeout")
    else:
        args.append("--no-dynamic-llm-timeout")
    if disable_llm:
        args.append("--disable-llm")
    args = ["--engine", "legacy", *args]
    return _run_python_script("run_agentic_porting_workflow.py", args)


TOOLS = [
    search_matlab_files_tool,
    build_dependency_graph_tool,
    select_file_order_tool,
    run_porting_compiler,
    run_full_porting_pipeline,
    extract_logic_report,
    compare_logic_report,
    run_parity_report,
    compare_parity_snapshots_report,
    generate_contract_tests_report,
    run_agentic_repair_cycle,
    matlab_help_tool,
    cleanup_pipeline_artifacts,
    ensure_module_entrypoints,
    sanitize_optional_imports,
    generate_matlab_native_compat,
    build_agent_context_report,
    generate_porting_prompt,
    run_agentic_porting_workflow,
]


def _tool_dispatch() -> dict[str, Callable[..., str]]:
    return {tool_fn.name: tool_fn for tool_fn in TOOLS}


def run_agent(prompt: str, model: str, max_steps: int) -> dict[str, Any]:
    llm = ChatOllama(model=model, validate_model_on_init=True, temperature=0, streaming=True).bind_tools(TOOLS)
    messages: list[Any] = [HumanMessage(content=prompt)]
    dispatch = _tool_dispatch()

    trace: list[dict[str, Any]] = []
    final_content: str = ""

    for _ in range(max_steps):
        result = llm.invoke(messages)
        if not isinstance(result, AIMessage):
            final_content = str(result)
            break
        messages.append(result)
        final_content = str(result.content)

        tool_calls = result.tool_calls or []
        if not tool_calls:
            break

        for call in tool_calls:
            name = call.get("name")
            call_id = call.get("id")
            args = call.get("args", {}) or {}
            tool_fn = dispatch.get(name)
            if tool_fn is None:
                output = json.dumps({"error": f"Unknown tool: {name}"})
            else:
                try:
                    output = tool_fn.invoke(args)
                except Exception as exc:  # noqa: BLE001
                    output = json.dumps({"error": str(exc)})
            trace.append({"tool": name, "args": args, "output": output})
            messages.append(ToolMessage(content=output, tool_call_id=call_id))

    return {"final_message": final_content, "trace": trace}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local Ollama agent over deterministic porting tools.")
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model name.")
    parser.add_argument("--max-steps", type=int, default=12, help="Max LLM tool-iteration steps.")
    parser.add_argument(
        "--prompt-file",
        default="../prompts/system_agentic_orchestrator_full.md",
        help="Optional prompt preamble file.",
    )
    parser.add_argument(
        "--prompt",
        default=(
            "Run a deterministic full porting cycle, then build compact context and summarize blockers."
        ),
        help="Agent prompt.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    prompt_file = (base / args.prompt_file).resolve()
    preamble = _load_prompt_file(prompt_file)
    full_prompt = args.prompt if not preamble else f"{preamble}\n\nTask:\n{args.prompt}"

    result = run_agent(prompt=full_prompt, model=args.model, max_steps=args.max_steps)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
