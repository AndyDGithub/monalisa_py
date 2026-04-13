#!/usr/bin/env python3
"""Run deterministic hybrid MATLAB->Python pipeline across one or more roots."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


SCRIPT_DIR = Path(__file__).resolve().parent

try:
    from monalisa_py.porting.scripts.get_function_call_graph import get_global_function_call_graph
    from monalisa_py.porting.scripts.porting_compiler import compile_project
    from monalisa_py.porting.scripts.search_matlab import build_hash_manifest, diff_manifests, search_matlab_files
    from monalisa_py.porting.scripts.select_file_order import compute_porting_order
except ImportError:
    from get_function_call_graph import get_global_function_call_graph
    from porting_compiler import compile_project
    from search_matlab import build_hash_manifest, diff_manifests, search_matlab_files
    from select_file_order import compute_porting_order


LEGACY_HASH_KEY = "__legacy_flat_manifest__"


def _run_script(script_path: Path, args: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(script_path), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _sanitize_tag(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip("/\\"))


def _root_tag(root: Path, repo_root: Path) -> str:
    try:
        rel = root.resolve().relative_to(repo_root.resolve())
        rel_text = "/".join(rel.parts)
    except ValueError:
        rel_text = root.name
    if not rel_text:
        rel_text = root.name or "root"
    return _sanitize_tag(rel_text)


def _load_multi_hash_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 2, "roots": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 2, "roots": {}}

    if isinstance(data, dict) and isinstance(data.get("roots"), dict):
        return {"version": int(data.get("version", 2)), "roots": dict(data["roots"])}

    # Backward compatibility: old flat manifest
    if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
        return {"version": 2, "roots": {LEGACY_HASH_KEY: dict(data)}}
    return {"version": 2, "roots": {}}


def _save_multi_hash_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _parse_roots(roots_arg: str, repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    for token in [t.strip() for t in roots_arg.split(",") if t.strip()]:
        p = (repo_root / token).resolve()
        if p.exists() and p.is_dir():
            roots.append(p)
    # Keep stable order + dedupe
    out: list[Path] = []
    seen: set[Path] = set()
    for p in roots:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def run_pipeline(
    *,
    repo_root: Path,
    roots: list[Path],
    generated_tests_root: Path,
    contracts_tests_root: Path,
    reports_dir: Path,
    state_dir: Path,
    native_map_file: Path,
    hash_manifest_file: Path,
    max_files: int | None,
    force: bool,
    skip_tests: bool,
    overwrite_manual: bool,
    generate_contract_tests: bool,
    run_parity: bool,
    parity_cases: Path | None,
    compare_parity_snapshots: bool,
    parity_reference_root: Path | None,
    parity_candidate_root: Path | None,
    verbose: bool,
) -> dict[str, Any]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    hash_store = _load_multi_hash_manifest(hash_manifest_file)
    roots_report: dict[str, Any] = {}

    script_dir = Path(__file__).resolve().parent
    extract_logic_path = script_dir / "extract_logic.py"
    compare_old_new_path = script_dir / "compare_old_new_logic.py"
    compare_mat_py_path = script_dir / "compare_matlab_python_logic.py"
    generate_contract_tests_path = script_dir / "generate_contract_tests.py"
    run_parity_case_path = script_dir / "run_parity_case.py"
    compare_parity_snapshots_path = script_dir / "compare_parity_snapshots.py"

    for root in roots:
        tag = _root_tag(root, repo_root)
        root_reports_dir = reports_dir / "roots" / tag
        root_reports_dir.mkdir(parents=True, exist_ok=True)

        matlab_files = search_matlab_files(root)
        new_manifest = build_hash_manifest(matlab_files, root=root)

        old_manifest = hash_store["roots"].get(tag, {})
        if not old_manifest and tag == "src" and LEGACY_HASH_KEY in hash_store["roots"]:
            old_manifest = hash_store["roots"][LEGACY_HASH_KEY]
        hash_diff = diff_manifests(old_manifest, new_manifest)
        hash_store["roots"][tag] = new_manifest

        dep_graph = get_global_function_call_graph(matlab_files)
        dep_graph_path = root_reports_dir / "dependency_graph.json"
        dep_graph_path.write_text(json.dumps(dep_graph, indent=2), encoding="utf-8")
        porting_order = compute_porting_order(dep_graph)
        porting_order_path = root_reports_dir / "porting_order.json"
        porting_order_path.write_text(json.dumps(porting_order, indent=2), encoding="utf-8")

        root_state_file = state_dir / f"porting_state_{tag}.json"
        root_generated_tests = generated_tests_root / tag
        root_compile_reports = root_reports_dir / "compiler"
        compile_summary = compile_project(
            matlab_root=root,
            python_root=root,
            tests_root=root_generated_tests,
            state_file=root_state_file,
            mapping_file=native_map_file,
            reports_dir=root_compile_reports,
            max_files=max_files,
            force=force,
            retries=1,
            run_tests=not skip_tests,
            preserve_manual=not overwrite_manual,
        )

        extracted_logic_report = root_reports_dir / "extracted_logic.json"
        extract_cmd = _run_script(
            extract_logic_path,
            [
                "--matlab-root",
                str(root),
                "--output",
                str(extracted_logic_report),
                "--include-python",
            ],
        )

        previous_logic_file = state_dir / f"previous_extracted_logic_{tag}.json"
        if extracted_logic_report.exists() and previous_logic_file.exists():
            compare_old_new = _run_script(
                compare_old_new_path,
                [
                    "--new",
                    str(extracted_logic_report),
                    "--old",
                    str(previous_logic_file),
                    "--output",
                    str(root_reports_dir / "differences_old_new_logic.json"),
                ],
            )
        elif extracted_logic_report.exists():
            compare_old_new = {"status": "skipped_first_run"}
        else:
            compare_old_new = {"status": "extract_logic_failed"}

        if extracted_logic_report.exists():
            shutil.copyfile(extracted_logic_report, previous_logic_file)

        compare_mat_py = _run_script(
            compare_mat_py_path,
            [str(extracted_logic_report), "--output", str(root_reports_dir / "logic_differences.json")],
        )

        contract_gen: dict[str, Any] = {"status": "skipped"}
        if generate_contract_tests:
            root_contracts_tests = contracts_tests_root / tag
            root_contract_report = root_reports_dir / "contract_test_generation_report.json"
            contract_gen = _run_script(
                generate_contract_tests_path,
                [
                    "--matlab-root",
                    str(root),
                    "--python-root",
                    str(root),
                    "--tests-root",
                    str(root_contracts_tests),
                    "--report",
                    str(root_contract_report),
                    "--summary-only",
                ],
            )

        roots_report[tag] = {
            "root": str(root),
            "hash_scan": {
                "matlab_file_count": len(matlab_files),
                "added": len(hash_diff["added"]),
                "changed": len(hash_diff["changed"]),
                "removed": len(hash_diff["removed"]),
            },
            "dependency_graph": {
                "graph_path": str(dep_graph_path),
                "porting_order_path": str(porting_order_path),
                "layers": len(porting_order),
            },
            "compile": compile_summary,
            "extract_logic": extract_cmd,
            "compare_old_new_logic": compare_old_new,
            "compare_matlab_python": compare_mat_py,
            "generate_contract_tests": contract_gen,
        }

    _save_multi_hash_manifest(hash_manifest_file, hash_store)

    steps: dict[str, Any] = {"roots": roots_report}

    if run_parity:
        if parity_cases and parity_cases.exists():
            parity_res = _run_script(
                run_parity_case_path,
                ["--cases-json", str(parity_cases), "--output", str(reports_dir / "parity_report.json")],
            )
            steps["parity_cases"] = parity_res
        else:
            steps["parity_cases"] = {"status": "skipped_no_cases"}

    if compare_parity_snapshots:
        args = [
            "--reference-root",
            str(parity_reference_root or (repo_root / "parity")),
            "--output",
            str(reports_dir / "parity_snapshot_comparison.json"),
        ]
        if parity_candidate_root is not None:
            args.extend(["--candidate-root", str(parity_candidate_root)])
        parity_snapshot_res = _run_script(compare_parity_snapshots_path, args)
        steps["parity_snapshots"] = parity_snapshot_res

    total_matlab_files = sum(v["hash_scan"]["matlab_file_count"] for v in roots_report.values())
    total_changed = sum(v["compile"].get("changed_files", 0) for v in roots_report.values())
    steps["summary"] = {
        "roots_processed": len(roots_report),
        "total_matlab_files": total_matlab_files,
        "total_changed_files": total_changed,
    }
    return steps


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic hybrid porting pipeline.")
    parser.add_argument(
        "--roots",
        default="src,demo,tests,third_part",
        help="Comma-separated MATLAB roots to process.",
    )
    parser.add_argument("--generated-tests-root", default="../tests/generated", help="Generated tests root directory.")
    parser.add_argument("--contracts-tests-root", default="../tests/contracts", help="Contract tests root directory.")
    parser.add_argument("--reports-dir", default="../reports", help="Reports directory.")
    parser.add_argument("--state-dir", default="../state", help="State directory.")
    parser.add_argument(
        "--native-map-file",
        default="../config/native_function_map.json",
        help="Native function map file.",
    )
    parser.add_argument(
        "--hash-manifest-file",
        default="../state/matlab_hashes.json",
        help="MATLAB hash manifest file.",
    )
    parser.add_argument("--max-files", type=int, default=None, help="Max changed files to process per root.")
    parser.add_argument("--force", action="store_true", help="Force regeneration.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip generated pytest during compile step.")
    parser.add_argument("--overwrite-manual", action="store_true", help="Allow overwrite of manually curated Python.")
    parser.add_argument(
        "--generate-contract-tests",
        action="store_true",
        help="Generate structural contract tests for translated files.",
    )
    parser.add_argument("--run-parity", action="store_true", help="Run parity cases from --parity-cases.")
    parser.add_argument("--parity-cases", default="../reports/parity_cases.json", help="Parity cases JSON path.")
    parser.add_argument(
        "--compare-parity-snapshots",
        action="store_true",
        help="Compare parity snapshot fingerprints between reference and candidate roots.",
    )
    parser.add_argument("--parity-reference-root", default="../../parity", help="Reference parity root.")
    parser.add_argument(
        "--parity-candidate-root",
        default=None,
        help="Candidate parity root (optional). If omitted, only reference structure is validated.",
    )
    parser.add_argument("--output", default="../reports/pipeline_run_report.json", help="Pipeline summary JSON output.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    repo_root = (base / "../../").resolve()
    roots = _parse_roots(args.roots, repo_root)
    if not roots:
        raise SystemExit(f"No valid roots resolved from --roots='{args.roots}'")

    generated_tests_root = (base / args.generated_tests_root).resolve()
    contracts_tests_root = (base / args.contracts_tests_root).resolve()
    reports_dir = (base / args.reports_dir).resolve()
    state_dir = (base / args.state_dir).resolve()
    native_map_file = (base / args.native_map_file).resolve()
    hash_manifest_file = (base / args.hash_manifest_file).resolve()
    parity_cases = (base / args.parity_cases).resolve() if args.parity_cases else None
    parity_reference_root = (base / args.parity_reference_root).resolve() if args.parity_reference_root else None
    parity_candidate_root = (base / args.parity_candidate_root).resolve() if args.parity_candidate_root else None
    output = (base / args.output).resolve()

    report = run_pipeline(
        repo_root=repo_root,
        roots=roots,
        generated_tests_root=generated_tests_root,
        contracts_tests_root=contracts_tests_root,
        reports_dir=reports_dir,
        state_dir=state_dir,
        native_map_file=native_map_file,
        hash_manifest_file=hash_manifest_file,
        max_files=args.max_files,
        force=args.force,
        skip_tests=args.skip_tests,
        overwrite_manual=args.overwrite_manual,
        generate_contract_tests=args.generate_contract_tests,
        run_parity=args.run_parity,
        parity_cases=parity_cases,
        compare_parity_snapshots=args.compare_parity_snapshots,
        parity_reference_root=parity_reference_root,
        parity_candidate_root=parity_candidate_root,
        verbose=args.verbose
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Pipeline report written to: {output}")
    print(json.dumps(report.get("summary", {}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
