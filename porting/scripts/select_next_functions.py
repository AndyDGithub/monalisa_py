#!/usr/bin/env python3
"""Select the next MATLAB files to port, ordered leaf-first by dependencies.

Reads the dependency graph (built by get_function_call_graph.py) and the
porting order (built by select_file_order.py), then filters out files that
already have an up-to-date Python equivalent.

Usage (CLI)
-----------
    # Show next 10 files, human-readable:
    python porting/scripts/select_next_functions.py --roots src,demo,tests,third_part

    # Output JSON for programmatic consumption:
    python porting/scripts/select_next_functions.py --roots src,demo,tests,third_part --json

    # Include already-ported files in output:
    python porting/scripts/select_next_functions.py --roots src,demo,tests,third_part --include-ported -n 20

Importable API
--------------
    from select_next_functions import select_next_files
    candidates = select_next_files(["src", "demo"], repo_root, n=5)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

try:
    from porting.lib.utils import configure_logging
    from porting.scripts.get_function_call_graph import get_global_function_call_graph
    from porting.scripts.search_matlab import search_matlab_files
    from porting.scripts.select_file_order import compute_porting_order
except ImportError:
    sys.path.insert(0, str(SCRIPT_DIR))
    from get_function_call_graph import get_global_function_call_graph  # type: ignore[no-redef]
    from search_matlab import search_matlab_files  # type: ignore[no-redef]
    from select_file_order import compute_porting_order  # type: ignore[no-redef]

    # utils may not be on path yet; fall back to a minimal inline implementation
    try:
        sys.path.insert(0, str(SCRIPT_DIR.parent / "lib"))
        from utils import configure_logging  # type: ignore[no-redef]
    except ImportError:
        import logging

        def configure_logging(name: str, *, verbose: bool = False) -> logging.Logger:  # type: ignore[misc]
            logger = logging.getLogger(name)
            if not logger.handlers:
                logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
            return logger


LOGGER = configure_logging("select_next_functions")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _expected_python_path(matlab_path: Path, repo_root: Path) -> Path:
    """Return the expected Python translation path for a MATLAB source file."""
    try:
        rel = matlab_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        # If the file is outside repo_root, use its name only
        rel = Path(matlab_path.name)
    return repo_root / rel.with_suffix(".py")


def select_next_files(
    roots: list[str],
    repo_root: Path,
    *,
    n: int = 10,
    skip_ported: bool = True,
) -> list[dict]:
    """Return up to *n* MATLAB files to port next, ordered leaf-first.

    Parameters
    ----------
    roots:
        Source root names relative to *repo_root* (e.g. ``["src", "demo"]``).
    repo_root:
        Absolute path to the repository root.
    n:
        Maximum number of candidates to return.
    skip_ported:
        When True (default), omit files that already have a Python equivalent.

    Returns
    -------
    list of dicts with keys:
        - layer (int): dependency layer (0 = no deps, higher = depends on lower)
        - matlab_file (str): absolute path of the MATLAB source
        - python_target (str): expected path of the Python translation
        - ported (bool): whether the Python file already exists
        - dep_count (int): number of unresolved dependencies (lower = sooner)
    """
    root_paths = [(repo_root / r.strip()).resolve() for r in roots if r.strip()]

    matlab_files: list[Path] = []
    for rp in root_paths:
        if rp.is_dir():
            matlab_files.extend(Path(p) for p in search_matlab_files(str(rp)))
        else:
            LOGGER.warning("Root not found, skipping: %s", rp)

    if not matlab_files:
        LOGGER.warning("No MATLAB files found under roots: %s", roots)
        return []

    LOGGER.info("Found %d MATLAB files across %d roots", len(matlab_files), len(root_paths))

    graph = get_global_function_call_graph(matlab_files)
    layers: list[list[str]] = compute_porting_order(graph)

    candidates: list[dict] = []
    for layer_idx, layer in enumerate(layers):
        for filepath_str in layer:
            path = Path(filepath_str)
            py_target = _expected_python_path(path, repo_root)
            is_ported = py_target.exists()

            if skip_ported and is_ported:
                continue

            # Count remaining unresolved dependencies (not yet ported)
            raw_deps: list[str] = graph.get(filepath_str, [])
            unresolved = sum(
                1 for dep in raw_deps
                if not _expected_python_path(Path(dep), repo_root).exists()
            )

            candidates.append({
                "layer": layer_idx,
                "matlab_file": str(path),
                "python_target": str(py_target),
                "ported": is_ported,
                "dep_count": unresolved,
            })

            if len(candidates) >= n:
                break
        if len(candidates) >= n:
            break

    return candidates


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="List next MATLAB files to port, leaf-first by dependency order.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--roots",
        default="src,demo,tests,third_part",
        help="Comma-separated source root directories (relative to --repo-root).",
    )
    parser.add_argument(
        "--repo-root",
        default="../../",
        help="Repository root (relative to this script's location).",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=10,
        help="Number of candidates to return.",
    )
    parser.add_argument(
        "--include-ported",
        action="store_true",
        help="Include files that already have a Python translation.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON instead of human-readable text (useful for scripts).",
    )
    args = parser.parse_args()

    repo_root = (SCRIPT_DIR / args.repo_root).resolve()
    roots = [r.strip() for r in args.roots.split(",") if r.strip()]

    candidates = select_next_files(
        roots,
        repo_root,
        n=args.n,
        skip_ported=not args.include_ported,
    )

    if args.as_json:
        print(json.dumps(candidates, indent=2))
        return 0

    if not candidates:
        print("All MATLAB files have been ported (or no files found).")
        return 0

    print(f"\nNext {len(candidates)} file(s) to port — leaf-first:\n")
    for c in candidates:
        status = "[DONE  ]" if c["ported"] else "[TODO  ]"
        deps_label = f"  unresolved_deps={c['dep_count']}" if c["dep_count"] > 0 else ""
        print(f"  {status} layer={c['layer']:>2}{deps_label}")
        print(f"           src: {c['matlab_file']}")
        print(f"           dst: {c['python_target']}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
