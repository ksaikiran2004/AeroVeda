from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_session_record() -> dict:
    data_file = Path(__file__).resolve().parents[1] / "data" / "exports" / "session_record_demo.json"
    if not data_file.exists():
        raise FileNotFoundError(f"Session record not found at {data_file}")

    with data_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_timeline() -> None:
    st.set_page_config(page_title="Mission Timeline", page_icon="🕒", layout="wide")

    record = load_session_record()
    events = record.get("events", [])

    st.title("Mission Timeline")
    st.caption(
        f"Session: {record.get('sessionId', 'N/A')} | "
        f"Scenario: {record.get('scenarioId', 'N/A')}"
    )

    if not events:
        st.warning("No mission events were found in the session record.")
        return

    event_rows = [
        {
            "Timestamp": event.get("timestampUtc", "N/A"),
            "Event Type": event.get("eventType", "N/A"),
            "Details": event.get("details", "N/A"),
        }
        for event in events
    ]
    st.dataframe(pd.DataFrame(event_rows), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    render_timeline()