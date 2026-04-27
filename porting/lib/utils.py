"""Shared utilities for the MATLAB->Python porting toolchain.

This module is the single source of truth for cross-cutting concerns:
subprocess execution, logging setup, JSON I/O, and path helpers.
All porting scripts import from here instead of reimplementing these patterns.

Importable API
--------------
configure_logging(name, verbose) -> Logger
run_command(cmd, cwd, *, ...) -> CommandResult
run_script(script, args, cwd, *, ...) -> CommandResult
load_json(path) -> dict
save_json(path, data)
resolve_roots(roots_str, base) -> list[Path]
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def configure_logging(name: str, *, verbose: bool = False) -> logging.Logger:
    """Return a logger named *name*, configured for console output.

    Safe to call multiple times: will not add duplicate handlers.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------

@dataclass
class CommandResult:
    """Outcome of a subprocess call."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool = field(default=False)

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "elapsed_seconds": self.elapsed_seconds,
            "timed_out": self.timed_out,
        }


def run_command(
    cmd: list[str],
    cwd: Path,
    *,
    timeout_seconds: float | None = None,
    stream: bool = False,
    logger: logging.Logger | None = None,
    step_name: str = "",
) -> CommandResult:
    """Execute *cmd* in *cwd* and return a :class:`CommandResult`.

    Parameters
    ----------
    cmd:
        Full command list (e.g. ``[sys.executable, "script.py", "--flag"]``).
    cwd:
        Working directory for the subprocess.
    timeout_seconds:
        Optional hard timeout. On expiry the result has ``timed_out=True`` and
        ``returncode=-1``.  Ignored when *stream=True*.
    stream:
        When True, forward subprocess stdout line-by-line to *logger* in real
        time (merges stderr into stdout).  Useful for long-running steps.
    logger:
        Logger used for start/done/fail messages and streamed output.
    step_name:
        Human-readable label included in log messages.
    """
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    label = step_name or " ".join(cmd[:2])
    if logger:
        logger.info("START %-36s | %s", label, " ".join(cmd))

    t0 = time.perf_counter()

    if stream:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        lines: list[str] = []
        assert proc.stdout is not None
        for raw in proc.stdout:
            line = raw.rstrip("\n")
            lines.append(line)
            if logger:
                logger.info("[%s] %s", label, line)
        returncode = proc.wait()
        stdout_text = "\n".join(lines)
        stderr_text = ""
        timed_out = False
    else:
        kwargs: dict[str, Any] = {}
        if timeout_seconds is not None:
            kwargs["timeout"] = timeout_seconds
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                env=env,
                **kwargs,
            )
            returncode = completed.returncode
            stdout_text = completed.stdout
            stderr_text = completed.stderr
            timed_out = False
        except subprocess.TimeoutExpired:
            elapsed = round(time.perf_counter() - t0, 2)
            if logger:
                logger.error("TIMEOUT %-36s (%.2fs)", label, elapsed)
            return CommandResult(
                command=cmd,
                returncode=-1,
                stdout="",
                stderr=f"Timed out after {timeout_seconds}s",
                elapsed_seconds=elapsed,
                timed_out=True,
            )

    elapsed = round(time.perf_counter() - t0, 2)
    if logger:
        if returncode == 0:
            logger.info("DONE  %-36s (%.2fs)", label, elapsed)
        else:
            logger.error("FAIL  %-36s (%.2fs) rc=%s", label, elapsed, returncode)

    return CommandResult(
        command=cmd,
        returncode=returncode,
        stdout=stdout_text,
        stderr=stderr_text,
        elapsed_seconds=elapsed,
        timed_out=timed_out,
    )


def run_script(
    script: Path,
    args: list[str],
    cwd: Path,
    *,
    step_name: str = "",
    stream: bool = False,
    timeout_seconds: float | None = None,
    logger: logging.Logger | None = None,
) -> CommandResult:
    """Convenience wrapper: run a Python script via the current interpreter."""
    cmd = [sys.executable, str(script), *args]
    return run_command(
        cmd,
        cwd,
        timeout_seconds=timeout_seconds,
        stream=stream,
        logger=logger,
        step_name=step_name or script.name,
    )


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file and return a dict.  Returns ``{}`` on any error."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_json(path: Path, data: Any, *, indent: int = 2) -> None:
    """Serialise *data* to *path*, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent), encoding="utf-8")


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def resolve_roots(roots_str: str, base: Path) -> list[Path]:
    """Parse a comma-separated roots string and resolve each path against *base*.

    Example::

        resolve_roots("src,demo,tests", repo_root)
        # -> [repo_root/src, repo_root/demo, repo_root/tests]
    """
    return [
        (base / token.strip()).resolve()
        for token in roots_str.split(",")
        if token.strip()
    ]


def repo_root_from_script(script_file: str, levels_up: int = 2) -> Path:
    """Compute the repository root relative to a script file.

    Typical usage in a script::

        REPO_ROOT = repo_root_from_script(__file__)
    """
    return Path(script_file).resolve().parents[levels_up - 1]


def delete_path(path: Path) -> None:
    """Delete a file or directory at *path*, ignoring any errors."""
    try:
        if path.is_dir():
            for child in path.iterdir():
                delete_path(child)
            path.rmdir()
        elif path.is_file():
            path.unlink()
    except OSError:
        pass


# ══════════════════════════
# MATLAB-compatible helpers
# ══════════════════════════

import numpy as np


def ndims(x: Any) -> int:
    """
    Équivalent de ndims MATLAB.
    """
    if isinstance(x, np.ndarray):
        return x.ndim

    # Pour listes imbriquées, on force conversion numpy
    try:
        return np.asarray(x).ndim
    except Exception:
        return 0


def strcmp(a: Any, b: Any) -> bool:
    """
    Équivalent simple de strcmp MATLAB.
    """
    return str(a) == str(b)


def islogical(x: Any) -> bool:
    """
    Équivalent de islogical MATLAB.
    """
    return isinstance(x, (bool, np.bool_))


def matlab_class(x: Any) -> str:
    """
    Approximation de class(x) MATLAB.
    Ici on ne gère que ce qui est utile pour ce port.
    """
    if isinstance(x, np.ndarray):
        if x.dtype == np.float32:
            return "single"
        if x.dtype == np.float64:
            return "double"
        if x.dtype == np.complex64:
            return "single"
        if x.dtype == np.complex128:
            return "double"
    return type(x).__name__


def int32(x: Any) -> np.int32:
    return np.int32(x)


def real(x: np.ndarray) -> np.ndarray:
    return np.real(x)


def imag(x: np.ndarray) -> np.ndarray:
    return np.imag(x)



import tkinter as tk
from tkinter import messagebox

# def errordlg(message: str) -> None:
#     root = tk.Tk()
#     root.withdraw()
#     messagebox.showerror("Error", message)
#     root.destroy()

# def warndlg(message: str) -> None:
#     root = tk.Tk()
#     root.withdraw()
#     messagebox.showwarning("Warning", message)
#     root.destroy()

# def questdlg(message: str) -> bool:
#     root = tk.Tk()
#     root.withdraw()
#     result = messagebox.askyesno("Question", message)
#     root.destroy()
#     return result

def errordlg(message: str) -> None:
    """
    Placeholder for MATLAB's errordlg function.
    In a real port, this could be implemented to show a GUI dialog or log an error.
    For now, it simply prints the message to stderr.
    """
    print(f"ERROR: {message}", file=sys.stderr)

def warndlg(message: str) -> None:
    """
    Placeholder for MATLAB's warndlg function.
    In a real port, this could be implemented to show a GUI dialog or log a warning.
    For now, it simply prints the message to stderr.
    """
    print(f"WARNING: {message}", file=sys.stderr)

def questdlg(message: str) -> bool:
    """
    Placeholder for MATLAB's questdlg function.
    In a real port, this could be implemented to show a GUI dialog or prompt the user.
    For now, it simply prompts in the console and returns True for 'yes' and False for 'no'.
    """
    response = input(f"{message} (y/n): ").strip().lower()
    return response == 'y'


def inputname(
    position: int,
    *args: Any,
    explicit_name: str | None = None,
    fallback_name: str = "",
    frame_depth: int = 2,
) -> str:
    """Best-effort MATLAB `inputname` compatibility wrapper."""
    from third_part.matlab_compat.matlab_runtime_metadata import resolve_inputname

    return resolve_inputname(
        position,
        args=args or None,
        explicit_name=explicit_name,
        fallback_name=fallback_name,
        frame_depth=frame_depth + 1,
    )


def assignin(
    scope: str,
    name: str,
    value: Any,
    runtime_metadata: Any | None = None,
) -> Any:
    """Best-effort MATLAB `assignin` compatibility wrapper."""
    from third_part.matlab_compat.matlab_runtime_metadata import assignin_runtime

    return assignin_runtime(scope, name, value, metadata=runtime_metadata)


def evalin(
    scope: str,
    expression: str,
    runtime_metadata: Any | None = None,
    default: Any = None,
) -> Any:
    """Best-effort MATLAB `evalin` compatibility wrapper."""
    from third_part.matlab_compat.matlab_runtime_metadata import evalin_runtime

    return evalin_runtime(scope, expression, metadata=runtime_metadata, default=default)
