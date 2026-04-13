#!/usr/bin/env python3
"""Build project-scoped instruction knowledge bases for MATLAB and Python.

This is intentionally project-scoped (functions actually used in monalisa_py/src),
not a full dump of all MATLAB/Python ecosystem APIs.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from monalisa_py.porting.scripts.porting_compiler import discover_matlab_files, parse_matlab_file
except ImportError:
    from porting_compiler import discover_matlab_files, parse_matlab_file


PRIMITIVES = [
    "ASSIGN",
    "CALL",
    "INDEX",
    "SLICE",
    "RESHAPE",
    "LOOP_FOR",
    "LOOP_WHILE",
    "BRANCH_IF",
    "BRANCH_ALT",
    "RETURN",
    "ARRAY_CREATE",
    "CONCAT",
    "REDUCE",
    "MATRIX_MUL",
    "ELEMENTWISE_OP",
]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def infer_primitives_for_name(name: str) -> list[str]:
    n = name.lower()
    out = {"CALL"}
    if any(k in n for k in ("reshape", "permute", "transpose")):
        out.add("RESHAPE")
    if any(k in n for k in ("sum", "mean", "prod", "max", "min", "norm")):
        out.add("REDUCE")
    if any(k in n for k in ("zeros", "ones", "rand", "cell", "array")):
        out.add("ARRAY_CREATE")
    if any(k in n for k in ("if", "find", "mask", "logical")):
        out.add("BRANCH_IF")
    return sorted(out)


def collect_project_calls(matlab_root: Path) -> tuple[Counter, set[str]]:
    files = discover_matlab_files(matlab_root)
    locals_set = {p.stem for p in files}
    counter: Counter = Counter()
    all_calls: set[str] = set()
    for f in files:
        parsed = parse_matlab_file(f, locals_set)
        for call in parsed.native_calls:
            lc = call.lower()
            counter[lc] += 1
            all_calls.add(lc)
    return counter, all_calls


def main() -> int:
    parser = argparse.ArgumentParser(description="Build project-scoped MATLAB/Python instruction KBs.")
    parser.add_argument("--matlab-root", default="../../src", help="MATLAB root for project scan.")
    parser.add_argument("--native-map", default="../config/native_function_map.json", help="Curated MATLAB->Python map.")
    parser.add_argument("--doc-map", default="../config/doc_native_map_candidates.json", help="Doc candidate map.")
    parser.add_argument("--matlab-kb-output", default="../config/instruction_kb_matlab_project.json")
    parser.add_argument("--python-kb-output", default="../config/instruction_kb_python_project.json")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    matlab_root = (base / args.matlab_root).resolve()
    native_map = load_json((base / args.native_map).resolve())
    doc_map = load_json((base / args.doc_map).resolve())
    matlab_out = (base / args.matlab_kb_output).resolve()
    python_out = (base / args.python_kb_output).resolve()

    usage, calls = collect_project_calls(matlab_root)

    matlab_entries: dict[str, dict] = {}
    python_entries: dict[str, dict] = {}

    for call in sorted(calls):
        curated = native_map.get(call) or native_map.get(call.lower()) or {}
        doc = doc_map.get(call) or {}
        py_symbol = curated.get("python") or doc.get("python")
        py_lib = curated.get("library") or doc.get("library")
        py_imports = curated.get("imports", [])

        matlab_entries[call] = {
            "language": "matlab",
            "symbol": call,
            "kind": "function_or_symbol",
            "usage_count": usage.get(call, 0),
            "instruction_primitives": infer_primitives_for_name(call),
            "translation_candidate": {
                "python_symbol": py_symbol,
                "python_library": py_lib,
                "python_imports": py_imports,
                "confidence": doc.get("confidence", "manual-needed"),
                "sources": doc.get("sources", []),
            },
            "reconstruction_hints": {
                "requires_shape_semantics": any(k in call for k in ("size", "num", "reshape", "permute")),
                "possible_index_base_shift": True,
                "requires_parity_test": True,
            },
        }

        if py_symbol:
            python_entries[py_symbol] = {
                "language": "python",
                "symbol": py_symbol,
                "library": py_lib,
                "imports": py_imports,
                "origin_matlab_symbols": sorted(
                    list(
                        set(
                            [call]
                            + [
                                m
                                for m, v in matlab_entries.items()
                                if (v["translation_candidate"]["python_symbol"] == py_symbol and m != call)
                            ]
                        )
                    )
                ),
                "instruction_primitives": infer_primitives_for_name(py_symbol),
                "reconstruction_hints": {
                    "vectorization_preferred": py_lib in {"numpy", "scipy", "python-stdlib"},
                    "requires_import": bool(py_imports),
                },
            }

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "monalisa_py project calls only",
        "primitive_vocabulary": PRIMITIVES,
        "entry_count": len(matlab_entries),
    }
    matlab_payload = {"meta": meta, "entries": matlab_entries}
    python_payload = {
        "meta": {**meta, "entry_count": len(python_entries)},
        "entries": python_entries,
    }

    matlab_out.parent.mkdir(parents=True, exist_ok=True)
    matlab_out.write_text(json.dumps(matlab_payload, indent=2), encoding="utf-8")
    python_out.parent.mkdir(parents=True, exist_ok=True)
    python_out.write_text(json.dumps(python_payload, indent=2), encoding="utf-8")

    print(f"MATLAB KB entries: {len(matlab_entries)}")
    print(f"Python KB entries: {len(python_entries)}")
    print(f"- {matlab_out}")
    print(f"- {python_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
