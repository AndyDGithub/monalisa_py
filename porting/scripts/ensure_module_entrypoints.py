#!/usr/bin/env python3
"""Ensure each module exports an entrypoint matching its filename stem.

When LLM repairs rewrite a module and rename the top-level function
(e.g. `unknown_function`), imports like:
  from ...bmSensa import bmSensa
fail even if logic exists.

This script adds deterministic aliases:
  bmSensa = unknown_function
when safe.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def _iter_py_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend([p for p in root.rglob("*.py") if p.is_file()])
    dedup = {p.resolve(): p for p in files}
    return sorted(dedup.values(), key=lambda p: str(p))


def _collect_module_level_functions(statements: list[ast.stmt], out: list[str]) -> None:
    for node in statements:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(node.name)
            continue
        if isinstance(node, ast.Try):
            _collect_module_level_functions(node.body, out)
            _collect_module_level_functions(node.orelse, out)
            _collect_module_level_functions(node.finalbody, out)
            for handler in node.handlers:
                _collect_module_level_functions(handler.body, out)
            continue
        if isinstance(node, ast.If):
            _collect_module_level_functions(node.body, out)
            _collect_module_level_functions(node.orelse, out)
            continue
        if isinstance(node, (ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)):
            _collect_module_level_functions(node.body, out)
            _collect_module_level_functions(getattr(node, "orelse", []), out)
            continue


def _module_level_function_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    body = getattr(tree, "body", [])
    if isinstance(body, list):
        _collect_module_level_functions(body, names)
    return names


def _choose_alias_target(function_names: list[str], expected_name: str) -> str | None:
    if expected_name in function_names:
        return None
    if "unknown_function" in function_names:
        return "unknown_function"
    public = [n for n in function_names if not n.startswith("_")]
    if len(public) == 1:
        return public[0]
    return None


def ensure_module_entrypoints(roots: list[Path], repo_root: Path, apply: bool) -> dict:
    files = _iter_py_files(roots)
    scanned = 0
    candidates: list[str] = []
    changed: list[str] = []

    for path in files:
        if path.name == "__init__.py":
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue

        stem = path.stem
        fn_names = _module_level_function_names(tree)
        target = _choose_alias_target(fn_names, stem)
        if not target:
            continue

        alias_line = f"{stem} = {target}"
        if alias_line in text:
            continue

        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        candidates.append(rel)
        if apply:
            trailer = "\n\n# Auto-generated entrypoint alias for import compatibility\n" + alias_line + "\n"
            path.write_text(text.rstrip() + trailer, encoding="utf-8")
            changed.append(rel)

    return {
        "mode": "apply" if apply else "dry-run",
        "python_files_scanned": scanned,
        "alias_candidates": len(candidates),
        "aliases_changed": len(changed),
        "changed_files": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure module entrypoint aliases match filename stems.")
    parser.add_argument(
        "--roots",
        default="../../src,../../demo,../../tests,../../third_part",
        help="Comma-separated roots to scan.",
    )
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Apply changes.")
    parser.add_argument("--output", default="../reports/entrypoint_alias_report.json", help="Output report.")
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    roots = [(base / t.strip()).resolve() for t in args.roots.split(",") if t.strip()]
    repo_root = (base / args.repo_root).resolve()
    report = ensure_module_entrypoints(roots=roots, repo_root=repo_root, apply=args.apply)

    output = (base / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.summary_only:
        compact = {
            "mode": report["mode"],
            "python_files_scanned": report["python_files_scanned"],
            "alias_candidates": report["alias_candidates"],
            "aliases_changed": report["aliases_changed"],
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
