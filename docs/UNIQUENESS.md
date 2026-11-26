# Uniqueness — seasonseat

## Closest alternatives
LupSeat (randomized single-event seating), neyc-exam-seat (single-event
anti-collusion), ChoralSeats (manual charting).

## Similarities
All assign people to seats in a grid with adjacency constraints.

## Meaningful differences
- Objective is fairness *across a season* (no repeated seats, balanced
  cumulative quality), not a single event.
- Independent verifier re-derives assignments, objective, and variety from the
  embedded input.

## Unique mechanism
Multi-event backtracking with a no-repeat-per-person constraint and a
quality-balance objective, plus an embedded-input certificate.

## Why independent repository
Distinct objective and verification model from single-event tools.

## Remaining uncertainties
Could not exhaustively survey all seating tools; the season-fairness objective
is the claimed distinction.