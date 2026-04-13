#!/usr/bin/env python3
"""Run an iterative agentic repair cycle for MATLAB->Python porting.

Cycle:
1) Run deterministic pipeline (compile + logic reports)
2) Generate structural contract tests (for functions without MATLAB tests)
3) Run pytest
4) If failing, collect failing targets and ask a local Ollama model to patch files
5) Repeat until success or max iterations
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
import time
import os
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger("agentic_repair_cycle")

try:
    from langchain_ollama import ChatOllama
except Exception:  # noqa: BLE001
    ChatOllama = None  # type: ignore[assignment]


SCRIPT_DIR = Path(__file__).resolve().parent


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)

FAILED_TEST_RE = re.compile(r"^FAILED\s+([^\s:]+\.py)::", re.MULTILINE)
TARGET_FILE_RE = re.compile(
    r'TARGET_FILE\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]\s*/\s*"([^"]+)"'
)
PY_FENCE_RE = re.compile(r"```python\s*(.*?)```", re.DOTALL | re.IGNORECASE)
GENERIC_FENCE_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
TRACEBACK_FILE_RE = re.compile(r'^\s*File "([^"]+\.py)"\s*,\s*line\s+\d+', re.MULTILINE)
PYTEST_PATHLINE_RE = re.compile(
    r"^(?:E\s+)?([A-Za-z]:[\\/][^:\n]+\.py|[A-Za-z0-9_.\\/\-]+\.py):\d+(?::|\s|$)",
    re.MULTILINE,
)

UNICODE_ASCII_REPLACEMENTS = {
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u00D7": "*",
    "\u00F7": "/",
    "\u2018": "'",
    "\u2019": "'",
    "\u201C": '"',
    "\u201D": '"',
}

MATLAB_HELP_CACHE: dict[str, str] = {}


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "elapsed_seconds": self.elapsed_seconds,
        }


def _run_command(
    cmd: list[str],
    cwd: Path,
    *,
    step_name: str,
    heartbeat_seconds: int,
    stream_output: bool,
) -> CommandResult:
    t0 = time.perf_counter()
    logger.info("START %s", step_name)
    logger.info("CMD   %s", " ".join(cmd))

    if stream_output:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        merged_lines: list[str] = []
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip("\n")
            merged_lines.append(line)
            logger.info("[%s] %s", step_name, line)
        returncode = proc.wait()
        stdout_text = ("\n".join(merged_lines) + ("\n" if merged_lines else ""))
        stderr_text = ""
    else:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        while True:
            try:
                stdout_text, stderr_text = proc.communicate(timeout=max(1, heartbeat_seconds))
                break
            except subprocess.TimeoutExpired:
                elapsed = time.perf_counter() - t0
                logger.info("... %s still running (%.1fs)", step_name, elapsed)
        returncode = proc.returncode

    elapsed_s = round(time.perf_counter() - t0, 2)
    if returncode == 0:
        logger.info("DONE  %s (%.2fs)", step_name, elapsed_s)
    else:
        logger.error("FAIL  %s (%.2fs) rc=%s", step_name, elapsed_s, returncode)

    return CommandResult(
        command=cmd,
        returncode=returncode,
        stdout=stdout_text,
        stderr=stderr_text,
        elapsed_seconds=elapsed_s,
    )


def _normalize_model_name(model: str) -> str:
    if not model:
        return model
    normalized = model.strip()

    # Try to recover mojibake text such as "qwen2.5â€‘7bâ€‘coder".
    try:
        normalized = normalized.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Normalize all Unicode dash-like characters to ASCII '-'.
    normalized = "".join("-" if unicodedata.category(ch) == "Pd" else ch for ch in normalized)
    normalized = normalized.replace("\u2212", "-")

    aliases = {
        "qwen2.5-7b-coder": "qwen2.5-coder:7b",
        "qwen2.5-coder-7b": "qwen2.5-coder:7b",
    }
    return aliases.get(normalized, normalized)


def _list_local_ollama_models() -> list[str]:
    try:
        proc = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return []
    if proc.returncode != 0:
        return []

    models: list[str] = []
    lines = [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]
    for line in lines[1:]:
        name = line.split()[0].strip()
        if name:
            models.append(name)
    return models


def _pull_ollama_model(model: str, heartbeat_seconds: int, stream_output: bool) -> bool:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    t0 = time.perf_counter()
    logger.info("START ollama_pull:%s", model)
    logger.info("CMD   ollama pull %s", model)

    if stream_output:
        proc = subprocess.Popen(
            ["ollama", "pull", model],
            cwd=str(SCRIPT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            logger.info("[ollama_pull:%s] %s", model, line.rstrip("\n"))
        returncode = proc.wait()
    else:
        proc = subprocess.Popen(
            ["ollama", "pull", model],
            cwd=str(SCRIPT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        while True:
            try:
                proc.communicate(timeout=max(1, heartbeat_seconds))
                break
            except subprocess.TimeoutExpired:
                logger.info("... ollama_pull:%s still running (%.1fs)", model, time.perf_counter() - t0)
        returncode = proc.returncode

    elapsed_s = round(time.perf_counter() - t0, 2)
    if returncode == 0:
        logger.info("DONE  ollama_pull:%s (%.2fs)", model, elapsed_s)
        return True
    logger.error("FAIL  ollama_pull:%s (%.2fs) rc=%s", model, elapsed_s, returncode)
    return False


def _resolve_model_for_run(
    requested_model: str,
    fallback_model: str,
    auto_pull_model: bool,
    heartbeat_seconds: int,
    stream_subprocess_logs: bool,
) -> dict[str, Any]:
    normalized = _normalize_model_name(requested_model)
    fallback_normalized = _normalize_model_name(fallback_model)
    local_models = _list_local_ollama_models()
    details: dict[str, Any] = {
        "requested_model": requested_model,
        "normalized_model": normalized,
        "fallback_model": fallback_normalized,
        "local_models_before": local_models,
        "auto_pull_model": auto_pull_model,
        "pulled_models": [],
    }

    if normalized in local_models:
        details["selected_model"] = normalized
        details["resolution"] = "requested_available"
        return details

    if auto_pull_model and normalized:
        logger.warning("Model '%s' not found locally. Attempting automatic pull.", normalized)
        if _pull_ollama_model(normalized, heartbeat_seconds, stream_subprocess_logs):
            details["pulled_models"].append(normalized)
            local_after_pull = _list_local_ollama_models()
            details["local_models_after_pull"] = local_after_pull
            if normalized in local_after_pull:
                details["selected_model"] = normalized
                details["resolution"] = "requested_pulled"
                return details

    local_models = _list_local_ollama_models()
    if fallback_normalized in local_models:
        details["selected_model"] = fallback_normalized
        details["resolution"] = "fallback_available"
        details["local_models_after_pull"] = local_models
        return details

    if auto_pull_model and fallback_normalized and fallback_normalized != normalized:
        logger.warning("Fallback model '%s' not found locally. Attempting automatic pull.", fallback_normalized)
        if _pull_ollama_model(fallback_normalized, heartbeat_seconds, stream_subprocess_logs):
            details["pulled_models"].append(fallback_normalized)
            local_after_pull = _list_local_ollama_models()
            details["local_models_after_pull"] = local_after_pull
            if fallback_normalized in local_after_pull:
                details["selected_model"] = fallback_normalized
                details["resolution"] = "fallback_pulled"
                return details

    local_models = _list_local_ollama_models()
    details["local_models_after_pull"] = local_models
    if local_models:
        details["selected_model"] = local_models[0]
        details["resolution"] = "first_local_model_fallback"
        return details

    details["selected_model"] = normalized
    details["resolution"] = "no_local_model_available"
    return details


def _run_script(
    script_name: str,
    args: list[str],
    repo_root: Path,
    *,
    step_name: str,
    heartbeat_seconds: int,
    stream_output: bool,
) -> CommandResult:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    return _run_command(
        cmd,
        cwd=repo_root,
        step_name=step_name,
        heartbeat_seconds=heartbeat_seconds,
        stream_output=stream_output,
    )


def _parse_failed_test_files(pytest_output: str, repo_root: Path) -> list[Path]:
    failed: list[Path] = []
    for m in FAILED_TEST_RE.finditer(pytest_output):
        rel = m.group(1).replace("/", "\\")
        p = (repo_root / rel).resolve()
        if p.exists():
            failed.append(p)
    # keep order, deduplicate
    seen: set[Path] = set()
    out: list[Path] = []
    for f in failed:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _target_from_test_file(test_file: Path) -> Path | None:
    try:
        text = test_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    m = TARGET_FILE_RE.search(text)
    if not m:
        return None
    parent_index = int(m.group(1))
    rel_target = m.group(2).replace("/", "\\")
    try:
        root = test_file.resolve().parents[parent_index]
    except IndexError:
        return None
    target = (root / rel_target).resolve()
    return target if target.exists() else None


def _candidate_files_from_traceback(
    pytest_output: str,
    repo_root: Path,
    excluded_roots: list[Path],
) -> list[Path]:
    candidates: list[Path] = []
    excluded_resolved = [p.resolve() for p in excluded_roots]

    for m in TRACEBACK_FILE_RE.finditer(pytest_output):
        raw = m.group(1).strip().replace("/", "\\")
        path = Path(raw)
        if not path.is_absolute():
            path = (repo_root / raw).resolve()
        else:
            path = path.resolve()

        if not path.exists() or path.suffix.lower() != ".py":
            continue
        if not str(path).startswith(str(repo_root.resolve())):
            continue
        if any(str(path).startswith(str(ex_root)) for ex_root in excluded_resolved):
            continue
        candidates.append(path)

    for m in PYTEST_PATHLINE_RE.finditer(pytest_output):
        raw = m.group(1).strip().replace("/", "\\")
        if not raw.endswith(".py"):
            continue
        path = Path(raw)
        if not path.is_absolute():
            path = (repo_root / raw).resolve()
        else:
            path = path.resolve()
        if not path.exists() or path.suffix.lower() != ".py":
            continue
        if not str(path).startswith(str(repo_root.resolve())):
            continue
        if any(str(path).startswith(str(ex_root)) for ex_root in excluded_resolved):
            continue
        candidates.append(path)

    out: list[Path] = []
    seen: set[Path] = set()
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _select_unique_by_basename(files: list[Path], limit: int) -> list[Path]:
    selected: list[Path] = []
    seen_names: set[str] = set()
    for test_file in files:
        base = test_file.name.lower()
        if base in seen_names:
            continue
        seen_names.add(base)
        selected.append(test_file)
        if len(selected) >= max(0, limit):
            break
    return selected


def _count_basename_collisions(paths: list[str]) -> int:
    by_name: dict[str, int] = defaultdict(int)
    for path in paths:
        by_name[Path(path).name.lower()] += 1
    return sum(1 for count in by_name.values() if count > 1)


def _build_pytest_targets(
    *,
    generated_tests: Path,
    contract_tests: Path,
    run_all_generated_tests: bool,
    generated_tests_per_iteration: int,
    run_all_contract_tests: bool,
    contracts_per_iteration: int,
) -> list[str]:
    pytest_targets: list[str] = []
    if run_all_generated_tests:
        pytest_targets.append(str(generated_tests))
    else:
        generated_files = sorted(generated_tests.rglob("test_*.py"))
        for p in _select_unique_by_basename(generated_files, generated_tests_per_iteration):
            pytest_targets.append(str(p))

    if not pytest_targets:
        pytest_targets.append(str(generated_tests))

    if run_all_contract_tests:
        pytest_targets.append(str(contract_tests))
    else:
        contract_files = sorted(contract_tests.rglob("test_contract_*.py"))
        for p in _select_unique_by_basename(contract_files, contracts_per_iteration):
            pytest_targets.append(str(p))
    return pytest_targets


def _ensure_test_package_markers(*roots: Path) -> dict[str, Any]:
    created: list[str] = []
    scanned_dirs = 0
    for root in roots:
        if not root.exists():
            continue
        candidate_dirs = [root] + [p for p in root.rglob("*") if p.is_dir()]
        for directory in candidate_dirs:
            scanned_dirs += 1
            has_tests = any(directory.glob("test_*.py"))
            if not has_tests:
                continue
            init_file = directory / "__init__.py"
            if init_file.exists():
                continue
            init_file.write_text("", encoding="utf-8")
            created.append(str(init_file))
    return {
        "scanned_dirs": scanned_dirs,
        "created_count": len(created),
        "created": created,
    }


def _candidate_files_from_logic_diff(logic_diff_path: Path, repo_root: Path, limit: int) -> list[Path]:
    if not logic_diff_path.exists():
        return []
    try:
        data = json.loads(logic_diff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    out: list[Path] = []
    for matlab_file in data:
        if not str(matlab_file).endswith(".m"):
            continue
        py_rel = str(matlab_file)[:-2] + ".py"
        py_abs = (repo_root / py_rel).resolve()
        if py_abs.exists():
            out.append(py_abs)
        if len(out) >= limit:
            break
    return out


def _todo_targets_from_analysis(analysis_report_path: Path, repo_root: Path, limit: int) -> list[Path]:
    if not analysis_report_path.exists():
        return []
    try:
        data = json.loads(analysis_report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    sites = data.get("matlab_todo_marker_sites") or []
    out: list[Path] = []
    seen: set[Path] = set()
    for entry in sites:
        if not isinstance(entry, str):
            continue
        rel = entry.split(":", 1)[0].strip().replace("/", "\\")
        candidate = (repo_root / rel).resolve()
        if candidate.exists() and candidate not in seen:
            seen.add(candidate)
            out.append(candidate)
        if len(out) >= limit:
            break
    return out


def _sanitize_tag(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip("/\\"))


def _root_token_to_report_tag(root_token: str) -> str:
    return _sanitize_tag(root_token)


def _load_porting_order_rank(repo_root: Path, roots_tokens: list[str]) -> dict[str, int]:
    """Load deterministic dependency order rank by python basename."""
    rank: dict[str, int] = {}
    next_rank = 0
    for token in roots_tokens:
        tag = _root_token_to_report_tag(token)
        order_path = repo_root / "porting" / "reports" / "roots" / tag / "porting_order.json"
        if not order_path.exists():
            continue
        try:
            data = json.loads(order_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        for layer in data:
            if not isinstance(layer, list):
                continue
            for item in layer:
                if not isinstance(item, str):
                    continue
                py_name = Path(item).with_suffix(".py").name.lower()
                if py_name not in rank:
                    rank[py_name] = next_rank
                    next_rank += 1
    return rank


def _sort_candidate_targets_by_rank(targets: list[Path], rank: dict[str, int]) -> list[Path]:
    if not targets:
        return targets
    if not rank:
        return targets
    indexed = list(enumerate(targets))
    indexed.sort(key=lambda t: (rank.get(t[1].name.lower(), 10**9), t[0]))
    return [item[1] for item in indexed]


def _normalize_unicode_ascii(text: str) -> str:
    if not text:
        return text
    for bad, good in UNICODE_ASCII_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text


def _file_complexity(path: Path) -> tuple[int, int]:
    """Return ``(n_lines, n_todos)`` for *path*.

    ``n_todos`` counts ``TODO(matlab`` occurrences, which is the primary driver
    of LLM inference time: each TODO requires the model to reason about a
    MATLAB→Python translation, making output length grow super-linearly with
    the number of unresolved markers.
    """
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 1, 0
    n_lines = source.count("\n") + 1
    n_todos = source.count("TODO(matlab")
    return n_lines, n_todos


def _line_count(path: Path) -> int:
    return _file_complexity(path)[0]


def _effective_llm_timeout_seconds(
    *,
    target_py: Path,
    fallback_timeout: int,
    dynamic_enabled: bool,
    base_seconds: int,
    per_line_seconds: int,
    min_seconds: int,
    max_seconds: int,
) -> int:
    """Compute a per-file LLM timeout that accounts for both length and TODO complexity.

    Formula::

        timeout = base
                + per_line  * n_lines               # output ∝ file length
                + per_line  * TODO_WEIGHT * n_todos  # each TODO ≈ 10 regular lines

    The ``TODO_WEIGHT`` multiplier captures the super-linear cost: a TODO marker
    forces the model to translate a MATLAB call, which requires far more reasoning
    than copying a plain Python line.  Empirically, a 200-line file with 20 TODOs
    ran for ~15 min on gpt-oss:20b; this formula targets that upper end.
    """
    if not dynamic_enabled:
        return max(1, fallback_timeout)

    TODO_WEIGHT = 10  # each TODO marker treated as ~10 plain lines of output cost
    n_lines, n_todos = _file_complexity(target_py)
    computed = int(base_seconds + per_line_seconds * (n_lines + TODO_WEIGHT * n_todos))
    if fallback_timeout > 0:
        computed = max(computed, int(fallback_timeout))
    computed = max(int(min_seconds), computed)
    if max_seconds > 0:
        computed = min(int(max_seconds), computed)
    return max(1, computed)


def _truncate_middle(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    head = max_chars // 2
    tail = max_chars - head
    return text[:head] + "\n# ... truncated ...\n" + text[-tail:]


def _trim_failure_context(pytest_text: str, max_chars: int, max_lines: int) -> str:
    lines = pytest_text.splitlines()
    if max_lines > 0 and len(lines) > max_lines:
        lines = lines[-max_lines:]
    text = "\n".join(lines)
    if max_chars > 0 and len(text) > max_chars:
        text = text[-max_chars:]
    return text


def _extract_matlab_function_names_from_todos(source: str, limit: int) -> list[str]:
    if not source or limit <= 0:
        return []
    names: list[str] = []
    seen: set[str] = set()
    matlab_keywords = {
        "if",
        "for",
        "while",
        "switch",
        "case",
        "otherwise",
        "end",
        "function",
        "classdef",
        "try",
        "catch",
        "disp",
    }
    for line in source.splitlines():
        if "TODO(matlab" not in line:
            continue
        for match in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*)\s*\(", line):
            fn = match.group(1)
            if fn.lower() in matlab_keywords:
                continue
            if fn not in seen:
                seen.add(fn)
                names.append(fn)
            if len(names) >= limit:
                return names
    return names


def _query_matlab_help(function_name: str, timeout_seconds: int) -> str:
    if function_name in MATLAB_HELP_CACHE:
        return MATLAB_HELP_CACHE[function_name]
    try:
        proc = subprocess.run(
            ["matlab", "-batch", f"help {function_name}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=max(1, timeout_seconds),
        )
    except (OSError, subprocess.TimeoutExpired):
        MATLAB_HELP_CACHE[function_name] = ""
        return ""
    help_text = (proc.stdout or "").strip()
    MATLAB_HELP_CACHE[function_name] = help_text if proc.returncode == 0 else ""
    return MATLAB_HELP_CACHE[function_name]


def _build_matlab_help_context(
    python_source: str,
    *,
    enabled: bool,
    max_functions: int,
    timeout_seconds: int,
    max_chars: int,
) -> str:
    if not enabled or max_functions <= 0:
        return ""
    function_names = _extract_matlab_function_names_from_todos(python_source, max_functions)
    if not function_names:
        return ""
    chunks: list[str] = []
    for fn in function_names:
        text = _query_matlab_help(fn, timeout_seconds)
        if not text:
            continue
        chunks.append(f"[{fn}]\n{_truncate_middle(text, max_chars)}")
    return "\n\n".join(chunks)


def _deterministic_sanitize_file(target_py: Path) -> dict[str, Any]:
    original = target_py.read_text(encoding="utf-8", errors="ignore")
    cleaned = _normalize_unicode_ascii(original)
    if cleaned == original:
        return {"target": str(target_py), "applied": False, "reason": "sanitize_no_change"}
    try:
        compile(cleaned, str(target_py), "exec")
    except SyntaxError as exc:
        return {"target": str(target_py), "applied": False, "reason": f"sanitize_not_compilable: {exc}"}
    target_py.write_text(cleaned + ("\n" if not cleaned.endswith("\n") else ""), encoding="utf-8")
    return {"target": str(target_py), "applied": True, "reason": "patched_by_sanitize_unicode"}


def _sanitize_unicode_in_roots(repo_root: Path, roots_tokens: list[str]) -> dict[str, Any]:
    scanned = 0
    changed: list[str] = []
    skipped_syntax_error: list[str] = []
    for token in roots_tokens:
        root = (repo_root / token).resolve()
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            scanned += 1
            original = py_file.read_text(encoding="utf-8", errors="ignore")
            cleaned = _normalize_unicode_ascii(original)
            if cleaned == original:
                continue
            try:
                compile(cleaned, str(py_file), "exec")
            except SyntaxError:
                skipped_syntax_error.append(str(py_file))
                continue
            py_file.write_text(cleaned + ("\n" if not cleaned.endswith("\n") else ""), encoding="utf-8")
            changed.append(str(py_file))
    return {
        "scanned_py_files": scanned,
        "changed_files": len(changed),
        "changed_paths": changed,
        "skipped_syntax_error_files": skipped_syntax_error,
    }


def _extract_python_code(response_text: str) -> str:
    fence = PY_FENCE_RE.search(response_text)
    if fence:
        return fence.group(1).strip()
    text = response_text.strip()
    if not text:
        return text
    lines = text.splitlines()
    starts = (
        '"""',
        "'''",
        "from ",
        "import ",
        "def ",
        "class ",
        "#!",
        "#",
        "@",
    )
    for idx, line in enumerate(lines):
        if line.lstrip().startswith(starts):
            candidate = "\n".join(lines[idx:]).strip()
            if candidate:
                return candidate
    # fallback: accept raw output as code
    return text


def _strip_outer_quotes(text: str) -> str:
    s = text.strip()
    if len(s) >= 6 and ((s.startswith('"""') and s.endswith('"""')) or (s.startswith("'''") and s.endswith("'''"))):
        return s[3:-3].strip()
    if len(s) >= 2 and ((s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'"))):
        return s[1:-1].strip()
    return s


def _ascii_preview(text: str, max_chars: int = 180) -> str:
    preview = text[:max_chars].replace("\r", " ").replace("\n", "\\n")
    return preview.encode("ascii", errors="replace").decode("ascii")


def _candidate_code_variants(raw_content: str) -> list[str]:
    content = raw_content.strip()
    if not content:
        return []
    # Drop common thinking tags/wrappers.
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    lines = [ln for ln in content.splitlines() if not ln.strip().lower().startswith("thinking...")]
    content = "\n".join(lines).strip()

    variants: list[str] = []
    seen: set[str] = set()

    def add_variant(candidate: str) -> None:
        c = candidate.strip()
        if not c:
            return
        if c not in seen:
            seen.add(c)
            variants.append(c)

    # Prefer fenced code blocks.
    for m in GENERIC_FENCE_RE.finditer(content):
        add_variant(m.group(1))

    add_variant(_extract_python_code(content))
    add_variant(_strip_outer_quotes(content))

    start_re = re.compile(r"^\s*(?:from\s+\S+\s+import|import\s+\S+|def\s+\w+\s*\(|class\s+\w+\s*[:(]|@|#|\"\"\"|''')", re.MULTILINE)
    for m in start_re.finditer(content):
        add_variant(content[m.start():])

    return variants


def _build_project_imports_context(
    target_py: Path,
    repo_root: Path,
    *,
    max_items: int = 20,
    max_chars: int = 1500,
) -> str:
    """Return import hints for project-local functions called in *target_py*.

    MATLAB convention is one function per file, so for every name called in the
    target we check whether ``<name>.py`` exists somewhere under *repo_root*.
    If it does, we emit the correct ``from <module> import <name>`` statement
    so the LLM knows to import rather than reimplement it.
    """
    try:
        target_source = target_py.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""

    # Collect all function-call-like names from the target file (fast regex).
    called_names: set[str] = set(re.findall(r"\b([A-Za-z][A-Za-z0-9_]*)\s*\(", target_source))

    # Remove built-ins, keywords, common stdlib/numpy names, and the file's own stem.
    _SKIP = {
        "def", "if", "for", "while", "class", "print", "len", "range", "int", "str",
        "float", "list", "dict", "set", "tuple", "bool", "zip", "map", "filter",
        "enumerate", "sorted", "reversed", "isinstance", "hasattr", "getattr", "setattr",
        "super", "type", "open", "min", "max", "sum", "abs", "round", "format",
        "np", "numpy", "scipy", "plt", "os", "sys", "re", "json", "math",
        "NotImplementedError", "ValueError", "TypeError", "RuntimeError",
    }
    called_names -= _SKIP
    called_names.discard(target_py.stem)

    if not called_names:
        return ""

    import_hints: list[str] = []
    seen: set[str] = set()
    repo_root_resolved = repo_root.resolve()

    for name in sorted(called_names):
        if name in seen or len(import_hints) >= max_items:
            break
        # Look for <name>.py anywhere under repo_root (excluding the target itself).
        for match in repo_root_resolved.rglob(f"{name}.py"):
            if match.resolve() == target_py.resolve():
                continue
            try:
                rel = match.resolve().relative_to(repo_root_resolved)
            except ValueError:
                continue
            module_path = ".".join(rel.with_suffix("").parts)
            import_hints.append(f"  from {module_path} import {name}")
            seen.add(name)
            break  # first match is sufficient

    if not import_hints:
        return ""

    lines = ["Project functions already ported — IMPORT them, do NOT redefine them inline:"] + import_hints
    result = "\n".join(lines)
    return result[:max_chars] if len(result) > max_chars else result


def _matlab_peer_for_python(py_file: Path, src_root: Path) -> Path | None:
    try:
        rel = py_file.relative_to(src_root)
    except ValueError:
        return None
    m_file = src_root / rel.with_suffix(".m")
    return m_file if m_file.exists() else None


def _repair_prompt(
    target_py: Path,
    matlab_source: str,
    python_source: str,
    failure_context: str,
    matlab_help_context: str,
    project_imports_context: str = "",
) -> str:
    matlab_help_section = f"\nMATLAB help snippets:\n{matlab_help_context}\n" if matlab_help_context else ""
    project_imports_section = (
        f"\n{project_imports_context}\n"
        if project_imports_context
        else ""
    )
    return f"""You are repairing a MATLAB-to-Python translated scientific function.

Rules:
- Output ONLY Python code for this exact file (no markdown, no explanations).
- Do NOT output analysis/thoughts/plans; only the final file content.
- Keep the same function name and argument list as currently in the Python file.
- Keep NumPy style and avoid placeholders like TODO/NotImplemented.
- Must compile on Python 3.13.
- Prefer small, safe fixes focused on failing tests/error context.
- CRITICAL: If a function is listed in "Project functions already ported" below, write an import statement for it — do NOT copy-paste or redefine its body in this file.
{project_imports_section}
Target file:
{target_py}

Failure context (latest):
{failure_context}

Current Python code:
{python_source}

MATLAB reference:
{matlab_source}
{matlab_help_section}
"""


def _is_nontrivial_matlab_source(matlab_source: str) -> bool:
    code_lines = [
        line
        for line in matlab_source.splitlines()
        if line.strip() and not line.strip().startswith("%")
    ]
    return len(code_lines) >= 25


def _looks_like_placeholder_output(candidate_code: str) -> bool:
    low = candidate_code.lower()
    if "placeholder function" in low or "not yet implemented" in low:
        return True
    if "todo(" in low or "notimplementederror" in low:
        return True
    non_empty = [line for line in candidate_code.splitlines() if line.strip()]
    if any(re.search(r"^\s*return\s+none\s*$", line, flags=re.IGNORECASE) for line in non_empty):
        has_real_ops = any(
            tok in low
            for tok in ("for ", "while ", "if ", "np.", "numpy.", "scipy.", "h5py.", "xml.")
        )
        if not has_real_ops and len(non_empty) <= 30:
            return True
    return False


def _has_expected_entrypoint(candidate_code: str, expected_name: str) -> bool:
    if not expected_name:
        return True
    if re.search(rf"^\s*def\s+{re.escape(expected_name)}\s*\(", candidate_code, flags=re.MULTILINE):
        return True
    if re.search(rf"^\s*class\s+{re.escape(expected_name)}\b", candidate_code, flags=re.MULTILINE):
        return True
    if re.search(rf"^\s*{re.escape(expected_name)}\s*=", candidate_code, flags=re.MULTILINE):
        return True
    return False


def _try_repair_file_with_llm(
    *,
    model: str,
    target_py: Path,
    src_root: Path,
    repo_root: Path,
    failure_context: str,
    max_context_chars: int,
    llm_timeout_seconds: int,
    enable_matlab_help: bool,
    matlab_help_max_functions: int,
    matlab_help_timeout_seconds: int,
) -> dict[str, Any]:
    matlab_peer = _matlab_peer_for_python(target_py, src_root)
    full_matlab_source = ""
    if matlab_peer is not None:
        full_matlab_source = matlab_peer.read_text(encoding="ISO-8859-1", errors="ignore")
    python_source = target_py.read_text(encoding="utf-8", errors="ignore")

    # Keep prompt bounded.
    matlab_source = _truncate_middle(full_matlab_source, max_context_chars)
    python_source = _truncate_middle(python_source, max_context_chars)
    if len(failure_context) > max_context_chars:
        failure_context = failure_context[-max_context_chars:]

    matlab_help_context = _build_matlab_help_context(
        python_source,
        enabled=enable_matlab_help,
        max_functions=matlab_help_max_functions,
        timeout_seconds=matlab_help_timeout_seconds,
        max_chars=max_context_chars // 2 if max_context_chars > 0 else 2000,
    )
    project_imports_context = _build_project_imports_context(
        target_py,
        repo_root,
        max_items=20,
        max_chars=max_context_chars // 3 if max_context_chars > 0 else 1500,
    )
    prompt = _repair_prompt(
        target_py=target_py,
        matlab_source=matlab_source,
        python_source=python_source,
        failure_context=failure_context,
        matlab_help_context=matlab_help_context,
        project_imports_context=project_imports_context,
    )

    llm_started = time.perf_counter()
    try:
        cli = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=max(1, llm_timeout_seconds),
        )
        if cli.returncode != 0:
            return {
                "target": str(target_py),
                "applied": False,
                "reason": f"llm_cli_error: rc={cli.returncode}",
                "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
            }
        content = (cli.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return {
            "target": str(target_py),
            "applied": False,
            "reason": f"llm_timeout: {llm_timeout_seconds}s",
            "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
        }
    except OSError:
        if ChatOllama is None:
            return {
                "target": str(target_py),
                "applied": False,
                "reason": "ollama_cli_unavailable_and_langchain_missing",
                "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
            }
        try:
            llm = ChatOllama(model=model, validate_model_on_init=True, temperature=0)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(llm.invoke, prompt)
                result = future.result(timeout=max(1, llm_timeout_seconds))
        except concurrent.futures.TimeoutError:
            return {
                "target": str(target_py),
                "applied": False,
                "reason": f"llm_timeout: {llm_timeout_seconds}s",
                "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM Repair Error for %s: %s", target_py, exc)
            return {
                "target": str(target_py),
                "applied": False,
                "reason": f"llm_invoke_error: {exc}",
                "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
            }
        content_obj = getattr(result, "content", result)
        if isinstance(content_obj, list):
            parts: list[str] = []
            for item in content_obj:
                if isinstance(item, dict):
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            content = "\n".join(parts).strip()
        else:
            content = str(content_obj).strip()

    candidate_code = ""
    last_syntax_error = ""
    for variant in _candidate_code_variants(content):
        normalized = _normalize_unicode_ascii(variant)
        if not normalized:
            continue
        try:
            compile(normalized, str(target_py), "exec")
            candidate_code = normalized
            break
        except SyntaxError as exc:
            last_syntax_error = str(exc)
            continue

    if not candidate_code:
        return {
            "target": str(target_py),
            "applied": False,
            "reason": (
                f"candidate_syntax_error: {last_syntax_error} | preview={_ascii_preview(content)}"
                if last_syntax_error
                else "empty_model_output"
            ),
            "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
        }

    if _is_nontrivial_matlab_source(full_matlab_source) and _looks_like_placeholder_output(candidate_code):
        return {
            "target": str(target_py),
            "applied": False,
            "reason": "candidate_rejected_placeholder",
            "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
        }

    expected_name = target_py.stem
    if (
        matlab_peer is not None
        and expected_name != "__init__"
        and not _has_expected_entrypoint(candidate_code, expected_name)
    ):
        return {
            "target": str(target_py),
            "applied": False,
            "reason": f"candidate_missing_entrypoint:{expected_name}",
            "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
        }

    old = target_py.read_text(encoding="utf-8", errors="ignore")
    if old.strip() == candidate_code.strip():
        return {
            "target": str(target_py),
            "applied": False,
            "reason": "no_change",
            "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
        }

    target_py.write_text(candidate_code + "\n", encoding="utf-8")
    return {
        "target": str(target_py),
        "applied": True,
        "reason": "patched_by_llm",
        "llm_elapsed_seconds": round(time.perf_counter() - llm_started, 2),
    }


def run_cycle(
    *,
    repo_root: Path,
    src_root: Path,
    roots: str,
    model: str,
    secondary_model: str,
    max_iterations: int,
    max_files_per_iteration: int,
    repair_all_candidates: bool,
    max_context_chars: int,
    dynamic_llm_timeout: bool,
    dynamic_timeout_base_seconds: int,
    dynamic_timeout_per_line_seconds: int,
    dynamic_timeout_min_seconds: int,
    dynamic_timeout_max_seconds: int,
    force_pipeline: bool,
    overwrite_manual: bool,
    generated_tests_per_iteration: int,
    run_all_generated_tests: bool,
    contracts_per_iteration: int,
    run_all_contract_tests: bool,
    disable_llm: bool,
    disable_import_autofix: bool,
    allow_matlab_todos: bool,
    verbose: bool,
    heartbeat_seconds: int,
    stream_subprocess_logs: bool,
    llm_timeout_seconds: int,
    failure_context_max_lines: int,
    enable_matlab_help: bool,
    matlab_help_max_functions: int,
    matlab_help_timeout_seconds: int,
) -> dict[str, Any]:
    reports_dir = repo_root / "porting" / "reports"
    generated_tests = repo_root / "porting" / "tests" / "generated"
    contract_tests = repo_root / "porting" / "tests" / "contracts"
    roots_tokens = [token.strip() for token in roots.split(",") if token.strip()]
    analysis_roots_tokens = list(roots_tokens) if roots_tokens else ["src"]
    if "third_part" not in analysis_roots_tokens:
        analysis_roots_tokens.append("third_part")
    analysis_roots_arg = ",".join(f"../../{token}" for token in analysis_roots_tokens)

    iterations: list[dict[str, Any]] = []
    finished_reason = "max_iterations_reached"

    for iteration in range(1, max_iterations + 1):
        step: dict[str, Any] = {"iteration": iteration}
        logger.info("=== Iteration %s/%s ===", iteration, max_iterations)
        if verbose:
            logger.debug("Iteration config: roots=%s model=%s", roots, model)

        pipeline_args = ["--skip-tests", "--generate-contract-tests"]
        pipeline_args.extend(["--roots", roots])
        if force_pipeline:
            pipeline_args.append("--force")
        if overwrite_manual:
            pipeline_args.append("--overwrite-manual")
        pipeline_run = _run_script(
            "run_porting_pipeline.py",
            pipeline_args,
            repo_root,
            step_name=f"iteration_{iteration}:pipeline",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["pipeline"] = pipeline_run.to_dict()
        if pipeline_run.returncode != 0:
            logger.warning("Pipeline step returned non-zero rc=%s", pipeline_run.returncode)

        native_compat_run = _run_script(
            "generate_matlab_native_compat.py",
            ["--roots", roots, "--apply", "--summary-only"],
            repo_root,
            step_name=f"iteration_{iteration}:generate_matlab_native_compat",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["generate_matlab_native_compat"] = native_compat_run.to_dict()
        try:
            step["generate_matlab_native_compat_summary"] = json.loads(native_compat_run.stdout or "{}")
        except json.JSONDecodeError:
            step["generate_matlab_native_compat_summary"] = {}

        entrypoint_alias_run = _run_script(
            "ensure_module_entrypoints.py",
            ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
            repo_root,
            step_name=f"iteration_{iteration}:ensure_module_entrypoints",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["ensure_module_entrypoints"] = entrypoint_alias_run.to_dict()
        try:
            step["ensure_module_entrypoints_summary"] = json.loads(entrypoint_alias_run.stdout or "{}")
        except json.JSONDecodeError:
            step["ensure_module_entrypoints_summary"] = {}
        logger.info(
            "Entrypoint aliases changed: %s",
            int((step["ensure_module_entrypoints_summary"] or {}).get("aliases_changed", 0) or 0),
        )

        optional_imports_run = _run_script(
            "sanitize_optional_imports.py",
            ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
            repo_root,
            step_name=f"iteration_{iteration}:sanitize_optional_imports",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["sanitize_optional_imports"] = optional_imports_run.to_dict()
        try:
            step["sanitize_optional_imports_summary"] = json.loads(optional_imports_run.stdout or "{}")
        except json.JSONDecodeError:
            step["sanitize_optional_imports_summary"] = {}
        logger.info(
            "Optional imports changed: %s",
            int((step["sanitize_optional_imports_summary"] or {}).get("optional_imports_changed", 0) or 0),
        )

        if not disable_import_autofix:
            import_fix_run = _run_script(
                "auto_fix_missing_imports.py",
                ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
                repo_root,
                step_name=f"iteration_{iteration}:auto_fix_missing_imports",
                heartbeat_seconds=heartbeat_seconds,
                stream_output=stream_subprocess_logs,
            )
            step["auto_fix_missing_imports"] = import_fix_run.to_dict()
            try:
                step["auto_fix_missing_imports_summary"] = json.loads(import_fix_run.stdout or "{}")
            except json.JSONDecodeError:
                step["auto_fix_missing_imports_summary"] = {}
            changed = int(step["auto_fix_missing_imports_summary"].get("files_changed", 0) or 0)
            logger.info("Auto-fix imports changed files: %s", changed)

        unicode_sanitize_summary = _sanitize_unicode_in_roots(repo_root, roots_tokens)
        step["sanitize_unicode_summary"] = unicode_sanitize_summary
        logger.info(
            "Unicode sanitize: scanned=%s changed=%s skipped=%s",
            unicode_sanitize_summary.get("scanned_py_files", 0),
            unicode_sanitize_summary.get("changed_files", 0),
            len(unicode_sanitize_summary.get("skipped_syntax_error_files", [])),
        )

        analysis_run = _run_script(
            "analyze_generated_files.py",
            ["--roots", analysis_roots_arg],
            repo_root,
            step_name=f"iteration_{iteration}:analyze_generated_files",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["analyze_generated_files"] = analysis_run.to_dict()
        analysis_report_path = repo_root / "porting" / "reports" / "generated_files_analysis.json"
        analysis_summary: dict[str, Any] = {}
        if analysis_report_path.exists():
            try:
                analysis_summary = json.loads(analysis_report_path.read_text(encoding="utf-8")).get("summary", {})
            except json.JSONDecodeError:
                analysis_summary = {}
        step["analysis_summary"] = analysis_summary
        porting_order_rank = _load_porting_order_rank(repo_root, roots_tokens)
        step["porting_order_rank_count"] = len(porting_order_rank)
        logger.info(
            "Analysis summary: python_files=%s todo_markers=%s fallback_stubs=%s",
            analysis_summary.get("python_files", 0),
            analysis_summary.get("matlab_todo_markers", 0),
            analysis_summary.get("fallback_stub_files", 0),
        )

        cleanup_run = _run_script(
            "cleanup_pipeline_artifacts.py",
            ["--apply", "--clean-cache", "--prune-stale-tests", "--remove-empty-dirs", "--json"],
            repo_root,
            step_name=f"iteration_{iteration}:cleanup_pipeline_artifacts",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["cleanup_pipeline_artifacts"] = cleanup_run.to_dict()
        try:
            step["cleanup_pipeline_artifacts_summary"] = json.loads(cleanup_run.stdout or "{}")
        except json.JSONDecodeError:
            step["cleanup_pipeline_artifacts_summary"] = {}

        test_packaging = _ensure_test_package_markers(generated_tests, contract_tests)
        step["ensure_test_package_markers"] = test_packaging
        logger.info(
            "Prepared test packages: created __init__.py files=%s",
            test_packaging.get("created_count", 0),
        )

        pytest_targets = _build_pytest_targets(
            generated_tests=generated_tests,
            contract_tests=contract_tests,
            run_all_generated_tests=run_all_generated_tests,
            generated_tests_per_iteration=generated_tests_per_iteration,
            run_all_contract_tests=run_all_contract_tests,
            contracts_per_iteration=contracts_per_iteration,
        )

        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--import-mode=importlib",
            "-p",
            "no:cacheprovider",
            *pytest_targets,
            "-q",
            "--maxfail=50",
        ]
        collisions = _count_basename_collisions(pytest_targets)
        step["pytest_basename_collisions"] = collisions
        if collisions:
            logger.warning("Pytest target basename collisions detected: %s", collisions)
        logger.info("Running pytest on %s targets", len(pytest_targets))
        pytest_run = _run_command(
            pytest_cmd,
            cwd=repo_root,
            step_name=f"iteration_{iteration}:pytest",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        step["pytest"] = pytest_run.to_dict()
        step["pytest_target_count"] = len(pytest_targets)
        logger.info("Pytest return code: %s", pytest_run.returncode)

        todo_count = int(analysis_summary.get("matlab_todo_markers", 0) or 0)
        if pytest_run.returncode == 0 and (allow_matlab_todos or todo_count == 0):
            finished_reason = "all_tests_passed"
            logger.info("Stopping: all tests passed and TODO policy satisfied.")
            iterations.append(step)
            break

        pytest_text = f"{pytest_run.stdout}\n{pytest_run.stderr}"
        failed_tests = _parse_failed_test_files(pytest_text, repo_root)
        candidate_targets: list[Path] = []
        traceback_targets = _candidate_files_from_traceback(
            pytest_output=pytest_text,
            repo_root=repo_root,
            excluded_roots=[generated_tests, contract_tests],
        )
        candidate_targets.extend(traceback_targets)
        for test_file in failed_tests:
            target = _target_from_test_file(test_file)
            if target is not None:
                candidate_targets.append(target)

        if repair_all_candidates:
            logic_diff_path = reports_dir / "logic_differences.json"
            candidate_targets.extend(
                _candidate_files_from_logic_diff(
                    logic_diff_path=logic_diff_path,
                    repo_root=repo_root,
                    limit=1_000_000,
                )
            )
            candidate_targets.extend(
                _todo_targets_from_analysis(
                    analysis_report_path=analysis_report_path,
                    repo_root=repo_root,
                    limit=1_000_000,
                )
            )
        elif not candidate_targets:
            logic_diff_path = reports_dir / "logic_differences.json"
            candidate_targets = _candidate_files_from_logic_diff(
                logic_diff_path=logic_diff_path,
                repo_root=repo_root,
                limit=max_files_per_iteration,
            )

        # Deduplicate and cap.
        uniq: list[Path] = []
        seen: set[Path] = set()
        for target in candidate_targets:
            if target not in seen:
                seen.add(target)
                uniq.append(target)
        candidate_targets = _sort_candidate_targets_by_rank(uniq, porting_order_rank)
        if not repair_all_candidates and max_files_per_iteration > 0:
            candidate_targets = candidate_targets[:max_files_per_iteration]

        if not candidate_targets:
            todo_limit = 1_000_000 if repair_all_candidates else max_files_per_iteration
            candidate_targets = _todo_targets_from_analysis(
                analysis_report_path=analysis_report_path,
                repo_root=repo_root,
                limit=todo_limit,
            )
            candidate_targets = _sort_candidate_targets_by_rank(candidate_targets, porting_order_rank)
            if not repair_all_candidates and max_files_per_iteration > 0:
                candidate_targets = candidate_targets[:max_files_per_iteration]

        step["candidate_targets"] = [str(p) for p in candidate_targets]

        if not candidate_targets:
            if pytest_run.returncode == 0 and todo_count > 0:
                finished_reason = "tests_passed_but_todos_remain"
            else:
                finished_reason = "no_candidate_targets"
            logger.warning("Stopping: %s", finished_reason)
            iterations.append(step)
            break

        if pytest_run.returncode == 0 and todo_count > 0:
            step["repair_trigger"] = {
                "reason": "matlab_todo_markers_remaining",
                "todo_markers": todo_count,
            }
            logger.info("Repair trigger: TODO markers remain (%s).", todo_count)

        if disable_llm:
            finished_reason = "llm_disabled"
            logger.info("Stopping: LLM disabled.")
            iterations.append(step)
            break

        if ChatOllama is None:
            finished_reason = "langchain_ollama_not_available"
            logger.error("Stopping: langchain_ollama is not available.")
            iterations.append(step)
            break

        repair_results: list[dict[str, Any]] = []
        failure_context = _trim_failure_context(
            pytest_text=pytest_text,
            max_chars=max_context_chars,
            max_lines=failure_context_max_lines,
        )
        for target in candidate_targets:
            target_timeout = _effective_llm_timeout_seconds(
                target_py=target,
                fallback_timeout=llm_timeout_seconds,
                dynamic_enabled=dynamic_llm_timeout,
                base_seconds=dynamic_timeout_base_seconds,
                per_line_seconds=dynamic_timeout_per_line_seconds,
                min_seconds=dynamic_timeout_min_seconds,
                max_seconds=dynamic_timeout_max_seconds,
            )
            logger.info("Attempting LLM repair for target: %s", target)
            logger.info("LLM timeout for %s: %ss", target.name, target_timeout)
            deterministic = _deterministic_sanitize_file(target)
            if deterministic.get("applied"):
                logger.info("Deterministic sanitize applied for %s", target)
                repair_results.append(deterministic)
                continue
            repair = _try_repair_file_with_llm(
                model=model,
                target_py=target,
                src_root=src_root,
                repo_root=repo_root,
                failure_context=failure_context,
                max_context_chars=max_context_chars,
                llm_timeout_seconds=target_timeout,
                enable_matlab_help=enable_matlab_help,
                matlab_help_max_functions=matlab_help_max_functions,
                matlab_help_timeout_seconds=matlab_help_timeout_seconds,
            )
            reason = str(repair.get("reason", ""))
            if (
                not repair.get("applied")
                and secondary_model
                and secondary_model != model
                and (
                    reason.startswith("llm_timeout")
                    or reason.startswith("empty_model_output")
                    or reason.startswith("candidate_syntax_error")
                    or reason.startswith("candidate_missing_entrypoint")
                )
            ):
                logger.info("Retrying target with secondary model: %s", secondary_model)
                retry = _try_repair_file_with_llm(
                    model=secondary_model,
                    target_py=target,
                    src_root=src_root,
                    repo_root=repo_root,
                    failure_context=failure_context,
                    max_context_chars=max_context_chars,
                    llm_timeout_seconds=target_timeout,
                    enable_matlab_help=enable_matlab_help,
                    matlab_help_max_functions=matlab_help_max_functions,
                    matlab_help_timeout_seconds=matlab_help_timeout_seconds,
                )
                retry["retry_from_model"] = model
                repair = retry
            repair_results.append(repair)
            logger.info("Repair result for %s: applied=%s reason=%s", target, repair.get("applied"), repair.get("reason"))
        step["repairs"] = repair_results

        if not any(r.get("applied") for r in repair_results):
            finished_reason = "no_patch_applied"
            logger.warning("Stopping: no patch applied.")
            iterations.append(step)
            break

        # Stabilize deterministic rewrites immediately after LLM patches so that
        # final iterations do not end with easily-fixable import/entrypoint issues.
        post_repair_stabilization: dict[str, Any] = {}
        post_alias_run = _run_script(
            "ensure_module_entrypoints.py",
            ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
            repo_root,
            step_name=f"iteration_{iteration}:post_repair:ensure_module_entrypoints",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        post_repair_stabilization["ensure_module_entrypoints"] = post_alias_run.to_dict()
        try:
            post_repair_stabilization["ensure_module_entrypoints_summary"] = json.loads(post_alias_run.stdout or "{}")
        except json.JSONDecodeError:
            post_repair_stabilization["ensure_module_entrypoints_summary"] = {}

        post_optional_run = _run_script(
            "sanitize_optional_imports.py",
            ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
            repo_root,
            step_name=f"iteration_{iteration}:post_repair:sanitize_optional_imports",
            heartbeat_seconds=heartbeat_seconds,
            stream_output=stream_subprocess_logs,
        )
        post_repair_stabilization["sanitize_optional_imports"] = post_optional_run.to_dict()
        try:
            post_repair_stabilization["sanitize_optional_imports_summary"] = json.loads(post_optional_run.stdout or "{}")
        except json.JSONDecodeError:
            post_repair_stabilization["sanitize_optional_imports_summary"] = {}

        if not disable_import_autofix:
            post_import_fix_run = _run_script(
                "auto_fix_missing_imports.py",
                ["--roots", analysis_roots_arg, "--apply", "--summary-only"],
                repo_root,
                step_name=f"iteration_{iteration}:post_repair:auto_fix_missing_imports",
                heartbeat_seconds=heartbeat_seconds,
                stream_output=stream_subprocess_logs,
            )
            post_repair_stabilization["auto_fix_missing_imports"] = post_import_fix_run.to_dict()
            try:
                post_repair_stabilization["auto_fix_missing_imports_summary"] = json.loads(
                    post_import_fix_run.stdout or "{}"
                )
            except json.JSONDecodeError:
                post_repair_stabilization["auto_fix_missing_imports_summary"] = {}

        post_unicode_summary = _sanitize_unicode_in_roots(repo_root, roots_tokens)
        post_repair_stabilization["sanitize_unicode_summary"] = post_unicode_summary
        step["post_repair_stabilization"] = post_repair_stabilization

        # On final iteration, run a final validation pass after patches.
        if iteration == max_iterations:
            final_analysis_run = _run_script(
                "analyze_generated_files.py",
                ["--roots", analysis_roots_arg],
                repo_root,
                step_name=f"iteration_{iteration}:final_validation:analyze_generated_files",
                heartbeat_seconds=heartbeat_seconds,
                stream_output=stream_subprocess_logs,
            )
            step["final_validation_analyze_generated_files"] = final_analysis_run.to_dict()
            final_analysis_summary: dict[str, Any] = {}
            if analysis_report_path.exists():
                try:
                    final_analysis_summary = json.loads(analysis_report_path.read_text(encoding="utf-8")).get(
                        "summary", {}
                    )
                except json.JSONDecodeError:
                    final_analysis_summary = {}
            step["final_validation_analysis_summary"] = final_analysis_summary

            final_pytest_targets = _build_pytest_targets(
                generated_tests=generated_tests,
                contract_tests=contract_tests,
                run_all_generated_tests=run_all_generated_tests,
                generated_tests_per_iteration=generated_tests_per_iteration,
                run_all_contract_tests=run_all_contract_tests,
                contracts_per_iteration=contracts_per_iteration,
            )
            final_pytest_cmd = [
                sys.executable,
                "-m",
                "pytest",
                "--import-mode=importlib",
                "-p",
                "no:cacheprovider",
                *final_pytest_targets,
                "-q",
                "--maxfail=50",
            ]
            logger.info("Running final validation pytest on %s targets", len(final_pytest_targets))
            final_pytest_run = _run_command(
                final_pytest_cmd,
                cwd=repo_root,
                step_name=f"iteration_{iteration}:final_validation:pytest",
                heartbeat_seconds=heartbeat_seconds,
                stream_output=stream_subprocess_logs,
            )
            step["final_validation_pytest"] = final_pytest_run.to_dict()
            step["final_validation_pytest_target_count"] = len(final_pytest_targets)
            final_todo_count = int(final_analysis_summary.get("matlab_todo_markers", 0) or 0)
            if final_pytest_run.returncode == 0 and (allow_matlab_todos or final_todo_count == 0):
                finished_reason = "all_tests_passed"
                logger.info(
                    "Final validation succeeded: pytest=0 and TODO policy satisfied (todo_markers=%s).",
                    final_todo_count,
                )
                iterations.append(step)
                break

        iterations.append(step)
        logger.info(
            "Iteration %s completed: repairs=%s applied=%s",
            iteration,
            len(repair_results),
            sum(bool(r.get("applied")) for r in repair_results),
        )

    if finished_reason == "max_iterations_reached" and iterations:
        last_step = iterations[-1]
        last_todo = int((last_step.get("analysis_summary") or {}).get("matlab_todo_markers", 0) or 0)
        if last_todo > 0:
            finished_reason = "max_iterations_reached_with_todos"

    summary = {
        "model": model,
        "secondary_model": secondary_model,
        "max_iterations": max_iterations,
        "repair_all_candidates": repair_all_candidates,
        "dynamic_llm_timeout": dynamic_llm_timeout,
        "dynamic_timeout_base_seconds": dynamic_timeout_base_seconds,
        "dynamic_timeout_per_line_seconds": dynamic_timeout_per_line_seconds,
        "dynamic_timeout_min_seconds": dynamic_timeout_min_seconds,
        "dynamic_timeout_max_seconds": dynamic_timeout_max_seconds,
        "iterations_ran": len(iterations),
        "finished_reason": finished_reason,
        "iterations": iterations,
    }
    logger.info("Repair cycle finished: reason=%s iterations=%s", finished_reason, len(iterations))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run iterative agentic repair cycle.")
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--src-root", default="../../src", help="Source root.")
    parser.add_argument(
        "--roots",
        default="src",
        help="Comma-separated roots passed to run_porting_pipeline.py.",
    )
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model name.")
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
        help="Auto-pull missing Ollama model(s).",
    )
    parser.add_argument(
        "--no-auto-pull-model",
        dest="auto_pull_model",
        action="store_false",
        help="Disable auto-pull and use only local models.",
    )
    parser.add_argument("--max-iterations", type=int, default=3, help="Max repair iterations.")
    parser.add_argument(
        "--max-files-per-iteration",
        type=int,
        default=5,
        help="Max candidate files sent to model per iteration.",
    )
    parser.add_argument(
        "--repair-all-candidates",
        action="store_true",
        help="Attempt repair on all detected candidates each iteration (ignores max-files-per-iteration cap).",
    )
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=12000,
        help="Max chars for each context section sent to model.",
    )
    parser.add_argument("--force-pipeline", action="store_true", help="Force file regeneration in each iteration.")
    parser.add_argument("--overwrite-manual", action="store_true", help="Allow pipeline to overwrite manual files.")
    parser.add_argument(
        "--generated-tests-per-iteration",
        type=int,
        default=120,
        help="Number of generated tests to run per iteration (ignored with --run-all-generated-tests).",
    )
    parser.add_argument(
        "--run-all-generated-tests",
        action="store_true",
        help="Run all generated tests each iteration (can be slow).",
    )
    parser.add_argument(
        "--contracts-per-iteration",
        type=int,
        default=30,
        help="Number of contract tests to run per iteration (ignored with --run-all-contract-tests).",
    )
    parser.add_argument(
        "--run-all-contract-tests",
        action="store_true",
        help="Run all generated contract tests each iteration (can be slow).",
    )
    parser.add_argument("--disable-llm", action="store_true", help="Do not call the LLM; run analysis loop only.")
    parser.add_argument(
        "--disable-import-autofix",
        action="store_true",
        help="Skip deterministic missing-import autofix step.",
    )
    parser.add_argument(
        "--allow-matlab-todos",
        action="store_true",
        help="Allow finishing with TODO(matlab-*) markers still present.",
    )
    parser.add_argument(
        "--output",
        default="../reports/agent_repair_cycle_report.json",
        help="Output report JSON path.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=20,
        help="Heartbeat interval for long-running subprocesses.",
    )
    parser.add_argument(
        "--stream-subprocess-logs",
        action="store_true",
        help="Stream stdout of child scripts/pytest live to console.",
    )
    parser.add_argument(
        "--llm-timeout-seconds",
        type=int,
        default=180,
        help="Hard timeout for each LLM repair invocation.",
    )
    parser.add_argument(
        "--dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_true",
        default=True,
        help="Enable dynamic LLM timeout based on file line count.",
    )
    parser.add_argument(
        "--no-dynamic-llm-timeout",
        dest="dynamic_llm_timeout",
        action="store_false",
        help="Disable dynamic LLM timeout and use fixed --llm-timeout-seconds.",
    )
    parser.add_argument(
        "--dynamic-timeout-base-seconds",
        type=int,
        default=45,
        help="Dynamic timeout base seconds (formula: base + per_line * line_count).",
    )
    parser.add_argument(
        "--dynamic-timeout-per-line-seconds",
        type=int,
        default=5,
        help="Dynamic timeout per source line.",
    )
    parser.add_argument(
        "--dynamic-timeout-min-seconds",
        type=int,
        default=60,
        help="Minimum dynamic timeout after clamping.",
    )
    parser.add_argument(
        "--dynamic-timeout-max-seconds",
        type=int,
        default=900,
        help="Maximum dynamic timeout after clamping.",
    )
    parser.add_argument(
        "--failure-context-max-lines",
        type=int,
        default=160,
        help="Maximum number of pytest output lines sent to the LLM.",
    )
    parser.add_argument(
        "--enable-matlab-help",
        action="store_true",
        help='Enrich repair prompt with snippets from "matlab -batch \\"help <fn>\\"".',
    )
    parser.add_argument(
        "--matlab-help-max-functions",
        type=int,
        default=1,
        help="Maximum MATLAB functions queried via help per repaired file.",
    )
    parser.add_argument(
        "--matlab-help-timeout-seconds",
        type=int,
        default=25,
        help="Timeout for each MATLAB help query.",
    )
    args = parser.parse_args()
    _configure_logging(args.verbose)

    base = Path(__file__).resolve().parent
    repo_root = (base / args.repo_root).resolve()
    src_root = (base / args.src_root).resolve()
    output = (base / args.output).resolve()

    model_resolution = _resolve_model_for_run(
        requested_model=args.model,
        fallback_model=args.fallback_model,
        auto_pull_model=args.auto_pull_model,
        heartbeat_seconds=args.heartbeat_seconds,
        stream_subprocess_logs=args.stream_subprocess_logs,
    )
    selected_model = str(model_resolution.get("selected_model", args.model))
    secondary_model = str(model_resolution.get("fallback_model", args.fallback_model))
    if secondary_model == selected_model:
        secondary_model = ""

    logger.info("Starting agentic repair cycle")
    logger.info(
        "roots=%s requested_model=%s selected_model=%s secondary_model=%s max_iterations=%s",
        args.roots,
        args.model,
        selected_model,
        secondary_model or "<none>",
        args.max_iterations,
    )
    logger.info("stream_subprocess_logs=%s heartbeat_seconds=%s", args.stream_subprocess_logs, args.heartbeat_seconds)
    logger.info(
        "llm_timeout_seconds=%s dynamic_timeout=%s(base=%s per_line=%s min=%s max=%s) "
        "failure_context_max_lines=%s enable_matlab_help=%s matlab_help_max_functions=%s",
        args.llm_timeout_seconds,
        args.dynamic_llm_timeout,
        args.dynamic_timeout_base_seconds,
        args.dynamic_timeout_per_line_seconds,
        args.dynamic_timeout_min_seconds,
        args.dynamic_timeout_max_seconds,
        args.failure_context_max_lines,
        args.enable_matlab_help,
        args.matlab_help_max_functions,
    )

    report = run_cycle(
        repo_root=repo_root,
        src_root=src_root,
        roots=args.roots,
        model=selected_model,
        secondary_model=secondary_model,
        max_iterations=args.max_iterations,
        max_files_per_iteration=args.max_files_per_iteration,
        repair_all_candidates=args.repair_all_candidates,
        max_context_chars=args.max_context_chars,
        dynamic_llm_timeout=args.dynamic_llm_timeout,
        dynamic_timeout_base_seconds=args.dynamic_timeout_base_seconds,
        dynamic_timeout_per_line_seconds=args.dynamic_timeout_per_line_seconds,
        dynamic_timeout_min_seconds=args.dynamic_timeout_min_seconds,
        dynamic_timeout_max_seconds=args.dynamic_timeout_max_seconds,
        force_pipeline=args.force_pipeline,
        overwrite_manual=args.overwrite_manual,
        generated_tests_per_iteration=args.generated_tests_per_iteration,
        run_all_generated_tests=args.run_all_generated_tests,
        contracts_per_iteration=args.contracts_per_iteration,
        run_all_contract_tests=args.run_all_contract_tests,
        disable_llm=args.disable_llm,
        disable_import_autofix=args.disable_import_autofix,
        allow_matlab_todos=args.allow_matlab_todos,
        verbose=args.verbose,
        heartbeat_seconds=args.heartbeat_seconds,
        stream_subprocess_logs=args.stream_subprocess_logs,
        llm_timeout_seconds=args.llm_timeout_seconds,
        failure_context_max_lines=args.failure_context_max_lines,
        enable_matlab_help=args.enable_matlab_help,
        matlab_help_max_functions=args.matlab_help_max_functions,
        matlab_help_timeout_seconds=args.matlab_help_timeout_seconds,
    )
    report["requested_model"] = args.model
    report["selected_model"] = selected_model
    report["model_resolution"] = model_resolution
    final_todo_markers = 0
    final_pytest_returncode: int | None = None
    if report.get("iterations"):
        last_step = report["iterations"][-1]
        analysis_summary = last_step.get("analysis_summary") or {}
        final_todo_markers = int(analysis_summary.get("matlab_todo_markers", 0) or 0)
        pytest_info = last_step.get("pytest") or {}
        if isinstance(pytest_info, dict):
            value = pytest_info.get("returncode")
            final_pytest_returncode = int(value) if isinstance(value, int) else None
    report["final_matlab_todo_markers"] = final_todo_markers
    report["final_pytest_returncode"] = final_pytest_returncode
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Agent repair cycle report written to: {output}")
    autofix_changed_total = 0
    sanitize_changed_total = 0
    for step in report.get("iterations", []):
        summary = step.get("auto_fix_missing_imports_summary") or {}
        if isinstance(summary, dict):
            autofix_changed_total += int(summary.get("files_changed", 0) or 0)
        sanitize_summary = step.get("sanitize_unicode_summary") or {}
        if isinstance(sanitize_summary, dict):
            sanitize_changed_total += int(sanitize_summary.get("changed_files", 0) or 0)
    print(
        json.dumps(
            {
                "finished_reason": report["finished_reason"],
                "iterations_ran": report["iterations_ran"],
                "autofix_imports_files_changed": autofix_changed_total,
                "unicode_sanitize_files_changed": sanitize_changed_total,
            },
            indent=2,
        )
    )
    success = report.get("finished_reason") == "all_tests_passed"
    if not success:
        logger.error(
            "Repair cycle did not converge: reason=%s final_todo_markers=%s final_pytest_returncode=%s",
            report.get("finished_reason"),
            final_todo_markers,
            final_pytest_returncode,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
