"""Heuristics to classify MATLAB sources for porting quality gates.

This module intentionally uses lightweight parsing only. It is used to:
- detect obvious undefined identifiers in MATLAB bodies,
- identify likely "invalid + unreferenced" sources that should not block
  the workflow with hard quality gates.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


_DECL_RE = re.compile(
    r"^\s*function\s+"
    r"(?:(?:\[(?P<outs_multi>[^\]]*)\])|(?P<out_single>[A-Za-z]\w*))?\s*=?\s*"
    r"(?P<name>[A-Za-z]\w*)\s*"
    r"(?:\((?P<args>[^)]*)\))?\s*$",
    re.IGNORECASE,
)
_TOKEN_RE = re.compile(r"(?<!\.)\b([A-Za-z]\w*)\b")
_CALL_RE = re.compile(r"(?<!\.)\b([A-Za-z]\w*)\s*\(")
_ASSIGN_RE = re.compile(r"^\s*(\[[^\]]+\]|[A-Za-z]\w*)\s*=")
_FOR_RE = re.compile(r"^\s*for\s+([A-Za-z]\w*)\s*=", re.IGNORECASE)

_MATLAB_KEYWORDS = {
    "if",
    "elseif",
    "else",
    "for",
    "while",
    "switch",
    "case",
    "otherwise",
    "end",
    "function",
    "classdef",
    "properties",
    "methods",
    "try",
    "catch",
    "return",
    "break",
    "continue",
    "global",
    "persistent",
}

_KNOWN_NAMES = {
    "pi",
    "inf",
    "nan",
    "eps",
    "i",
    "j",
    "true",
    "false",
    "nargin",
    "nargout",
    "varargin",
    "varargout",
}


def _split_comment_and_code(line: str) -> str:
    """Strip MATLAB comments while respecting single-quoted strings."""
    in_quote = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "'":
            if in_quote and i + 1 < len(line) and line[i + 1] == "'":
                i += 2
                continue
            in_quote = not in_quote
        elif ch == "%" and not in_quote:
            return line[:i]
        i += 1
    return line


def _strip_single_quoted_strings(line: str) -> str:
    return re.sub(r"'([^']|'')*'", " ", line)


def _parse_decl(line: str) -> tuple[str, list[str], list[str]]:
    match = _DECL_RE.match(line.strip())
    if not match:
        return "unknown_function", [], []
    outs_raw = match.group("outs_multi") or match.group("out_single") or ""
    args_raw = match.group("args") or ""
    name = match.group("name") or "unknown_function"
    if match.group("outs_multi"):
        outs = [x.strip() for x in outs_raw.split(",") if x.strip()]
    elif outs_raw.strip():
        outs = [outs_raw.strip()]
    else:
        outs = []
    args = [x.strip() for x in args_raw.split(",") if x.strip()]
    return name, args, outs


def analyze_matlab_file(path: Path) -> dict[str, Any]:
    """Return a conservative analysis of obvious undefined identifiers."""
    if not path.exists():
        return {
            "file_found": False,
            "function_name": path.stem,
            "has_discarded_args": False,
            "undefined_identifiers": [],
            "invalid_source": False,
        }

    text = path.read_text(encoding="ISO-8859-1", errors="ignore")
    lines = text.splitlines()

    function_name = path.stem
    args: list[str] = []
    rets: list[str] = []
    has_discarded_args = False

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("function "):
            function_name, args, rets = _parse_decl(stripped)
            has_discarded_args = any(a == "~" for a in args)
            break

    declared: set[str] = {a for a in args if a and a != "~"} | {r for r in rets if r}
    called: set[str] = set()
    used: set[str] = set()

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        code = _split_comment_and_code(raw_line)
        code = _strip_single_quoted_strings(code).strip()
        if not code:
            continue

        decl_match = _ASSIGN_RE.match(code)
        if decl_match:
            lhs = decl_match.group(1).strip()
            if lhs.startswith("[") and lhs.endswith("]"):
                declared.update(x.strip() for x in lhs[1:-1].split(",") if x.strip())
            else:
                declared.add(lhs)

        for_match = _FOR_RE.match(code)
        if for_match:
            declared.add(for_match.group(1))

        calls_here = {m.group(1) for m in _CALL_RE.finditer(code)}
        called.update(calls_here)

        for token in _TOKEN_RE.findall(code):
            low = token.lower()
            if low in _MATLAB_KEYWORDS:
                continue
            used.add(token)

    undefined = sorted(
        token
        for token in used
        if token not in declared
        and token not in called
        and token != function_name
        and token.lower() not in _KNOWN_NAMES
    )

    invalid_source = bool(undefined)
    return {
        "file_found": True,
        "function_name": function_name,
        "has_discarded_args": bool(has_discarded_args),
        "undefined_identifiers": undefined,
        "invalid_source": invalid_source,
    }


@lru_cache(maxsize=4)
def _referenced_basenames(repo_root_text: str) -> set[str]:
    repo_root = Path(repo_root_text)
    path = repo_root / "script_outputs" / "all_files_function_call_graph.json"
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if not isinstance(payload, dict):
        return set()
    referenced: set[str] = set()
    for value in payload.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    referenced.add(Path(item).name.lower())
    return referenced


def is_unreferenced_in_call_graph(matlab_file: Path, repo_root: Path) -> bool | None:
    """Return True/False when call-graph data exists, else None."""
    referenced = _referenced_basenames(str(repo_root.resolve()))
    if not referenced:
        return None
    return matlab_file.name.lower() not in referenced


def matlab_quality_for_python_file(python_file: Path, repo_root: Path) -> dict[str, Any]:
    matlab_file = python_file.with_suffix(".m")
    analysis = analyze_matlab_file(matlab_file)
    unreferenced = is_unreferenced_in_call_graph(matlab_file, repo_root) if analysis.get("file_found") else None
    invalid = bool(analysis.get("invalid_source", False))
    special_case = invalid and (unreferenced is True)

    return {
        "matlab_file_found": bool(analysis.get("file_found", False)),
        "matlab_file": str(matlab_file),
        "invalid_source": invalid,
        "has_discarded_args": bool(analysis.get("has_discarded_args", False)),
        "undefined_identifiers": list(analysis.get("undefined_identifiers", [])),
        "unreferenced_in_call_graph": unreferenced,
        "special_case_invalid_unreferenced": special_case,
    }
