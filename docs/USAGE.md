# Usage — seasonseat

## Input format

```json
{
  "people": [{"id": "alice"}, {"id": "bob"}],
  "seats": [{"id": "A1", "row": 0, "col": 0, "quality": 10}],
  "events": 3,
  "conflicts": [["alice", "bob"]],
  "fixed": {"0": {"alice": "A1"}}
}
```

## Commands

- `python -m seasonseat plan INPUT [-o OUT] [--node-budget N]`
- `python -m seasonseat verify REPORT`
- `python -m seasonseat demo`