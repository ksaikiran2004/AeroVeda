---
Owner: Platform
Status: Active
Last-reviewed: 2026-10-04
---

# Platform scripts

This area holds operational tooling for the AeroVeda platform. The current focus is on deterministic simulation and export workflows.

## Headless session export

Use the headless runner to create a demo session record from the mission logic and store it in the dashboard export area.

```bash
python3 platform/scripts/headless/run_session_export.py
```

The output is written to:

```text
dashboard/streamlit/data/exports/session_record_demo.json
```
