#!/usr/bin/env python3
"""Deterministic strict MATLAB -> Python base porter.

This script intentionally does not use any LLM. It creates a stable,
compilable Python baseline from a MATLAB file:
- preserves MATLAB comments as Python comments (comment parity baseline),
- preserves function name/arity and return variable names,
- auto-imports known helpers from matlab_native / porting.lib.utils when used.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MATLAB_DECL_RE = re.compile(
    r"^\s*function\s+"
    r"(?:(?:\[(?P<outs_multi>[^\]]*)\])|(?P<out_single>[A-Za-z]\w*))?\s*=?\s*"
    r"(?P<name>[A-Za-z]\w*)\s*"
    r"(?:\((?P<args>[^)]*)\))?\s*$",
    re.IGNORECASE,
)
MATLAB_CALL_RE = re.compile(r"(?<!\.)\b([A-Za-z]\w*)\s*\(")
MEX_WRAPPER_LINE_RE = re.compile(
    r"^(?:\[[^\]]+\]\s*=|[A-Za-z]\w+\s*=)?\s*(?P<native>[A-Za-z]\w*_mex)\s*(?:\((?P<args>.*)\))?\s*;?$",
    re.IGNORECASE,
)

try:
    from monalisa_py.porting.lib.matlab_source_quality import matlab_quality_for_python_file
except ImportError:
    try:
        from porting.lib.matlab_source_quality import matlab_quality_for_python_file
    except ImportError:
        def matlab_quality_for_python_file(python_file: Path, repo_root: Path) -> dict[str, Any]:
            return {
                "matlab_file_found": python_file.with_suffix(".m").exists(),
                "invalid_source": False,
                "undefined_identifiers": [],
                "unreferenced_in_call_graph": None,
                "special_case_invalid_unreferenced": False,
            }


def _parse_decl(line: str, default_name: str) -> tuple[str, list[str], list[str]]:
    text = line.strip()
    if not text.lower().startswith("function"):
        return default_name, [], []

    body = text[len("function") :].strip()
    if not body:
        return default_name, [], []

    if "%" in body:
        body = body.split("%", 1)[0].strip()

    returns: list[str] = []
    if "=" in body:
        left, right = body.split("=", 1)
        left = left.strip()
        body = right.strip()
        if left.startswith("[") and left.endswith("]"):
            returns = [x.strip() for x in left[1:-1].split(",") if x.strip()]
        elif left:
            returns = [left]

    name_match = re.match(r"^([A-Za-z]\w*)\s*(?:\((?P<args>[^)]*)\))?$", body)
    if not name_match:
        return default_name, [], returns

    name = name_match.group(1) or default_name
    args_raw = (name_match.group("args") or "").strip()
    args = [x.strip() for x in args_raw.split(",") if x.strip()]
    return name, args, returns


def _sanitize_identifier(name: str, *, prefix: str) -> str:
    cleaned = re.sub(r"\W+", "_", (name or "").strip()).strip("_")
    if not cleaned:
        cleaned = prefix
    if cleaned[0].isdigit():
        cleaned = f"{prefix}_{cleaned}"
    if cleaned in {"None", "True", "False", "class", "def", "return", "for", "while", "if"}:
        cleaned = f"{prefix}_{cleaned}"
    return cleaned


def _sanitize_arg_list(args: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for idx, raw in enumerate(args):
        if raw == "~":
            base = f"unused_{idx + 1}"
        else:
            base = _sanitize_identifier(raw, prefix="arg")
        candidate = base
        suffix = 2
        while candidate in seen:
            candidate = f"{base}_{suffix}"
            suffix += 1
        seen.add(candidate)
        out.append(candidate)
    return out


def _sanitize_return_list(returns: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for idx, raw in enumerate(returns):
        base = _sanitize_identifier(raw, prefix=f"out_{idx + 1}")
        candidate = base
        suffix = 2
        while candidate in seen:
            candidate = f"{base}_{suffix}"
            suffix += 1
        seen.add(candidate)
        out.append(candidate)
    return out


def _extract_matlab_comments_and_body(matlab_text: str) -> tuple[list[str], list[str]]:
    comments: list[str] = []
    body_lines: list[str] = []
    for line in matlab_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("%"):
            comment = stripped.lstrip("%").strip()
            comments.append(comment if comment else "")
            continue
        if stripped.lower().startswith("function "):
            continue
        body_lines.append(stripped)
    return comments, body_lines


def _extract_called_names(matlab_text: str) -> set[str]:
    names: set[str] = set()
    for line in matlab_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        for m in MATLAB_CALL_RE.finditer(stripped):
            names.add(m.group(1))
    return names


def _is_under_mex_folder(path: Path) -> bool:
    return any(part.lower() == "mex" for part in path.parts)


def _detect_trivial_mex_wrapper(matlab_file: Path, body_lines: list[str]) -> dict[str, str] | None:
    """Detect very small MATLAB wrappers that only delegate to a single *_mex call."""
    if not _is_under_mex_folder(matlab_file):
        return None

    executable = [
        line.strip()
        for line in body_lines
        if line.strip() and line.strip().lower() not in {"end", "return"}
    ]
    if len(executable) != 1:
        return None

    candidate = executable[0]
    match = MEX_WRAPPER_LINE_RE.match(candidate)
    if not match:
        return None

    return {
        "native_function": str(match.group("native") or "").strip(),
        "original_line": candidate,
    }


def _load_defined_names(py_file: Path) -> set[str]:
    if not py_file.exists():
        return set()
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()
    out: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
    return out


def _resolve_py_paths(repo_root: Path) -> tuple[Path, Path]:
    matlab_native = repo_root / "third_part" / "matlab_compat" / "matlab_native.py"
    utils_mod = repo_root / "porting" / "lib" / "utils.py"
    return matlab_native, utils_mod


def _build_imports(called_names: set[str], repo_root: Path) -> list[str]:
    matlab_native_file, utils_file = _resolve_py_paths(repo_root)
    matlab_native_names = _load_defined_names(matlab_native_file)
    utils_names = _load_defined_names(utils_file)

    mn_used = sorted(name for name in called_names if name in matlab_native_names)
    ut_used = sorted(name for name in called_names if name in utils_names)

    imports: list[str] = ["from __future__ import annotations"]
    if mn_used:
        imports.append(f"from third_part.matlab_compat.matlab_native import {', '.join(mn_used)}")
    if ut_used:
        imports.append(f"from porting.lib.utils import {', '.join(ut_used)}")
    return imports


def build_strict_port_result(
    *,
    matlab_file: Path,
    python_file: Path,
    repo_root: Path,
) -> dict[str, Any]:
    matlab_text = matlab_file.read_text(encoding="ISO-8859-1", errors="ignore")
    lines = matlab_text.splitlines()
    decl_line = next((ln for ln in lines if ln.strip().lower().startswith("function ")), "")
    function_name, args_raw, returns_raw = _parse_decl(decl_line, default_name=matlab_file.stem)
    args = _sanitize_arg_list(args_raw)
    returns = _sanitize_return_list(returns_raw)
    comments, body_lines = _extract_matlab_comments_and_body(matlab_text)
    called_names = _extract_called_names(matlab_text)
    imports = _build_imports(called_names, repo_root)
    mex_wrapper = _detect_trivial_mex_wrapper(matlab_file, body_lines)
    matlab_quality = matlab_quality_for_python_file(python_file, repo_root)
    special_case_invalid_unreferenced = bool(matlab_quality.get("special_case_invalid_unreferenced", False))

    body: list[str] = []
    body.append(f'def {function_name}({", ".join(args)}):')
    if mex_wrapper:
        native_fn = mex_wrapper.get("native_function", "")
        original_line = mex_wrapper.get("original_line", "")
        body.append('    """Skipped MATLAB MEX wrapper."""')
        if comments:
            body.append("    # MATLAB comments")
            for c in comments:
                body.append(f"    # {c}")
        if original_line:
            body.append(f"    # MATLAB wrapper line: {original_line}")
        body.append("    raise NotImplementedError(")
        body.append('        "MATLAB MEX wrapper skipped during porting. "')
        body.append(
            f'        "Underlying native function \'{native_fn}\' has no Python equivalent yet."'
        )
        body.append("    )")
        status = "skipped_mex_wrapper"
        skip_reason = "simple MATLAB wrapper around native MEX function"
        native_backend_required = True
        native_function = native_fn
    elif special_case_invalid_unreferenced:
        imports = ["from __future__ import annotations"]
        undefined_names = ", ".join(matlab_quality.get("undefined_identifiers", [])[:8])
        body.append('    """Deterministic placeholder for invalid/unreferenced MATLAB source."""')
        if comments:
            body.append("    # MATLAB comments")
            for c in comments:
                body.append(f"    # {c}")
        body.append(
            "    # MATLAB source appears invalid and unreferenced in call graph; "
            f"undefined identifiers: {undefined_names or 'n/a'}."
        )
        body.append("    # Keeping a safe placeholder prevents false workflow retries.")
        if returns:
            for rv in returns:
                body.append(f"    {rv} = None")
            if len(returns) == 1:
                body.append(f"    return {returns[0]}")
            else:
                body.append(f"    return {', '.join(returns)}")
        else:
            body.append("    return None")
        status = "invalid_matlab_source_unreferenced"
        skip_reason = "invalid_matlab_source_unreferenced"
        native_backend_required = False
        native_function = ""
    else:
        body.append('    """Strict deterministic baseline port from MATLAB."""')
        if comments:
            body.append("    # MATLAB comments")
            for c in comments:
                body.append(f"    # {c}")
        if body_lines:
            body.append("    # MATLAB body snapshot (untranslated, kept for parity context)")
            for ln in body_lines[:120]:
                body.append(f"    # MATLAB: {ln}")
            if len(body_lines) > 120:
                body.append(f"    # MATLAB: ... ({len(body_lines) - 120} more lines)")
        body.append("    # TODO(matlab-logic): translate MATLAB logic faithfully.")
        if returns:
            for rv in returns:
                body.append(f"    {rv} = None")
            if len(returns) == 1:
                body.append(f"    return {returns[0]}")
            else:
                body.append(f"    return {', '.join(returns)}")
        else:
            body.append("    return None")
        status = "strict_baseline"
        skip_reason = ""
        native_backend_required = False
        native_function = ""

    generated = "\n".join(imports + ["", ""] + body).rstrip() + "\n"
    previous = ""
    if python_file.exists():
        previous = python_file.read_text(encoding="utf-8", errors="ignore")

    changed = previous != generated
    return {
        "matlab_file": str(matlab_file.resolve()),
        "python_file": str(python_file.resolve()),
        "function_name": function_name,
        "args": args,
        "returns": returns,
        "comment_lines_matlab": len(comments),
        "body_lines_matlab": len(body_lines),
        "imports": imports,
        "changed": changed,
        "status": status,
        "skip_reason": skip_reason,
        "native_backend_required": native_backend_required,
        "native_function": native_function,
        "matlab_quality": matlab_quality,
        "generated_code": generated,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic strict MATLAB -> Python baseline porter.")
    parser.add_argument("--matlab-file", required=True, help="Path to MATLAB source file (.m).")
    parser.add_argument("--python-file", default="", help="Path to Python target file (.py).")
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Apply generated code to --python-file.")
    parser.add_argument("--output", default="../reports/strict_port_base_report.json", help="Output report JSON path.")
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary only.")
    args = parser.parse_args()

    base = SCRIPT_DIR
    repo_root = (base / args.repo_root).resolve()
    matlab_file = (repo_root / args.matlab_file).resolve() if not Path(args.matlab_file).is_absolute() else Path(args.matlab_file).resolve()
    if not matlab_file.exists() or matlab_file.suffix.lower() != ".m":
        raise SystemExit(f"MATLAB file not found or invalid: {matlab_file}")

    if args.python_file.strip():
        python_file = (repo_root / args.python_file).resolve() if not Path(args.python_file).is_absolute() else Path(args.python_file).resolve()
    else:
        try:
            rel = matlab_file.relative_to(repo_root)
            python_file = (repo_root / rel.with_suffix(".py")).resolve()
        except ValueError:
            python_file = matlab_file.with_suffix(".py").resolve()

    report = build_strict_port_result(matlab_file=matlab_file, python_file=python_file, repo_root=repo_root)
    if args.apply:
        python_file.parent.mkdir(parents=True, exist_ok=True)
        python_file.write_text(str(report["generated_code"]), encoding="utf-8")

    output = (base / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output_payload = dict(report)
    output_payload["mode"] = "apply" if args.apply else "dry-run"
    output.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    if args.summary_only:
        compact = {
            "mode": output_payload["mode"],
            "matlab_file": output_payload["matlab_file"],
            "python_file": output_payload["python_file"],
            "changed": output_payload["changed"],
            "function_name": output_payload["function_name"],
            "imports_count": len(output_payload["imports"]),
            "comment_lines_matlab": output_payload["comment_lines_matlab"],
            "status": output_payload.get("status", ""),
            "native_function": output_payload.get("native_function", ""),
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(output_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
