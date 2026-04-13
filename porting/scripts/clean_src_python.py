#!/usr/bin/env python3
"""Remove Python files from src for a fresh porting demo run.

Default mode is dry-run. Use --apply to actually delete files.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def _collect_python_files(src_root: Path, keep_init: bool) -> list[Path]:
    files: list[Path] = []
    for path in src_root.rglob("*.py"):
        if keep_init and path.name == "__init__.py":
            continue
        files.append(path)
    return sorted(files)


def _collect_pycache_dirs(src_root: Path) -> list[Path]:
    return sorted(p for p in src_root.rglob("__pycache__") if p.is_dir())


def _safe_unlink(path: Path) -> bool:
    try:
        path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _safe_rmtree(path: Path) -> bool:
    try:
        shutil.rmtree(path)
        return True
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean all Python files from src for demo reset.")
    parser.add_argument("--src-root", default="../../src", help="Source root directory.")
    parser.add_argument("--keep-init", action="store_true", help="Keep __init__.py files.")
    parser.add_argument("--remove-pycache", action="store_true", help="Also remove __pycache__ directories.")
    parser.add_argument("--apply", action="store_true", help="Apply deletion (default: dry-run only).")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--max-print", type=int, default=40, help="Max paths to print in text mode.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    src_root = (base / args.src_root).resolve()
    if not src_root.exists():
        raise SystemExit(f"Source root not found: {src_root}")

    py_files = _collect_python_files(src_root, keep_init=args.keep_init)
    pycache_dirs = _collect_pycache_dirs(src_root) if args.remove_pycache else []

    deleted_files: list[str] = []
    deleted_pycache: list[str] = []
    failed: list[str] = []

    if args.apply:
        for path in py_files:
            if _safe_unlink(path):
                deleted_files.append(str(path))
            else:
                failed.append(str(path))
        for path in pycache_dirs:
            if _safe_rmtree(path):
                deleted_pycache.append(str(path))
            else:
                failed.append(str(path))

    summary = {
        "mode": "apply" if args.apply else "dry-run",
        "src_root": str(src_root),
        "keep_init": bool(args.keep_init),
        "remove_pycache": bool(args.remove_pycache),
        "candidates_python_files": len(py_files),
        "candidates_pycache_dirs": len(pycache_dirs),
        "deleted_python_files": len(deleted_files),
        "deleted_pycache_dirs": len(deleted_pycache),
        "failed": len(failed),
        "python_files": [str(p) for p in py_files],
        "pycache_dirs": [str(p) for p in pycache_dirs],
        "failed_paths": failed,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Mode: {summary['mode']}")
    print(f"Python file candidates: {summary['candidates_python_files']}")
    print(f"__pycache__ candidates: {summary['candidates_pycache_dirs']}")
    to_show = py_files[: max(0, args.max_print)]
    for p in to_show:
        print(f"- {p}")
    if len(py_files) > len(to_show):
        print(f"... ({len(py_files) - len(to_show)} more)")
    if args.apply:
        print(f"Deleted Python files: {summary['deleted_python_files']}")
        print(f"Deleted __pycache__ dirs: {summary['deleted_pycache_dirs']}")
        if failed:
            print(f"Failed paths: {len(failed)}")
    else:
        print("Dry-run only. Re-run with --apply to delete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

