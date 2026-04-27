#!/usr/bin/env python3
"""Compatibility entrypoint for agentic repair cycle.

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


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--engine", choices=["v2", "legacy"], default="v2")
    known, unknown = parser.parse_known_args()
    if known.engine == "legacy":
        return _run("run_agentic_repair_cycle_legacy.py", unknown)
    return _run("run_agentic_repair_cycle_v2.py", unknown)


if __name__ == "__main__":
    raise SystemExit(main())

