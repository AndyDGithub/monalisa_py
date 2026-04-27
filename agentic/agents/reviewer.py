from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
from types import SimpleNamespace
from typing import Any

from agentic.state import PortingGraphState
from agentic.tools import LegacyToolbox

try:
    from porting.lib.matlab_source_quality import matlab_quality_for_python_file
except Exception:  # pragma: no cover - optional runtime helper
    def matlab_quality_for_python_file(python_file: Path, repo_root: Path) -> dict[str, Any]:
        return {
            "matlab_file_found": python_file.with_suffix(".m").exists(),
            "matlab_file": str(python_file.with_suffix(".m")),
            "invalid_source": False,
            "has_discarded_args": False,
            "undefined_identifiers": [],
            "unreferenced_in_call_graph": None,
            "special_case_invalid_unreferenced": False,
        }


@dataclass(slots=True)
class ReviewerAgent:
    toolbox: LegacyToolbox
    _MATLAB_RUNTIME_TOKEN_RE = re.compile(r"\b(inputname|assignin|evalin)\b")

    @staticmethod
    def _source_quality_flags(file_path: str, *, allow_matlab_todos: bool) -> dict[str, Any]:
        target = Path(file_path)
        if not target.exists():
            return {"file_missing": True, "matlab_todo_markers": 0, "fallback_stub": False}

        text = target.read_text(encoding="utf-8", errors="ignore")
        todo_markers = text.count("TODO(matlab")
        fallback_stub = (
            "Fallback stub generated because automatic translation did not compile yet" in text
            or "# compile_error:" in text
        )
        untranslated_snapshot = (
            "MATLAB body snapshot (untranslated" in text
            or "translate MATLAB logic faithfully" in text
        )
        path_tokens = {part.lower() for part in target.parts}
        is_mex_wrapper = "mex" in path_tokens
        not_implemented_count = text.count("NotImplementedError(")
        pass_only_callable_count = 0
        try:
            tree = ast.parse(text)
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
        except SyntaxError:
            # Syntax issues are already covered by tests/import checks.
            pass

        if allow_matlab_todos:
            todo_markers = 0
        return {
            "file_missing": False,
            "matlab_todo_markers": int(todo_markers),
            "fallback_stub": bool(fallback_stub),
            "untranslated_snapshot": bool(untranslated_snapshot),
            "is_mex_wrapper": bool(is_mex_wrapper),
            "not_implemented_count": int(not_implemented_count),
            "pass_only_callable_count": int(pass_only_callable_count),
        }

    @staticmethod
    def _comment_parity_flags(file_path: str) -> dict[str, Any]:
        py_path = Path(file_path)
        if not py_path.exists():
            return {
                "matlab_file_found": False,
                "matlab_comment_lines": 0,
                "python_comment_lines": 0,
                "comment_parity_ok": True,
                "reason": "python_file_missing",
            }

        matlab_path = py_path.with_suffix(".m")
        if not matlab_path.exists():
            return {
                "matlab_file_found": False,
                "matlab_comment_lines": 0,
                "python_comment_lines": sum(
                    1 for line in py_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                    if line.strip().startswith("#")
                ),
                "comment_parity_ok": True,
                "reason": "matlab_peer_missing",
            }

        matlab_text = matlab_path.read_text(encoding="ISO-8859-1", errors="ignore")
        python_text = py_path.read_text(encoding="utf-8", errors="ignore")
        matlab_comment_lines = sum(1 for line in matlab_text.splitlines() if line.strip().startswith("%"))
        python_comment_lines = sum(1 for line in python_text.splitlines() if line.strip().startswith("#"))

        # Light-but-actionable parity heuristic:
        # - if MATLAB has no comments, parity is trivially OK;
        # - if MATLAB has comments, require at least some Python comments.
        if matlab_comment_lines <= 0:
            parity_ok = True
        elif python_comment_lines <= 0:
            parity_ok = False
        else:
            ratio = python_comment_lines / max(1, matlab_comment_lines)
            parity_ok = ratio >= 0.15 or python_comment_lines >= min(6, matlab_comment_lines)

        return {
            "matlab_file_found": True,
            "matlab_comment_lines": int(matlab_comment_lines),
            "python_comment_lines": int(python_comment_lines),
            "comment_parity_ok": bool(parity_ok),
            "reason": "",
        }

    def _runtime_semantics_flags(self, file_path: str) -> dict[str, Any]:
        py_path = Path(file_path)
        if not py_path.exists():
            return {
                "matlab_file_found": False,
                "required_tokens": [],
                "python_support_ok": True,
                "python_hits": [],
                "reason": "python_file_missing",
            }

        matlab_path = py_path.with_suffix(".m")
        if not matlab_path.exists():
            return {
                "matlab_file_found": False,
                "required_tokens": [],
                "python_support_ok": True,
                "python_hits": [],
                "reason": "matlab_peer_missing",
            }

        matlab_text = matlab_path.read_text(encoding="ISO-8859-1", errors="ignore")
        required_tokens = sorted(set(self._MATLAB_RUNTIME_TOKEN_RE.findall(matlab_text)))
        if not required_tokens:
            return {
                "matlab_file_found": True,
                "required_tokens": [],
                "python_support_ok": True,
                "python_hits": [],
                "reason": "",
            }

        python_text = py_path.read_text(encoding="utf-8", errors="ignore")
        python_hits: list[str] = []

        if "matlab_runtime_metadata" in python_text:
            python_hits.append("import:matlab_runtime_metadata")

        token_checks = {
            "inputname": re.compile(r"\b(resolve_inputname|inputname)\b"),
            "assignin": re.compile(r"\b(assignin_runtime|assignin)\b"),
            "evalin": re.compile(r"\b(evalin_runtime|evalin)\b"),
        }

        missing: list[str] = []
        for token in required_tokens:
            matcher = token_checks.get(token)
            if matcher is None:
                continue
            if matcher.search(python_text):
                python_hits.append(f"token:{token}")
            else:
                missing.append(token)

        return {
            "matlab_file_found": True,
            "required_tokens": required_tokens,
            "missing_tokens": missing,
            "python_hits": python_hits,
            "python_support_ok": len(missing) == 0,
            "reason": "",
        }

    def _matlab_source_quality_flags(self, file_path: str, repo_root: Path) -> dict[str, Any]:
        py_path = Path(file_path)
        if not py_path.exists():
            return {
                "matlab_file_found": False,
                "matlab_file": str(py_path.with_suffix(".m")),
                "invalid_source": False,
                "has_discarded_args": False,
                "undefined_identifiers": [],
                "unreferenced_in_call_graph": None,
                "special_case_invalid_unreferenced": False,
            }
        return matlab_quality_for_python_file(py_path, repo_root)

    def review_current(self, state: PortingGraphState) -> dict[str, Any]:
        current_file = state.get("current_file", "")
        if not current_file:
            return {
                "last_repair_result": {
                    "current_file": "",
                    "reviewer_verdict": "needs_retry",
                    "detail": "no_current_file",
                }
            }

        prior = dict(state.get("last_repair_result", {}))
        if str(prior.get("repair_finished_reason", "")) == "paused_on_applied_false":
            return {
                "last_repair_result": {
                    "current_file": current_file,
                    "reviewer_verdict": "rejected",
                    "test_returncode": 1,
                    "parity_returncode": 1,
                    "repair_finished_reason": "paused_on_applied_false",
                    "detail": "paused_on_applied_false",
                }
            }

        test_targets = self.toolbox.get_target_tests(current_file)
        test_scope = "targeted"
        if test_targets:
            test_result = self.toolbox.run_test(test_targets)
        else:
            # Do not run the full generated/contracts suite for a single-file
            # review when no direct tests are mapped for the target.
            test_scope = "none"
            test_result = SimpleNamespace(
                returncode=0,
                stdout="",
                stderr="",
                elapsed_seconds=0.0,
            )
        parity_cases_path = str(self.toolbox.report_root / "parity_cases.json")
        parity_result = self.toolbox.run_parity_case(parity_cases_path)
        forced_target_error = str(prior.get("forced_target_error", ""))
        repair_args = dict(state.get("repair_args", {}))
        allow_matlab_todos = bool(repair_args.get("allow_matlab_todos", False))
        quality = self._source_quality_flags(current_file, allow_matlab_todos=allow_matlab_todos)
        comment_parity = self._comment_parity_flags(current_file)
        runtime_semantics = self._runtime_semantics_flags(current_file)
        repo_root = Path(str(state.get("repo_root", str(self.toolbox.repo_root))))
        matlab_quality = self._matlab_source_quality_flags(current_file, repo_root)

        enforce_comment_parity = bool(repair_args.get("enforce_comment_parity", True))
        enforce_matlab_todo_gate = bool(repair_args.get("enforce_matlab_todo_gate", True)) and not allow_matlab_todos
        enforce_fallback_stub_gate = bool(repair_args.get("enforce_fallback_stub_gate", True))
        enforce_untranslated_placeholder_gate = bool(
            repair_args.get("enforce_untranslated_placeholder_gate", True)
        )
        enforce_test_scope_gate = bool(repair_args.get("enforce_test_scope_gate", True))
        enforce_runtime_metadata_gate = bool(repair_args.get("enforce_runtime_metadata_gate", True))
        special_case_invalid_unreferenced = bool(matlab_quality.get("special_case_invalid_unreferenced", False))

        quality_blockers: list[str] = []
        if enforce_fallback_stub_gate and bool(quality.get("fallback_stub", False)) and not special_case_invalid_unreferenced:
            quality_blockers.append("fallback_stub")
        if (
            enforce_matlab_todo_gate
            and int(quality.get("matlab_todo_markers", 0)) > 0
            and not special_case_invalid_unreferenced
        ):
            quality_blockers.append("matlab_todo_markers")
        if (
            enforce_comment_parity
            and not bool(comment_parity.get("comment_parity_ok", True))
            and not special_case_invalid_unreferenced
        ):
            quality_blockers.append("comment_parity")
        if (
            enforce_untranslated_placeholder_gate
            and bool(quality.get("untranslated_snapshot", False))
            and not special_case_invalid_unreferenced
        ):
            quality_blockers.append("untranslated_snapshot")
        if (
            enforce_untranslated_placeholder_gate
            and int(quality.get("pass_only_callable_count", 0)) > 0
            and not special_case_invalid_unreferenced
            and not bool(quality.get("is_mex_wrapper", False))
        ):
            quality_blockers.append("pass_only_callable")
        if (
            enforce_untranslated_placeholder_gate
            and int(quality.get("not_implemented_count", 0)) > 0
            and not special_case_invalid_unreferenced
            and not bool(quality.get("is_mex_wrapper", False))
        ):
            quality_blockers.append("not_implemented_stub")
        if (
            enforce_runtime_metadata_gate
            and bool(runtime_semantics.get("required_tokens", []))
            and not bool(runtime_semantics.get("python_support_ok", True))
            and not special_case_invalid_unreferenced
        ):
            quality_blockers.append("runtime_metadata_semantics")

        if forced_target_error == "target_file_not_found":
            verdict = "rejected"
        elif bool(quality.get("file_missing", False)):
            verdict = "rejected"
        elif test_scope == "none" and enforce_test_scope_gate and not special_case_invalid_unreferenced:
            verdict = "needs_retry"
        elif test_result.returncode == 0 and parity_result.returncode == 0:
            verdict = "needs_retry" if quality_blockers else "approved"
        elif test_result.returncode != 0 and parity_result.returncode == 0:
            verdict = "needs_retry"
        else:
            verdict = "rejected"

        detail = {
            "repair_finished_reason": str(prior.get("repair_finished_reason", "")),
            "repair_returncode": prior.get("repair_returncode"),
            "repair_applied_count": prior.get("repair_applied_count"),
            "repair_backend": str(prior.get("repair_backend", "")),
            "test_returncode": test_result.returncode,
            "parity_returncode": parity_result.returncode,
            "test_scope": test_scope,
            "test_target_count": len(test_targets),
            "test_targets": test_targets[:10],
            "forced_target_error": forced_target_error,
            "source_quality": quality,
            "comment_parity": comment_parity,
            "runtime_semantics": runtime_semantics,
            "matlab_source_quality": matlab_quality,
            "quality_blockers": quality_blockers,
            "quality_gate_config": {
                "enforce_fallback_stub_gate": enforce_fallback_stub_gate,
                "enforce_matlab_todo_gate": enforce_matlab_todo_gate,
                "enforce_comment_parity": enforce_comment_parity,
                "enforce_untranslated_placeholder_gate": enforce_untranslated_placeholder_gate,
                "enforce_test_scope_gate": enforce_test_scope_gate,
                "enforce_runtime_metadata_gate": enforce_runtime_metadata_gate,
            },
            "test_stdout_tail": test_result.stdout[-2500:],
            "test_stderr_tail": test_result.stderr[-2500:],
            "parity_stdout_tail": parity_result.stdout[-1500:],
            "parity_stderr_tail": parity_result.stderr[-1500:],
        }

        return {
            "last_repair_result": {
                **prior,
                "current_file": current_file,
                "reviewer_verdict": verdict,
                "test_returncode": test_result.returncode,
                "parity_returncode": parity_result.returncode,
                "detail": str(detail),
            }
        }
