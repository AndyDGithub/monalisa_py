#!/usr/bin/env python3
"""Extract instruction-level logic from MATLAB files."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

try:
    from monalisa_py.porting.scripts.porting_compiler import discover_matlab_files, parse_matlab_file
except ImportError:
    from porting_compiler import discover_matlab_files, parse_matlab_file


OPCODE_BY_BLOCK_TYPE = {
    "function_decl": "FUNC_DECL",
    "assignment": "ASSIGN",
    "call": "CALL",
    "if": "BRANCH_IF",
    "branch": "BRANCH_ALT",
    "for": "LOOP_FOR",
    "while": "LOOP_WHILE",
    "return": "RETURN",
    "end": "BLOCK_END",
    "comment": "COMMENT",
    "statement": "STATEMENT",
    "blank": "BLANK",
}


PY_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def load_json_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def classify_symbol(name: str, kb_entries: dict, local_functions: set[str]) -> str:
    n = name.lower()
    if name in local_functions or n in {x.lower() for x in local_functions}:
        return "project_function"
    kb_entry = kb_entries.get(n) or kb_entries.get(name)
    if kb_entry:
        candidate = kb_entry.get("translation_candidate", {})
        if candidate.get("python_symbol") not in (None, "UNRESOLVED"):
            return "matlab_builtin_or_known"
    if name and name[0].islower():
        return "unknown_or_variable"
    return "unknown"


def candidate_from_maps(name: str, native_map: dict, doc_map: dict, kb_entries: dict) -> dict:
    c_lower = name.lower()
    n_map = native_map.get(c_lower) or native_map.get(name)
    d_map = doc_map.get(c_lower) or doc_map.get(name)
    kb = kb_entries.get(c_lower) or kb_entries.get(name) or {}
    kb_cand = kb.get("translation_candidate", {})

    python_symbol = (
        (n_map or {}).get("python")
        or (d_map or {}).get("python")
        or kb_cand.get("python_symbol")
    )
    python_library = (
        (n_map or {}).get("library")
        or (d_map or {}).get("library")
        or kb_cand.get("python_library")
    )
    imports = (
        (n_map or {}).get("imports")
        or kb_cand.get("python_imports")
        or []
    )
    confidence = (d_map or {}).get("confidence") or kb_cand.get("confidence") or "unknown"
    sources = (d_map or {}).get("sources") or kb_cand.get("sources") or []

    return {
        "python_symbol": python_symbol,
        "python_library": python_library,
        "imports": imports,
        "confidence": confidence,
        "sources": sources,
    }


def discover_python_files(root: Path, include_python_only: bool = False) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*.py"):
        if p.is_dir():
            continue
        if any(part.startswith(".") for part in p.parts):
            continue
        if not include_python_only and not p.with_suffix(".m").exists():
            continue
        files.append(p)
    return sorted(files)


def parse_python_signature(path: Path) -> tuple[str, list[str], list[str]]:
    source = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return path.stem, [], []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            returns: list[str] = []
            for sub in ast.walk(node):
                if isinstance(sub, ast.Return) and sub.value is not None:
                    if isinstance(sub.value, ast.Tuple):
                        returns = [f"ret_{i}" for i, _ in enumerate(sub.value.elts, start=1)]
                    else:
                        returns = ["ret"]
                    break
            return node.name, args, returns
    return path.stem, [], []


def extract_python_calls(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return []
    return [m.group(1) for m in PY_CALL_RE.finditer(stripped)]


def detect_python_block_type(line: str) -> str:
    s = line.strip()
    if not s:
        return "blank"
    if s.startswith("#"):
        return "comment"
    if s.startswith("def "):
        return "function_decl"
    if s.startswith("for "):
        return "for"
    if s.startswith("while "):
        return "while"
    if s.startswith("if "):
        return "if"
    if s.startswith(("elif ", "else")):
        return "branch"
    if s.startswith("return"):
        return "return"
    if "=" in s:
        return "assignment"
    if "(" in s and ")" in s:
        return "call"
    return "statement"


def parse_python_file(path: Path, local_function_names: set[str]) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    source_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    function_name, args, returns = parse_python_signature(path)
    dependencies: set[str] = set()
    native_calls: set[str] = set()
    blocks: list[dict] = []

    for i, line in enumerate(raw.splitlines(), start=1):
        block_type = detect_python_block_type(line)
        if block_type in {"comment", "blank", "function_decl"}:
            calls = []
        else:
            calls = extract_python_calls(line)
        for call in calls:
            if call == function_name:
                continue
            if call in local_function_names:
                dependencies.add(f"{call}.py")
            else:
                native_calls.add(call)
        blocks.append(
            {
                "line": i,
                "opcode": OPCODE_BY_BLOCK_TYPE.get(block_type, "STATEMENT"),
                "block_type": block_type,
                "text": line.strip(),
                "calls": [{"name": c, "symbol_type": "python_symbol", "translation_candidate": {}} for c in calls],
                "translation_plan": {
                    "suggested_imports": [],
                    "unresolved_calls": 0,
                    "ready_for_codegen": True,
                },
            }
        )

    logic_hash = hashlib.sha256(
        "\n".join(f"{b['block_type']}|{','.join([c['name'] for c in b['calls']])}|{b['text']}" for b in blocks).encode(
            "utf-8"
        )
    ).hexdigest()

    return {
        "function_name": function_name,
        "args": args,
        "returns": returns,
        "dependencies": sorted(dependencies),
        "native_calls": sorted(native_calls),
        "source_hash": source_hash,
        "logic_hash": logic_hash,
        "translation_summary": {
            "total_blocks": len(blocks),
            "unresolved_blocks": 0,
            "suggested_imports": [],
            "ready_ratio": 1.0 if blocks else 0.0,
        },
        "instruction_blocks": blocks,
    }


def build_instruction_blocks(parsed, native_map: dict, doc_map: dict, kb_entries: dict, local_functions: set[str]) -> list[dict]:
    blocks: list[dict] = []
    for b in parsed.blocks:
        calls = []
        block_imports: set[str] = set()
        block_unresolved = 0
        for c in b.calls:
            candidate = candidate_from_maps(c, native_map, doc_map, kb_entries)
            symbol_type = classify_symbol(c, kb_entries, local_functions)
            if candidate.get("python_symbol") is None and symbol_type != "project_function":
                block_unresolved += 1
            for imp in candidate.get("imports", []):
                block_imports.add(imp)
            calls.append(
                {
                    "name": c,
                    "symbol_type": symbol_type,
                    "translation_candidate": candidate,
                }
            )
        blocks.append(
            {
                "line": b.line,
                "opcode": OPCODE_BY_BLOCK_TYPE.get(b.block_type, "STATEMENT"),
                "block_type": b.block_type,
                "text": b.text,
                "calls": calls,
                "translation_plan": {
                    "suggested_imports": sorted(block_imports),
                    "unresolved_calls": block_unresolved,
                    "ready_for_codegen": block_unresolved == 0,
                },
            }
        )
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract MATLAB logic blocks to JSON.")
    parser.add_argument("--matlab-root", default="../../src", help="Root directory containing MATLAB files.")
    parser.add_argument("--output", default="../reports/extracted_logic.json", help="Output JSON path.")
    parser.add_argument("--native-map", default="../config/native_function_map.json", help="Curated native map JSON.")
    parser.add_argument(
        "--doc-map",
        default="../config/doc_native_map_candidates.json",
        help="Doc-scraped candidate map JSON.",
    )
    parser.add_argument(
        "--instruction-kb",
        default="../config/instruction_kb_matlab_project.json",
        help="Instruction KB JSON for project-scoped symbol enrichment.",
    )
    parser.add_argument(
        "--include-python",
        action="store_true",
        help="Also extract Python logic for `.py` files (paired with MATLAB by default).",
    )
    parser.add_argument(
        "--include-python-only",
        action="store_true",
        help="When --include-python is set, include `.py` files without `.m` sibling.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files extracted.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    matlab_root = (base / args.matlab_root).resolve()
    output = (base / args.output).resolve()
    native_map = load_json_if_exists((base / args.native_map).resolve())
    doc_map = load_json_if_exists((base / args.doc_map).resolve())
    instruction_kb = load_json_if_exists((base / args.instruction_kb).resolve())
    kb_entries = instruction_kb.get("entries", {})

    matlab_files = discover_matlab_files(matlab_root)
    local_functions = {p.stem for p in matlab_files}
    if args.limit is not None:
        matlab_files = matlab_files[: max(0, args.limit)]

    extracted: dict[str, dict] = {}
    for fpath in matlab_files:
        parsed = parse_matlab_file(fpath, local_functions)
        instruction_blocks = build_instruction_blocks(parsed, native_map, doc_map, kb_entries, local_functions)
        unresolved_blocks = sum(1 for b in instruction_blocks if not b["translation_plan"]["ready_for_codegen"])
        suggested_imports = sorted(
            {imp for b in instruction_blocks for imp in b["translation_plan"]["suggested_imports"]}
        )
        extracted[str(fpath)] = {
            "function_name": parsed.function_name,
            "args": parsed.args,
            "returns": parsed.returns,
            "dependencies": parsed.dependencies,
            "native_calls": parsed.native_calls,
            "source_hash": parsed.source_hash,
            "logic_hash": parsed.logic_hash,
            "translation_summary": {
                "total_blocks": len(instruction_blocks),
                "unresolved_blocks": unresolved_blocks,
                "suggested_imports": suggested_imports,
                "ready_ratio": 0.0 if not instruction_blocks else (len(instruction_blocks) - unresolved_blocks) / len(instruction_blocks),
            },
            "instruction_blocks": instruction_blocks,
        }

    if args.include_python:
        python_files = discover_python_files(matlab_root, include_python_only=args.include_python_only)
        if args.limit is not None:
            python_files = python_files[: max(0, args.limit)]
        py_local_functions = {p.stem for p in python_files}
        for ppath in python_files:
            extracted[str(ppath)] = parse_python_file(ppath, py_local_functions)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(extracted, indent=2), encoding="utf-8")
    print(f"Extracted logic for {len(extracted)} files into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
