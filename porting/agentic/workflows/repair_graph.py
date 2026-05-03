from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from porting.agentic.agents import CoordinatorAgent, DocumentorAgent, PortingAgent, ReviewerAgent
from porting.agentic.state import PortingGraphState
from porting.agentic.tools import LegacyToolbox

LOGGER = logging.getLogger("porting.agentic.repair_graph")


def build_repair_cycle_workflow(
    *,
    toolbox: LegacyToolbox,
    max_retries_per_file: int,
):
    coordinator = CoordinatorAgent(max_retries_per_file=max_retries_per_file)
    porter = PortingAgent(toolbox=toolbox)
    reviewer = ReviewerAgent(toolbox=toolbox)
    documentor = DocumentorAgent(toolbox=toolbox)

    graph = StateGraph(PortingGraphState)

    def pick_current_file(state: PortingGraphState) -> dict[str, Any]:
        out = coordinator.pick_current_file(state)
        current = out.get("current_file", "")
        LOGGER.info("local.pick_current_file current=%s pending=%s", current or "<none>", len(state.get("pending_files", [])))
        return out

    def port_current_file(state: PortingGraphState) -> dict[str, Any]:
        current = state.get("current_file", "")
        LOGGER.info("local.port_current_file target=%s", current or "<none>")
        return porter.port_or_repair_current(state)

    def review_current_file(state: PortingGraphState) -> dict[str, Any]:
        current = state.get("current_file", "")
        LOGGER.info("local.review_current_file target=%s", current or "<none>")
        return reviewer.review_current(state)

    def decide_local(state: PortingGraphState) -> dict[str, Any]:
        out = coordinator.decide_local(state)
        LOGGER.info("local.decide_local decision=%s", out.get("last_decision", ""))
        return out

    def document_cycle_event(state: PortingGraphState) -> dict[str, Any]:
        out = documentor.record_cycle_event(state)
        LOGGER.info("local.document_cycle_event change_log=%s", out.get("change_log_path", ""))
        return out

    graph.add_node("pick_current_file", pick_current_file)
    graph.add_node("port_current_file", port_current_file)
    graph.add_node("review_current_file", review_current_file)
    graph.add_node("decide_local", decide_local)
    graph.add_node("document_cycle_event", document_cycle_event)
    graph.add_node("done", lambda _: {})

    graph.set_entry_point("pick_current_file")

    def route_after_pick(state: PortingGraphState) -> str:
        current = str(state.get("current_file", "")).strip()
        return "done" if not current else "port_current_file"

    def route_after_document(state: PortingGraphState) -> str:
        decision = str(state.get("last_decision", "next_file"))
        if decision == "retry_file":
            return "port_current_file"
        return "done"

    graph.add_conditional_edges(
        "pick_current_file",
        route_after_pick,
        {
            "done": "done",
            "port_current_file": "port_current_file",
        },
    )
    graph.add_edge("port_current_file", "review_current_file")
    graph.add_edge("review_current_file", "decide_local")
    graph.add_edge("decide_local", "document_cycle_event")
    graph.add_conditional_edges(
        "document_cycle_event",
        route_after_document,
        {
            "port_current_file": "port_current_file",
            "done": "done",
        },
    )
    graph.add_edge("done", END)

    return graph.compile()
