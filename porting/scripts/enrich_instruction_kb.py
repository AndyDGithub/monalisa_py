#!/usr/bin/env python3
"""
Post-process instruction KBs:
- Clean noisy symbols
- Enrich primitives
- Fix MATLAB -> Python mappings (NumPy, stdlib)
- Improve reconstruction hints
"""

from __future__ import annotations
import json
from pathlib import Path

# =========================
# CONFIG
# =========================

NUMPY_MAP = {
    "abs": "np.abs",
    "acos": "np.arccos",
    "asin": "np.arcsin",
    "atan": "np.arctan",
    "cos": "np.cos",
    "sin": "np.sin",
    "tan": "np.tan",
    "angle": "np.angle",
    "sqrt": "np.sqrt",
    "log": "np.log",
    "exp": "np.exp",
    "fft": "np.fft.fft",
    "ifft": "np.fft.ifft",
    "zeros": "np.zeros",
    "ones": "np.ones",
    "eye": "np.eye",
    "size": "np.shape",
}

STDLIB_MAP = {
    "length": "len",
    "all": "all",
    "any": "any",
    "assert": "assert",
}

SPECIAL_MAP = {
    "addpath": ("sys.path.append", "sys", ["import sys"]),
}

# Heuristiques
MATH_FUNCS = {
    "abs", "acos", "asin", "atan", "cos", "sin", "tan",
    "sqrt", "log", "exp", "angle"
}

ARRAY_CREATORS = {"zeros", "ones", "eye", "rand", "array", "cell"}

REDUCE_FUNCS = {"sum", "mean", "prod", "max", "min", "norm"}

# =========================
# HELPERS
# =========================

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def is_noise_symbol(name: str) -> bool:
    # élimine variables locales type a1, b2, argx...
    return (
        len(name) <= 3
        and any(c.isdigit() for c in name)
    ) or name.startswith("arg")

def enrich_primitives(name: str, primitives: list[str]) -> list[str]:
    p = set(primitives)

    if name in MATH_FUNCS:
        p.add("ELEMENTWISE_OP")

    if name in ARRAY_CREATORS:
        p.add("ARRAY_CREATE")

    if name in REDUCE_FUNCS:
        p.add("REDUCE")

    return sorted(p)

def resolve_mapping(name: str):
    # priorité: numpy
    if name in NUMPY_MAP:
        return {
            "python_symbol": NUMPY_MAP[name],
            "python_library": "numpy",
            "python_imports": ["import numpy as np"],
            "confidence": "high"
        }

    # stdlib
    if name in STDLIB_MAP:
        return {
            "python_symbol": STDLIB_MAP[name],
            "python_library": "python-stdlib",
            "python_imports": [],
            "confidence": "high"
        }

    # cas spéciaux
    if name in SPECIAL_MAP:
        sym, lib, imp = SPECIAL_MAP[name]
        return {
            "python_symbol": sym,
            "python_library": lib,
            "python_imports": imp,
            "confidence": "medium"
        }

    return None

def enrich_hints(entry: dict, name: str):
    hints = entry["reconstruction_hints"]

    if name in NUMPY_MAP:
        hints["vectorized_equivalent"] = True

    if name in ARRAY_CREATORS:
        hints["creates_array"] = True

    if name in REDUCE_FUNCS:
        hints["reduces_dimension"] = True

    if entry["translation_candidate"]["python_symbol"] is None:
        hints["unresolved"] = True

# =========================
# MAIN
# =========================

def enrich(matlab_kb_path: Path, python_kb_path: Path):
    matlab_kb = load_json(matlab_kb_path)
    python_kb = load_json(python_kb_path)

    matlab_entries = matlab_kb["entries"]
    new_matlab_entries = {}

    python_entries = {}

    for name, entry in matlab_entries.items():

        # 1. FILTER bruit
        if is_noise_symbol(name):
            entry["kind"] = "user_defined_or_unknown"

        # 2. ENRICH primitives
        entry["instruction_primitives"] = enrich_primitives(
            name,
            entry["instruction_primitives"]
        )

        # 3. FIX mapping
        mapping = resolve_mapping(name)
        if mapping:
            entry["translation_candidate"].update(mapping)
        else:
            if not entry["translation_candidate"]["python_symbol"]:
                entry["translation_candidate"]["python_symbol"] = "UNRESOLVED"
                entry["translation_candidate"]["confidence"] = "low"

        # 4. ENRICH hints
        enrich_hints(entry, name)

        new_matlab_entries[name] = entry

        # 5. REBUILD python KB propre
        py_sym = entry["translation_candidate"]["python_symbol"]

        if py_sym and py_sym != "UNRESOLVED":
            python_entries.setdefault(py_sym, {
                "language": "python",
                "symbol": py_sym,
                "library": entry["translation_candidate"]["python_library"],
                "imports": entry["translation_candidate"]["python_imports"],
                "origin_matlab_symbols": [],
                "instruction_primitives": entry["instruction_primitives"],
                "reconstruction_hints": {
                    "vectorization_preferred": True,
                    "requires_import": bool(entry["translation_candidate"]["python_imports"]),
                }
            })

            python_entries[py_sym]["origin_matlab_symbols"].append(name)

    # nettoyage duplicates
    for v in python_entries.values():
        v["origin_matlab_symbols"] = sorted(set(v["origin_matlab_symbols"]))

    # update KB
    matlab_kb["entries"] = new_matlab_entries
    matlab_kb["meta"]["entry_count"] = len(new_matlab_entries)

    python_kb["entries"] = python_entries
    python_kb["meta"]["entry_count"] = len(python_entries)

    save_json(matlab_kb_path, matlab_kb)
    save_json(python_kb_path, python_kb)

    print(f"[ENRICH] MATLAB entries: {len(new_matlab_entries)}")
    print(f"[ENRICH] Python entries: {len(python_entries)}")


# =========================
# CLI
# =========================

if __name__ == "__main__":
    base = Path(__file__).resolve().parent

    matlab_kb = base / "../config/instruction_kb_matlab_project.json"
    python_kb = base / "../config/instruction_kb_python_project.json"

    enrich(matlab_kb, python_kb)