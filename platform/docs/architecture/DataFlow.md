# Data Flow

## Summary

AeroVeda generates operational event data in the Unity simulator and passes it to the dashboard through JSON artifacts.

## Flow

1. The simulator starts a training session.
2. Threats, sensors, and operator inputs are processed during execution.
3. Events and telemetry are serialized into structured JSON.
4. Session artifacts are written to the shared data pipeline.
5. The Streamlit dashboard reads the data for analysis and review.

## Data classes

- Session record
- Scenario definition
- Threat definitions
- Scoring outcomes
- Export bundle metadata
- Annotation records

## Storage boundaries

```text
simulator/unity     → produces session logs and scenario events
shared/contracts    → defines the data model
platform/data       → stores exported results and consumption artifacts
dashboard/streamlit → reads, validates, visualizes, and reports on data
```

## Recommended data lifecycle

```text
Scenario launch
   ↓
Simulation run
   ↓
Telemetry export
   ↓
Schema validation
   ↓
Dashboard ingestion
   ↓
AAR and analytics output
```

## Design intent

This keeps the core product simple and practical: no over-engineered service layer, just a product-grade simulation-to-dashboard flow that is easy to package and demo.
