# Deployment Notes

This folder contains packaging and installation assets for shipping AeroVeda in a desktop-first format.

## Intent

- package the Unity simulator
- package the Streamlit dashboard
- generate a simplified installer flow for training environments
- support offline deployment for demonstration and evaluation

## Typical workflow

1. Build simulator from Unity project.
2. Package dashboard as a local Python app.
3. Export scenario and session assets from shared definitions.
4. Install into a training machine through a desktop setup bundle.

## Recommended target

AeroVeda should ship as a desktop product with local runtime dependencies and a local data folder rather than a cloud-first architecture.
