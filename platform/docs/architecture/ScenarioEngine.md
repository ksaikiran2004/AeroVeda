# Scenario Engine

## Purpose

The scenario engine defines how a training situation is created, validated, and executed inside the simulator.

## Core scenario elements

- threat composition
- operator objective
- environmental setup
- detection constraints
- timeline progression
- score triggers
- success and failure conditions

## Scenario lifecycle

```text
Scenario definition loaded
   ↓
Validation against schema and rules
   ↓
Environment setup
   ↓
Threat generation and objective assignment
   ↓
Runtime execution
   ↓
Score and telemetry export
```

## Design intent

Scenarios should be authored as data rather than hardcoded procedural flows wherever possible. This allows faster iteration and future scenario expansion.

## Important principle

Threats, entities, and difficulty should all be driven by shared definitions so the simulator and dashboard remain aligned.
