#!/usr/bin/env python3
"""Cleanup stale artifacts produced by the porting pipeline.

Default mode is dry-run. Use --apply to remove files/directories.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


TARGET_FILE_RE = re.compile(
    r'TARGET_FILE\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]\s*/\s*"([^"]+)"'
)


def _safe_rmtree(path: Path) -> bool:
    try:
        shutil.rmtree(path)
        return True
    except OSError:
        return False


def _safe_unlink(path: Path) -> bool:
    try:
        path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _iter_cache_dirs(root: Path) -> list[Path]:
    return sorted(
        [p for p in root.rglob("__pycache__") if p.is_dir()]
        + [p for p in root.rglob(".pytest_cache") if p.is_dir()]
    )


def _target_from_test_file(test_file: Path) -> Path | None:
    try:
        text = test_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    match = TARGET_FILE_RE.search(text)
    if not match:
        return None
    parent_index = int(match.group(1))
    rel_target = match.group(2).replace("/", "\\")
    try:
        root = test_file.resolve().parents[parent_index]
    except IndexError:
        return None
    return (root / rel_target).resolve()


def _find_stale_tests(tests_root: Path) -> list[Path]:
    stale: list[Path] = []
    if not tests_root.exists():
        return stale
    for test_file in tests_root.rglob("test_*.py"):
        target = _target_from_test_file(test_file)
        if target is None:
            continue
        if not target.exists():
            stale.append(test_file)
    return sorted(stale)


def _find_empty_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    candidates = sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True)
    return [p for p in candidates if not any(p.iterdir())]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup stale pipeline artifacts.")
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--tests-root", default="../tests", help="Porting tests root.")
    parser.add_argument("--clean-cache", action="store_true", help="Remove __pycache__/.pytest_cache under repo root.")
    parser.add_argument(
        "--prune-stale-tests",
        action="store_true",
        help="Remove generated/contract tests whose TARGET_FILE no longer exists.",
    )
    parser.add_argument("--remove-empty-dirs", action="store_true", help="Remove empty directories under tests root.")
    parser.add_argument("--apply", action="store_true", help="Apply cleanup actions (default dry-run).")
    parser.add_argument("--json", action="store_true", help="Output JSON summary.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    repo_root = (base / args.repo_root).resolve()
    tests_root = (base / args.tests_root).resolve()

    cache_dirs = _iter_cache_dirs(repo_root) if args.clean_cache else []
    stale_tests = _find_stale_tests(tests_root) if args.prune_stale_tests else []
    empty_dirs = _find_empty_dirs(tests_root) if args.remove_empty_dirs else []

    removed_cache: list[str] = []
    removed_tests: list[str] = []
    removed_empty_dirs: list[str] = []
    failures: list[str] = []

    if args.apply:
        for path in cache_dirs:
            if _safe_rmtree(path):
                removed_cache.append(str(path))
            else:
                failures.append(str(path))
        for path in stale_tests:
            if _safe_unlink(path):
                removed_tests.append(str(path))
            else:
                failures.append(str(path))
        for path in empty_dirs:
            if _safe_rmtree(path):
                removed_empty_dirs.append(str(path))
            else:
                failures.append(str(path))

    summary = {
        "mode": "apply" if args.apply else "dry-run",
        "repo_root": str(repo_root),
        "tests_root": str(tests_root),
        "cache_dirs_candidates": len(cache_dirs),
        "stale_test_candidates": len(stale_tests),
        "empty_dirs_candidates": len(empty_dirs),
        "removed_cache_dirs": len(removed_cache),
        "removed_stale_tests": len(removed_tests),
        "removed_empty_dirs": len(removed_empty_dirs),
        "failures": len(failures),
        "cache_dirs": [str(p) for p in cache_dirs],
        "stale_tests": [str(p) for p in stale_tests],
        "empty_dirs": [str(p) for p in empty_dirs],
        "failure_paths": failures,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Mode: {summary['mode']}")
    print(f"Cache dir candidates: {summary['cache_dirs_candidates']}")
    print(f"Stale test candidates: {summary['stale_test_candidates']}")
    print(f"Empty dir candidates: {summary['empty_dirs_candidates']}")
    if args.apply:
        print(f"Removed cache dirs: {summary['removed_cache_dirs']}")
        print(f"Removed stale tests: {summary['removed_stale_tests']}")
        print(f"Removed empty dirs: {summary['removed_empty_dirs']}")
        if failures:
            print(f"Failures: {len(failures)}")
    else:
        print("Dry-run only. Re-run with --apply to remove.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
