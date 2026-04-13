#!/usr/bin/env python3
"""Sanitize optional third-party imports to keep modules importable.

Current rule set:
- Wrap top-level `import pydicom` (and alias form) in try/except so
  module import does not fail when dependency is missing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IMPORT_PYDICOM_RE = re.compile(r"^(?P<indent>\s*)import\s+pydicom(?:\s+as\s+(?P<alias>[A-Za-z_]\w*))?\s*$")


def _iter_py_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend([p for p in root.rglob("*.py") if p.is_file()])
    dedup = {p.resolve(): p for p in files}
    return sorted(dedup.values(), key=lambda p: str(p))


def _rewrite_optional_imports(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changed = 0

    for line in lines:
        stripped = line.rstrip("\r\n")
        m = IMPORT_PYDICOM_RE.match(stripped)
        if not m:
            out.append(line)
            continue

        indent = m.group("indent") or ""
        alias = m.group("alias") or "pydicom"
        block = (
            f"{indent}try:\n"
            f"{indent}    import pydicom as {alias}\n"
            f"{indent}except Exception:  # noqa: BLE001\n"
            f"{indent}    {alias} = None\n"
        )
        out.append(block)
        changed += 1

    if changed == 0:
        return text, 0
    return "".join(out), changed


def sanitize_optional_imports(roots: list[Path], repo_root: Path, apply: bool) -> dict:
    files = _iter_py_files(roots)
    changed_files: list[str] = []
    candidate_files: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rewritten, changed = _rewrite_optional_imports(text)
        if changed == 0:
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        candidate_files.append(rel)
        if apply:
            path.write_text(rewritten, encoding="utf-8")
            changed_files.append(rel)

    return {
        "mode": "apply" if apply else "dry-run",
        "python_files_scanned": len(files),
        "optional_import_candidates": len(candidate_files),
        "optional_imports_changed": len(changed_files),
        "changed_files": changed_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize optional third-party imports.")
    parser.add_argument(
        "--roots",
        default="../../src,../../demo,../../tests,../../third_part",
        help="Comma-separated roots to scan.",
    )
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Apply rewrites.")
    parser.add_argument("--output", default="../reports/optional_imports_report.json", help="Output report path.")
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    roots = [(base / t.strip()).resolve() for t in args.roots.split(",") if t.strip()]
    repo_root = (base / args.repo_root).resolve()
    report = sanitize_optional_imports(roots=roots, repo_root=repo_root, apply=args.apply)

    output = (base / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.summary_only:
        compact = {
            "mode": report["mode"],
            "python_files_scanned": report["python_files_scanned"],
            "optional_import_candidates": report["optional_import_candidates"],
            "optional_imports_changed": report["optional_imports_changed"],
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

