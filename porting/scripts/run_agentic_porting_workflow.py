#!/usr/bin/env python3
"""Compatibility entrypoint for agentic porting workflow.

Default engine is LangGraph v2.
Use `--engine legacy` to run the previous procedural workflow.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def _run(script_name: str, passthrough_args: list[str]) -> int:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *passthrough_args]
    proc = subprocess.run(cmd, check=False)
    return proc.returncode


def _normalize_legacy_flags(args: list[str]) -> list[str]:
    """Drop legacy no-op flags so old commands keep working."""
    no_op_flags = {"--force", "--overwrite-manual"}
    normalized: list[str] = []
    for token in args:
        if token in no_op_flags:
            continue
        normalized.append(token)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--engine", choices=["v2", "legacy"], default="v2")
    known, unknown = parser.parse_known_args()
    passthrough = _normalize_legacy_flags(unknown)
    if known.engine == "legacy":
        return _run("run_agentic_porting_workflow_legacy.py", passthrough)
    return _run("run_agentic_porting_workflow_v2.py", passthrough)


if __name__ == "__main__":
    raise SystemExit(main())

