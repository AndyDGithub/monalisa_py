from __future__ import annotations

import json
import logging
import queue
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CHANGE_LOG_LOCK = threading.Lock()


@dataclass(slots=True)
class ScriptResult:
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


class LegacyToolbox:
    """Thin wrappers around existing CLI scripts.

    This keeps v2 LangGraph nodes deterministic and allows incremental
    migration without rewriting every legacy tool at once.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.script_root = (self.repo_root / "porting" / "scripts").resolve()
        self.report_root = (self.repo_root / "porting" / "reports").resolve()
        self.log_root = (self.repo_root / "porting" / "logs").resolve()
        self._target_test_index: dict[str, list[str]] | None = None

    LOGGER = logging.getLogger("agentic.legacy_toolbox")
    _LEGACY_REPAIR_VALUE_KEYS = {
        "repo_root",
        "src_root",
        "model",
        "fallback_model",
        "max_iterations",
        "max_files_per_iteration",
        "max_context_chars",
        "generated_tests_per_iteration",
        "contracts_per_iteration",
        "target_file",
        "resume_from_report",
        "output",
        "heartbeat_seconds",
        "llm_timeout_seconds",
        "dynamic_timeout_base_seconds",
        "dynamic_timeout_per_line_seconds",
        "dynamic_timeout_min_seconds",
        "dynamic_timeout_max_seconds",
        "failure_context_max_lines",
        "per_file_pytest_timeout_seconds",
        "matlab_help_max_functions",
        "matlab_help_timeout_seconds",
        "main_model_retries",
        "log_file",
        "requirements_output",
        "sync_env_timeout_seconds",
        "quality_blockers",
        "retry_feedback",
    }
    _LEGACY_REPAIR_BOOL_POSITIVE_KEYS = {
        "repair_all_candidates",
        "force_pipeline",
        "overwrite_manual",
        "run_all_generated_tests",
        "run_all_contract_tests",
        "disable_llm",
        "disable_import_autofix",
        "allow_matlab_todos",
        "pause_on_applied_false",
        "skip_pipeline",
        "verbose",
        "stream_subprocess_logs",
        "enable_matlab_help",
        "sync_env",
        "force_quality_cleanup",
    }
    _LEGACY_REPAIR_BOOL_NEGATED_KEYS = {
        "auto_pull_model": "no-auto-pull-model",
        "dynamic_llm_timeout": "no-dynamic-llm-timeout",
        "enable_strict_prefilter": "disable-strict-prefilter",
    }

    def _script(self, name: str) -> Path:
        return self.script_root / name

    def _run_python_script(
        self,
        script_name: str,
        args: list[str] | None = None,
        *,
        timeout_seconds: int = 600,
        stream_output: bool = False,
    ) -> ScriptResult:
        argv = [sys.executable, "-u", str(self._script(script_name))]
        if args:
            argv.extend(args)
        started = datetime.now(tz=timezone.utc)
        if stream_output:
            proc = subprocess.Popen(
                argv,
                cwd=str(self.repo_root),
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
            timeout_s = max(1, int(timeout_seconds))
            heartbeat_s = 20
            last_heartbeat = time.perf_counter()
            started_perf = last_heartbeat

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
                    self.LOGGER.info("[%s] %s", script_name, item)

                returncode = proc.poll()
                if returncode is not None and reader_done:
                    break

                now = time.perf_counter()
                elapsed = now - started_perf
                if now - last_heartbeat >= heartbeat_s:
                    self.LOGGER.info("[%s] ... still running (%.1fs)", script_name, elapsed)
                    last_heartbeat = now

                if elapsed >= timeout_s:
                    proc.kill()
                    returncode = proc.wait()
                    stderr_text = f"hard_timeout_exceeded:{timeout_s}s"
                    self.LOGGER.error("[%s] hard timeout exceeded after %.1fs", script_name, elapsed)
                    break

                if not drained_any:
                    time.sleep(0.1)

            try:
                proc.stdout.close()
            except Exception:
                pass
            reader.join(timeout=1.0)
            stdout_text = "\n".join(merged_lines)
            if stdout_text:
                stdout_text += "\n"
        else:
            proc = subprocess.run(
                argv,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )
            returncode = proc.returncode
            stdout_text = proc.stdout
            stderr_text = proc.stderr

        elapsed = (datetime.now(tz=timezone.utc) - started).total_seconds()
        return ScriptResult(
            command=argv,
            returncode=returncode,
            stdout=stdout_text,
            stderr=stderr_text,
            elapsed_seconds=round(elapsed, 2),
        )

    def _legacy_repair_extra_args(
        self,
        repair_args: dict[str, Any],
        *,
        skip_keys: set[str] | None = None,
    ) -> list[str]:
        skip = set(skip_keys or set())
        args: list[str] = []
        for key, value in repair_args.items():
            if key in skip:
                continue
            if key in self._LEGACY_REPAIR_VALUE_KEYS:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
                continue
            if key in self._LEGACY_REPAIR_BOOL_POSITIVE_KEYS:
                if bool(value):
                    args.append(f"--{key.replace('_', '-')}")
                continue
            if key in self._LEGACY_REPAIR_BOOL_NEGATED_KEYS:
                if not bool(value):
                    args.append(f"--{self._LEGACY_REPAIR_BOOL_NEGATED_KEYS[key]}")
                continue
            self.LOGGER.debug("Ignoring unsupported legacy repair arg: %s=%r", key, value)
        return args

    @staticmethod
    def _try_extract_json(stdout: str) -> dict[str, Any]:
        text = (stdout or "").strip()
        if not text:
            return {}
        try:
            payload = json.loads(text)
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            pass

        first = text.find("{")
        last = text.rfind("}")
        if first >= 0 and last > first:
            try:
                payload = json.loads(text[first : last + 1])
                return payload if isinstance(payload, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}

    @staticmethod
    def _try_extract_json_any(stdout: str) -> Any:
        text = (stdout or "").strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        first = text.find("[")
        last = text.rfind("]")
        if first >= 0 and last > first:
            try:
                return json.loads(text[first : last + 1])
            except json.JSONDecodeError:
                return None
        first = text.find("{")
        last = text.rfind("}")
        if first >= 0 and last > first:
            try:
                return json.loads(text[first : last + 1])
            except json.JSONDecodeError:
                return None
        return None

    def search_matlab(self, directory: str) -> ScriptResult:
        return self._run_python_script("search_matlab.py", ["--directory", directory, "--json"])

    def get_function_call_graph(self, root: str, output: str) -> ScriptResult:
        return self._run_python_script(
            "get_function_call_graph.py",
            ["--root", root, "--output", output, "--json"],
        )

    def select_file_order(self, input_path: str, output_path: str) -> ScriptResult:
        return self._run_python_script(
            "select_file_order.py",
            ["--input", input_path, "--output", output_path],
        )

    def build_agent_context(self) -> ScriptResult:
        return self._run_python_script("build_agent_context.py", [])

    def select_next_function(self, roots: list[str], n: int = 1) -> tuple[ScriptResult, list[str]]:
        roots_arg = ",".join(roots)
        result = self._run_python_script(
            "select_next_functions.py",
            ["--roots", roots_arg, "-n", str(n), "--json"],
        )
        payload_any = self._try_extract_json_any(result.stdout)
        if isinstance(payload_any, list):
            out: list[str] = []
            for item in payload_any:
                if isinstance(item, dict):
                    value = item.get("matlab_file")
                    if value:
                        out.append(str(value))
                elif isinstance(item, str):
                    out.append(item)
            return result, out
        if isinstance(payload_any, dict):
            candidates = payload_any.get("candidates", [])
            if isinstance(candidates, list):
                return result, [str(x) for x in candidates]
        return result, []

    def run_repair_cycle(
        self,
        roots: list[str],
        repair_args: dict[str, Any],
        *,
        target_file: str | None = None,
    ) -> ScriptResult:
        subprocess_timeout_seconds = max(120, int(repair_args.get("repair_subprocess_timeout_seconds", 1800) or 1800))
        output_override = repair_args.get("output")
        if target_file and not output_override:
            stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            stem = Path(target_file).stem
            output_override = str((self.report_root / f"agent_repair_cycle_report_{stem}_{stamp}.json").resolve())

        # Prefer LangGraph v2 file-level repair when a target is specified.
        if target_file:
            args = [
                "--roots",
                ",".join(roots),
                "--model",
                str(repair_args.get("model", "gpt-oss:20b")),
                "--fallback-model",
                str(repair_args.get("fallback_model", "gpt-oss:20b")),
                "--max-iterations",
                str(int(repair_args.get("max_iterations", 1) or 1)),
                "--max-files-per-iteration",
                "1",
                "--target-file",
                target_file,
            ]
            if output_override:
                args.extend(["--output", str(output_override)])
            handled_keys = {
                "model",
                "fallback_model",
                "max_iterations",
                "max_files_per_iteration",
                "target_file",
                "output",
            }
            args.extend(self._legacy_repair_extra_args(repair_args, skip_keys=handled_keys))
            return self._run_python_script(
                "run_agentic_repair_cycle_legacy.py",
                args,
                timeout_seconds=subprocess_timeout_seconds,
                stream_output=bool(repair_args.get("stream_subprocess_logs", False)),
            )

        # Backward-compatible whole-cycle call.
        args = ["--roots", ",".join(roots)]
        skip_keys: set[str] = set()
        if output_override:
            args.extend(["--output", str(output_override)])
            skip_keys.add("output")
        args.extend(self._legacy_repair_extra_args(repair_args, skip_keys=skip_keys))
        return self._run_python_script(
            "run_agentic_repair_cycle_legacy.py",
            args,
            timeout_seconds=subprocess_timeout_seconds,
            stream_output=bool(repair_args.get("stream_subprocess_logs", False)),
        )

    def run_test(self, targets: list[str] | None = None) -> ScriptResult:
        cmd = [sys.executable, "-m", "pytest", "--import-mode=importlib", "-p", "no:cacheprovider"]
        if targets:
            cmd.extend(targets)
        else:
            cmd.extend([str(self.repo_root / "porting" / "tests" / "generated")])
            cmd.extend([str(self.repo_root / "porting" / "tests" / "contracts")])
        cmd.extend(["-q", "--maxfail=50"])
        started = datetime.now(tz=timezone.utc)
        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        elapsed = (datetime.now(tz=timezone.utc) - started).total_seconds()
        return ScriptResult(
            command=cmd,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            elapsed_seconds=round(elapsed, 2),
        )

    def run_parity_case(self, cases_json: str) -> ScriptResult:
        path = Path(cases_json)
        if not path.exists():
            return ScriptResult(
                command=["run_parity_case.py", "--cases-json", cases_json],
                returncode=0,
                stdout=json.dumps({"skipped": True, "reason": "missing_cases_json", "path": str(path)}),
                stderr="",
                elapsed_seconds=0.0,
            )
        return self._run_python_script("run_parity_case.py", ["--cases-json", cases_json], timeout_seconds=1800)

    def clean_project(self, clean_all: bool = False) -> ScriptResult:
        args = ["--all"] if clean_all else ["--clean-pycache", "--clean-pytest-cache"]
        return self._run_python_script("clean_project.py", args)

    def ensure_module_entrypoints(self, roots: list[str], apply: bool = True) -> ScriptResult:
        args = ["--roots", ",".join(roots), "--summary-only"]
        if apply:
            args.append("--apply")
        return self._run_python_script("ensure_module_entrypoints.py", args)

    def auto_fix_missing_imports(self, roots: list[str], apply: bool = True) -> ScriptResult:
        args = ["--roots", ",".join(roots), "--summary-only"]
        if apply:
            args.append("--apply")
        return self._run_python_script("auto_fix_missing_imports.py", args)

    def document_change(self, file_path: str, summary: str, details: dict[str, Any]) -> Path:
        self.log_root.mkdir(parents=True, exist_ok=True)
        target = self.log_root / "change_log.jsonl"
        event = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "file": file_path,
            "summary": summary,
            "details": details,
        }
        acquired = _CHANGE_LOG_LOCK.acquire(timeout=2.0)
        if acquired:
            try:
                with target.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=True) + "\n")
                return target
            finally:
                _CHANGE_LOG_LOCK.release()

        # Fallback in case of lock contention: never block a worker indefinitely.
        spill = self.log_root / f"change_log_spill_{threading.get_ident()}.jsonl"
        with spill.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=True) + "\n")
        self.LOGGER.warning("change_log lock timeout; wrote event to spill file: %s", spill)
        return spill

    _TARGET_FILE_RE = re.compile(
        r'TARGET_FILE\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]\s*/\s*"([^"]+)"'
    )
    _TEST_TAGS = {"src", "demo", "tests", "third_part"}

    @classmethod
    def _prefer_tagged_tests(cls, paths: list[str]) -> list[str]:
        """Prefer tests under contracts/<tag>/ or generated/<tag>/ when available."""
        deduped = sorted(set(paths))
        tagged: list[str] = []
        for raw in deduped:
            parts = [p.lower() for p in Path(raw).parts]
            for anchor in ("generated", "contracts"):
                if anchor in parts:
                    idx = parts.index(anchor)
                    if idx + 1 < len(parts) and parts[idx + 1] in cls._TEST_TAGS:
                        tagged.append(raw)
                        break
        if tagged:
            return sorted(set(tagged))
        return deduped

    def _build_target_test_index(self) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        tests_root = self.repo_root / "porting" / "tests"
        roots = [tests_root / "generated", tests_root / "contracts"]

        for root in roots:
            if not root.exists():
                continue
            for test_path in root.rglob("test_*.py"):
                try:
                    text = test_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                match = self._TARGET_FILE_RE.search(text)
                if not match:
                    continue
                parent_index = int(match.group(1))
                rel_target = match.group(2).replace("/", "\\")
                try:
                    resolved_root = test_path.resolve().parents[parent_index]
                except IndexError:
                    continue
                target = (resolved_root / rel_target).resolve()
                key = str(target).lower()
                index.setdefault(key, []).append(str(test_path.resolve()))

        for key in list(index.keys()):
            deduped = sorted(set(index[key]))
            index[key] = self._prefer_tagged_tests(deduped)
        return index

    def get_target_tests(self, target_file: str) -> list[str]:
        target = Path(target_file).resolve()
        if self._target_test_index is None:
            self._target_test_index = self._build_target_test_index()

        key = str(target).lower()
        direct = list(self._target_test_index.get(key, []))
        if direct:
            return direct

        # Fallback by stem if the exact path did not match.
        tests_root = self.repo_root / "porting" / "tests"
        out: list[str] = []
        name = f"test_{target.stem}.py"
        for root in [tests_root / "generated", tests_root / "contracts"]:
            if not root.exists():
                continue
            for p in root.rglob(name):
                out.append(str(p.resolve()))
        return self._prefer_tagged_tests(out)

    def read_latest_repair_report(self) -> dict[str, Any]:
        path = self.report_root / "agent_repair_cycle_report.json"
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except (OSError, json.JSONDecodeError):
            return {}
        return {}
