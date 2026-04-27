# IDE Agent Guide — MATLAB → Python Porting

This document tells an IDE agent (Claude Code, Cursor, Codex, …) exactly what to
do and ask in order to drive the porting pipeline.  Read it before issuing any
command to the porting toolchain.

---

## 1. Your mission

You are porting the `monalisa` MATLAB library to Python so that it can be used
without a MATLAB licence.  You drive a set of deterministic scripts that do the
heavy lifting; you only write or edit code yourself as a last resort.

**Success criteria** (check these after every iteration):

| Signal | File | What to look for |
|---|---|---|
| TODO markers trending down | `porting/reports/generated_files_analysis.json` | `summary.matlab_todo_markers` → 0 |
| Tests passing | pytest exit code | exit 0 |
| Parity OK (when snapshots exist) | `porting/reports/parity_snapshot_comparison.json` | `summary.ok` → true |
| Repair cycle bounded | `porting/reports/agent_repair_cycle_report.json` | no runaway iterations |

---

## 2. Workflow overview

```
┌──────────────────────────────────────────────┐
│  You (IDE agent)                             │
│  - Read reports                              │
│  - Run scripts with appropriate arguments    │
│  - Inspect logs                              │
│  - Manually fix files as last resort         │
└──────────────────┬───────────────────────────┘
                   │ custom args / monitoring
                   ▼
┌──────────────────────────────────────────────┐
│  run_agentic_porting_workflow.py             │  ← main entry point
│  (deterministic pipeline + repair cycle)     │
└──────┬──────────────┬────────────────────────┘
       │              │
       ▼              ▼
 run_porting_    run_agentic_
 pipeline.py     repair_cycle.py
       │              │
       ▼              ▼
 (compiler,      (LLM patches,
  analysis,       pytest loop,
  tests,          bounded iters)
  parity)
```

---

## 3. Standard operating procedure

### Step 1 — Orient yourself

Always start by checking what is already done:

```bash
# Current porting health at a glance
python porting/scripts/build_agent_context.py
cat porting/state/agent_context_compact.json
```

Key fields to read:
- `total_matlab_files` — total scope
- `total_changed_files` — files with pending changes since last run
- `matlab_todo_markers` — unresolved MATLAB calls (target: 0)
- `top_blockers` — files with most TODOs (port these first)

### Step 2 — Decide what to port next

```bash
# See which files are next in dependency order (leaf-first)
python porting/scripts/select_next_functions.py \
    --roots src,demo,tests,third_part \
    --n 20

# For JSON output (easier to parse programmatically):
python porting/scripts/select_next_functions.py \
    --roots src,demo,tests,third_part \
    --n 20 --json
```

### Step 3 — Run the full pipeline

Start with a deterministic-only pass to see what the compiler can do automatically:

```bash
# Deterministic-only (no LLM, fast, safe to repeat)
python porting/scripts/run_agentic_porting_workflow.py \
    --roots src,demo,tests,third_part \
    --disable-llm \
    --force \
    --skip-tests
```

Then run with LLM repair for files that still have TODOs:

```bash
# Full workflow with LLM repair (recommended settings)
python porting/scripts/run_agentic_porting_workflow.py \
    --roots src,demo,tests,third_part \
    --force --overwrite-manual \
    --model granite3.2:8b \
    --fallback-model gpt-oss:20b \
    --auto-pull-model \
    --max-iterations 3 \
    --max-files-per-iteration 20 \
    --stream-repair-logs \
    --llm-timeout-seconds 180 \
    --dynamic-llm-timeout \
    --dynamic-timeout-base-seconds 45 \
    --dynamic-timeout-per-line-seconds 3 \
    --dynamic-timeout-min-seconds 60 \
    --dynamic-timeout-max-seconds 900 \
    --enable-matlab-help \
    --matlab-help-max-functions 1 \
    --matlab-help-timeout-seconds 20
```

**Read the streaming logs.** Look for:
- `FAIL` lines → which step failed and why
- `[agentic_repair_cycle]` lines → LLM repair progress
- `matlab_todo_markers` in the final decision JSON

### Step 4 — Inspect reports

```bash
# See which files still have issues
cat porting/reports/generated_files_analysis.json | python -m json.tool

# See repair cycle outcome
cat porting/reports/agent_repair_cycle_report.json | python -m json.tool
```

### Step 5 — Fix imports deterministically

```bash
python porting/scripts/auto_fix_missing_imports.py \
    --roots ../../src,../../demo,../../tests,../../third_part \
    --apply \
    --summary-only
```

### Step 6 — Fix remaining TODO markers (iterative)

If TODO markers remain after the workflow, target specific files:

```bash
# Re-run repair cycle on a specific file
python porting/scripts/run_agentic_repair_cycle.py \
    --roots src,demo,tests,third_part \
    --model granite3.2:8b \
    --max-iterations 5 \
    --max-files-per-iteration 5 \
    --enable-matlab-help \
    --stream-subprocess-logs
```

### Step 7 — Manually edit as last resort

If the LLM cannot fix a file after several iterations, read the file and edit it:

```bash
# Check what the compiler produced for a specific file
cat src/path/to/file.py
```

Look for `# TODO(matlab-*)` comments — these are calls the compiler could not
map automatically.  Replace them with correct Python equivalents using:
- `config/native_function_map.json` — curated MATLAB→Python map
- `porting/docs/TODO_TRANSLATION_EXAMPLES.md` — translation examples
- `porting/docs/EXAMPLE_ORIGINAL_TO_PORTED.md` — full ported file example

---

## 4. Script reference by scope

### Project scope (orchestrators)

| Script | Purpose | Key args |
|---|---|---|
| `run_agentic_porting_workflow.py` | Main entry point: deterministic + optional LLM repair | `--roots`, `--model`, `--max-iterations`, `--disable-llm` |
| `run_porting_pipeline.py` | Deterministic pipeline only | `--roots`, `--force`, `--skip-tests` |
| `build_agent_context.py` | Build compact JSON + prompt for next agent call | (none required) |
| `get_prompt_for_porting.py` | Generate ready-to-paste prompt | `--mode full\|compact\|repair` |

### Directory / multiple-file scope

| Script | Purpose | Key args |
|---|---|---|
| `search_matlab.py` | Find and hash MATLAB files | `--root`, `--output` |
| `get_function_call_graph.py` | Build dependency graph | `--roots`, `--output` |
| `select_file_order.py` | Compute leaf-first porting order | `--graph` (JSON) |
| `select_next_functions.py` | List next files to port | `--roots`, `-n`, `--json` |
| `auto_fix_missing_imports.py` | Add missing project-local imports | `--roots`, `--apply` |
| `analyze_generated_files.py` | Count TODOs, risks, stubs | `--roots` |
| `run_agentic_repair_cycle.py` | LLM-driven iterative repair | `--roots`, `--model`, `--max-iterations` |
| `clean_project.py` | Remove porting artifacts | `--all` or selective flags |
| `cleanup_pipeline_artifacts.py` | Remove stale tests, caches | `--apply` |

### File scope (atomic tools)

| Script | Purpose | Key args |
|---|---|---|
| `porting_compiler.py` | Incremental MATLAB→Python transpiler | `--matlab-root`, `--python-root`, `--force` |
| `extract_logic.py` | Extract MATLAB/Python instruction blocks | `--path` |
| `compare_matlab_python_logic.py` | Diff MATLAB vs Python logic | `--matlab`, `--python` |
| `compare_old_new_logic.py` | Diff upstream MATLAB changes | `--old`, `--new` |
| `generate_contract_tests.py` | Generate structural tests | `--roots` |
| `run_parity_case.py` | Run parity metrics (L2/NMSE) | `--case` (JSON) |
| `compare_parity_snapshots.py` | Compare parity fingerprints | `--ref`, `--cand` |

### One-time setup tools (run once, not in the loop)

| Script | Purpose |
|---|---|
| `scrape_function_docs.py` | Crawl MATLAB/Python docs to build mapping candidates |
| `build_project_instruction_kb.py` | Build project-specific symbol knowledge base |
| `enrich_instruction_kb.py` | Post-process and clean the knowledge base |
| `generate_matlab_native_compat.py` | Generate `third_part/matlab_compat/matlab_native.py` |
| `bootstrap_porting_task.py` | Create a task YAML file from template |

---

## 5. Decision flowchart

```
Start
  │
  ├─ build_agent_context.py → read matlab_todo_markers
  │
  ├─ markers == 0 AND tests pass?
  │     YES → Done ✓
  │     NO  ↓
  │
  ├─ Run run_agentic_porting_workflow.py (deterministic + LLM)
  │     │
  │     ├─ markers decreased? → loop back to top
  │     │
  │     └─ markers stuck for 2+ iterations?
  │           │
  │           ├─ Run auto_fix_missing_imports.py
  │           ├─ Inspect top_blockers manually
  │           └─ Manually edit file (last resort)
  │
  └─ After each manual edit: re-run pipeline to validate
```

---

## 6. Reading JSON reports

### `porting/reports/generated_files_analysis.json`

```json
{
  "summary": {
    "auto_generated": 42,          // files the compiler produced
    "manual": 5,                   // files you edited manually
    "fallback_stubs": 3,           // files with NotImplementedError body
    "matlab_todo_markers": 18,     // ← KEY METRIC: how many TODOs remain
    "compile_errors": 0            // syntax errors in generated Python
  },
  "details": [...]                 // per-file breakdown
}
```

### `porting/reports/agent_repair_cycle_report.json`

```json
{
  "iterations": [
    {
      "iteration": 1,
      "targets_attempted": 5,
      "targets_patched": 3,
      "tests_before": {"failed": 10, "passed": 40},
      "tests_after":  {"failed": 7,  "passed": 43}
    }
  ],
  "final_status": "partial_success"  // or "success" / "failure"
}
```

### `porting/state/agent_context_compact.json`

```json
{
  "total_matlab_files": 200,
  "matlab_todo_markers": 18,
  "top_blockers": [
    {"file": "src/.../foo.py", "todo_count": 7},
    ...
  ]
}
```

---

## 7. What NOT to do

- **Do not read full source files** to understand the project; use the reports
  and compact context instead.
- **Do not run LLM repair on every iteration** if TODO markers are not
  decreasing; investigate why instead.
- **Do not increase `--max-iterations` indefinitely** — if stuck, change the
  model or fix manually.
- **Do not skip `--stream-repair-logs`** — you need to see what the repair
  cycle is doing.
- **Do not overwrite manually curated files** unless you pass `--overwrite-manual`
  intentionally.

---

## 8. Useful one-liners

```bash
# How many TODOs remain?
python -c "import json,pathlib; d=json.loads(pathlib.Path('porting/reports/generated_files_analysis.json').read_text()); print(d['summary']['matlab_todo_markers'])"

# Which files still have TODOs?
python porting/scripts/analyze_generated_files.py --roots ../../src,../../demo,../../tests,../../third_part

# List unresolved MATLAB function calls across all generated files
grep -r "TODO(matlab-" src/ demo/ tests/ third_part/ --include="*.py" | sort | uniq -c | sort -rn | head -30

# Dry-run cleanup
python porting/scripts/cleanup_pipeline_artifacts.py --clean-cache --prune-stale-tests --remove-empty-dirs

# Apply cleanup
python porting/scripts/cleanup_pipeline_artifacts.py --clean-cache --prune-stale-tests --remove-empty-dirs --apply
```

---

## 9. File locations quick reference

```
porting/
├── config/native_function_map.json     ← curated MATLAB→Python mapping (edit me)
├── state/agent_context_compact.json    ← current porting status (read me first)
├── state/porting_agent_prompt.txt      ← ready-to-paste prompt for an external LLM
├── reports/generated_files_analysis.json
├── reports/agent_repair_cycle_report.json
├── reports/pipeline_run_report.json
├── lib/utils.py                        ← shared utilities (importable)
├── prompts/system_ide_agent.md         ← system prompt for IDE agents
├── docs/AGENT_TOOLING_MAP.md          ← script-to-purpose reference
└── docs/TODO_TRANSLATION_EXAMPLES.md  ← how to translate specific MATLAB calls
```

## LangGraph v2 migration note

Default orchestration entrypoints now route to LangGraph v2:

```bash
python porting/scripts/run_agentic_porting_workflow.py --roots src,demo,tests,third_part
python porting/scripts/run_agentic_repair_cycle.py --current-file src/fourier3/bcaNeith3.py
```

To force the old procedural behavior:

```bash
python porting/scripts/run_agentic_porting_workflow.py --engine legacy --roots src,demo,tests,third_part
python porting/scripts/run_agentic_repair_cycle.py --engine legacy --target-file src/fourier3/bcaNeith3.py
```
