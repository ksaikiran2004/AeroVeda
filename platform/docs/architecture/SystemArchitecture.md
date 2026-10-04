# System Architecture

## Overview

AeroVeda is designed as a modular desktop training product. It combines a Unity simulator, a shared contract layer, and a Streamlit dashboard into a single training workflow.

The architecture is intentionally split by responsibility so that the project can evolve from an MVP into a full training system without a rewrite.

## Architectural layers

### 1. Simulation layer
The Unity simulation layer handles:
- scenario execution
- entity lifecycle
- threat behavior
- operator actions
- scoring operations
- telemetry export

### 2. Content and contract layer
The shared layer defines:
- threat definitions
- scenario definitions
- score definitions
- session schema
- entity metadata
- future expansion modules

### 3. Analysis and review layer
The dashboard layer reads exported session records and provides:
- mission summary
- analytics
- competency tracking
- reporting
- AAR generation

## Recommended repository placement

```text
AeroVeda/
├── simulator/
│   └── unity/
├── dashboard/
│   └── streamlit/
├── shared/
│   ├── contracts/
│   ├── schemas/
│   ├── threat_library/
│   ├── entity_definitions/
│   └── future_modules/
├── platform/
│   ├── docs/
│   ├── data/
│   ├── deployment/
│   └── tests/
└── README.md
```

## Core module architecture

The simulator should be built as modular systems rather than as a single scene script:

```text
AeroVeda.Core
├── CompositionRoot
├── SimulationContext
├── EventBus
├── GameBootstrapper
├── AppLifecycle
└── Managers/
    ├── ScenarioManager
    ├── ThreatManager
    ├── ScoringManager
    ├── SessionRecorder
    └── AARBuilder
```

## Class hierarchy

```text
MonoBehaviour
└── BaseEntity
    ├── FriendlyEntity
    ├── ThreatEntity
    ├── SensorEntity
    └── EnvironmentEntity

ScriptableObject
├── ThreatDefinition
├── ScenarioDefinition
├── DifficultyProfile
├── ResponseRule
└── TrainingObjective
```

## Interfaces and modularity

Use interfaces where appropriate for:
- event communication
- scenario loading
- threat generation
- score adjudication
- session export
- AAR creation

Examples:
- IEventBus
- IScenarioManager
- IThreatLibrary
- IScoringManager
- ISessionExporter
- IAARBuilder

This prevents tight coupling between gameplay logic and data/reporting logic.

## Training loop

```text
Mission Start
   ↓
Threat Appears
   ↓
User Detects Threat
   ↓
User Classifies Threat
   ↓
User Selects Response
   ↓
Scoring and Adjudication
   ↓
Session Record Export
   ↓
After Action Review
```

## Data flow

```text
Unity Simulator
   ↓
Telemetry + events + actions
   ↓
SessionRecord JSON
   ↓
Shared contracts / schema validation
   ↓
Streamlit dashboard
   ↓
AAR, analytics, recommendations
```

## MVP implementation order

The implementation order should be:
1. Core architecture
2. Entity system
3. Threat definition system
4. SessionRecord schema
5. Scenario manager
6. Detection and classification workflow
7. Response logic
8. Scoring engine
9. Session export and AAR generation
10. Dashboard ingestion

## Product principles

- Keep the simulator and dashboard loosely coupled.
- Use JSON session records as the interoperability layer.
- Prefer shared content definitions and rule-based evaluation.
- Keep the architecture ready for expansion into surveillance, interception, swarm defense, and border security scenarios.
- Do not add cloud or microservice complexity before the product loop is validated.
