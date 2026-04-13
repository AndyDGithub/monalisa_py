#!/usr/bin/env python3
"""Compare two extracted logic snapshots (old/new) and emit a structured diff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _signature(info: dict[str, Any]) -> dict[str, Any]:
    return {
        "function_name": info.get("function_name"),
        "args": info.get("args", []),
        "returns": info.get("returns", []),
    }


def compare_logic(new_logic_path: str | Path, old_logic_path: str | Path, differences_path: str | Path) -> dict[str, Any]:
    new_logic = _load_json(Path(new_logic_path))
    old_logic = _load_json(Path(old_logic_path))

    differences: dict[str, Any] = {}

    new_files = set(new_logic)
    old_files = set(old_logic)

    for file_path in sorted(new_files - old_files):
        differences[file_path] = {
            "status": "new_file",
            "new": {
                "signature": _signature(new_logic[file_path]),
                "source_hash": new_logic[file_path].get("source_hash"),
                "logic_hash": new_logic[file_path].get("logic_hash"),
            },
        }

    for file_path in sorted(old_files - new_files):
        differences[file_path] = {
            "status": "deleted_file",
            "old": {
                "signature": _signature(old_logic[file_path]),
                "source_hash": old_logic[file_path].get("source_hash"),
                "logic_hash": old_logic[file_path].get("logic_hash"),
            },
        }

    for file_path in sorted(new_files & old_files):
        new_info = new_logic[file_path]
        old_info = old_logic[file_path]

        new_source_hash = new_info.get("source_hash")
        old_source_hash = old_info.get("source_hash")
        new_logic_hash = new_info.get("logic_hash")
        old_logic_hash = old_info.get("logic_hash")

        if new_source_hash == old_source_hash and new_logic_hash == old_logic_hash:
            continue

        file_diff: dict[str, Any] = {"status": "modified"}

        if _signature(new_info) != _signature(old_info):
            file_diff["signature"] = {
                "old": _signature(old_info),
                "new": _signature(new_info),
            }

        old_deps = sorted(old_info.get("dependencies", []))
        new_deps = sorted(new_info.get("dependencies", []))
        if old_deps != new_deps:
            file_diff["dependencies"] = {
                "added": sorted(set(new_deps) - set(old_deps)),
                "removed": sorted(set(old_deps) - set(new_deps)),
            }

        old_calls = sorted(old_info.get("native_calls", []))
        new_calls = sorted(new_info.get("native_calls", []))
        if old_calls != new_calls:
            file_diff["native_calls"] = {
                "added": sorted(set(new_calls) - set(old_calls)),
                "removed": sorted(set(old_calls) - set(new_calls)),
            }

        if old_logic_hash != new_logic_hash:
            file_diff["logic_hash"] = {"old": old_logic_hash, "new": new_logic_hash}
        if old_source_hash != new_source_hash:
            file_diff["source_hash"] = {"old": old_source_hash, "new": new_source_hash}

        differences[file_path] = file_diff

    out = Path(differences_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(differences, indent=2), encoding="utf-8")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare old/new extracted logic snapshots.")
    parser.add_argument("--new", required=True, help="New extracted logic JSON path.")
    parser.add_argument("--old", required=True, help="Old extracted logic JSON path.")
    parser.add_argument("--output", default="../reports/differences_old_new_logic.json", help="Output diff JSON path.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    new_path = (base / args.new).resolve()
    old_path = (base / args.old).resolve()
    out_path = (base / args.output).resolve()

    differences = compare_logic(new_path, old_path, out_path)
    print(f"Differences written to: {out_path}")
    print(f"Changed files: {len(differences)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
