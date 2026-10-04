# Scoring Engine

## Purpose

The scoring engine evaluates operator performance based on threat handling, decision quality, timing, and scenario outcome.

## Core scoring inputs

- threat type and context
- detection quality
- response timing
- decision correctness
- enforcement or avoidance outcome
- rule compliance

## Evaluation model

Scoring should be built around deterministic rule evaluation rather than opaque AI scoring.

This ensures:
- explainability
- repeatability
- easier debugging
- stronger AAR output

## Lifecycle

```text
Scenario start
   ↓
Operator actions
   ↓
Event adjudication
   ↓
Rule evaluation
   ↓
Score aggregation
   ↓
Final training summary
```

## Expected outputs

- competency score
- mission performance summary
- time-based metrics
- scenario-specific rubric scoring
- summary for dashboard reporting

## Key principle

The scoring engine should turn raw session behavior into understandable performance metrics without requiring external infrastructure.
