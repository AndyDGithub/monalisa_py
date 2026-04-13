#!/usr/bin/env python3
"""Run parity checks between MATLAB and Python artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PARITY_PKG_ROOT = (SCRIPT_DIR / "../python").resolve()
if str(PARITY_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PARITY_PKG_ROOT))

from monalisa_py.parity import compare_image_files  # type: ignore  # noqa: E402


def run_single_case(case: dict[str, Any]) -> dict[str, Any]:
    matlab_path = Path(case["matlab_path"]).resolve()
    python_path = Path(case["python_path"]).resolve()
    matlab_var = case.get("matlab_var", "matlab_image")
    python_var = case.get("python_var")
    l2_threshold = float(case.get("l2_threshold", 1e-6))
    nmse_threshold = float(case.get("nmse_threshold", 1e-6))

    metrics = compare_image_files(
        matlab_path=matlab_path,
        python_path=python_path,
        matlab_var=matlab_var,
        python_var=python_var,
        l2_threshold=l2_threshold,
        nmse_threshold=nmse_threshold,
    )
    ok = bool(metrics.ok_l2 and metrics.ok_nmse)
    payload = {
        "case_id": case.get("case_id") or f"{matlab_path.name}__{python_path.name}",
        "matlab_path": str(matlab_path),
        "python_path": str(python_path),
        "thresholds": {"l2_threshold": l2_threshold, "nmse_threshold": nmse_threshold},
        "metrics": asdict(metrics),
        "ok": ok,
    }
    return payload


def load_cases(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.cases_json:
        data = json.loads(Path(args.cases_json).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            cases = data.get("cases", [])
        else:
            cases = data
        if not isinstance(cases, list):
            raise ValueError("Invalid cases JSON format, expected list or {'cases': [...]} ")
        return [dict(case) for case in cases]

    if not args.matlab_path or not args.python_path:
        raise ValueError("Either --cases-json or both --matlab-path/--python-path must be provided.")

    return [
        {
            "case_id": args.case_id,
            "matlab_path": args.matlab_path,
            "python_path": args.python_path,
            "matlab_var": args.matlab_var,
            "python_var": args.python_var,
            "l2_threshold": args.l2_threshold,
            "nmse_threshold": args.nmse_threshold,
        }
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run parity checks for MATLAB vs Python artifacts.")
    parser.add_argument("--matlab-path", default=None, help="Path to MATLAB reference artifact (.mat).")
    parser.add_argument("--python-path", default=None, help="Path to Python artifact (.mat or .npy).")
    parser.add_argument("--case-id", default=None, help="Optional case identifier.")
    parser.add_argument("--matlab-var", default="matlab_image", help="MATLAB .mat variable name.")
    parser.add_argument("--python-var", default=None, help="Python .mat variable name (if python artifact is .mat).")
    parser.add_argument("--l2-threshold", type=float, default=1e-6, help="L2 threshold.")
    parser.add_argument("--nmse-threshold", type=float, default=1e-6, help="NMSE threshold.")
    parser.add_argument(
        "--cases-json",
        default=None,
        help="JSON file path containing a list of parity cases.",
    )
    parser.add_argument(
        "--output",
        default="../reports/parity_report.json",
        help="Output JSON report path.",
    )
    parser.add_argument("--fail-on-mismatch", action="store_true", help="Exit code 1 when any case fails.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    output = (base / args.output).resolve()

    cases = load_cases(args)
    results: list[dict[str, Any]] = []
    for case in cases:
        try:
            results.append(run_single_case(case))
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "case_id": case.get("case_id") or "unknown_case",
                    "ok": False,
                    "error": str(exc),
                    "matlab_path": case.get("matlab_path"),
                    "python_path": case.get("python_path"),
                }
            )

    total = len(results)
    passed = sum(1 for r in results if r.get("ok"))
    failed = total - passed
    report = {
        "summary": {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": failed,
        },
        "results": results,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Parity report written to: {output}")
    print(f"Passed: {passed}/{total}")
    if failed:
        print(f"Failed: {failed}")
    if args.fail_on_mismatch and failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
