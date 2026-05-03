# Porting Framework — MATLAB → Python (monalisa)

Deterministic-first, agent-assisted migration system for `monalisa_py`.

---

## Objective

- Port the MATLAB `monalisa` library to Python reproducibly.
- Keep LLM usage bounded and cheap.
- Validate with structural contract tests and numerical parity checks.

## Core philosophy

1. **Deterministic scripts** do discovery, ordering, transpilation, and reporting.
2. **Agentic repair** runs only when deterministic output still has blockers.
3. **Reports and compact context** drive decisions — never full-repo prompts.

---

## Directory layout

```
porting/
├── config/                         Configuration (mapping files, parity config)
│   └── native_function_map.json    ← Curated MATLAB→Python symbol map (edit me)
├── lib/                            Shared Python utilities (importable)
│   └── utils.py                    logging, subprocess runner, JSON I/O
├── scripts/                        CLI entry points (each runnable standalone)
├── prompts/                        LLM system prompts
│   ├── system_ide_agent.md         ← Load this if you are an IDE agent
│   └── system_agentic_orchestrator_compact.md
├── docs/                           Operator guides
│   ├── IDE_AGENT_GUIDE.md          ← Full step-by-step for IDE agents
│   └── AGENT_TOOLING_MAP.md        Script-to-purpose reference
├── reports/                        Generated analysis outputs
├── state/                          Persistent hashes and compact context
├── tests/                          Generated and contract tests
└── tasks/                          YAML task definitions
```

---

## Quick-start commands

### One-command workflow (recommended)

In your IDE agent (Claude code, Codex, Cursor, etc):
1. Prompt to tha agent : 
```
"Load porting/prompts/system_ide_agent.md as your system prompt, then run:
python porting/scripts/build_agent_context.py"
```

### If you do not have an IDE agent
From the **repository root**:

```bash
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
or
```bash
python porting/scripts/run_agentic_porting_workflow.py \
      --roots src,demo,tests,third_part \
      --disable-llm --skip-tests
```
then 
```bash
python porting/scripts/run_agentic_porting_workflow.py \
      --roots src,demo,tests,third_part \
      --force \
      --overwrite-manual \
      --parallel-files-per-cycle 8 \
      --enable-parallel-repair \
      --parallel-repair-max-workers 8 \
      --skip-pipeline \
      --dynamic-llm-timeout \
      --dynamic-timeout-base-seconds 45 \
      --dynamic-timeout-per-line-seconds 3 \
      --dynamic-timeout-min-seconds 60 \
      --dynamic-timeout-max-seconds 600 \
      --enable-matlab-help \
      --matlab-help-max-functions 1 \
      --matlab-help-timeout-seconds 20
```

### Deterministic-only (no LLM, fast, safe to repeat)

```bash
python porting/scripts/run_agentic_porting_workflow.py \
    --roots src,demo,tests,third_part \
    --disable-llm --skip-tests
```

### Deterministic pipeline only

```bash
python porting/scripts/run_porting_pipeline.py \
    --roots src,demo,tests,third_part \
    --force --skip-tests \
    --generate-contract-tests \
    --compare-parity-snapshots
```

### What to port next (dependency order)

```bash
python porting/scripts/select_next_functions.py \
    --roots src,demo,tests,third_part -n 20
```

### Build agent context and prompt

```bash
python porting/scripts/build_agent_context.py
python porting/scripts/get_prompt_for_porting.py --mode full
# → porting/state/porting_agent_prompt.txt
```

### Fix missing imports

```bash
python porting/scripts/auto_fix_missing_imports.py \
    --roots ../../src,../../demo,../../tests,../../third_part \
    --apply --summary-only
```

### Cleanup artifacts

```bash
# Dry-run first:
python porting/scripts/cleanup_pipeline_artifacts.py \
    --clean-cache --prune-stale-tests --remove-empty-dirs

# Apply:
python porting/scripts/cleanup_pipeline_artifacts.py \
    --clean-cache --prune-stale-tests --remove-empty-dirs --apply
```

---

## Health metrics

After every workflow run, check these files:

| File | Key field | Target |
|---|---|---|
| `reports/generated_files_analysis.json` | `summary.matlab_todo_markers` | 0 |
| `reports/generated_files_analysis.json` | `summary.compile_errors` | 0 |
| `reports/agent_repair_cycle_report.json` | `final_status` | `"success"` |
| `reports/parity_snapshot_comparison.json` | `summary.ok` | `true` |

---

## For IDE agents (Claude Code, Cursor, Codex, …)

**Start here:**

1. Load `porting/prompts/system_ide_agent.md` as your system prompt.
2. Read `porting/docs/IDE_AGENT_GUIDE.md` for the full operating procedure.
3. Begin every session with:
   ```bash
   python porting/scripts/build_agent_context.py
   cat porting/state/agent_context_compact.json
   ```

**What you should ask (or tell) the IDE agent:**

- "Port the next 10 MATLAB files in dependency order" → runs `select_next_functions.py` + workflow
- "How many TODO markers remain?" → reads `generated_files_analysis.json`
- "Fix the import errors in the generated files" → runs `auto_fix_missing_imports.py`
- "Run the full porting pipeline with LLM repair" → runs `run_agentic_porting_workflow.py`
- "What is blocking progress?" → reads `agent_context_compact.json` top_blockers
- "Clean up stale test artifacts" → runs `cleanup_pipeline_artifacts.py`
- "Translate the TODO on line N of file X" → reads `TODO_TRANSLATION_EXAMPLES.md`, edits file

---

## Documentation index

| Document | Purpose |
|---|---|
| `docs/IDE_AGENT_GUIDE.md` | Step-by-step operating procedure for IDE agents |
| `prompts/system_ide_agent.md` | System prompt to load into an IDE agent |
| `prompts/system_agentic_orchestrator_compact.md` | Compact orchestrator prompt |
| `prompts/system_agentic_orchestrator_full.md` | Full orchestrator prompt |
| `docs/AGENT_TOOLING_MAP.md` | Every script, its purpose, and its key arguments |
| `docs/TODO_TRANSLATION_EXAMPLES.md` | How to translate specific MATLAB TODO markers |
| `docs/EXAMPLE_ORIGINAL_TO_PORTED.md` | Full MATLAB→Python file example |
| `lib/utils.py` | Shared utilities for scripts (importable) |

## LangGraph v2 Entry Points (Default)

The canonical entrypoints now route to LangGraph v2 by default:

```bash
python porting/scripts/run_agentic_porting_workflow.py --roots src,demo,tests,third_part
python porting/scripts/run_agentic_repair_cycle.py --current-file src/fourier3/bcaNeith3.py
```

To run the previous procedural engine explicitly:

```bash
python porting/scripts/run_agentic_porting_workflow.py --engine legacy --roots src,demo,tests,third_part
python porting/scripts/run_agentic_repair_cycle.py --engine legacy --target-file src/fourier3/bcaNeith3.py
```

Architecture and migration details:
`porting/docs/LANGGRAPH_V2_ARCHITECTURE.md`
