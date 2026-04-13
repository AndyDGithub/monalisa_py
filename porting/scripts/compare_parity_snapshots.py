#!/usr/bin/env python3
"""Compare MATLAB parity snapshots via fingerprint manifests.

A snapshot directory is any folder containing `fingerprints.json`.
Comparison is fingerprint-based (sha256 + metadata), deterministic and lightweight.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _find_snapshot_dirs(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    if not root.exists():
        return out
    for fp in root.rglob("fingerprints.json"):
        if not fp.is_file():
            continue
        snap_dir = fp.parent
        key = str(snap_dir.relative_to(root)).replace("\\", "/")
        out[key] = snap_dir
    return dict(sorted(out.items()))


def _load_fingerprints(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    vars_list = data.get("variables", []) if isinstance(data, dict) else []
    out: dict[str, dict[str, Any]] = {}
    for item in vars_list:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        out[name] = {
            "sha256": item.get("sha256"),
            "class": item.get("class"),
            "size": item.get("size"),
            "is_complex": item.get("is_complex"),
        }
    return out


def compare_snapshots(reference_root: Path, candidate_root: Path | None) -> dict[str, Any]:
    ref_snaps = _find_snapshot_dirs(reference_root)
    cand_snaps = _find_snapshot_dirs(candidate_root) if candidate_root is not None else {}

    missing_snapshot_dirs = sorted(set(ref_snaps) - set(cand_snaps))
    extra_snapshot_dirs = sorted(set(cand_snaps) - set(ref_snaps))
    common_snapshot_dirs = sorted(set(ref_snaps) & set(cand_snaps))

    per_snapshot: list[dict[str, Any]] = []
    for key in common_snapshot_dirs:
        ref_fp = _load_fingerprints(ref_snaps[key] / "fingerprints.json")
        cand_fp = _load_fingerprints(cand_snaps[key] / "fingerprints.json")

        ref_vars = set(ref_fp)
        cand_vars = set(cand_fp)
        missing_vars = sorted(ref_vars - cand_vars)
        extra_vars = sorted(cand_vars - ref_vars)

        variable_mismatches: list[dict[str, Any]] = []
        for name in sorted(ref_vars & cand_vars):
            ref_item = ref_fp[name]
            cand_item = cand_fp[name]
            if ref_item == cand_item:
                continue
            variable_mismatches.append(
                {
                    "name": name,
                    "reference": ref_item,
                    "candidate": cand_item,
                }
            )

        per_snapshot.append(
            {
                "snapshot": key,
                "missing_variables": missing_vars,
                "extra_variables": extra_vars,
                "variable_mismatches": variable_mismatches,
                "ok": (not missing_vars) and (not extra_vars) and (not variable_mismatches),
            }
        )

    failing_snapshots = [s for s in per_snapshot if not s["ok"]]

    summary = {
        "reference_snapshot_dirs": len(ref_snaps),
        "candidate_snapshot_dirs": len(cand_snaps),
        "missing_snapshot_dirs": len(missing_snapshot_dirs),
        "extra_snapshot_dirs": len(extra_snapshot_dirs),
        "common_snapshot_dirs": len(common_snapshot_dirs),
        "failing_snapshot_dirs": len(failing_snapshots),
        "ok": (
            candidate_root is not None
            and not missing_snapshot_dirs
            and not extra_snapshot_dirs
            and not failing_snapshots
        ),
    }

    return {
        "summary": summary,
        "reference_root": str(reference_root),
        "candidate_root": str(candidate_root) if candidate_root else None,
        "missing_snapshot_dirs": missing_snapshot_dirs,
        "extra_snapshot_dirs": extra_snapshot_dirs,
        "snapshots": per_snapshot,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare parity snapshot fingerprints.")
    parser.add_argument("--reference-root", default="../../parity", help="Reference parity root.")
    parser.add_argument(
        "--candidate-root",
        default=None,
        help="Candidate parity root with python-generated snapshots.",
    )
    parser.add_argument(
        "--output",
        default="../reports/parity_snapshot_comparison.json",
        help="Output report JSON path.",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit 1 if candidate exists and mismatch is detected.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    reference_root = (base / args.reference_root).resolve()
    candidate_root = (base / args.candidate_root).resolve() if args.candidate_root else None
    output = (base / args.output).resolve()

    report = compare_snapshots(reference_root, candidate_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Parity snapshot report written to: {output}")
    print(json.dumps(report["summary"], indent=2))

    if args.fail_on_mismatch and candidate_root is not None and not report["summary"]["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
