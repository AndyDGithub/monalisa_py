from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _repo_root_from_here() -> Path:
    # src/mex/m/compile_mex_for_monalisa.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def _command_filename_for_platform() -> str:
    system_name = platform.system().lower()
    if system_name.startswith("win"):
        return "mex_command_windows.txt"
    if system_name == "darwin":
        return "mex_command_mac_llvm.txt"
    return "mex_command_linux.txt"


def _read_command_lines(command_file: Path) -> list[str]:
    lines: list[str] = []
    current = ""
    for raw in command_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("%"):
            continue
        if line.endswith("..."):
            current += line[:-3].rstrip() + " "
            continue
        full = (current + line).strip()
        current = ""
        if full:
            lines.append(full)
    if current.strip():
        lines.append(current.strip())
    return lines


def _discover_mex_commands(repo_root: Path) -> list[dict[str, str]]:
    src_root = (repo_root / "src").resolve()
    if not src_root.exists():
        return []

    command_filename = _command_filename_for_platform()
    out: list[dict[str, str]] = []
    for command_file in sorted(src_root.rglob(command_filename)):
        for command in _read_command_lines(command_file):
            out.append(
                {
                    "command_file": str(command_file),
                    "working_directory": str(command_file.parent),
                    "command": command,
                }
            )
    return out


def run_compile_mex_for_monalisa(
    *,
    repo_root: Path | None = None,
    execute: bool = True,
    fail_on_error: bool = False,
) -> dict[str, Any]:
    root = repo_root.resolve() if repo_root is not None else _repo_root_from_here()
    commands = _discover_mex_commands(root)
    mex_on_path = shutil.which("mex") is not None

    report: dict[str, Any] = {
        "repo_root": str(root),
        "platform": platform.system(),
        "command_file_name": _command_filename_for_platform(),
        "commands_discovered": len(commands),
        "commands_executed": 0,
        "commands_skipped": 0,
        "commands_failed": 0,
        "mex_on_path": bool(mex_on_path),
        "entries": [],
    }

    for item in commands:
        command = str(item["command"]).strip()
        wd = Path(str(item["working_directory"]))
        entry: dict[str, Any] = dict(item)

        if not execute:
            entry["status"] = "skipped_dry_run"
            report["commands_skipped"] += 1
            report["entries"].append(entry)
            continue

        if command.lower().startswith("mex ") and not mex_on_path:
            entry["status"] = "skipped_missing_mex_executable"
            entry["reason"] = "mex executable is not available in PATH."
            report["commands_skipped"] += 1
            report["entries"].append(entry)
            continue

        proc = subprocess.run(
            command,
            cwd=str(wd),
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        entry["returncode"] = int(proc.returncode)
        entry["stdout_tail"] = proc.stdout[-2000:]
        entry["stderr_tail"] = proc.stderr[-2000:]
        if proc.returncode == 0:
            entry["status"] = "ok"
            report["commands_executed"] += 1
        else:
            entry["status"] = "failed"
            report["commands_failed"] += 1
            report["commands_executed"] += 1
        report["entries"].append(entry)

    if fail_on_error and int(report["commands_failed"]) > 0:
        raise RuntimeError(
            f"MEX compilation failed for {report['commands_failed']} command(s)."
        )
    return report


def compile_mex_for_monalisa() -> None:
    """
    Compile MEX backends for MONALISA when available on this machine.

    Backward-compatible wrapper with zero arguments (kept for contract tests).
    Behavior can be controlled with environment variable `MONALISA_MEX_EXECUTE`:
    - `0` => discovery/dry-run only
    - any other value => execute commands (best effort)
    """
    execute = os.environ.get("MONALISA_MEX_EXECUTE", "1") != "0"
    run_compile_mex_for_monalisa(execute=execute, fail_on_error=False)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile MONALISA MEX backends.")
    parser.add_argument("--repo-root", default=None, help="Repository root (defaults to auto-detected root).")
    parser.add_argument("--dry-run", action="store_true", help="Discover commands without executing them.")
    parser.add_argument("--fail-on-error", action="store_true", help="Return non-zero if any command fails.")
    parser.add_argument("--output", default=None, help="Optional JSON output report path.")
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary JSON.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _repo_root_from_here()
    try:
        report = run_compile_mex_for_monalisa(
            repo_root=repo_root,
            execute=not args.dry_run,
            fail_on_error=bool(args.fail_on_error),
        )
    except RuntimeError as exc:
        report = {
            "repo_root": str(repo_root),
            "error": str(exc),
            "failed": True,
        }
        if args.output:
            output_path = Path(args.output).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.summary_only:
        compact = {
            "commands_discovered": report.get("commands_discovered", 0),
            "commands_executed": report.get("commands_executed", 0),
            "commands_skipped": report.get("commands_skipped", 0),
            "commands_failed": report.get("commands_failed", 0),
            "mex_on_path": report.get("mex_on_path", False),
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
