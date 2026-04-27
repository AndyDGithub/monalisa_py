# LangGraph V2 Architecture - MATLAB -> Python Porting

## Assumptions

1. Existing CLI scripts remain the source of truth for deterministic operations.
2. LangGraph orchestrates decisions and retries, but does not replace deterministic scripts yet.
3. Some tool names listed as MCP (`run_agentic_repair_on_file`, `run_test`) are currently mapped to existing scripts/pytest wrappers.
4. Full parity data may not be available in every local run; parity failures are handled as reviewer signals.

## 1) Critical analysis

### Why your idea is strong

1. Procedural monolith scripts are hard to adapt when decision logic grows.
2. Explicit graph transitions make retry/stop behavior auditable.
3. Multi-agent split avoids "one magic prompt" and makes failures diagnosable.
4. State-driven orchestration is a better fit for long, iterative migration.

### Risks

1. Over-agentization can hide deterministic failures under LLM retries.
2. If global state is not strict, decisions become non-reproducible.
3. Poor stop rules cause expensive loops.
4. Tool wrappers can drift from legacy script behavior unless contracts are explicit.

### Mitigations

1. Deterministic-first policy in every cycle (imports, entrypoints, static checks).
2. Hard caps: `max_cycles`, `max_retries_per_file`.
3. Structured verdict schema (`approved` / `rejected` / `needs_retry`).
4. Every node writes machine-readable traces.

## 2) Target architecture

### Global workflow (`run_agentic_porting_workflow_v2`)

1. Ingest request.
2. Run deterministic analysis:
   - `search_matlab`
   - `get_function_call_graph`
   - `select_file_order`
   - `build_agent_context`
3. Build shared state (`pending_files`, `file_progress`, `repair_args`, limits).
4. Invoke local repair workflow repeatedly.
5. Reevaluate global status.
6. Stop on success or blocked condition.

### Local workflow (`run_agentic_repair_cycle_v2`)

1. Coordinator picks current file.
2. Porting agent executes repair cycle.
3. Reviewer runs tests/parity and emits verdict.
4. Coordinator decides retry vs next file vs blocked.
5. Documentor logs change event.

## 3) Shared state design

Implemented in `monalisa_py.agentic.state.PortingGraphState`:

1. Project context: `repo_root`, `roots`, `request_id`, `user_request`.
2. Analysis artifacts: `matlab_files`, `call_graph_path`, `porting_order`, `reports`.
3. Execution pointers: `pending_files`, `current_file`, `current_index`.
4. Validation status: `file_progress`, `approved_files`, `blocked_files`.
5. Retry/cycle control: `cycle_index`, `max_cycles`, `max_retries_per_file`.
6. Workflow controls: `repair_args`, `last_decision`, `phase`, `stop_reason`.
7. Traceability: `history`, `change_log_path`, `last_repair_result`.

## 4) Concrete code organization

```text
porting/python/monalisa_py/agentic/
  __init__.py
  config.py
  state.py
  agents/
    __init__.py
    coordinator.py
    porter.py
    reviewer.py
    documentor.py
  tools/
    __init__.py
    legacy_toolbox.py
  workflows/
    __init__.py
    global_graph.py
    repair_graph.py
  cli/
    __init__.py
    run_agentic_porting_workflow_v2.py
    run_agentic_repair_cycle_v2.py
```

### Legacy scripts reused by wrappers

1. `search_matlab.py`
2. `get_function_call_graph.py`
3. `select_file_order.py`
4. `build_agent_context.py`
5. `run_agentic_repair_cycle.py`
6. `run_parity_case.py`
7. `auto_fix_missing_imports.py`
8. `ensure_module_entrypoints.py`
9. `clean_project.py`

### Obsolescence policy

1. Current scripts remain active.
2. Procedural orchestration scripts become "backend tools" over time.
3. Decision logic migrates to LangGraph nodes incrementally.

## 5) Migration plan

1. Keep existing scripts untouched and wrap them in `LegacyToolbox`.
2. Introduce typed shared state and deterministic decision rules.
3. Deploy local repair graph first (single-file loop).
4. Integrate global graph orchestration on top.
5. Route current CLI entrypoints to v2 in shadow mode.
6. Compare v1 vs v2 outputs on same task set.
7. Promote v2 as default once convergence and runtime are stable.

## 6) Graph transition rules (implemented)

### Global graph

1. `ingest_request -> run_initial_analysis -> build_shared_state -> initialize_queue`.
2. `decide_need_repair`:
   - if pending files: `run_repair_cycle`
   - else: `finalize`
3. `reevaluate_global`:
   - if stop: `finalize`
   - else: `run_repair_cycle`

### Local graph

1. `pick_current_file`:
   - if no file: `done`
   - else: `port_current_file`
2. `port_current_file -> review_current_file -> decide_local -> document_cycle_event`
3. `document_cycle_event`:
   - `retry_file` -> `port_current_file`
   - otherwise -> `done`

## 7) Decision policy

1. Retry same file when reviewer returns `needs_retry` and retries <= max.
2. Mark blocked when retries exceed `max_retries_per_file`.
3. Approve file only when reviewer returns `approved`.
4. Move to next file when approved or blocked.
5. Stop global workflow when:
   - all pending processed with no blocked files (`stop_success`)
   - max cycles reached with pending files (`stop_blocked`)
   - all processed but blocked remains (`stop_blocked`)

