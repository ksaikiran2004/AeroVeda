# System Architecture

## Overview

AeroVeda is built as a desktop training platform with a clean separation between simulation, data exchange, and analysis.

The system has three major layers:

1. Simulation Layer — Unity-based operational training environment
2. Data and Contract Layer — JSON definitions, session records, and shared schemas
3. Analysis Layer — Streamlit dashboard for ingestion, metrics, AAR, and reporting

## Primary architecture flow

```text
Unity Simulator
   ↓
Session JSON Logs
   ↓
Shared Contracts / Threat Library
   ↓
Streamlit Dashboard
   ↓
AAR + Analytics + Review
```

## Responsibility split

### Simulator
The simulator manages:
- scenario execution
- threat behavior
- environment state
- operator actions
- scoring events
- telemetry capture

### Shared model
The shared layer defines contracts that all systems depend on:
- scenario definition
- session record
- scoring outcomes
- threat definitions
- entity metadata

### Dashboard
The dashboard is responsible for:
- ingesting exported session data
- validating session integrity
- showing training analytics
- generating AAR views
- summarizing operator performance

## Node responsibilities

- `simulator/unity` owns runtime simulation logic.
- `shared` owns data model definitions and scenario assets.
- `dashboard/streamlit` owns introspection and review workflows.
- `platform` owns deployment, validation, packaging, and documentation.

## Design principles

- Keep simulator and dashboard loosely coupled.
- Use JSON as the interoperability format.
- Prefer shared definitions over duplicated logic.
- Treat architecture and contracts as source-of-truth artifacts.
- Keep the project deployable on standard desktop systems.
