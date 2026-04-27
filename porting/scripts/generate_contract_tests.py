#!/usr/bin/env python3
"""Generate structural contract tests for MATLAB->Python translated files.

These tests are useful when no MATLAB tests exist for a function:
- module import smoke check
- expected function name exists
- positional argument count matches MATLAB declaration
- generated python file is not a fallback stub
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from monalisa_py.porting.scripts.porting_compiler import discover_matlab_files, parse_matlab_file
except ImportError:
    from porting_compiler import discover_matlab_files, parse_matlab_file

try:
    from monalisa_py.porting.lib.matlab_source_quality import matlab_quality_for_python_file
except ImportError:
    try:
        from porting.lib.matlab_source_quality import matlab_quality_for_python_file
    except ImportError:
        def matlab_quality_for_python_file(python_file: Path, repo_root: Path) -> dict:
            return {
                "matlab_file_found": python_file.with_suffix(".m").exists(),
                "invalid_source": False,
                "undefined_identifiers": [],
                "unreferenced_in_call_graph": None,
                "special_case_invalid_unreferenced": False,
            }


TEST_TEMPLATE = '''"""Auto-generated structural contract test (MATLAB -> Python)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import inspect
{skip_import}
{skip_block}


TARGET_FILE = Path(__file__).resolve().parents[{target_parent_index}] / "{target_rel}"
EXPECTED_FUNCTION_NAME = "{function_name}"
EXPECTED_ARG_COUNT = {expected_arg_count}


def _load_module():
    spec = spec_from_file_location("ported_module", TARGET_FILE)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_module_importable():
    module = _load_module()
    assert module is not None


def test_expected_function_exists():
    module = _load_module()
    assert hasattr(module, EXPECTED_FUNCTION_NAME)
    fn = getattr(module, EXPECTED_FUNCTION_NAME)
    assert callable(fn)


def test_positional_arity_matches_matlab():
    module = _load_module()
    fn = getattr(module, EXPECTED_FUNCTION_NAME)
    sig = inspect.signature(fn)
    positional = [
        p
        for p in sig.parameters.values()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    assert len(positional) == EXPECTED_ARG_COUNT


def test_not_fallback_stub():
    text = TARGET_FILE.read_text(encoding="utf-8", errors="ignore")
    assert "Fallback stub generated because automatic translation did not compile yet" not in text
    assert "# compile_error:" not in text
'''


def _test_filename_for(rel_m: Path) -> str:
    stem = "_".join(rel_m.with_suffix("").parts)
    return f"test_contract_{stem}.py"


def _parent_index(child: Path, ancestor: Path) -> int:
    child_resolved = child.resolve()
    ancestor_resolved = ancestor.resolve()
    for idx, p in enumerate(child_resolved.parents):
        if p == ancestor_resolved:
            return idx
    raise ValueError(f"Ancestor {ancestor_resolved} not found in parents of {child_resolved}")


def generate_contract_tests(
    matlab_root: Path,
    python_root: Path,
    tests_root: Path,
    report_path: Path,
) -> dict:
    matlab_files = discover_matlab_files(matlab_root)
    local_names = {f.stem for f in matlab_files}

    created = 0
    updated = 0
    skipped_missing_python: list[str] = []
    skipped_invalid_unreferenced: list[str] = []
    generated_files: list[str] = []

    tests_root.mkdir(parents=True, exist_ok=True)
    repo_root = matlab_root.parent.resolve()

    for mf in matlab_files:
        rel_m = mf.relative_to(matlab_root)
        py_file = python_root / rel_m.with_suffix(".py")
        if not py_file.exists():
            skipped_missing_python.append(str(rel_m).replace("\\", "/"))
            continue

        parsed = parse_matlab_file(mf, local_names)
        function_name = parsed.function_name or py_file.stem
        expected_arg_count = len(parsed.args)
        source_quality = matlab_quality_for_python_file(py_file, repo_root)
        special_case_invalid_unreferenced = bool(source_quality.get("special_case_invalid_unreferenced", False))
        skip_import = ""
        skip_block = ""
        if special_case_invalid_unreferenced:
            undefined_names = ", ".join(source_quality.get("undefined_identifiers", [])[:8])
            reason = (
                "MATLAB source appears invalid and unreferenced in call graph; "
                f"undefined identifiers: {undefined_names or 'n/a'}"
            )
            reason_escaped = reason.replace('"', '\\"')
            skip_import = "import pytest"
            skip_block = f'pytestmark = pytest.mark.skip(reason="{reason_escaped}")'
            skipped_invalid_unreferenced.append(str(rel_m).replace("\\", "/"))

        test_name = _test_filename_for(rel_m)
        test_path = tests_root / test_name
        target_parent_index = _parent_index(test_path, repo_root)
        target_rel = str(py_file.resolve().relative_to(repo_root)).replace("\\", "/")
        test_content = TEST_TEMPLATE.format(
            target_rel=target_rel,
            function_name=function_name,
            expected_arg_count=expected_arg_count,
            target_parent_index=target_parent_index,
            skip_import=skip_import,
            skip_block=skip_block,
        )
        old = test_path.read_text(encoding="utf-8") if test_path.exists() else None
        if old is None:
            created += 1
        elif old != test_content:
            updated += 1

        if old != test_content:
            test_path.write_text(test_content, encoding="utf-8")
        generated_files.append(str(test_path))

    report = {
        "matlab_files": len(matlab_files),
        "contract_tests_written": len(generated_files),
        "created": created,
        "updated": updated,
        "skipped_missing_python": skipped_missing_python,
        "skipped_invalid_unreferenced": skipped_invalid_unreferenced,
        "generated_files": generated_files,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate structural contract tests for translated files.")
    parser.add_argument("--matlab-root", default="../../src", help="MATLAB source root.")
    parser.add_argument("--python-root", default="../../src", help="Python source root.")
    parser.add_argument("--tests-root", default="../tests/contracts", help="Output directory for generated tests.")
    parser.add_argument(
        "--report",
        default="../reports/contract_test_generation_report.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only compact summary to stdout (report file still contains full payload).",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    report = generate_contract_tests(
        matlab_root=(base / args.matlab_root).resolve(),
        python_root=(base / args.python_root).resolve(),
        tests_root=(base / args.tests_root).resolve(),
        report_path=(base / args.report).resolve(),
    )
    if args.summary_only:
        compact = {
            "matlab_files": report["matlab_files"],
            "contract_tests_written": report["contract_tests_written"],
            "created": report["created"],
            "updated": report["updated"],
            "skipped_missing_python": len(report["skipped_missing_python"]),
            "skipped_invalid_unreferenced": len(report.get("skipped_invalid_unreferenced", [])),
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
