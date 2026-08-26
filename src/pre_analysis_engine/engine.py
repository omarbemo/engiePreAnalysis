"""Entry point for the deterministic pre-analysis engine. This is what
downstream stages (Planning Agent, HITL UI, Delivery report) call — the
Finding list this returns is the locked contract those stages consume.

Takes an already-parsed resource list, not a file path — parsing is a
separate teammate's task. See the plan's Integration Contract for the
exact shape this function expects.
"""
from pre_analysis_engine.graph import build_reference_graph
from pre_analysis_engine.rules import evaluate_tier_one, Finding  # noqa: F401


def run_pre_analysis(resources: list) -> list:
    graph = build_reference_graph(resources)
    return evaluate_tier_one(resources, graph)
