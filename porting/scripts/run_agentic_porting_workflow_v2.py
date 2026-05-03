#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import importlib


def _bootstrap_python_path() -> None:
    """
    Ensure that both the repository root and legacy package root are in sys.path for imports.
    This allows the v2 workflow to import modules from both the new agentic package and the legacy monalisa_py package as needed.
    """
    script_dir = Path(__file__).resolve().parent
    repo_root = (script_dir / ".." / "..").resolve()
    legacy_pkg_root = (script_dir / ".." / "python").resolve()
    for path in (repo_root, legacy_pkg_root):
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def main() -> int:
    _bootstrap_python_path()
    for module_name in (
        "porting.agentic.cli.run_agentic_porting_workflow_v2",
        "monalisa_py.agentic.cli.run_agentic_porting_workflow_v2",
    ):
        try:
            module = importlib.import_module(module_name)
            return module.main()
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError(
        "Cannot import LangGraph v2 CLI module. Expected one of: "
        "porting.agentic.cli.run_agentic_porting_workflow_v2 or "
        "monalisa_py.agentic.cli.run_agentic_porting_workflow_v2"
    )


if __name__ == "__main__":
    raise SystemExit(main())
