#!/usr/bin/env python3
"""Create a new task YAML from template."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", help="e.g. TASK-0042")
    parser.add_argument("source_matlab", help="MATLAB source file path")
    parser.add_argument("target_python", help="Python target file path")
    args = parser.parse_args()

    template_path = Path("porting/tasks/task_template.yaml")
    data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    data["id"] = args.task_id
    data["source_matlab"] = args.source_matlab
    data["target_python"] = args.target_python

    out = Path("porting/tasks") / f"{args.task_id}.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"Created {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
