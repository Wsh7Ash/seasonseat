"""Exact seasonal seating planner for seasonseat."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .model import Problem, Seat


@dataclass
class PlanResult:
    status: str  # "optimal" | "feasible" | "infeasible"
    assignments: list[dict[str, str]]  # per event: person_id -> seat_id
    objective: float  # quality range (max-min cumulative quality)
    variety: int  # distinct adjacent person-pairs across events
    nodes: int
    reason: str = ""


def _seat_quality(problem: Problem) -> dict[str, float]:
    return {s.seat_id: s.quality for s in problem.seats}


def _adjacent(problem: Problem) -> dict[str, set[str]]:
    return problem.seats[0] and problem.adjacent_seats() if False else problem.adjacent_seats() if hasattr(problem, 'adjacent_seats') else {}


def plan(problem: Problem, node_budget: int = 200000) -> PlanResult:
    people = problem.person_ids
    seats = problem.seat_ids
    n_people = len(people)
    n_seats = len(seats)
    n_events = problem.events
    q = _seat_quality(problem)
    adj = problem.adjacent_seats()
    conflicts = problem.conflicts

    # conflict person pairs -> set of frozensets
    conflict_pairs: set[frozenset[str]] = set(conflicts)

    # fixed assignments
    fixed = problem.fixed or {}

    # Precompute seat adjacency for person-pair conflict checking: two seats adjacent?
    seat_adjacent: dict[str, set[str]] = adj

    def seats_adjacent(sa: str, sb: str) -> bool:
        return sb in seat_adjacent.get(sa, set())

    # person index
    person_index = {pid: i for i, pid in enumerate(people)}

    # used seats per person across events
    used_by_person: list[set[str]] = [set() for _ in people]

    # assignments: events x people -> seat or None
    assign: list[list[str | None]] = [[None] * n_people for _ in range(n_events)]

    # cumulative quality per person
    cumq: list[float] = [0.0] * n_people

    # variety: set of frozenset person pairs adjacent in some event
    variety_pairs: set[frozenset[str]] = set()

    # track current variety count incrementally? We'll compute at leaf.

    nodes = [0]
    best: dict[str, Any] = {"range": math.inf, "variety": -1, "assignments": None}

    # Precompute min/max seat quality
    qs = [q[sid] for sid in seats]
    qmin = min(qs)
    qmax = max(qs)

    def current_quality_range_lower_bound(remaining_events: int) -> float:
        # each person's final cumq in [cumq + remaining*qmin, cumq + remaining*qmax]
        lo = [cumq[i] + remaining_events * qmin for i in range(n_people)]
        hi = [cumq[i] + remaining_events * qmax for i in range(n_people)]
        # lower bound on (max final - min final): max of lo - min of hi? 
        # range >= max(lo) - min(hi) roughly
        return max(lo) - min(hi)

    # feasibility of completing: enough unused seats per person? check at event start.

    def backtrack(event: int, person_idx: int) -> None:
        if nodes[0] >= node_budget:
            return
        if best["assignments"] is not None and best["range"] <= 1e-9:
            return
        nodes[0] += 1
        if event == n_events:
            # leaf: evaluate
            rng = max(cumq) - min(cumq)
            # compute variety
            vpairs: set[frozenset[str]] = set()
            for e in range(n_events):
                # build seat->person
                seat_to_person: dict[str, str] = {}
                for pi, pid in enumerate(people):
                    seat_to_person[assign[e][pi]] = pid  # type: ignore
                for sa, pa in [(assign[e][pi], people[pi]) for pi in range(n_people)]:
                    for sb in seat_adjacent.get(sa, set()):
                        pb = seat_to_person.get(sb)
                        if pb is not None and pb != pa:
                            vpairs.add(frozenset((pa, pb)))
            var = len(vpairs)
            # compare
            if rng < best["range"] - 1e-12 or (abs(rng - best["range"]) <= 1e-12 and var > best["variety"]):
                best["range"] = rng
                best["variety"] = var
                best["assignments"] = [ [assign[e][pi] for pi in range(n_people)] for e in range(n_events)]
            return

        # if starting a new event, person_idx should be 0
        if person_idx == 0:
            # check node budget / pruning before event
            remaining_after_this = n_events - event  # includes this event
            # lower bound on range after all remaining (including this)
            lb = current_quality_range_lower_bound(remaining_after_this)
            if best["assignments"] is not None and lb > best["range"] + 1e-9:
                return
            # check feasibility: enough seats not used by each person for remaining events?
            # quick: for each person, unused seats count >= remaining events
            for pi in range(n_people):
                unused = n_seats - len(used_by_person[pi])
                if unused < (n_events - event):
                    return  # infeasible branch

        if person_idx == n_people:
            # event complete; move to next event
            backtrack(event + 1, 0)
            return

        pid = people[person_idx]
        pi = person_index[pid]

        # candidate seats
        # fixed?
        fixed_seat = None
        if event in fixed and pid in fixed[event]:
            fixed_seat = fixed[event][pid]

        candidates: list[str] = []
        if fixed_seat is not None:
            candidates = [fixed_seat]
        else:
            for sid in seats:
                if sid in used_by_person[pi]:
                    continue
                # seat must not already be used in this event
                # check distinctness within event
                if sid in [assign[event][k] for k in range(person_idx)]:
                    continue
                candidates.append(sid)

        # conflict check: if any already-assigned person in this event conflicts with pid,
        # their seats must not be adjacent.
        # precompute conflicting already assigned
        for sid in candidates:
            ok = True
            for k in range(person_idx):
                other_pid = people[k]
                if frozenset((pid, other_pid)) in conflict_pairs:
                    other_seat = assign[event][k]
                    if other_seat is not None and seats_adjacent(sid, other_seat):
                        ok = False
                        break
            if not ok:
                continue
            # also fixed conflict check with fixed people? handled as they are assigned in order maybe not if fixed order; but fixed seats assigned when their person index reached. For people before, fine.

            # assign
            assign[event][pi] = sid
            used_by_person[pi].add(sid)
            cumq[pi] += q[sid]

            backtrack(event, person_idx + 1)

            # undo
            assign[event][pi] = None
            used_by_person[pi].discard(sid)
            cumq[pi] -= q[sid]

        # if no candidates, branch dies

    # initial feasibility check
    # if seats < people already checked in model

    backtrack(0, 0)

    if best["assignments"] is None:
        # determine if infeasible
        return PlanResult(status="infeasible", assignments=[], objective=0.0, variety=0, nodes=nodes[0], reason="no feasible assignment found")

    assignments = []
    for e in range(n_events):
        m = {}
        for pi, pid in enumerate(people):
            m[pid] = best["assignments"][e][pi]
        assignments.append(m)

    # classify optimal vs feasible (if node budget exhausted without proving)
    status = "optimal" if (nodes[0] < node_budget or best["range"] <= 1e-9) else "feasible"
    return PlanResult(status=status, assignments=assignments, objective=float(best["range"]), variety=int(best["variety"]), nodes=nodes[0])


def verify(problem: Problem, report: dict) -> tuple[bool, list[str]]:
    """Independently re-derive and check a plan report. Returns (ok, errors)."""
    errors: list[str] = []
    # extract
    inp = report.get("input")
    if inp is None:
        errors.append("report missing 'input'")
        return False, errors
    try:
        p2 = problem  # use given
    except Exception:
        pass
    # rebuild problem from input to ensure consistency
    try:
        from .model import load_problem
        p_check = load_problem(inp)
    except Exception as e:
        errors.append(f"invalid embedded input: {e}")
        return False, errors

    # compare problem identity (people/seats/events)
    if p_check.person_ids != problem.person_ids:
        errors.append("embedded people differ from problem")
    if p_check.seat_ids != problem.seat_ids:
        errors.append("embedded seats differ from problem")
    if p_check.events != problem.events:
        errors.append("embedded events differ from problem")

    assignments = report.get("assignments")
    if not isinstance(assignments, list) or len(assignments) != problem.events:
        errors.append("assignments must be a list with one entry per event")
        return False, errors

    people = problem.person_ids
    seats = problem.seat_ids
    q = {s.seat_id: s.quality for s in problem.seats}
    adj = problem.adjacent_seats()
    seat_adj = adj
    conflicts = problem.conflicts

    # check each event
    cumq = {pid: 0.0 for pid in people}
    used_by_person = {pid: set() for pid in people}
    variety_pairs: set[frozenset[str]] = set()
    for ei, ev in enumerate(assignments):
        if not isinstance(ev, dict):
            errors.append(f"event {ei}: not an object")
            continue
        if set(ev.keys()) != set(people):
            errors.append(f"event {ei}: person set mismatch")
            continue
        vals = list(ev.values())
        if len(set(vals)) != len(vals):
            errors.append(f"event {ei}: duplicate seat")
        for pid in people:
            sid = ev[pid]
            if sid not in seats:
                errors.append(f"event {ei}: {pid} unknown seat {sid}")
                continue
            if sid in used_by_person[pid]:
                errors.append(f"event {ei}: {pid} repeats seat {sid}")
            used_by_person[pid].add(sid)
            cumq[pid] += q[sid]
        # conflicts adjacency
        seat_to_person = {sid: pid for pid, sid in ev.items()}
        for (a, b) in [(x, y) for x in people for y in people if x < y]:
            if frozenset((a, b)) in conflicts:
                sa, sb = ev[a], ev[b]
                if sb in seat_adj.get(sa, set()):
                    errors.append(f"event {ei}: conflicting people {a},{b} adjacent")
        # variety
        for pid in people:
            sa = ev[pid]
            for sb in seat_adj.get(sa, set()):
                pb = seat_to_person.get(sb)
                if pb is not None and pb != pid:
                    variety_pairs.add(frozenset((pid, pb)))

    if errors:
        return False, errors

    # objective check
    rng = max(cumq.values()) - min(cumq.values())
    reported_rng = report.get("objective")
    if reported_rng is None or abs(float(reported_rng) - rng) > 1e-9:
        errors.append(f"objective mismatch: reported {reported_rng}, recomputed {rng}")
    reported_var = report.get("variety")
    if reported_var is None or int(reported_var) != len(variety_pairs):
        errors.append(f"variety mismatch: reported {reported_var}, recomputed {len(variety_pairs)}")

    # status sanity: if reported infeasible but we found feasible, flag
    return (len(errors) == 0), errors
