from __future__ import annotations

import concurrent.futures
import json
import logging
from pathlib import Path
from typing import Any
from uuid import uuid4

from langgraph.graph import END, StateGraph

from agentic.agents import CoordinatorAgent, DocumentorAgent
from agentic.config import WorkflowConfig
from agentic.state import PortingGraphState
from agentic.tools import LegacyToolbox
from agentic.workflows.repair_graph import build_repair_cycle_workflow

LOGGER = logging.getLogger("agentic.global_graph")


def _flatten_porting_order(payload: Any) -> list[str]:
    if isinstance(payload, list):
        out: list[str] = []
        for item in payload:
            out.extend(_flatten_porting_order(item))
        return out
    if isinstance(payload, str):
        return [payload]
    return []


def _extract_order_with_layers(payload: Any) -> list[tuple[str, int]]:
    """Extract (entry, layer) while preserving top-level layer groups when present."""
    out: list[tuple[str, int]] = []
    if isinstance(payload, list):
        top_level_all_lists = all(isinstance(item, list) for item in payload if item is not None)
        if top_level_all_lists and payload:
            for layer_idx, item in enumerate(payload):
                if isinstance(item, list):
                    for nested in _flatten_porting_order(item):
                        out.append((nested, layer_idx))
                elif isinstance(item, str):
                    out.append((item, layer_idx))
            return out
        for item in payload:
            out.extend(_extract_order_with_layers(item))
        return out
    if isinstance(payload, str):
        return [(payload, 0)]
    return out


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _is_under_roots(path: Path, repo_root: Path, roots: list[str]) -> bool:
    resolved = path.resolve()
    for root in roots:
        root_path = (repo_root / root).resolve()
        if str(resolved).startswith(str(root_path)):
            return True
    return False


def _build_matlab_name_lookup(matlab_files: list[str]) -> dict[str, list[Path]]:
    lookup: dict[str, list[Path]] = {}
    for item in matlab_files:
        p = Path(item)
        key = p.name.lower()
        lookup.setdefault(key, []).append(p)
    return lookup


def _resolve_matlab_path(
    raw: str,
    *,
    repo_root: Path,
    roots: list[str],
    matlab_name_lookup: dict[str, list[Path]],
) -> Path | None:
    token = raw.strip()
    if not token:
        return None
    token = token.replace("/", "\\")
    candidate_paths: list[Path] = []
    p = Path(token)

    if p.is_absolute():
        candidate_paths.append(p)
    else:
        candidate_paths.append((repo_root / p).resolve())
        if p.suffix.lower() == ".m":
            candidate_paths.extend(matlab_name_lookup.get(p.name.lower(), []))
        elif p.suffix == "":
            candidate_paths.extend(matlab_name_lookup.get(f"{p.name}.m".lower(), []))

    for candidate in candidate_paths:
        candidate = candidate.resolve()
        if candidate.exists() and candidate.suffix.lower() == ".m" and _is_under_roots(candidate, repo_root, roots):
            return candidate
    return None


def _matlab_path_to_python_target(path: Path, repo_root: Path) -> str:
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
        return str((repo_root / rel.with_suffix(".py")).resolve())
    except ValueError:
        return str(path.with_suffix(".py").resolve())


def build_global_porting_workflow(config: WorkflowConfig):
    """Builds a LangGraph v2 workflow for global coordination of MATLAB to Python porting."""
    toolbox = LegacyToolbox(repo_root=config.repo_root)
    coordinator = CoordinatorAgent(max_retries_per_file=config.max_retries_per_file)
    documentor = DocumentorAgent(toolbox=toolbox)
    repair_app = build_repair_cycle_workflow(
        toolbox=toolbox,
        max_retries_per_file=config.max_retries_per_file,
    )

    script_outputs = (config.repo_root / "script_outputs").resolve()
    script_outputs.mkdir(parents=True, exist_ok=True)
    graph_output = script_outputs / "all_files_function_call_graph.json"
    order_output = script_outputs / "porting_order.json"

    def ingest_request(state: PortingGraphState) -> dict[str, Any]:
        request_id = state.get("request_id") or str(uuid4())
        user_request = state.get("user_request", "agentic matlab->python porting")
        LOGGER.info("global.ingest_request request_id=%s roots=%s", request_id, ",".join(config.roots))
        base_repair_args = {
            "model": config.llm_model,
            "fallback_model": config.fallback_model,
            "auto_pull_model": False,
            "max_iterations": 1,
            "max_files_per_iteration": 1,
            "generated_tests_per_iteration": config.generated_tests_per_iteration,
            "contracts_per_iteration": config.contracts_per_iteration,
            "llm_timeout_seconds": config.llm_timeout_seconds,
            "dynamic_llm_timeout": config.dynamic_llm_timeout,
            "dynamic_timeout_base_seconds": config.dynamic_timeout_base_seconds,
            "dynamic_timeout_per_line_seconds": config.dynamic_timeout_per_line_seconds,
            "dynamic_timeout_min_seconds": config.dynamic_timeout_min_seconds,
            "dynamic_timeout_max_seconds": config.dynamic_timeout_max_seconds,
            "enable_matlab_help": config.enable_matlab_help,
            "matlab_help_max_functions": config.matlab_help_max_functions,
            "matlab_help_timeout_seconds": config.matlab_help_timeout_seconds,
            "stream_subprocess_logs": config.stream_subprocess_logs,
            "allow_matlab_todos": config.allow_matlab_todos,
            "enable_strict_prefilter": config.enable_strict_prefilter,
            "pause_on_applied_false": config.pause_on_applied_false,
            "sync_env": config.sync_env,
            "requirements_output": config.requirements_output,
            "enforce_comment_parity": True,
            "enforce_matlab_todo_gate": True,
            "enforce_fallback_stub_gate": True,
            "enforce_untranslated_placeholder_gate": True,
            "enforce_test_scope_gate": True,
            "enforce_runtime_metadata_gate": True,
        }
        incoming_repair_args = dict(state.get("repair_args", {}))
        base_repair_args.update(incoming_repair_args)
        reports = dict(state.get("reports", {}))
        reports.setdefault("repair_backend", "legacy_script_subprocess")
        return {
            "request_id": request_id,
            "user_request": user_request,
            "repo_root": str(config.repo_root),
            "roots": list(config.roots),
            "phase": "bootstrap",
            "cycle_index": int(state.get("cycle_index", 0)),
            "max_cycles": int(state.get("max_cycles", config.max_cycles)),
            "max_retries_per_file": int(state.get("max_retries_per_file", config.max_retries_per_file)),
            "repair_args": base_repair_args,
            "reports": reports,
            "history": list(state.get("history", [])),
            "file_progress": dict(state.get("file_progress", {})),
            "approved_files": list(state.get("approved_files", [])),
            "blocked_files": list(state.get("blocked_files", [])),
        }

    def run_initial_analysis(state: PortingGraphState) -> dict[str, Any]:
        roots = list(state.get("roots", config.roots))
        LOGGER.info("global.run_initial_analysis roots=%s", ",".join(roots))
        matlab_files: list[str] = []

        def _search_root(root_name: str) -> list[str]:
            search = toolbox.search_matlab(directory=str(config.repo_root / root_name))
            if search.returncode != 0:
                return []
            payload = toolbox._try_extract_json(search.stdout)
            files = payload.get("files", [])
            if not isinstance(files, list):
                return []
            return [str(x) for x in files]

        if len(roots) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(roots), 8)) as pool:
                futures = [pool.submit(_search_root, root_name) for root_name in roots]
                for future in futures:
                    matlab_files.extend(future.result())
        else:
            for root in roots:
                matlab_files.extend(_search_root(root))
        matlab_files = sorted(set(matlab_files))
        LOGGER.info("global.run_initial_analysis matlab_files=%s", len(matlab_files))

        graph_run = toolbox.get_function_call_graph(root=str(config.repo_root), output=str(graph_output))
        order_run = toolbox.select_file_order(input_path=str(graph_output), output_path=str(order_output))
        context_run = toolbox.build_agent_context()
        LOGGER.info(
            "global.analysis_scripts call_graph_rc=%s select_order_rc=%s context_rc=%s",
            graph_run.returncode,
            order_run.returncode,
            context_run.returncode,
        )

        reports = dict(state.get("reports", {}))
        reports.update(
            {
                "call_graph": str(graph_output),
                "porting_order": str(order_output),
                "build_agent_context_stdout": context_run.stdout[-4000:],
                "analysis_stderr": "\n".join(
                    x for x in [graph_run.stderr.strip(), order_run.stderr.strip(), context_run.stderr.strip()] if x
                ),
            }
        )
        return {
            "phase": "analysis",
            "matlab_files": matlab_files,
            "call_graph_path": str(graph_output),
            "reports": reports,
        }

    def build_shared_state(state: PortingGraphState) -> dict[str, Any]:
        roots = list(state.get("roots", config.roots))
        matlab_files = list(state.get("matlab_files", []))
        matlab_lookup = _build_matlab_name_lookup(matlab_files)
        order: list[str] = []
        file_layer_map: dict[str, int] = {}
        source = "none"

        _, candidates = toolbox.select_next_function(
            roots=roots,
            n=max(2000, len(matlab_files) + 512),
        )
        next_candidates: list[str] = []
        for index, raw in enumerate(candidates):
            matlab_path = _resolve_matlab_path(
                raw,
                repo_root=config.repo_root,
                roots=roots,
                matlab_name_lookup=matlab_lookup,
            )
            if matlab_path is None:
                continue
            py_target = _matlab_path_to_python_target(matlab_path, config.repo_root)
            next_candidates.append(py_target)
            file_layer_map.setdefault(py_target, index)
        next_candidates = _dedupe_preserve(next_candidates)

        order_from_select_file_order: list[str] = []
        layer_map_from_select_file_order: dict[str, int] = {}
        if order_output.exists():
            try:
                payload = json.loads(order_output.read_text(encoding="utf-8"))
                layered = _extract_order_with_layers(payload)
                resolved: list[str] = []
                for raw, layer_idx in layered:
                    matlab_path = _resolve_matlab_path(
                        raw,
                        repo_root=config.repo_root,
                        roots=roots,
                        matlab_name_lookup=matlab_lookup,
                    )
                    if matlab_path is None:
                        continue
                    py_target = _matlab_path_to_python_target(matlab_path, config.repo_root)
                    resolved.append(py_target)
                    layer_map_from_select_file_order.setdefault(py_target, int(layer_idx))
                order_from_select_file_order = _dedupe_preserve(resolved)
            except json.JSONDecodeError:
                order_from_select_file_order = []

        if next_candidates and order_from_select_file_order:
            allowed = set(next_candidates)
            order = [p for p in order_from_select_file_order if p in allowed]
            for index, py_target in enumerate(order):
                file_layer_map[py_target] = int(layer_map_from_select_file_order.get(py_target, index))
            source = "select_file_order_filtered_by_select_next_functions"
        elif order_from_select_file_order:
            order = list(order_from_select_file_order)
            for index, py_target in enumerate(order):
                file_layer_map[py_target] = int(layer_map_from_select_file_order.get(py_target, index))
            source = "select_file_order"
        elif next_candidates:
            order = list(next_candidates)
            for index, py_target in enumerate(order):
                file_layer_map.setdefault(py_target, index)
            source = "select_next_functions"

        if not order:
            fallback_items = [
                _matlab_path_to_python_target(Path(item), config.repo_root)
                for item in matlab_files
                if Path(item).suffix.lower() == ".m"
            ]
            order = _dedupe_preserve(fallback_items)
            for index, py_target in enumerate(order):
                file_layer_map.setdefault(py_target, index)
            source = "matlab_files_fallback"
        else:
            for index, py_target in enumerate(order):
                file_layer_map.setdefault(py_target, int(file_layer_map.get(py_target, index)))
        LOGGER.info(
            "global.build_shared_state pending_files=%s source=%s",
            len(order),
            source,
        )

        reports = dict(state.get("reports", {}))
        reports["porting_order"] = str(order_output)
        return {
            "porting_order": order,
            "file_layer_map": file_layer_map,
            "pending_files": list(order),
            "phase": "repair_cycle",
            "reports": reports,
        }

    def initialize_queue(state: PortingGraphState) -> dict[str, Any]:
        return coordinator.initialize_queue(state)

    def decide_need_repair(state: PortingGraphState) -> dict[str, Any]:
        pending = list(state.get("pending_files", []))
        LOGGER.info("global.decide_need_repair pending=%s", len(pending))
        if pending:
            return {"last_decision": "next_file", "phase": "repair_cycle"}
        return {"last_decision": "stop_success", "phase": "done", "stop_reason": "no_pending_files"}

    def run_repair_cycle(state: PortingGraphState) -> dict[str, Any]:
        next_state = dict(state)
        next_state["cycle_index"] = int(state.get("cycle_index", 0)) + 1
        pending = list(state.get("pending_files", []))
        if not pending:
            return next_state

        repair_args = dict(state.get("repair_args", {}))
        batch_size = max(1, int(repair_args.get("parallel_files_per_cycle", 1) or 1))
        enable_parallel = bool(repair_args.get("enable_parallel_repair", False))
        skip_pipeline = bool(repair_args.get("skip_pipeline", False))
        sync_env = bool(repair_args.get("sync_env", False))
        parallel_repair_max_workers = max(1, int(repair_args.get("parallel_repair_max_workers", 8) or 8))
        layer_map = {k: int(v) for k, v in dict(state.get("file_layer_map", {})).items()}

        first = pending[0]
        first_layer = int(layer_map.get(first, 0))
        batch_files = [f for f in pending if int(layer_map.get(f, first_layer)) == first_layer][:batch_size]
        if not batch_files:
            batch_files = [first]

        allow_parallel = bool(enable_parallel and skip_pipeline and len(batch_files) > 1)
        LOGGER.info(
            "global.run_repair_cycle cycle=%s batch_size=%s layer=%s parallel=%s workers_cap=%s",
            next_state["cycle_index"],
            len(batch_files),
            first_layer,
            allow_parallel,
            parallel_repair_max_workers,
        )

        def _invoke_for_file(
            file_path: str,
            base_state: dict[str, Any],
            *,
            force_sync_env: bool | None = None,
        ) -> dict[str, Any]:
            local_state = dict(base_state)
            local_state["pending_files"] = [file_path]
            local_state["current_file"] = file_path
            local_state["defer_change_log_write"] = True
            if force_sync_env is not None:
                local_repair_args = dict(local_state.get("repair_args", {}))
                local_repair_args["sync_env"] = bool(force_sync_env)
                local_state["repair_args"] = local_repair_args
            return dict(repair_app.invoke(local_state))

        merged_state = dict(next_state)
        if allow_parallel:
            results: list[dict[str, Any]] = []
            remaining_for_pool = list(batch_files)
            if sync_env and batch_files:
                # Sync environment once in the first worker, then fan out without
                # per-worker pip contention.
                bootstrap_target = batch_files[0]
                LOGGER.warning(
                    "sync_env=True with parallel repair: bootstrapping env on %s, then running remaining files with sync_env=False.",
                    bootstrap_target,
                )
                results.append(_invoke_for_file(bootstrap_target, dict(merged_state), force_sync_env=True))
                remaining_for_pool = batch_files[1:]
            if remaining_for_pool:
                pool_base_state = dict(merged_state)
                if sync_env:
                    pool_repair_args = dict(pool_base_state.get("repair_args", {}))
                    pool_repair_args["sync_env"] = False
                    pool_base_state["repair_args"] = pool_repair_args
                max_workers = min(len(remaining_for_pool), parallel_repair_max_workers)
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
                    futures = [
                        pool.submit(_invoke_for_file, file_path, dict(pool_base_state))
                        for file_path in remaining_for_pool
                    ]
                    results.extend(f.result() for f in futures)
            # Merge conservatively: per-file progress and global lists.
            approved = set(merged_state.get("approved_files", []))
            blocked = set(merged_state.get("blocked_files", []))
            file_progress = dict(merged_state.get("file_progress", {}))
            history = list(merged_state.get("history", []))
            change_log_path = str(toolbox.log_root / "change_log.jsonl")
            for res in results:
                current = str(res.get("current_file", "")).strip()
                if current and isinstance(res.get("file_progress"), dict) and current in res["file_progress"]:
                    file_progress[current] = dict(res["file_progress"][current])
                approved.update(res.get("approved_files", []))
                blocked.update(res.get("blocked_files", []))
                last_repair_result = dict(res.get("last_repair_result", {}) or {})
                verdict = str(last_repair_result.get("reviewer_verdict", "needs_retry"))
                if current:
                    summary = f"{current} -> {verdict}"
                    history.append(summary)
                    # Write sequentially in the parent thread to avoid lock contention.
                    change_log_path = str(
                        toolbox.document_change(
                            file_path=current,
                            summary=summary,
                            details=last_repair_result,
                        )
                    )
                merged_state["last_repair_result"] = dict(res.get("last_repair_result", {}))
                merged_state["last_decision"] = str(res.get("last_decision", merged_state.get("last_decision", "")))
            merged_state["approved_files"] = sorted(approved)
            merged_state["blocked_files"] = sorted(blocked)
            merged_state["file_progress"] = file_progress
            merged_state["history"] = history
            merged_state["change_log_path"] = change_log_path
            merged_state["pending_files"] = [p for p in pending if p not in set(batch_files)]
        else:
            # Safe fallback: batched but sequential.
            current_state = dict(merged_state)
            processed: set[str] = set()
            for file_path in batch_files:
                local_state = dict(current_state)
                local_state["pending_files"] = [file_path]
                local_state["current_file"] = file_path
                current_state = dict(repair_app.invoke(local_state))
                processed.add(file_path)
            merged_state = dict(current_state)
            merged_state["pending_files"] = [p for p in pending if p not in processed]

        total_files = len(state.get("porting_order", merged_state.get("porting_order", [])))
        n_approved = len(merged_state.get("approved_files", []))
        n_blocked = len(merged_state.get("blocked_files", []))
        n_pending = len(merged_state.get("pending_files", []))
        n_done = n_approved + n_blocked
        pct = int(100 * n_done / total_files) if total_files else 0
        LOGGER.info(
            "global.progress  %d/%d done (%d%%)  approved=%d  blocked=%d  pending=%d  | cycle=%s file=%s decision=%s",
            n_done,
            total_files,
            pct,
            n_approved,
            n_blocked,
            n_pending,
            next_state["cycle_index"],
            merged_state.get("current_file", ""),
            merged_state.get("last_decision", ""),
        )
        return merged_state

    def reevaluate_global(state: PortingGraphState) -> dict[str, Any]:
        out = coordinator.decide_global(state)
        LOGGER.info(
            "global.reevaluate decision=%s phase=%s pending=%s blocked=%s",
            out.get("last_decision", ""),
            out.get("phase", ""),
            len(state.get("pending_files", [])),
            len(state.get("blocked_files", [])),
        )
        return out

    def finalize(state: PortingGraphState) -> dict[str, Any]:
        out = documentor.write_global_summary(state)
        LOGGER.info("global.finalize summary=%s", out.get("reports", {}).get("global_summary", ""))
        return out

    def route_from_need_repair(state: PortingGraphState) -> str:
        decision = str(state.get("last_decision", "next_file"))
        if decision == "stop_success":
            return "finalize"
        return "run_repair_cycle"

    def route_after_reevaluate(state: PortingGraphState) -> str:
        decision = str(state.get("last_decision", "next_file"))
        if decision in {"stop_success", "stop_blocked"}:
            return "finalize"
        return "run_repair_cycle"

    graph = StateGraph(PortingGraphState)
    graph.add_node("ingest_request", ingest_request)
    graph.add_node("run_initial_analysis", run_initial_analysis)
    graph.add_node("build_shared_state", build_shared_state)
    graph.add_node("initialize_queue", initialize_queue)
    graph.add_node("decide_need_repair", decide_need_repair)
    graph.add_node("run_repair_cycle", run_repair_cycle)
    graph.add_node("reevaluate_global", reevaluate_global)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("ingest_request")
    graph.add_edge("ingest_request", "run_initial_analysis")
    graph.add_edge("run_initial_analysis", "build_shared_state")
    graph.add_edge("build_shared_state", "initialize_queue")
    graph.add_edge("initialize_queue", "decide_need_repair")
    graph.add_conditional_edges(
        "decide_need_repair",
        route_from_need_repair,
        {
            "run_repair_cycle": "run_repair_cycle",
            "finalize": "finalize",
        },
    )
    graph.add_edge("run_repair_cycle", "reevaluate_global")
    graph.add_conditional_edges(
        "reevaluate_global",
        route_after_reevaluate,
        {
            "run_repair_cycle": "run_repair_cycle",
            "finalize": "finalize",
        },
    )
    graph.add_edge("finalize", END)

    return graph.compile()
