"""Command-line interface for seasonseat."""

from __future__ import annotations

import argparse
import json
import sys

from .model import load_problem_file, ModelError
from .planner import plan, verify
from .report import build_report, dump_json, load_json, render_text


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        problem = load_problem_file(args.input)
    except (ModelError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    result = plan(problem, node_budget=args.node_budget)
    report = build_report(problem, result)
    if args.output:
        dump_json(args.output, report)
    print(render_text(report))
    if result.status == "infeasible":
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        report = load_json(args.report)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    # rebuild problem from embedded input
    try:
        from .model import load_problem
        problem = load_problem(report["input"])
    except Exception as e:
        print(f"error: invalid embedded input: {e}", file=sys.stderr)
        return 2
    ok, errors = verify(problem, report)
    if ok:
        print("verify: OK")
        return 0
    for e in errors:
        print(f"verify: {e}", file=sys.stderr)
    return 1


def cmd_demo(args: argparse.Namespace) -> int:
    import os, tempfile
    sample = {
        "people": [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}, {"id": "p4"}],
        "seats": [
            {"id": "A1", "row": 0, "col": 0, "quality": 10},
            {"id": "A2", "row": 0, "col": 1, "quality": 8},
            {"id": "A3", "row": 0, "col": 2, "quality": 7},
            {"id": "B1", "row": 1, "col": 0, "quality": 6},
            {"id": "B2", "row": 1, "col": 1, "quality": 4},
            {"id": "B3", "row": 1, "col": 2, "quality": 5},
            {"id": "C1", "row": 2, "col": 0, "quality": 3},
            {"id": "C2", "row": 2, "col": 1, "quality": 2},
            {"id": "C3", "row": 2, "col": 2, "quality": 1},
        ],
        "events": 3,
        "conflicts": [["p1", "p2"]],
    }
    d = tempfile.mkdtemp()
    inp = os.path.join(d, "in.json")
    out = os.path.join(d, "out.json")
    with open(inp, "w") as f:
        json.dump(sample, f)
    rc = cmd_plan(argparse.Namespace(input=inp, output=out, node_budget=200000))
    if rc != 0:
        return rc
    rc2 = cmd_verify(argparse.Namespace(report=out))
    return rc2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="seasonseat")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="plan seasonal seating")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.add_argument("--node-budget", type=int, default=200000)
    p.set_defaults(func=cmd_plan)
    v = sub.add_parser("verify", help="verify a plan report")
    v.add_argument("report")
    v.set_defaults(func=cmd_verify)
    d = sub.add_parser("demo", help="run built-in demo")
    d.set_defaults(func=cmd_demo)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
