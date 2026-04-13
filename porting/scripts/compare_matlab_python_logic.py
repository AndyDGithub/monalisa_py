#!/usr/bin/env python3
"""Compare extracted MATLAB and Python logic snapshots."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _normalize_dep_set(values: list[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        name = Path(str(value)).stem
        if name:
            out.add(name.lower())
    return out


def compare_logic(extracted_logic_path: Path, differences_path: Path) -> dict:
    extracted_logic = json.loads(extracted_logic_path.read_text(encoding="utf-8"))
    differences: dict[str, dict] = {}

    for matlab_file, logic in extracted_logic.items():
        if not matlab_file.endswith(".m"):
            continue
        python_file = matlab_file[:-2] + ".py"
        if python_file not in extracted_logic:
            differences[matlab_file] = {
                "status": "missing_python_file",
                "missing_target": python_file,
                "native_calls": logic.get("native_calls", []),
            }
            continue

        py_logic = extracted_logic[python_file]
        file_diff: dict[str, object] = {}

        if logic.get("function_name") != py_logic.get("function_name"):
            file_diff["function_name"] = {
                "matlab": logic.get("function_name"),
                "python": py_logic.get("function_name"),
            }
        if logic.get("args") != py_logic.get("args"):
            file_diff["args"] = {"matlab": logic.get("args"), "python": py_logic.get("args")}
        matlab_returns = logic.get("returns") or []
        python_returns = py_logic.get("returns") or []
        if len(matlab_returns) != len(python_returns):
            file_diff["returns"] = {"matlab": logic.get("returns"), "python": py_logic.get("returns")}

        matlab_deps = _normalize_dep_set(logic.get("dependencies", []))
        py_deps = _normalize_dep_set(py_logic.get("dependencies", []))
        fn_stem = str(logic.get("function_name") or "").lower()
        if fn_stem:
            matlab_deps.discard(fn_stem)
            py_deps.discard(fn_stem)
        if matlab_deps != py_deps:
            file_diff["dependencies"] = {
                "added_in_python": sorted(py_deps - matlab_deps),
                "missing_in_python": sorted(matlab_deps - py_deps),
            }

        if file_diff:
            differences[matlab_file] = {"status": "logic_mismatch", **file_diff}

    differences_path.parent.mkdir(parents=True, exist_ok=True)
    differences_path.write_text(json.dumps(differences, indent=2), encoding="utf-8")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare MATLAB/Python extracted logic.")
    parser.add_argument("extracted_logic_path", help="Path to extracted logic JSON.")
    parser.add_argument("--output", default="../reports/logic_differences.json", help="Difference JSON output path.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    extracted = Path(args.extracted_logic_path)
    if not extracted.is_absolute():
        extracted = (base / extracted).resolve()
    out = (base / args.output).resolve()

    differences = compare_logic(extracted, out)
    print(f"Wrote {len(differences)} logic mismatches to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
