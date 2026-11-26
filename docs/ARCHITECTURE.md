# Architecture — seasonseat

model.py: parsing/validation, adjacency model.
planner.py: exact backtracking search, verify().
report.py: JSON/text rendering, embedded input.
cli.py: plan/verify/demo commands.

Data flow: input JSON -> Problem -> plan() -> PlanResult -> build_report -> JSON.
verify: report JSON -> rebuild Problem from embedded input -> verify().