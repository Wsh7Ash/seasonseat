"""Input parsing and validation for seasonseat."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class ModelError(ValueError):
    """Raised when an input document is invalid."""


@dataclass
class Seat:
    seat_id: str
    row: int
    col: int
    quality: float


@dataclass
class Person:
    person_id: str
    name: str = ""


@dataclass
class Problem:
    people: list[Person]
    seats: list[Seat]
    events: int
    conflicts: set[frozenset[str]] = field(default_factory=set)
    # optional fixed assignments: event_index -> {person_id: seat_id}
    fixed: dict[int, dict[str, str]] = field(default_factory=dict)

    @property
    def person_ids(self) -> list[str]:
        return [p.person_id for p in self.people]

    @property
    def seat_ids(self) -> list[str]:
        return [s.seat_id for s in self.seats]

    def seat_by_id(self, sid: str) -> Seat:
        for s in self.seats:
            if s.seat_id == sid:
                return s
        raise KeyError(sid)

    def adjacent_seats(self) -> dict[str, set[str]]:
        # seats are adjacent if same row and cols differ by 1, or same col and rows differ by 1, or diagonal
        out: dict[str, set[str]] = {s.seat_id: set() for s in self.seats}
        bypos = {(s.row, s.col): s.seat_id for s in self.seats}
        for s in self.seats:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nid = bypos.get((s.row + dr, s.col + dc))
                    if nid is not None:
                        out[s.seat_id].add(nid)
        return out


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ModelError(msg)


def load_problem(data: Any) -> Problem:
    if not isinstance(data, dict):
        raise ModelError("input must be a JSON object")
    people_raw = data.get("people")
    seats_raw = data.get("seats")
    events = data.get("events")
    _require(isinstance(people_raw, list) and len(people_raw) > 0, "people must be a non-empty list")
    _require(isinstance(seats_raw, list) and len(seats_raw) > 0, "seats must be a non-empty list")
    _require(isinstance(events, int) and not isinstance(events, bool) and events > 0, "events must be a positive integer")

    people: list[Person] = []
    seen_p: set[str] = set()
    for i, p in enumerate(people_raw):
        if not isinstance(p, dict):
            raise ModelError(f"people[{i}] must be an object")
        pid = p.get("id")
        _require(isinstance(pid, str) and pid, f"people[{i}].id must be a non-empty string")
        _require(pid not in seen_p, f"duplicate person id {pid!r}")
        seen_p.add(pid)
        name = p.get("name", "")
        _require(isinstance(name, str), f"people[{i}].name must be a string")
        people.append(Person(person_id=pid, name=name))

    seats: list[Seat] = []
    seen_s: set[str] = set()
    for i, s in enumerate(seats_raw):
        if not isinstance(s, dict):
            raise ModelError(f"seats[{i}] must be an object")
        sid = s.get("id")
        _require(isinstance(sid, str) and sid, f"seats[{i}].id must be a non-empty string")
        _require(sid not in seen_s, f"duplicate seat id {sid!r}")
        seen_s.add(sid)
        row = s.get("row")
        col = s.get("col")
        quality = s.get("quality", 0)
        _require(isinstance(row, int) and not isinstance(row, bool), f"seats[{i}].row must be an integer")
        _require(isinstance(col, int) and not isinstance(col, bool), f"seats[{i}].col must be an integer")
        _require(isinstance(quality, (int, float)) and not isinstance(quality, bool), f"seats[{i}].quality must be a number")
        import math
        _require(math.isfinite(quality), f"seats[{i}].quality must be finite")
        seats.append(Seat(seat_id=sid, row=row, col=col, quality=float(quality)))

    _require(len(seats) >= len(people), "need at least as many seats as people")

    conflicts: set[frozenset[str]] = set()
    for c in data.get("conflicts", []) or []:
        if not (isinstance(c, list) and len(c) == 2):
            raise ModelError("each conflict must be a 2-element list of person ids")
        a, b = c
        _require(a in seen_p and b in seen_p, "conflict references unknown person")
        _require(a != b, "conflict must reference two distinct people")
        conflicts.add(frozenset((a, b)))

    fixed: dict[int, dict[str, str]] = {}
    fixed_raw = data.get("fixed", {}) or {}
    if not isinstance(fixed_raw, dict):
        raise ModelError("fixed must be an object")
    for ek, v in fixed_raw.items():
        try:
            ei = int(ek)
        except (TypeError, ValueError):
            raise ModelError(f"fixed key {ek!r} must be an integer event index")
        _require(0 <= ei < events, f"fixed event index {ei} out of range")
        if not isinstance(v, dict):
            raise ModelError(f"fixed[{ei}] must be an object")
        fmap: dict[str, str] = {}
        for pid, sid in v.items():
            _require(pid in seen_p, f"fixed[{ei}] references unknown person {pid!r}")
            _require(sid in seen_s, f"fixed[{ei}] references unknown seat {sid!r}")
            fmap[pid] = sid
        # check uniqueness within event
        if len(set(fmap.values())) != len(fmap):
            raise ModelError(f"fixed[{ei}] assigns the same seat twice")
        fixed[ei] = fmap

    return Problem(people=people, seats=seats, events=events, conflicts=conflicts, fixed=fixed)


def load_problem_file(path: str) -> Problem:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return load_problem(data)
