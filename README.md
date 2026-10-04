# AeroVeda

AeroVeda is an AI-enabled drone and counter-drone training platform designed for realistic threat detection, response simulation, and after-action review.

## Product goal

The project is designed around a desktop-first workflow:

1. Unity simulator runs a mission or scenario.
2. Threat events and operator actions are recorded.
3. Structured JSON session records are exported.
4. Streamlit dashboard ingests the session data.
5. Analytics, scored outcomes, and AAR are generated.

This is the product foundation for the final architecture, not a throwaway prototype.

## Repository structure

```text
AeroVeda/
├── simulator/
│   └── unity/
│       └── Assets/
│           └── AeroVeda/
├── dashboard/
│   └── streamlit/
├── shared/
│   ├── contracts/
│   ├── schemas/
│   ├── threat_library/
│   ├── entity_definitions/
│   ├── fixtures/
│   └── future_modules/
├── platform/
│   ├── docs/
│   ├── data/
│   ├── deployment/
│   ├── scripts/
│   ├── samples/
│   └── tests/
├── .github/
├── README.md
├── LICENSE
└── .gitignore
```

## System architecture

### Simulation layer
Unity owns the runtime simulation and interaction logic:
- mission execution
- threat spawning
- detection actions
- classification flow
- response selection
- scoring and telemetry export

### Shared contract layer
The shared layer owns the source-of-truth data model:
- scenario definitions
- threat definitions
- scoring contracts
- session record schema
- entity metadata

### Analysis layer
The Streamlit dashboard consumes captured JSON to provide:
- AAR and mission summary
- performance analytics
- training progression views
- reporting and annotation tools

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
Session Record Generated
   ↓
After Action Review
```

## MVP scope

The current MVP focuses on the following user-facing capabilities:
- Counter-UAS operations
- protocol and mission training
- detection/classification/response workflow
- scoring and final score generation
- JSON session record export
- AAR generation based on deterministic rules

## Future expansion

The architecture supports future modules such as:
- Surveillance missions
- Interceptor operations
- Border security
- Counter-terror operations
- Swarm defense
- adaptive difficulty progression

## Design principles

- Use Unity 2022 LTS.
- Favor modular architecture over monolithic scripts.
- Keep interfaces and domain boundaries explicit.
- Use ScriptableObjects for reusable definitions.
- Generate JSON for interoperability.
- Design for future expansion rather than a throwaway demo.
