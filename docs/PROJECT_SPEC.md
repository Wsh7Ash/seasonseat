# Project Specification — seasonseat

## Vision
Balance seating exposure across a season of events.

## Target audience
Event organizers, venue managers, teachers, choir directors, anyone assigning
seats repeatedly to the same group.

## Problem
Single-event seating charts leave the same people in the same quality seats and
the same pairs adjacent every time.

## Existing alternatives
LupSeat, neyc-exam-seat, ChoralSeats, berkeley seating app. These optimize one
event; none balances exposure across a season with a no-repeat and conflict
constraint.

## Differentiation
Season is one coupled assignment problem: no person repeats a seat across
events, quality exposure balanced, conflicts respected in every event,
independent verifier re-derives the report.

## Core functionality
- Parse and validate input.
- Exact backtracking search with quality-balance objective.
- Conflict enforcement.
- Report with embedded input.
- Independent verify command.

## Architecture
model -> planner (backtracking) -> report (JSON/text) -> cli.

## Testing
Unit tests for model, plan, verify, CLI demo.

## Definition of done
Tests pass, demo passes, verify passes, docs present.

## Limitations
Small rosters only; quality weights user-supplied.