#!/usr/bin/env python3
"""Build MATLAB function dependency graph for one file or whole project."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from monalisa_py.porting.scripts.search_matlab import search_matlab_files
except ImportError:
    from search_matlab import search_matlab_files


MATLAB_CALL_RE = re.compile(r"(?<!\.)\b([A-Za-z][A-Za-z0-9_]*)\s*\(")
MATLAB_DECL_RE = re.compile(
    r"^\s*function\s+(?:\[[^\]]*\]\s*=|\S+\s*=)?\s*([A-Za-z][A-Za-z0-9_]*)"
)

MATLAB_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "case",
    "otherwise",
    "end",
    "function",
    "addpath",
    "try",
    "catch",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="ISO-8859-1", errors="ignore")


def extract_function_definitions(file_list: list[str]) -> dict[str, str]:
    """
    Return mapping {function_name -> file_name.m} for project-local MATLAB functions.
    """
    func_to_file: dict[str, str] = {}
    for file_str in file_list:
        path = Path(file_str)
        if path.suffix.lower() != ".m":
            continue
        # Always map file stem to file for projects where call-sites use file names.
        func_to_file[path.stem] = path.name
        for line in _read_text(path).splitlines():
            match = MATLAB_DECL_RE.match(line)
            if match:
                func_to_file[match.group(1)] = path.name
    return func_to_file


def _extract_calls_from_line(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("%") or stripped.startswith("function "):
        return []
    return [m.group(1) for m in MATLAB_CALL_RE.finditer(stripped)]


def get_dependency_graph_file(file_path: str | Path, func_to_file: dict[str, str]) -> dict[str, list[str]]:
    """
    Parse a MATLAB file and return {file_name.m: [dependency1.m, ...]}.
    Dependencies include only local project MATLAB functions.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".m":
        return {path.name: []}

    self_name = path.stem
    dependencies: set[str] = set()
    for line in _read_text(path).splitlines():
        for call in _extract_calls_from_line(line):
            if call in MATLAB_KEYWORDS or call == self_name:
                continue
            dep_file = func_to_file.get(call)
            if dep_file and dep_file != path.name:
                dependencies.add(dep_file)
    return {path.name: sorted(dependencies)}


def get_global_function_call_graph(matlab_files: list[str]) -> dict[str, list[str]]:
    func_to_file = extract_function_definitions(matlab_files)
    global_graph: dict[str, list[str]] = {}
    for file_str in matlab_files:
        global_graph.update(get_dependency_graph_file(file_str, func_to_file))
    return global_graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Build MATLAB dependency graph.")
    parser.add_argument(
        "--root",
        default="../../src",
        help="Root directory to scan for MATLAB files.",
    )
    parser.add_argument("--file", default=None, help="Optional single file path to inspect.")
    parser.add_argument(
        "--output",
        default="../../script_outputs/all_files_function_call_graph.json",
        help="Output JSON file for global graph.",
    )
    parser.add_argument("--json", action="store_true", help="Print graph as JSON to stdout.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    root = (base / args.root).resolve()
    output_path = (base / args.output).resolve()

    matlab_files = search_matlab_files(root)
    func_to_file = extract_function_definitions(matlab_files)

    if args.file:
        graph = get_dependency_graph_file((base / args.file).resolve(), func_to_file)
        print(json.dumps(graph, indent=2))
        return 0

    global_graph = get_global_function_call_graph(matlab_files)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(global_graph, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(global_graph, indent=2))
    else:
        print(f"Dependency graph written to: {output_path}")
        print(f"Files analyzed: {len(global_graph)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
