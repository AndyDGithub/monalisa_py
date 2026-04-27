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
import ast
import concurrent.futures
import hashlib
import json
import logging
import queue
import re
import subprocess
import sys
import threading
import time
import os
import shutil
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("agentic_repair_cycle")

try:
    from langchain_ollama import ChatOllama
except Exception:  # noqa: BLE001
    ChatOllama = None  # type: ignore[assignment]


SCRIPT_DIR = Path(__file__).resolve().parent


def _configure_logging(verbose: bool, log_file: str | None = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info("Logging to file: %s", log_file)

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
TRANSLATION_EXAMPLES_CACHE: str | None = None
SUCCESS_EXAMPLES_CACHE: str | None = None
_TARGET_TEST_INDEX_CACHE: dict[str, Any] = {"signature": None, "index": {}}
_PER_FILE_PYTEST_CACHE: dict[tuple[Any, ...], tuple[bool, str]] = {}
_QUICK_QUALITY_CACHE: dict[tuple[str, int, int], list[str]] = {}

# Matches ANSI/VT escape sequences (color codes, cursor movement, etc.)
# that some Ollama models (e.g. granite) embed in their output.
_ANSI_ESCAPE_RE = re.compile(
    r"\x1b(?:[@-Z\\-_]|\[[0-9;]*[mGKHFJABCDHfsuhlniqr]|\][^\x07]*\x07)"
)


def _strip_ansi(text: str) -> str:
    """Remove ANSI terminal escape sequences from LLM output."""
    return _ANSI_ESCAPE_RE.sub("", text)


def _ollama_cli_available() -> bool:
    return shutil.which("ollama") is not None


def _file_has_matlab_todo_markers(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "TODO(matlab" in text


def _load_translation_examples_context(repo_root: Path, max_chars: int) -> str:
    global TRANSLATION_EXAMPLES_CACHE  # noqa: PLW0603
    if TRANSLATION_EXAMPLES_CACHE is None:
        prompt_path = repo_root / "porting" / "prompts" / "matlab_to_python_examples.md"
        if prompt_path.exists():
            TRANSLATION_EXAMPLES_CACHE = prompt_path.read_text(encoding="utf-8", errors="ignore").strip()
        else:
            TRANSLATION_EXAMPLES_CACHE = ""
    dynamic = _load_success_examples_context(repo_root)
    parts = [part for part in [TRANSLATION_EXAMPLES_CACHE, dynamic] if part]
    merged = "\n\n".join(parts).strip()
    if not merged:
        return ""
    if max_chars > 0 and len(merged) > max_chars:
        return merged[:max_chars]
    return merged


def _load_success_examples_context(repo_root: Path) -> str:
    global SUCCESS_EXAMPLES_CACHE  # noqa: PLW0603
    if SUCCESS_EXAMPLES_CACHE is not None:
        return SUCCESS_EXAMPLES_CACHE

    change_log = repo_root / "porting" / "logs" / "change_log.jsonl"
    if not change_log.exists():
        SUCCESS_EXAMPLES_CACHE = ""
        return SUCCESS_EXAMPLES_CACHE

    try:
        lines = change_log.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        SUCCESS_EXAMPLES_CACHE = ""
        return SUCCESS_EXAMPLES_CACHE

    approved_paths: list[Path] = []
    seen: set[str] = set()
    # Keep only recent events to bound startup cost.
    for raw in reversed(lines[-2000:]):
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        details = payload.get("details", {}) if isinstance(payload.get("details", {}), dict) else {}
        verdict = str(details.get("reviewer_verdict", ""))
        file_value = str(payload.get("file", "")).strip()
        if verdict != "approved" or not file_value:
            continue
        py_path = Path(file_value)
        if py_path.suffix.lower() != ".py":
            continue
        key = str(py_path.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        approved_paths.append(py_path)
        if len(approved_paths) >= 6:
            break

    if not approved_paths:
        SUCCESS_EXAMPLES_CACHE = ""
        return SUCCESS_EXAMPLES_CACHE

    blocks: list[str] = []
    for py_path in approved_paths:
        try:
            py_text = py_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        m_path = py_path.with_suffix(".m")
        if not m_path.exists():
            continue
        try:
            m_text = m_path.read_text(encoding="ISO-8859-1", errors="ignore")
        except OSError:
            continue

        py_sig = next(
            (line.strip() for line in py_text.splitlines() if line.strip().startswith(("def ", "class "))),
            "",
        )
        m_sig = next((line.strip() for line in m_text.splitlines() if line.strip().startswith("function")), "")
        if not py_sig and not m_sig:
            continue

        try:
            rel = py_path.resolve().relative_to(repo_root.resolve())
            label = str(rel).replace("\\", "/")
        except ValueError:
            label = py_path.name
        block = [f"- {label}"]
        if m_sig:
            block.append(f"  MATLAB: {m_sig}")
        if py_sig:
            block.append(f"  Python: {py_sig}")
        blocks.append("\n".join(block))

    if not blocks:
        SUCCESS_EXAMPLES_CACHE = ""
        return SUCCESS_EXAMPLES_CACHE

    SUCCESS_EXAMPLES_CACHE = "Recent approved project examples:\n" + "\n".join(blocks)
    return SUCCESS_EXAMPLES_CACHE


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
    hard_timeout_seconds: int | None = None,
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
        stderr_text = ""
        assert proc.stdout is not None

        line_queue: "queue.Queue[str | None]" = queue.Queue()

        def _reader_thread() -> None:
            try:
                for raw_line in proc.stdout:
                    line_queue.put(raw_line.rstrip("\n"))
            finally:
                line_queue.put(None)

        reader = threading.Thread(target=_reader_thread, daemon=True)
        reader.start()

        reader_done = False
        last_heartbeat = t0

        while True:
            drained_any = False
            while True:
                try:
                    item = line_queue.get_nowait()
                except queue.Empty:
                    break
                if item is None:
                    reader_done = True
                    break
                drained_any = True
                merged_lines.append(item)
                logger.info("[%s] %s", step_name, item)

            returncode = proc.poll()
            if returncode is not None and reader_done:
                break

            now = time.perf_counter()
            elapsed = now - t0
            if now - last_heartbeat >= max(1, heartbeat_seconds):
                logger.info("... %s still running (%.1fs)", step_name, elapsed)
                last_heartbeat = now

            if hard_timeout_seconds and elapsed >= max(1, hard_timeout_seconds):
                proc.kill()
                returncode = proc.wait()
                stderr_text = f"hard_timeout_exceeded:{int(hard_timeout_seconds)}s"
                logger.error("TIMEOUT %s after %.1fs", step_name, elapsed)
                break

            if not drained_any:
                time.sleep(0.1)

        try:
            proc.stdout.close()
        except Exception:
            pass
        reader.join(timeout=1.0)
        stdout_text = ("\n".join(merged_lines) + ("\n" if merged_lines else ""))
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
                if hard_timeout_seconds and elapsed >= max(1, hard_timeout_seconds):
                    proc.kill()
                    stdout_text, stderr_text = proc.communicate()
                    stderr_text = (
                        (stderr_text + "\n") if stderr_text else ""
                    ) + f"hard_timeout_exceeded:{int(hard_timeout_seconds)}s"
                    break
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


def _list_local_ollama_models(timeout_seconds: int = 10) -> list[str]:
    try:
        proc = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=max(1, int(timeout_seconds)),
        )
    except subprocess.TimeoutExpired:
        logger.warning("Timeout while listing local Ollama models (timeout=%ss).", int(timeout_seconds))
        return []
    except OSError:
        return []
    if proc.returncode != 0:
        logger.warning("Failed to list local Ollama models (rc=%s).", proc.returncode)
        return []

    models: list[str] = []
    lines = [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]
    for line in lines[1:]:
        name = line.split()[0].strip()
        if name:
            models.append(name)
    return models


def _pull_ollama_model(
    model: str,
    heartbeat_seconds: int,
    stream_output: bool,
    *,
    hard_timeout_seconds: int = 900,
) -> bool:
    pull_run = _run_command(
        ["ollama", "pull", model],
        cwd=SCRIPT_DIR,
        step_name=f"ollama_pull:{model}",
        heartbeat_seconds=heartbeat_seconds,
        stream_output=stream_output,
        hard_timeout_seconds=max(60, int(hard_timeout_seconds)),
    )
    return pull_run.returncode == 0


def _resolve_model_for_run(
    requested_model: str,
    fallback_model: str,
    auto_pull_model: bool,
    heartbeat_seconds: int,
    stream_subprocess_logs: bool,
    *,
    ollama_list_timeout_seconds: int = 10,
    ollama_pull_timeout_seconds: int = 900,
) -> dict[str, Any]:
    normalized = _normalize_model_name(requested_model)
    fallback_normalized = _normalize_model_name(fallback_model)
    list_timeout = max(1, int(ollama_list_timeout_seconds))
    pull_timeout = max(60, int(ollama_pull_timeout_seconds))

    def _refresh_local_models() -> list[str]:
        return _list_local_ollama_models(timeout_seconds=list_timeout)

    local_models = _refresh_local_models()
    details: dict[str, Any] = {
        "requested_model": requested_model,
        "normalized_model": normalized,
        "fallback_model": fallback_normalized,
        "local_models_before": local_models,
        "auto_pull_model": auto_pull_model,
        "pulled_models": [],
        "ollama_list_timeout_seconds": list_timeout,
        "ollama_pull_timeout_seconds": pull_timeout,
    }

    if normalized in local_models:
        details["selected_model"] = normalized
        details["resolution"] = "requested_available"
        return details

    if auto_pull_model and normalized:
        logger.warning("Model '%s' not found locally. Attempting automatic pull.", normalized)
        if _pull_ollama_model(
            normalized,
            heartbeat_seconds,
            stream_subprocess_logs,
            hard_timeout_seconds=pull_timeout,
        ):
            details["pulled_models"].append(normalized)
            local_after_pull = _refresh_local_models()
            details["local_models_after_pull"] = local_after_pull
            if normalized in local_after_pull:
                details["selected_model"] = normalized
                details["resolution"] = "requested_pulled"
                return details

    local_models = _refresh_local_models()
    if fallback_normalized in local_models:
        details["selected_model"] = fallback_normalized
        details["resolution"] = "fallback_available"
        details["local_models_after_pull"] = local_models
        return details

    if auto_pull_model and fallback_normalized and fallback_normalized != normalized:
        logger.warning("Fallback model '%s' not found locally. Attempting automatic pull.", fallback_normalized)
        if _pull_ollama_model(
            fallback_normalized,
            heartbeat_seconds,
            stream_subprocess_logs,
            hard_timeout_seconds=pull_timeout,
        ):
            details["pulled_models"].append(fallback_normalized)
            local_after_pull = _refresh_local_models()
            details["local_models_after_pull"] = local_after_pull
            if fallback_normalized in local_after_pull:
                details["selected_model"] = fallback_normalized
                details["resolution"] = "fallback_pulled"
                return details

    local_models = _refresh_local_models()
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


def _read_sync_env_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_sync_env_state(path: Path, payload: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:  # noqa: BLE001
        logger.warning("Failed to write sync-env state file: %s", path)


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
    translation_examples_context: str,
    runtime_semantics_context: str,
    project_imports_context: str = "",
    extra_instruction: str = "",
) -> str:
    matlab_help_section = f"\nMATLAB help snippets:\n{matlab_help_context}\n" if matlab_help_context else ""
    translation_examples_section = (
        f"\nReference MATLAB->Python translations (style guide):\n{translation_examples_context}\n"
        if translation_examples_context
        else ""
    )
    project_imports_section = (
        f"\n{project_imports_context}\n"
        if project_imports_context
        else ""
    )
    runtime_semantics_section = (
        f"\nMATLAB runtime semantics to preserve:\n{runtime_semantics_context}\n"
        if runtime_semantics_context
        else ""
    )
    extra_section = (
        f"\n!!! RETRY INSTRUCTION (previous attempt failed) !!!\n{extra_instruction}\n"
        if extra_instruction
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
{extra_section}{project_imports_section}{runtime_semantics_section}
{translation_examples_section}
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


def _matlab_runtime_semantics_context(matlab_source: str) -> str:
    required: list[str] = []
    for token in ("inputname", "assignin", "evalin"):
        if re.search(rf"\b{token}\b", matlab_source):
            required.append(token)
    if not required:
        return ""

    guidance: list[str] = [
        f"Detected MATLAB runtime semantics: {', '.join(required)}.",
        "Use deterministic helpers from third_part.matlab_compat.matlab_runtime_metadata.",
        "Do not rely on ad-hoc inspect/eval when helper functions are available.",
    ]
    if "inputname" in required:
        guidance.append("For inputname: prefer explicit var_name kwarg and resolve_inputname(..., args=(...)).")
    if "assignin" in required:
        guidance.append("For assignin: use assignin_runtime(scope, name, value, metadata=...).")
    if "evalin" in required:
        guidance.append("For evalin: use evalin_runtime(scope, expression, metadata=..., default=...).")
    return "\n".join(guidance)


def _merge_quality_blockers_csv(explicit_blockers: str, inferred_blockers: list[str]) -> str:
    merged: list[str] = []
    seen: set[str] = set()
    for token in str(explicit_blockers or "").split(","):
        cleaned = token.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        merged.append(cleaned)
    for token in inferred_blockers:
        cleaned = str(token).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        merged.append(cleaned)
    return ",".join(merged)


def _infer_quick_quality_blockers(target_py: Path, src_root: Path) -> list[str]:
    matlab_peer = _matlab_peer_for_python(target_py, src_root)
    py_mtime = int(target_py.stat().st_mtime_ns) if target_py.exists() else -1
    m_mtime = int(matlab_peer.stat().st_mtime_ns) if matlab_peer and matlab_peer.exists() else -1
    cache_key = (str(target_py.resolve()), py_mtime, m_mtime)
    cached = _QUICK_QUALITY_CACHE.get(cache_key)
    if cached is not None:
        return list(cached)

    try:
        py_text = target_py.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        _QUICK_QUALITY_CACHE[cache_key] = []
        return []

    blockers: list[str] = []
    if "TODO(matlab" in py_text:
        blockers.append("matlab_todo_markers")
    if "MATLAB body snapshot (untranslated" in py_text or "translate MATLAB logic faithfully" in py_text:
        blockers.append("untranslated_snapshot")
    if "Fallback stub generated because automatic translation did not compile yet" in py_text or "# compile_error:" in py_text:
        blockers.append("fallback_stub")

    path_tokens = {part.lower() for part in target_py.parts}
    is_mex_wrapper = "mex" in path_tokens
    if not is_mex_wrapper and "NotImplementedError(" in py_text:
        blockers.append("not_implemented_stub")

    if not is_mex_wrapper:
        try:
            tree = ast.parse(py_text)
            pass_only_callable_count = 0
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                body = list(node.body)
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(getattr(body[0], "value", None), ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    body = body[1:]
                if body and all(isinstance(stmt, ast.Pass) for stmt in body):
                    pass_only_callable_count += 1
            if pass_only_callable_count > 0:
                blockers.append("pass_only_callable")
        except SyntaxError:
            pass

    if matlab_peer is not None and matlab_peer.exists():
        try:
            matlab_text = matlab_peer.read_text(encoding="ISO-8859-1", errors="ignore")
        except OSError:
            matlab_text = ""

        matlab_comment_lines = sum(1 for line in matlab_text.splitlines() if line.strip().startswith("%"))
        python_comment_lines = sum(1 for line in py_text.splitlines() if line.strip().startswith("#"))
        if matlab_comment_lines > 0:
            if python_comment_lines <= 0:
                blockers.append("comment_parity")
            else:
                ratio = python_comment_lines / max(1, matlab_comment_lines)
                if ratio < 0.15 and python_comment_lines < min(6, matlab_comment_lines):
                    blockers.append("comment_parity")

        required_tokens = sorted(set(re.findall(r"\b(inputname|assignin|evalin)\b", matlab_text)))
        if required_tokens:
            token_checks = {
                "inputname": re.compile(r"\b(resolve_inputname|inputname)\b"),
                "assignin": re.compile(r"\b(assignin_runtime|assignin)\b"),
                "evalin": re.compile(r"\b(evalin_runtime|evalin)\b"),
            }
            missing = [
                token
                for token in required_tokens
                if token in token_checks and not token_checks[token].search(py_text)
            ]
            if missing:
                blockers.append("runtime_metadata_semantics")

    deduped = sorted(set(blockers))
    _QUICK_QUALITY_CACHE[cache_key] = deduped
    return list(deduped)


def _quality_cleanup_instruction(quality_blockers: str) -> str:
    blockers = [token.strip() for token in str(quality_blockers or "").split(",") if token.strip()]
    if not blockers:
        return ""
    hints: list[str] = [
        "Previous reviewer blocked this file even when tests passed.",
        f"Quality blockers to fix now: {', '.join(blockers)}.",
        "Do not return unchanged code if these blockers remain.",
    ]
    if "comment_parity" in blockers:
        hints.append("Add concise comments/docstring to preserve MATLAB comment intent.")
    if "matlab_todo_markers" in blockers:
        hints.append("Replace TODO(matlab-*) markers with concrete executable code.")
    if "runtime_metadata_semantics" in blockers:
        hints.append(
            "Use runtime helpers for inputname/assignin/evalin from third_part.matlab_compat.matlab_runtime_metadata."
        )
    if "untranslated_snapshot" in blockers or "pass_only_callable" in blockers or "not_implemented_stub" in blockers:
        hints.append("Remove placeholder/untranslated sections and implement real logic.")
    return "\n".join(hints)


def _retry_feedback_instruction(retry_feedback: str) -> str:
    text = str(retry_feedback or "").strip()
    if not text:
        return ""
    if len(text) > 1800:
        text = text[-1800:]
    return (
        "Previous attempt context (use this to avoid repeating the same failure):\n"
        f"{text}"
    )


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
    if "todo(" in low:
        return True
    if "notimplementederror" in low:
        # Allow mex-wrapper style files that intentionally expose unsupported
        # backends while still implementing real control-flow logic.
        non_empty = [line for line in candidate_code.splitlines() if line.strip()]
        logic_tokens = ("if ", "elif ", "for ", "while ", "return ", "np.", "numpy.")
        has_logic = any(tok in low for tok in logic_tokens)
        if len(non_empty) <= 40 and not has_logic:
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


def _target_test_index_signature(generated_tests: Path, contract_tests: Path) -> tuple[Any, ...]:
    def _sig(path: Path) -> tuple[str, int]:
        if not path.exists():
            return (str(path.resolve()), -1)
        try:
            return (str(path.resolve()), int(path.stat().st_mtime_ns))
        except OSError:
            return (str(path.resolve()), -1)

    return (*_sig(generated_tests), *_sig(contract_tests))


def _build_target_test_index(generated_tests: Path, contract_tests: Path) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for root in (generated_tests, contract_tests):
        if not root.is_dir():
            continue
        for test_path in root.rglob("test_*.py"):
            try:
                text = test_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            m = TARGET_FILE_RE.search(text)
            if not m:
                continue
            parent_index = int(m.group(1))
            rel_target = m.group(2).replace("/", "\\")
            try:
                resolved_root = test_path.resolve().parents[parent_index]
            except IndexError:
                continue
            target = (resolved_root / rel_target).resolve()
            key = str(target).lower()
            index.setdefault(key, []).append(str(test_path.resolve()))

    for key in list(index.keys()):
        index[key] = sorted(set(index[key]))
    return index


def _get_target_test_index(generated_tests: Path, contract_tests: Path) -> dict[str, list[str]]:
    signature = _target_test_index_signature(generated_tests, contract_tests)
    cached_signature = _TARGET_TEST_INDEX_CACHE.get("signature")
    cached_index = _TARGET_TEST_INDEX_CACHE.get("index")
    if cached_signature == signature and isinstance(cached_index, dict):
        return cached_index
    index = _build_target_test_index(generated_tests, contract_tests)
    _TARGET_TEST_INDEX_CACHE["signature"] = signature
    _TARGET_TEST_INDEX_CACHE["index"] = index
    return index


def _test_files_for_target(
    target_py: Path,
    generated_tests: Path,
    contract_tests: Path,
) -> list[Path]:
    index = _get_target_test_index(generated_tests, contract_tests)
    key = str(target_py.resolve()).lower()
    mapped = [Path(p) for p in index.get(key, []) if Path(p).exists()]
    if mapped:
        return mapped

    # Fallback by stem when TARGET_FILE is not present in a generated test.
    stem = target_py.stem
    fallback: list[Path] = []
    for test_dir in (generated_tests, contract_tests):
        if not test_dir.is_dir():
            continue
        for candidate in test_dir.rglob(f"test_{stem}.py"):
            if candidate.exists():
                fallback.append(candidate.resolve())
    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in fallback:
        if candidate not in seen:
            seen.add(candidate)
            deduped.append(candidate)
    return deduped


def _run_pytest_for_target(
    target_py: Path,
    repo_root: Path,
    generated_tests: Path,
    contract_tests: Path,
    *,
    heartbeat_seconds: int = 20,
    stream_output: bool = False,
    per_file_pytest_timeout_seconds: int = 180,
) -> tuple[bool, str]:
    """Run pytest on all mapped tests for *target_py*.

    Returns (passed, output_text).  If no test file exists, returns (False, "").
    """
    test_files = _test_files_for_target(target_py, generated_tests, contract_tests)
    if not test_files:
        return False, ""
    target_mtime = int(target_py.stat().st_mtime_ns) if target_py.exists() else -1
    tests_signature: tuple[Any, ...] = tuple(
        (str(test_file), int(test_file.stat().st_mtime_ns) if test_file.exists() else -1)
        for test_file in test_files
    )
    cache_key: tuple[Any, ...] = (str(target_py.resolve()), target_mtime, *tests_signature)
    cached = _PER_FILE_PYTEST_CACHE.get(cache_key)
    if cached is not None:
        return cached
    cmd = [
        sys.executable, "-m", "pytest",
        "--import-mode=importlib",
        "-p", "no:cacheprovider",
        *[str(test_file) for test_file in test_files],
        "-q", "--tb=short", "--no-header",
    ]
    result = _run_command(
        cmd,
        cwd=repo_root,
        step_name=f"per_file_pytest:{target_py.name}",
        heartbeat_seconds=heartbeat_seconds,
        stream_output=stream_output,
        hard_timeout_seconds=max(30, int(per_file_pytest_timeout_seconds or 0)),
    )
    output = f"{result.stdout}\n{result.stderr}"
    cached_result = (result.returncode == 0, output)
    _PER_FILE_PYTEST_CACHE[cache_key] = cached_result
    return cached_result


def _strict_prefilter_report_path(reports_dir: Path, target_py: Path) -> Path:
    digest = hashlib.sha1(str(target_py).encode("utf-8", errors="ignore")).hexdigest()[:10]
    return reports_dir / f"strict_prefilter_{target_py.stem}_{digest}.json"


def _run_strict_prefilter_for_target(
    *,
    target_py: Path,
    roots: str,
    repo_root: Path,
    reports_dir: Path,
    heartbeat_seconds: int,
    stream_output: bool,
) -> dict[str, Any]:
    report_path = _strict_prefilter_report_path(reports_dir, target_py)
    output_arg = f"../reports/{report_path.name}"
    run = _run_script(
        "evaluate_strict_port_batch.py",
        [
            "--repo-root",
            "../../",
            "--roots",
            roots,
            "--target-python-file",
            str(target_py),
            "--output",
            output_arg,
            "--summary-only",
        ],
        repo_root,
        step_name=f"strict_prefilter:{target_py.name}",
        heartbeat_seconds=heartbeat_seconds,
        stream_output=stream_output,
    )
    info: dict[str, Any] = {
        "target": str(target_py),
        "report_path": str(report_path),
        "script": run.to_dict(),
        "action": "",
        "before_returncode": None,
        "after_returncode": None,
        "strict_changed_vs_current": False,
        "strict_status": "",
        "strict_skip_reason": "",
        "strict_native_backend_required": False,
        "strict_native_function": "",
    }
    if run.returncode != 0 or not report_path.exists():
        return info
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return info
    if not isinstance(payload, dict):
        return info
    results = payload.get("results", [])
    if not isinstance(results, list) or not results:
        return info
    row = results[0] if isinstance(results[0], dict) else {}
    before = row.get("before", {}) if isinstance(row.get("before", {}), dict) else {}
    after = row.get("after", {}) if isinstance(row.get("after", {}), dict) else {}
    info["action"] = str(row.get("action", ""))
    info["before_returncode"] = before.get("returncode")
    info["after_returncode"] = after.get("returncode")
    info["strict_changed_vs_current"] = bool(row.get("strict_changed_vs_current", False))
    info["strict_status"] = str(row.get("strict_status", ""))
    info["strict_skip_reason"] = str(row.get("strict_skip_reason", ""))
    info["strict_native_backend_required"] = bool(row.get("strict_native_backend_required", False))
    info["strict_native_function"] = str(row.get("strict_native_function", ""))
    return info


def _is_pause_worthy_reason(reason: str) -> bool:
    if not reason:
        return True
    ignored_prefixes = (
        "already_passing",
        "strict_prefilter_keep_current",
        "strict_prefilter_rollback_keep_current",
    )
    return not any(reason.startswith(prefix) for prefix in ignored_prefixes)


# Matches "ImportError: cannot import name 'foo'" and "ModuleNotFoundError: No module named 'bar'"
_IMPORT_ERROR_RE = re.compile(
    r"(?:ImportError|ModuleNotFoundError)[^\n]*"
    r"(?:cannot import name ['\"]([^'\"]+)['\"]|No module named ['\"]([^'\"]+)['\"])",
    re.IGNORECASE,
)


def _is_cascade_failure(target_py: Path, test_output: str) -> tuple[bool, str]:
    """Return (True, broken_name) when test output shows an import error from a dependency.

    A *cascade* failure is one where the ImportError refers to a module OTHER than the
    target itself — meaning the target's own test fails because one of its imports is
    broken, not because the target's own code is broken.
    """
    target_module = target_py.stem
    for m in _IMPORT_ERROR_RE.finditer(test_output):
        broken = m.group(1) or m.group(2) or ""
        broken_base = broken.split(".")[-1]
        if broken_base and broken_base != target_module:
            return True, broken_base
    return False, ""


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
    extra_instruction: str = "",
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
    runtime_semantics_context = _matlab_runtime_semantics_context(full_matlab_source)
    prompt = _repair_prompt(
        target_py=target_py,
        matlab_source=matlab_source,
        python_source=python_source,
        failure_context=failure_context,
        matlab_help_context=matlab_help_context,
        translation_examples_context=_load_translation_examples_context(
            repo_root,
            max_chars=max_context_chars // 2 if max_context_chars > 0 else 3000,
        ),
        runtime_semantics_context=runtime_semantics_context,
        project_imports_context=project_imports_context,
        extra_instruction=extra_instruction,
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
        content = _strip_ansi((cli.stdout or "").strip())
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
            llm = ChatOllama(model=model, validate_model_on_init=True, temperature=0, streaming=True)
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
            content = _strip_ansi("\n".join(parts).strip())
        else:
            content = _strip_ansi(str(content_obj).strip())

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
    per_file_pytest_timeout_seconds: int,
    enable_matlab_help: bool,
    matlab_help_max_functions: int,
    matlab_help_timeout_seconds: int,
    target_file: str,
    force_quality_cleanup: bool,
    quality_blockers: str,
    retry_feedback: str,
    sync_env: bool,
    requirements_output: str,
    sync_env_timeout_seconds: int,
    enable_strict_prefilter: bool,
    pause_on_applied_false: bool,
    skip_pipeline: bool,
    main_model_retries: int = 3,
) -> dict[str, Any]:
    reports_dir = repo_root / "porting" / "reports"
    generated_tests = repo_root / "porting" / "tests" / "generated"
    contract_tests = repo_root / "porting" / "tests" / "contracts"
    requirements_path = Path(requirements_output).expanduser()
    if not requirements_path.is_absolute():
        requirements_path = (repo_root / requirements_path).resolve()
    else:
        requirements_path = requirements_path.resolve()
    sync_env_state_path = requirements_path.with_suffix(requirements_path.suffix + ".sync_state.json")
    roots_tokens = [token.strip() for token in roots.split(",") if token.strip()]
    analysis_roots_tokens = list(roots_tokens) if roots_tokens else ["src"]
    if "third_part" not in analysis_roots_tokens:
        analysis_roots_tokens.append("third_part")
    analysis_roots_arg = ",".join(f"../../{token}" for token in analysis_roots_tokens)
    requirements_roots_tokens = list(analysis_roots_tokens)
    for extra_root in ("agentic", "porting"):
        if extra_root not in requirements_roots_tokens:
            requirements_roots_tokens.append(extra_root)
    requirements_roots_arg = ",".join(f"../../{token}" for token in requirements_roots_tokens)

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
        if skip_pipeline:
            step["pipeline"] = {
                "command": [],
                "returncode": 0,
                "stdout": "",
                "stderr": "",
                "elapsed_seconds": 0.0,
                "skipped": True,
            }
            logger.info("Skipping pipeline step (--skip-pipeline).")
        else:
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

        if target_file.strip():
            step["cleanup_pipeline_artifacts"] = {
                "skipped": True,
                "reason": "target_file_mode",
            }
            step["cleanup_pipeline_artifacts_summary"] = {
                "skipped": True,
                "reason": "target_file_mode",
            }
        else:
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

        if sync_env:
            req_args = [
                "--roots",
                requirements_roots_arg,
                "--repo-root",
                "../../",
                "--output",
                str(requirements_path),
                "--summary-only",
            ]
            req_run = _run_script(
                "generate_requirements_deterministic.py",
                req_args,
                repo_root,
                step_name=f"iteration_{iteration}:generate_requirements_deterministic",
                heartbeat_seconds=heartbeat_seconds,
                stream_output=stream_subprocess_logs,
            )
            step["generate_requirements_deterministic"] = req_run.to_dict()
            try:
                step["generate_requirements_deterministic_summary"] = json.loads(req_run.stdout or "{}")
            except json.JSONDecodeError:
                step["generate_requirements_deterministic_summary"] = {}

            if req_run.returncode == 0:
                requirements_hash = ""
                try:
                    requirements_hash = hashlib.sha256(requirements_path.read_bytes()).hexdigest()
                except OSError:
                    requirements_hash = ""
                sync_state = _read_sync_env_state(sync_env_state_path)
                state_hash = str(sync_state.get("requirements_hash", ""))
                state_python = str(sync_state.get("python_executable", ""))
                can_skip_sync = bool(
                    requirements_hash
                    and requirements_hash == state_hash
                    and state_python == sys.executable
                    and bool(sync_state.get("ok", False))
                )
                if can_skip_sync:
                    step["sync_env"] = {
                        "skipped": True,
                        "reason": "requirements_unchanged",
                        "requirements_output": str(requirements_path),
                        "requirements_hash": requirements_hash,
                    }
                    logger.info("Skipping sync-env: requirements unchanged.")
                else:
                    sync_cmd = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--disable-pip-version-check",
                        "--no-input",
                        "--retries",
                        "1",
                        "--timeout",
                        "20",
                        "-r",
                        str(requirements_path),
                    ]
                    sync_run = _run_command(
                        sync_cmd,
                        cwd=repo_root,
                        step_name=f"iteration_{iteration}:sync_env",
                        heartbeat_seconds=heartbeat_seconds,
                        stream_output=stream_subprocess_logs,
                        hard_timeout_seconds=max(60, int(sync_env_timeout_seconds or 0)),
                    )
                    step["sync_env"] = sync_run.to_dict()
                    if sync_run.returncode != 0:
                        logger.warning("sync-env failed with rc=%s; continuing workflow.", sync_run.returncode)
                    else:
                        _write_sync_env_state(
                            sync_env_state_path,
                            {
                                "ok": True,
                                "requirements_hash": requirements_hash,
                                "python_executable": sys.executable,
                                "requirements_output": str(requirements_path),
                                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                            },
                        )
            else:
                step["sync_env"] = {
                    "skipped": True,
                    "reason": "requirements_generation_failed",
                    "requirements_output": str(requirements_path),
                }
                logger.warning("Skipping sync-env because requirements generation failed.")
        else:
            step["generate_requirements_deterministic"] = {
                "skipped": True,
                "reason": "sync_env_disabled",
                "requirements_output": str(requirements_path),
            }
            step["sync_env"] = {
                "skipped": True,
                "reason": "sync_env_disabled",
                "requirements_output": str(requirements_path),
            }

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

        if target_file.strip():
            forced_target = Path(target_file).expanduser()
            if not forced_target.is_absolute():
                forced_target = (repo_root / forced_target).resolve()
            else:
                forced_target = forced_target.resolve()
            if forced_target.exists():
                candidate_targets = [forced_target]
                step["forced_target_file"] = str(forced_target)
            else:
                candidate_targets = []
                step["forced_target_file"] = str(forced_target)
                step["forced_target_error"] = "target_file_not_found"
                logger.warning("Forced target file not found: %s", forced_target)

        step["candidate_targets"] = [str(p) for p in candidate_targets]

        if not candidate_targets:
            if pytest_run.returncode == 0 and todo_count > 0:
                finished_reason = "tests_passed_but_todos_remain"
            else:
                finished_reason = "no_candidate_targets"
            logger.warning("Stopping: %s", finished_reason)
            iterations.append(step)
            break

        require_todo_cleanup = pytest_run.returncode == 0 and todo_count > 0 and (not allow_matlab_todos)
        if require_todo_cleanup:
            step["repair_trigger"] = {
                "reason": "matlab_todo_markers_remaining",
                "todo_markers": todo_count,
            }
            logger.info("Repair trigger: TODO markers remain (%s).", todo_count)

        llm_runtime_enabled = (not disable_llm) and (_ollama_cli_available() or (ChatOllama is not None))
        step["llm_runtime"] = {
            "disable_llm_flag": bool(disable_llm),
            "ollama_cli_available": bool(_ollama_cli_available()),
            "langchain_ollama_available": bool(ChatOllama is not None),
            "enabled": bool(llm_runtime_enabled),
        }
        if disable_llm:
            logger.info("LLM disabled: running strict/deterministic-only repair attempts.")
        elif not llm_runtime_enabled:
            logger.error(
                "No LLM runtime available (ollama CLI missing and langchain_ollama unavailable): "
                "running strict/deterministic-only repair attempts."
            )

        repair_results: list[dict[str, Any]] = []
        strict_prefilter_results: list[dict[str, Any]] = []
        pause_trigger: dict[str, Any] | None = None
        failure_context = _trim_failure_context(
            pytest_text=pytest_text,
            max_chars=max_context_chars,
            max_lines=failure_context_max_lines,
        )

        def _record_repair_result(result: dict[str, Any]) -> None:
            nonlocal pause_trigger
            repair_results.append(result)
            if pause_trigger is not None or not pause_on_applied_false:
                return
            if bool(result.get("applied")):
                return
            reason = str(result.get("reason", ""))
            if not _is_pause_worthy_reason(reason):
                return
            pause_trigger = {
                "target": str(result.get("target", "")),
                "reason": reason,
                "iteration": iteration,
            }
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

            if target.name.startswith("test_"):
                logger.info("Skipping LLM repair for test file %s", target.name)
                continue

            inferred_quality_blockers = _infer_quick_quality_blockers(target, src_root)
            effective_quality_blockers = _merge_quality_blockers_csv(quality_blockers, inferred_quality_blockers)
            force_quality_cleanup_for_target = (
                bool(target_file.strip()) and (bool(force_quality_cleanup) or bool(effective_quality_blockers))
            )
            if effective_quality_blockers:
                logger.info(
                    "Target %s quality blockers: %s",
                    target.name,
                    effective_quality_blockers,
                )

            if enable_strict_prefilter:
                strict_info = _run_strict_prefilter_for_target(
                    target_py=target,
                    roots=roots,
                    repo_root=repo_root,
                    reports_dir=reports_dir,
                    heartbeat_seconds=heartbeat_seconds,
                    stream_output=stream_subprocess_logs,
                )
                strict_prefilter_results.append(strict_info)
                strict_action = str(strict_info.get("action", ""))
                if strict_action in {"keep_current", "rollback_keep_current"}:
                    if force_quality_cleanup_for_target:
                        logger.info(
                            "Strict prefilter kept current file for %s, but quality cleanup is required; continuing.",
                            target.name,
                        )
                    else:
                        _record_repair_result(
                            {
                                "target": str(target),
                                "applied": False,
                                "reason": f"strict_prefilter_{strict_action}",
                                "strict_prefilter": strict_info,
                            }
                        )
                        logger.info("Strict prefilter kept current file for %s: action=%s", target.name, strict_action)
                        if pause_trigger is not None:
                            break
                        continue
                if strict_action == "keep_strict_ported":
                    after_rc = strict_info.get("after_returncode")
                    if after_rc == 0:
                        _record_repair_result(
                            {
                                "target": str(target),
                                "applied": bool(strict_info.get("strict_changed_vs_current", True)),
                                "reason": "strict_prefilter_port_kept_and_passing",
                                "strict_prefilter": strict_info,
                            }
                        )
                        logger.info(
                            "Strict prefilter produced passing file for %s; skipping LLM repair.",
                            target.name,
                        )
                        if pause_trigger is not None:
                            break
                        continue
                    logger.info(
                        "Strict prefilter kept baseline for %s but tests still fail; continuing repair.",
                        target.name,
                    )

            # --- Skip-if-passing: per-file pytest before spending LLM time ---
            already_passing, per_file_out = _run_pytest_for_target(
                target, repo_root, generated_tests, contract_tests,
                heartbeat_seconds=heartbeat_seconds,
                stream_output=False,
                per_file_pytest_timeout_seconds=per_file_pytest_timeout_seconds,
            )
            has_todo_markers = _file_has_matlab_todo_markers(target)
            # In target-file mode, force TODO cleanup attempts for the current file
            # even when the global suite is red because of unrelated modules.
            force_target_todo_cleanup = bool(target_file.strip()) and (not allow_matlab_todos) and has_todo_markers
            if (
                already_passing
                and not (require_todo_cleanup and has_todo_markers)
                and not force_target_todo_cleanup
                and not force_quality_cleanup_for_target
            ):
                _record_repair_result({
                    "target": str(target),
                    "applied": False,
                    "reason": "already_passing",
                })
                logger.info("Skipping %s: already passing", target.name)
                if pause_trigger is not None:
                    break
                continue
            if already_passing and (require_todo_cleanup or force_target_todo_cleanup) and has_todo_markers:
                logger.info(
                    "Target %s passes tests but still has TODO(matlab*) markers; attempting LLM cleanup.",
                    target.name,
                )
            if already_passing and force_quality_cleanup_for_target:
                logger.info(
                    "Target %s passes tests but reviewer quality blockers require cleanup: %s",
                    target.name,
                    effective_quality_blockers or "<unspecified>",
                )

            # --- Cascade-failure detection: broken dep → fix dep first ---
            cascade, broken_dep = _is_cascade_failure(target, per_file_out)
            if cascade:
                _record_repair_result({
                    "target": str(target),
                    "applied": False,
                    "reason": f"cascade_dependency_failure:{broken_dep}",
                })
                logger.info(
                    "Skipping %s: cascade failure from broken dependency '%s'",
                    target.name, broken_dep,
                )
                if pause_trigger is not None:
                    break
                continue

            # --- Deterministic fix (no LLM needed) ---
            logger.info("Attempting repair for target: %s (timeout=%ss)", target.name, target_timeout)
            deterministic = _deterministic_sanitize_file(target)
            if deterministic.get("applied"):
                logger.info("Deterministic sanitize applied for %s", target.name)
                _record_repair_result(deterministic)
                if pause_trigger is not None:
                    break
                continue

            # --- Per-file retry: main model N times, then fallback once ---
            if not llm_runtime_enabled:
                _record_repair_result(
                    {
                        "target": str(target),
                        "applied": False,
                        "reason": "llm_disabled" if disable_llm else "no_llm_runtime_available",
                    }
                )
                if pause_trigger is not None:
                    break
                continue

            llm_kwargs = dict(
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
            repair: dict[str, Any] = {}
            applied = False
            base_parts = [
                _quality_cleanup_instruction(effective_quality_blockers),
                _retry_feedback_instruction(retry_feedback),
            ]
            base_extra_instruction = "\n\n".join(part for part in base_parts if part)
            extra_instruction = base_extra_instruction
            
            for attempt in range(1, main_model_retries + 1):
                repair = _try_repair_file_with_llm(  # type: ignore[arg-type]
                    model=model, extra_instruction=extra_instruction, **llm_kwargs
                )
                reason = str(repair.get("reason", ""))
                repair["attempt"] = attempt
                repair["used_model"] = model
                if repair.get("applied"):
                    applied = True
                    break
                logger.info(
                    "Main model attempt %s/%s for %s: reason=%s",
                    attempt, main_model_retries, target.name, reason,
                )
                # Retrying won't help for timeout/env errors or no_change
                if (
                    reason.startswith("llm_timeout")
                    or reason.startswith("llm_cli_error")
                    or reason.startswith("ollama_cli_unavailable")
                    or reason == "no_change"
                ):
                    break
                # Escalate the prompt based on what went wrong
                fn_name = target.stem
                if reason.startswith("candidate_missing_entrypoint"):
                    extra_instruction = (
                        (base_extra_instruction + "\n\n") if base_extra_instruction else ""
                    ) + (
                        f"Your previous output did NOT contain 'def {fn_name}(' or 'class {fn_name}'.\n"
                        f"Output ONLY valid Python source code. "
                        f"The first non-comment, non-import line MUST define: def {fn_name}(...)  or  class {fn_name}.\n"
                        f"No explanations, no markdown, no prose — ONLY Python source code."
                    )
                elif reason.startswith("candidate_syntax_error"):
                    extra_instruction = (
                        (base_extra_instruction + "\n\n") if base_extra_instruction else ""
                    ) + (
                        "Your previous output had a Python syntax error.\n"
                        "Output ONLY valid Python 3.13 source code — no markdown fences (```), "
                        "no ANSI escape sequences, no colored text, no explanations.\n"
                        "Start directly with the import statements or the function definition."
                    )
                elif reason.startswith("candidate_rejected_placeholder"):
                    extra_instruction = (
                        (base_extra_instruction + "\n\n") if base_extra_instruction else ""
                    ) + (
                        "Your previous output was a placeholder/stub (contains TODO or NotImplemented).\n"
                        "Provide a COMPLETE, working implementation based on the MATLAB reference.\n"
                        "Every TODO marker must be replaced with real Python logic."
                    )

            if not applied and secondary_model and secondary_model != model:
                reason = str(repair.get("reason", ""))
                if (
                    reason.startswith("llm_timeout")
                    or reason.startswith("empty_model_output")
                    or reason.startswith("candidate_syntax_error")
                    or reason.startswith("candidate_missing_entrypoint")
                    or reason == "no_change"
                ):
                    logger.info("Retrying target with fallback model: %s", secondary_model)
                    # Pass the last escalated instruction to the fallback model too
                    fallback_repair = _try_repair_file_with_llm(  # type: ignore[arg-type]
                        model=secondary_model, extra_instruction=extra_instruction, **llm_kwargs
                    )
                    fallback_repair["retry_from_model"] = model
                    fallback_repair["used_model"] = secondary_model
                    repair = fallback_repair

            if effective_quality_blockers:
                repair["quality_blockers"] = [
                    token.strip()
                    for token in effective_quality_blockers.split(",")
                    if token.strip()
                ]
            _record_repair_result(repair)
            logger.info(
                "Repair result for %s: applied=%s reason=%s",
                target.name, repair.get("applied"), repair.get("reason"),
            )
            if pause_trigger is not None:
                break
        step["repairs"] = repair_results
        if strict_prefilter_results:
            step["strict_prefilter"] = strict_prefilter_results

        if pause_trigger is not None:
            step["pause_trigger"] = pause_trigger
            finished_reason = "paused_on_applied_false"
            logger.error(
                "Pausing run on applied=False: target=%s reason=%s",
                pause_trigger.get("target", ""),
                pause_trigger.get("reason", ""),
            )
            iterations.append(step)
            break

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
        "force_quality_cleanup": bool(force_quality_cleanup),
        "quality_blockers": str(quality_blockers or ""),
        "retry_feedback": str(retry_feedback or "")[:1200],
        "sync_env": sync_env,
        "requirements_output": str(requirements_path),
        "sync_env_timeout_seconds": int(sync_env_timeout_seconds),
        "enable_strict_prefilter": enable_strict_prefilter,
        "pause_on_applied_false": pause_on_applied_false,
        "skip_pipeline": skip_pipeline,
        "iterations_ran": len(iterations),
        "finished_reason": finished_reason,
        "iterations": iterations,
    }
    if finished_reason == "paused_on_applied_false" and iterations:
        summary["pause_trigger"] = iterations[-1].get("pause_trigger", {})
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
        "--sync-env",
        action="store_true",
        help="Generate deterministic requirements and install them before pytest.",
    )
    parser.add_argument(
        "--requirements-output",
        default="porting/reports/requirements.generated.txt",
        help="Requirements file written by deterministic generation step.",
    )
    parser.add_argument(
        "--sync-env-timeout-seconds",
        type=int,
        default=180,
        help="Hard timeout (seconds) for the sync-env pip install step.",
    )
    parser.add_argument(
        "--target-file",
        default="",
        help="Optional single Python file target to prioritize/force in this run.",
    )
    parser.add_argument(
        "--force-quality-cleanup",
        action="store_true",
        help="Force LLM cleanup even when target tests already pass (useful for reviewer quality blockers).",
    )
    parser.add_argument(
        "--quality-blockers",
        default="",
        help="Comma-separated reviewer quality blockers to address on retry.",
    )
    parser.add_argument(
        "--retry-feedback",
        default="",
        help="Additional retry context propagated from previous reviewer/repair attempt.",
    )
    parser.add_argument(
        "--enable-strict-prefilter",
        dest="enable_strict_prefilter",
        action="store_true",
        default=True,
        help="Run deterministic strict baseline prefilter before LLM repair on each target.",
    )
    parser.add_argument(
        "--disable-strict-prefilter",
        dest="enable_strict_prefilter",
        action="store_false",
        help="Disable strict baseline prefilter step.",
    )
    parser.add_argument(
        "--pause-on-applied-false",
        action="store_true",
        help="Pause run immediately when a repair attempt returns applied=False (except benign skip reasons).",
    )
    parser.add_argument(
        "--resume-from-report",
        default="",
        help="Resume from a previous report JSON (reuses paused target when available).",
    )
    parser.add_argument(
        "--skip-pipeline",
        action="store_true",
        help="Skip run_porting_pipeline.py step (useful when resuming to avoid overwrite/regeneration).",
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
        "--per-file-pytest-timeout-seconds",
        type=int,
        default=180,
        help="Hard timeout for targeted per-file pytest probes used before LLM repair.",
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
    parser.add_argument(
        "--main-model-retries",
        type=int,
        default=3,
        help=(
            "How many times to retry the main model on a single file before trying "
            "the fallback model. Retrying is skipped early for timeout/env errors."
        ),
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Append all log output to this file in addition to stdout (useful for crash recovery).",
    )
    argv_tokens = sys.argv[1:]
    explicit_target_file = any(token == "--target-file" or token.startswith("--target-file=") for token in argv_tokens)
    explicit_max_iterations = any(
        token == "--max-iterations" or token.startswith("--max-iterations=") for token in argv_tokens
    )
    explicit_skip_pipeline = any(
        token == "--skip-pipeline" or token.startswith("--skip-pipeline=") for token in argv_tokens
    )

    args = parser.parse_args()
    _configure_logging(args.verbose, log_file=args.log_file)

    base = Path(__file__).resolve().parent
    repo_root = (base / args.repo_root).resolve()
    src_root = (base / args.src_root).resolve()
    output_path = Path(args.output).expanduser()
    if output_path.is_absolute():
        output = output_path.resolve()
    else:
        output = (repo_root / output_path).resolve()

    resumed_from_report = ""
    if args.resume_from_report.strip():
        resume_path = Path(args.resume_from_report)
        if not resume_path.is_absolute():
            resume_path = (base / resume_path).resolve()
        else:
            resume_path = resume_path.resolve()
        if resume_path.exists():
            resumed_from_report = str(resume_path)
            try:
                previous = json.loads(resume_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                previous = {}
            if isinstance(previous, dict):
                resume_state = previous.get("resume_state", {}) if isinstance(previous.get("resume_state", {}), dict) else {}
                pause_trigger = previous.get("pause_trigger", {}) if isinstance(previous.get("pause_trigger", {}), dict) else {}
                resume_target = str(resume_state.get("target_file") or pause_trigger.get("target") or "").strip()
                if resume_target and not explicit_target_file:
                    args.target_file = resume_target
                remaining = resume_state.get("remaining_iterations")
                if isinstance(remaining, int) and remaining > 0 and not explicit_max_iterations:
                    args.max_iterations = remaining
                if not explicit_skip_pipeline:
                    args.skip_pipeline = True
        else:
            logger.warning("resume-from-report file not found: %s", resume_path)

    ollama_list_timeout_seconds = 10
    ollama_pull_timeout_seconds = max(300, int(args.sync_env_timeout_seconds or 0) * 5)
    logger.info(
        "Resolving model selection (ollama_list_timeout=%ss ollama_pull_timeout=%ss)...",
        ollama_list_timeout_seconds,
        ollama_pull_timeout_seconds,
    )
    model_resolution = _resolve_model_for_run(
        requested_model=args.model,
        fallback_model=args.fallback_model,
        auto_pull_model=args.auto_pull_model,
        heartbeat_seconds=args.heartbeat_seconds,
        stream_subprocess_logs=args.stream_subprocess_logs,
        ollama_list_timeout_seconds=ollama_list_timeout_seconds,
        ollama_pull_timeout_seconds=ollama_pull_timeout_seconds,
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
        "failure_context_max_lines=%s per_file_pytest_timeout_seconds=%s "
        "enable_matlab_help=%s matlab_help_max_functions=%s "
        "main_model_retries=%s strict_prefilter=%s pause_on_applied_false=%s skip_pipeline=%s "
        "force_quality_cleanup=%s quality_blockers=%s retry_feedback_len=%s "
        "sync_env=%s requirements_output=%s sync_env_timeout_seconds=%s resumed_from=%s log_file=%s",
        args.llm_timeout_seconds,
        args.dynamic_llm_timeout,
        args.dynamic_timeout_base_seconds,
        args.dynamic_timeout_per_line_seconds,
        args.dynamic_timeout_min_seconds,
        args.dynamic_timeout_max_seconds,
        args.failure_context_max_lines,
        args.per_file_pytest_timeout_seconds,
        args.enable_matlab_help,
        args.matlab_help_max_functions,
        args.main_model_retries,
        args.enable_strict_prefilter,
        args.pause_on_applied_false,
        args.skip_pipeline,
        args.force_quality_cleanup,
        args.quality_blockers,
        len(str(args.retry_feedback or "")),
        args.sync_env,
        args.requirements_output,
        args.sync_env_timeout_seconds,
        resumed_from_report or "<none>",
        args.log_file or "<none>",
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
        per_file_pytest_timeout_seconds=args.per_file_pytest_timeout_seconds,
        enable_matlab_help=args.enable_matlab_help,
        matlab_help_max_functions=args.matlab_help_max_functions,
        matlab_help_timeout_seconds=args.matlab_help_timeout_seconds,
        target_file=args.target_file,
        force_quality_cleanup=args.force_quality_cleanup,
        quality_blockers=args.quality_blockers,
        retry_feedback=args.retry_feedback,
        sync_env=args.sync_env,
        requirements_output=args.requirements_output,
        sync_env_timeout_seconds=args.sync_env_timeout_seconds,
        enable_strict_prefilter=args.enable_strict_prefilter,
        pause_on_applied_false=args.pause_on_applied_false,
        skip_pipeline=args.skip_pipeline,
        main_model_retries=args.main_model_retries,
    )
    report["requested_model"] = args.model
    report["selected_model"] = selected_model
    report["model_resolution"] = model_resolution
    if resumed_from_report:
        report["resumed_from_report"] = resumed_from_report
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
    if report.get("finished_reason") == "paused_on_applied_false":
        pause_trigger = report.get("pause_trigger", {}) if isinstance(report.get("pause_trigger", {}), dict) else {}
        pause_target = str(pause_trigger.get("target", "")).strip()
        remaining_iterations = max(1, int(args.max_iterations) - int(report.get("iterations_ran", 0)))
        suggested_cmd = (
            f'python porting/scripts/run_agentic_repair_cycle.py --engine legacy '
            f'--resume-from-report "{output}"'
        )
        report["resume_state"] = {
            "target_file": pause_target,
            "remaining_iterations": remaining_iterations,
            "suggested_command": suggested_cmd,
        }

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
    if report.get("finished_reason") == "paused_on_applied_false":
        resume_state = report.get("resume_state", {}) if isinstance(report.get("resume_state", {}), dict) else {}
        print(
            json.dumps(
                {
                    "pause_trigger": report.get("pause_trigger", {}),
                    "resume_state": resume_state,
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
