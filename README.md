# seasonseat

Plan seating across a whole season of events so that, over the season, each
attendee's cumulative seat quality is balanced, no one sits in the same seat
twice, and conflicts (people who should not sit next to each other) are
respected in every event. Every plan embeds its own input so an independent
command can re-derive and verify it.

## Problem

One-off seating charts optimize a single event. Across a season, the same
people end up in the same "good" or "bad" seats, and the same pairs end up
next to each other. seasonseat treats the season as one coupled assignment
problem and balances exposure over all events.

## Features

- Multi-event planning with a no-repeat-seat constraint per person.
- Quality-balance objective (minimize max-min cumulative seat quality).
- Conflict pairs (people who must not be adjacent) enforced in every event.
- Adjacency-variety tracking (distinct neighbor pairs across events).
- Independent `verify` command re-derives the report from its embedded input.
- Exit codes: 0 success, 1 infeasible/no plan, 2 input error.

## Requirements

Python 3.11+. Standard library only.

## Installation

```bash
cd seasonseat
python -m seasonseat demo
```

## Quick start

```bash
python -m seasonseat plan examples/sample.json -o report.json
python -m seasonseat verify report.json
```

## Usage

See `docs/USAGE.md`.

## Testing

```bash
python -m unittest discover -s tests
python -m compileall -q seasonseat
```

## Limitations

- Exact search; practical for small rosters (roughly up to 8 people, 6 events).
- Quality values are user-supplied planning weights, not an objective measure
  of seat quality.
- No accessibility, sight-line, or furniture constraints beyond the grid
  adjacency model.
- Not a substitute for a venue's seating policy.

## License

MIT. See `LICENSE`.