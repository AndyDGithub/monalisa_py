#!/usr/bin/env python3
"""Compute deterministic MATLAB porting order from dependency graph."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_dependency_graph(json_file: str | Path) -> dict[str, list[str]]:
    data = json.loads(Path(json_file).read_text(encoding="utf-8"))
    return {str(k): [str(x) for x in v] for k, v in data.items()}


def compute_porting_order(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Layered topological order.

    - A file appears in a layer once all in-project dependencies are already resolved.
    - External dependencies are ignored.
    - Cycles are grouped by selecting a deterministic minimal unresolved set.
    """
    remaining = {node: set(deps) for node, deps in graph.items()}
    reverse: dict[str, set[str]] = {node: set() for node in remaining}
    for parent, deps in remaining.items():
        for dep in deps:
            reverse.setdefault(dep, set()).add(parent)

    layers: list[list[str]] = []
    while remaining:
        # True leaves first.
        leaves = sorted(node for node, deps in remaining.items() if not deps)

        # If none, strip external unresolved deps and retry.
        if not leaves:
            for node, deps in remaining.items():
                deps.intersection_update(remaining.keys())
            leaves = sorted(node for node, deps in remaining.items() if not deps)

        # Still none => cycle: break deterministically on minimal indegree set.
        if not leaves:
            min_size = min(len(deps) for deps in remaining.values())
            leaves = sorted(node for node, deps in remaining.items() if len(deps) == min_size)

        layers.append(leaves)

        for leaf in leaves:
            for parent in reverse.get(leaf, set()):
                if parent in remaining:
                    remaining[parent].discard(leaf)
            remaining.pop(leaf, None)
    return layers


def save_porting_order(order: list[list[str]], output_file: str | Path) -> None:
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(order, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Select file porting order from dependency graph.")
    parser.add_argument(
        "--input",
        default="../../script_outputs/all_files_function_call_graph.json",
        help="Dependency graph JSON path.",
    )
    parser.add_argument(
        "--output",
        default="../../script_outputs/porting_order.json",
        help="Output JSON path.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    input_json = (base / args.input).resolve()
    output_json = (base / args.output).resolve()

    graph = load_dependency_graph(input_json)
    order = compute_porting_order(graph)

    # Keep only MATLAB files in output order (defensive filter).
    matlab_order = [[name for name in step if name.lower().endswith(".m")] for step in order]
    matlab_order = [step for step in matlab_order if step]
    save_porting_order(matlab_order, output_json)

    print(f"Porting order computed successfully: {output_json}")
    print(f"Total layers: {len(matlab_order)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
