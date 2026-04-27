from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class WorkflowConfig:
    repo_root: Path
    roots: list[str] = field(default_factory=lambda: ["src", "demo", "tests", "third_part"])
    max_cycles: int = 12
    max_retries_per_file: int = 3
    generated_tests_per_iteration: int = 120
    contracts_per_iteration: int = 30
    llm_model: str = "gpt-oss:20b"
    fallback_model: str = "gpt-oss:20b"
    stream_subprocess_logs: bool = True
    enable_matlab_help: bool = True
    matlab_help_max_functions: int = 1
    matlab_help_timeout_seconds: int = 20
    dynamic_llm_timeout: bool = True
    llm_timeout_seconds: int = 180
    dynamic_timeout_base_seconds: int = 45
    dynamic_timeout_per_line_seconds: int = 3
    dynamic_timeout_min_seconds: int = 60
    dynamic_timeout_max_seconds: int = 900
    allow_matlab_todos: bool = False
    enable_strict_prefilter: bool = True
    pause_on_applied_false: bool = False
    sync_env: bool = False
    requirements_output: str = "porting/reports/requirements.generated.txt"
