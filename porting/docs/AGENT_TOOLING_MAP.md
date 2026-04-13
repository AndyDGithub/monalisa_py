# Agent Tooling Map

Canonical reference for every script in `porting/scripts/`.
Scripts are grouped by scope (project → directory → file → one-time).

For operating procedures see `docs/IDE_AGENT_GUIDE.md`.  
For the shared importable library see `lib/utils.py`.

---

## Shared library

### `porting/lib/utils.py`

Importable by any script.  No CLI.

| Symbol | Purpose |
|---|---|
| `configure_logging(name, *, verbose)` | Return a named logger with console handler |
| `run_command(cmd, cwd, *, timeout_seconds, stream, logger, step_name)` | Run a subprocess, return `CommandResult` |
| `run_script(script, args, cwd, *, ...)` | Convenience wrapper for Python scripts |
| `load_json(path)` | Load a JSON file, return `{}` on error |
| `save_json(path, data)` | Write JSON, create parent dirs |
| `resolve_roots(roots_str, base)` | Parse comma-separated roots string |
| `CommandResult` | Dataclass: command, returncode, stdout, stderr, elapsed_seconds, timed_out |

---

## Project scope — orchestrators

### `run_agentic_porting_workflow.py`

**Main entry point.**  Runs the deterministic pipeline, then (if needed) the
LLM repair cycle.

Key arguments:

| Argument | Default | Purpose |
|---|---|---|
| `--roots` | `src,demo,tests,third_part` | Comma-separated source roots |
| `--force` | off | Force full regeneration |
| `--overwrite-manual` | off | Allow overwriting manually curated files |
| `--model` | `gpt-oss:20b` | Primary Ollama model |
| `--fallback-model` | `gpt-oss:20b` | Fallback if primary is unavailable |
| `--max-iterations` | 2 | LLM repair iterations |
| `--max-files-per-iteration` | 5 | Files repaired per iteration |
| `--disable-llm` | off | Skip LLM repair entirely |
| `--stream-repair-logs` | off | Forward repair logs to console in real time |
| `--dynamic-llm-timeout` | on | Scale timeout by file length |
| `--enable-matlab-help` | off | Enrich prompts with `matlab -batch "help <fn>"` |

---

### `run_porting_pipeline.py`

Deterministic pipeline only (no LLM).  Called internally by the workflow.

Key arguments: `--roots`, `--force`, `--skip-tests`, `--generate-contract-tests`,
`--compare-parity-snapshots`, `--overwrite-manual`.

---

### `build_agent_context.py`

Aggregates reports into a compact JSON + plain-text prompt for the next agent call.

Output:
- `porting/state/agent_context_compact.json`
- `porting/state/agent_context_compact.prompt.txt`

---

### `get_prompt_for_porting.py`

Generates a ready-to-paste agent prompt combining the system prompt and current
compact context.

Key arguments: `--mode full|compact|repair`.  
Output: `porting/state/porting_agent_prompt.txt`.

---

## Directory / multiple-file scope

### `search_matlab.py`

MATLAB file discovery and SHA256 hash tracking.

Importable API: `search_matlab_files(root)`, `build_hash_manifest(files)`,
`diff_manifests(old, new)`.

---

### `get_function_call_graph.py`

Builds the MATLAB function dependency graph for a list of `.m` files.

Importable API: `get_global_function_call_graph(matlab_files)` → `dict[str, list[str]]`.

---

### `select_file_order.py`

Topological sort of the dependency graph into dependency layers (leaf-first).

Importable API: `compute_porting_order(graph)` → `list[list[str]]`.

---

### `select_next_functions.py`

Lists the next MATLAB files to port, ordered by dependency layer, skipping
already-ported files.

Key arguments: `--roots`, `-n`, `--include-ported`, `--json`.  
Importable API: `select_next_files(roots, repo_root, *, n, skip_ported)`.

---

### `auto_fix_missing_imports.py`

Scans all generated Python files and inserts missing project-local imports
(`from src.<module> import <name>`).

Key arguments: `--roots`, `--apply` (dry-run by default), `--summary-only`.

---

### `analyze_generated_files.py`

Analyses generated Python files for health: TODO markers, compile errors,
fallback stubs, risky True/False() calls.

Key arguments: `--roots`.  
Output: `porting/reports/generated_files_analysis.json`.

---

### `run_agentic_repair_cycle.py`

LLM-driven iterative repair: pipeline → pytest → collect failures → LLM patch
→ repeat.

Key arguments: `--roots`, `--model`, `--fallback-model`, `--max-iterations`,
`--max-files-per-iteration`, `--enable-matlab-help`, `--dynamic-llm-timeout`,
`--stream-subprocess-logs`.  
Output: `porting/reports/agent_repair_cycle_report.json`.

---

### `compare_matlab_python_logic.py`

Compares extracted MATLAB logic against the generated Python for
function-name, arg, and return-value mismatches.

---

### `compare_old_new_logic.py`

Diffs two extracted-logic snapshots to identify MATLAB files changed upstream.

---

### `compare_parity_snapshots.py`

Compares SHA256 fingerprint manifests from MATLAB and Python parity runs.

---

### `generate_contract_tests.py`

Generates structural pytest files (`test_contract_*.py`) that verify each
translated module is importable, functions exist, arity matches, and no
fallback stubs remain.

---

### `clean_project.py`

Removes porting artifacts: state JSON, reports, generated tests, `__pycache__`.  
Key arguments: `--all` or selective flags (`--state`, `--reports`, `--tests`).

---

### `cleanup_pipeline_artifacts.py`

Removes stale generated tests (whose TARGET_FILE no longer exists), empty
directories, and cache folders.

Key arguments: `--clean-cache`, `--prune-stale-tests`, `--remove-empty-dirs`,
`--apply` (dry-run by default).

---

## File scope — atomic tools

### `porting_compiler.py`

Incremental MATLAB→Python transpiler.  Discovers `.m` files, builds dependency
graph, generates Python skeletons with `# TODO(matlab-*)` markers for
unresolved calls, persists state via content/logic hashes.

Key arguments: `--matlab-root`, `--python-root`, `--mapping-file`,
`--force`, `--skip-tests`, `--overwrite-manual`.

Importable API: `compile_project(matlab_root, python_root, ...)`.

---

### `extract_logic.py`

Parses MATLAB or Python source into instruction blocks (function_decl,
assignment, call, if, for, while, return, …) and computes a logic hash.

Importable API: `parse_matlab_file(path, local_functions)`,
`parse_python_file(path)`.

---

### `run_parity_case.py`

Runs a single parity check (L2 / NMSE / SSIM) comparing a MATLAB reference
artifact against the Python candidate.

Key arguments: `--case` (JSON case definition).

---

### `bootstrap_porting_task.py`

Creates a new task YAML from the template, pre-filled with source/target paths.

---

## One-time setup tools

These are run once to build configuration; they are not part of the daily
porting loop.

| Script | Purpose |
|---|---|
| `scrape_function_docs.py` | Crawl MATLAB and Python docs to build `doc_function_catalog.json` |
| `build_project_instruction_kb.py` | Build project-scoped symbol knowledge bases |
| `enrich_instruction_kb.py` | Post-process and clean the knowledge bases |
| `generate_matlab_native_compat.py` | Generate `third_part/matlab_compat/matlab_native.py` stub library |

---

## Deprecated / experimental

| Script | Status | Note |
|---|---|---|
| `porting_agent_ollama.py` | Experimental | LangChain-based tool-dispatch agent; superseded by `run_agentic_repair_cycle.py` for most use cases |
