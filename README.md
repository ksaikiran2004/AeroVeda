# AeroVeda

AI-enabled military training platform for drone threat detection, classification, engagement decision-making, and after-action review.

## Architecture split

This repository is organized by responsibility rather than by language alone:

- `backend/` — runtime simulation engine and game systems
- `frontend/` — user-facing dashboard and review tools
- `shared/` — contract schemas, fixtures, and shared definitions
- `platform/` — CI, scripts, docs, tests, and sample content

## Repository layout

```text
AeroVeda/
├── backend/
│   └── simulator/
├── frontend/
│   └── dashboard/
├── shared/
├── platform/
│   ├── .github/
│   ├── docs/
│   ├── scripts/
│   ├── tests/
│   └── samples/
├── README.md
└── LICENSE
```

## Design intent

- Frontend handles presentation, analytics, and reporting.
- Backend handles the simulator and runtime logic.
- Shared holds contract-level source-of-truth definitions.
- Platform owns build, validation, docs, and operations.
