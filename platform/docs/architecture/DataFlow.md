# Data Flow

## Summary

AeroVeda follows a deterministic training loop: simulation produces telemetry, telemetry becomes a session record, and the dashboard consumes that record for review and analytics.

## Core flow

```text
Mission Start
   ↓
ScenarioDefinition loaded
   ↓
ThreatEntity spawned
   ↓
Detect Threat
   ↓
Classify Threat
   ↓
Select Response
   ↓
Adjudication and scoring
   ↓
SessionRecord JSON
   ↓
AAR and dashboard reporting
```

## Data objects

### ScenarioDefinition
Stores scenario metadata, environment, objective, threat composition, and rules.

### ThreatDefinition
Defines a threat’s identity, category, behavior, and scoring profile.

### SessionRecord
Captures:
- session ID
- scenario ID
- operator ID
- threat type
- detection time
- classification
- response choice
- score
- event timeline

### AARSummary
Contains the final mission summary, mistakes, and rule-based recommendations.

## Storage boundaries

```text
simulator/unity     -> produces runtime events and session artifacts
shared/contracts    -> defines the canonical data model
platform/data       -> stores exported sessions and training outputs
dashboard/streamlit -> reads, validates, and visualizes session records
```

## Execution path

1. Scenario starts in Unity.
2. Threats are created from ScriptableObjects.
3. Player actions are recorded as events.
4. The scoring system computes detection and response quality.
5. SessionRecord is serialized to JSON.
6. Dashboard loads and validates the JSON.
7. AAR and analytics are generated using deterministic rule logic.

## Contract-first design

The architecture depends on the following shared definitions:
- `ThreatDefinition` for all threat types
- `ScenarioDefinition` for mission setup
- `SessionRecord` as the exported outcome

This ensures future threats and scenarios can be added without rewriting logic.

## Design intent

The purpose is to keep the product understandable and deployable while still enabling feature growth. The data model should remain the single source of truth between simulation and review.
