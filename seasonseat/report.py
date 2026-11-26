"""Report building and rendering for seasonseat."""

from __future__ import annotations

import json
from typing import Any

from .model import Problem
from .planner import PlanResult


def build_report(problem: Problem, result: PlanResult) -> dict[str, Any]:
    import dataclasses
    # serialize problem input
    inp = {
        "people": [{"id": p.person_id, "name": p.name} for p in problem.people],
        "seats": [{"id": s.seat_id, "row": s.row, "col": s.col, "quality": s.quality} for s in problem.seats],
        "events": problem.events,
        "conflicts": [sorted(list(c)) for c in problem.conflicts],
        "fixed": {str(k): v for k, v in problem.fixed.items()},
    }
    report = {
        "input": inp,
        "status": result.status,
        "assignments": result.assignments,
        "objective": result.objective,
        "variety": result.variety,
        "nodes": result.nodes,
        "reason": result.reason,
    }
    return report


def render_text(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"status: {report['status']}")
    lines.append(f"objective (quality range): {report['objective']:.4f}")
    lines.append(f"adjacency variety (distinct pairs): {report['variety']}")
    lines.append(f"search nodes: {report['nodes']}")
    if report.get("reason"):
        lines.append(f"reason: {report['reason']}")
    lines.append("")
    for ei, ev in enumerate(report["assignments"]):
        lines.append(f"Event {ei}:")
        for pid, sid in ev.items():
            lines.append(f"  {pid} -> {sid}")
    return "\n".join(lines) + "\n"


def dump_json(path: str, report: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
