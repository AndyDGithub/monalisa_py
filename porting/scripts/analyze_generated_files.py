#!/usr/bin/env python3
"""Analyze generated Python files and report translation health."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


COMPILE_ERROR_RE = re.compile(r"SyntaxError:\s*([^|]+)")
TRUE_FALSE_CALL_RE = re.compile(r"\b(?:True|False)\s*\(")
TODO_MARKER_RE = re.compile(r"#\s*TODO\(matlab-(?:line|control)\):")
MEX_WRAPPER_STUB_RE = re.compile(r"Skipped MATLAB MEX wrapper|MATLAB MEX wrapper skipped during porting")


def analyze_roots(src_roots: list[Path]) -> dict:
    files: list[Path] = []
    for root in src_roots:
        if root.exists():
            files.extend(sorted(root.rglob("*.py")))
    # Deduplicate in case of overlap.
    files = sorted({p.resolve(): p for p in files}.values(), key=lambda p: str(p))

    fallback_files: list[str] = []
    auto_generated_files: list[str] = []
    manual_files: list[str] = []
    risky_true_false_calls: list[str] = []
    matlab_todo_marker_sites: list[str] = []
    mex_wrapper_stub_files: list[str] = []
    compile_error_kinds: Counter = Counter()

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = None
        for root in src_roots:
            try:
                rel = str(path.relative_to(root)).replace("\\", "/")
                rel = f"{root.name}/{rel}"
                break
            except ValueError:
                continue
        if rel is None:
            rel = str(path)

        if "Auto-generated from MATLAB source" in text:
            auto_generated_files.append(rel)
        else:
            manual_files.append(rel)

        if "# compile_error:" in text:
            fallback_files.append(rel)
            match = COMPILE_ERROR_RE.search(text)
            kind = match.group(1).strip() if match else "unknown_syntax_error"
            compile_error_kinds[kind] += 1
        if MEX_WRAPPER_STUB_RE.search(text):
            mex_wrapper_stub_files.append(rel)

        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                if TODO_MARKER_RE.search(line):
                    matlab_todo_marker_sites.append(f"{rel}: {line.strip()}")
                continue
            if TRUE_FALSE_CALL_RE.search(line):
                risky_true_false_calls.append(f"{rel}: {line.strip()}")

    return {
        "summary": {
            "python_files": len(files),
            "auto_generated_files": len(auto_generated_files),
            "manual_files": len(manual_files),
            "fallback_stub_files": len(fallback_files),
            "risky_true_false_calls": len(risky_true_false_calls),
            "matlab_todo_markers": len(matlab_todo_marker_sites),
            "mex_wrapper_stub_files": len(mex_wrapper_stub_files),
        },
        "compile_error_top_kinds": dict(compile_error_kinds.most_common(15)),
        "fallback_stub_files": fallback_files,
        "risky_true_false_call_sites": risky_true_false_calls,
        "matlab_todo_marker_sites": matlab_todo_marker_sites,
        "mex_wrapper_stub_files": mex_wrapper_stub_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze generated Python files.")
    parser.add_argument(
        "--roots",
        default="../../src",
        help="Comma-separated source roots to scan (e.g. ../../src,../../demo).",
    )
    parser.add_argument("--output", default="../reports/generated_files_analysis.json", help="Output JSON report.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    src_roots = [(base / token.strip()).resolve() for token in args.roots.split(",") if token.strip()]
    out = (base / args.output).resolve()

    report = analyze_roots(src_roots)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    print(f"Analyzed {summary['python_files']} files under {len(src_roots)} root(s)")
    print(f"Fallback stubs: {summary['fallback_stub_files']}")
    print(f"Risky True/False calls: {summary['risky_true_false_calls']}")
    print(f"MATLAB TODO markers: {summary['matlab_todo_markers']}")
    print(f"MEX wrapper stubs: {summary['mex_wrapper_stub_files']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
