#!/usr/bin/env python3
"""Evaluate strict deterministic porting against current Python files.

Policy per file:
- Keep current if current passes tests and strict-ported fails.
- Keep strict-ported if strict-ported passes and current fails.
- Keep strict-ported if both fail.
- Keep current if both pass.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from strict_port_base import build_strict_port_result
from search_matlab import search_matlab_files


SCRIPT_DIR = Path(__file__).resolve().parent


def _resolve_repo_root(repo_root_arg: str) -> Path:
    root = Path(repo_root_arg)
    if root.is_absolute():
        return root.resolve()
    return (SCRIPT_DIR / root).resolve()


def _iter_matlab_files(repo_root: Path, roots_csv: str, max_files: int) -> list[Path]:
    roots = [x.strip() for x in roots_csv.split(",") if x.strip()]
    out: list[Path] = []
    for token in roots:
        root = (repo_root / token).resolve()
        if not root.exists():
            continue
        out.extend(Path(p) for p in search_matlab_files(root))
    out = sorted(set(p.resolve() for p in out))
    if max_files > 0:
        out = out[:max_files]
    return out


def _matlab_to_python_target(matlab_file: Path, repo_root: Path) -> Path:
    try:
        rel = matlab_file.resolve().relative_to(repo_root.resolve())
        return (repo_root / rel.with_suffix(".py")).resolve()
    except ValueError:
        return matlab_file.with_suffix(".py").resolve()


def _tests_for_target(repo_root: Path, target_py: Path) -> list[Path]:
    tests_root = repo_root / "porting" / "tests"
    name = f"test_{target_py.stem}.py"
    out: list[Path] = []
    for root in [tests_root / "generated", tests_root / "contracts"]:
        if not root.exists():
            continue
        out.extend(p.resolve() for p in root.rglob(name))
    dedup = sorted(set(out))
    return dedup


def _run_pytest(repo_root: Path, test_paths: list[Path]) -> dict[str, Any]:
    if not test_paths:
        return {
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
            "tests_count": 0,
        }
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--import-mode=importlib",
        "-p",
        "no:cacheprovider",
        *[str(p) for p in test_paths],
        "-q",
        "--maxfail=50",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "returncode": int(proc.returncode),
        "stdout_tail": proc.stdout[-2500:],
        "stderr_tail": proc.stderr[-2500:],
        "tests_count": len(test_paths),
    }


def _decision(before_rc: int | None, after_rc: int | None, *, force_keep_strict: bool = False) -> str:
    if force_keep_strict:
        return "keep_strict_ported"

    # No target tests available: avoid destructive replacement.
    if before_rc is None and after_rc is None:
        return "keep_current"

    before_pass = before_rc == 0
    after_pass = after_rc == 0

    if before_pass and not after_pass:
        return "rollback_keep_current"
    if not before_pass and after_pass:
        return "keep_strict_ported"
    if not before_pass and not after_pass:
        return "keep_strict_ported"
    return "keep_current"


def _evaluate_one(repo_root: Path, matlab_file: Path, python_file: Path) -> dict[str, Any]:
    tests = _tests_for_target(repo_root, python_file)
    before = _run_pytest(repo_root, tests)

    had_original = python_file.exists()
    original_text = python_file.read_text(encoding="utf-8", errors="ignore") if had_original else ""

    strict_report = build_strict_port_result(
        matlab_file=matlab_file,
        python_file=python_file,
        repo_root=repo_root,
    )
    python_file.parent.mkdir(parents=True, exist_ok=True)
    python_file.write_text(str(strict_report["generated_code"]), encoding="utf-8")

    after = _run_pytest(repo_root, tests)
    strict_status = str(strict_report.get("status", "strict_baseline"))
    force_keep_strict = strict_status == "skipped_mex_wrapper" and bool(strict_report.get("changed", False))
    action = _decision(
        before.get("returncode"),
        after.get("returncode"),
        force_keep_strict=force_keep_strict,
    )

    if action in {"rollback_keep_current", "keep_current"}:
        if had_original:
            python_file.write_text(original_text, encoding="utf-8")
        else:
            try:
                python_file.unlink()
            except OSError:
                pass

    return {
        "matlab_file": str(matlab_file),
        "python_file": str(python_file),
        "tests": [str(p) for p in tests],
        "before": before,
        "after": after,
        "action": action,
        "strict_changed_vs_current": bool(strict_report.get("changed", False)),
        "strict_imports": strict_report.get("imports", []),
        "strict_status": strict_status,
        "strict_skip_reason": str(strict_report.get("skip_reason", "")),
        "strict_native_backend_required": bool(strict_report.get("native_backend_required", False)),
        "strict_native_function": str(strict_report.get("native_function", "")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch evaluate strict deterministic ports.")
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--roots", default="src,demo,tests,third_part", help="Comma-separated roots.")
    parser.add_argument("--max-files", type=int, default=0, help="Max files to evaluate (0 = all).")
    parser.add_argument("--target-python-file", default="", help="Optional single Python target file.")
    parser.add_argument("--target-matlab-file", default="", help="Optional single MATLAB source file.")
    parser.add_argument("--output", default="../reports/strict_port_batch_report.json", help="Output JSON report.")
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary.")
    args = parser.parse_args()

    repo_root = _resolve_repo_root(args.repo_root)
    results: list[dict[str, Any]] = []

    if args.target_matlab_file.strip() or args.target_python_file.strip():
        if args.target_matlab_file.strip():
            matlab_file = Path(args.target_matlab_file)
            matlab_file = (repo_root / matlab_file).resolve() if not matlab_file.is_absolute() else matlab_file.resolve()
        elif args.target_python_file.strip():
            py = Path(args.target_python_file)
            py = (repo_root / py).resolve() if not py.is_absolute() else py.resolve()
            matlab_file = py.with_suffix(".m")
        else:
            raise SystemExit("Missing target inputs.")

        if args.target_python_file.strip():
            python_file = Path(args.target_python_file)
            python_file = (repo_root / python_file).resolve() if not python_file.is_absolute() else python_file.resolve()
        else:
            python_file = _matlab_to_python_target(matlab_file, repo_root)

        if not matlab_file.exists():
            raise SystemExit(f"MATLAB file not found: {matlab_file}")

        results.append(_evaluate_one(repo_root, matlab_file, python_file))
    else:
        matlab_files = _iter_matlab_files(repo_root, args.roots, args.max_files)
        for matlab_file in matlab_files:
            python_file = _matlab_to_python_target(matlab_file, repo_root)
            results.append(_evaluate_one(repo_root, matlab_file, python_file))

    summary = {
        "files_evaluated": len(results),
        "rollback_keep_current": sum(1 for r in results if r["action"] == "rollback_keep_current"),
        "keep_current": sum(1 for r in results if r["action"] == "keep_current"),
        "keep_strict_ported": sum(1 for r in results if r["action"] == "keep_strict_ported"),
        "skipped_mex_wrapper": sum(1 for r in results if r.get("strict_status") == "skipped_mex_wrapper"),
    }

    payload = {
        "repo_root": str(repo_root),
        "roots": [x.strip() for x in args.roots.split(",") if x.strip()],
        "summary": summary,
        "results": results,
    }

    output = (SCRIPT_DIR / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.summary_only:
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
