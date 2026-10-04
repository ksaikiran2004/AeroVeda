from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_session_record() -> dict:
    data_file = Path(__file__).resolve().parent / "data" / "exports" / "session_record_demo.json"
    if not data_file.exists():
        raise FileNotFoundError(f"Session record not found at {data_file}")

    with data_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _as_percent(value: float) -> str:
    return f"{float(value) * 100:.2f}%"


def render_page() -> None:
    st.set_page_config(page_title="Mission Overview", page_icon="🛩️", layout="wide")

    record = load_session_record()

    st.title("Mission Overview")
    st.caption(f"Source: {Path('data/exports/session_record_demo.json').as_posix()}")

    summary_col, score_col, correctness_col = st.columns([1.5, 1, 1])

    with summary_col:
        st.subheader("Mission Summary")
        mission_summary = {
            "Session ID": record.get("sessionId", "N/A"),
            "Scenario": record.get("scenarioId", "N/A"),
            "Threat Type": record.get("actualThreatType", record.get("threatType", "N/A")),
            "Difficulty": record.get("difficultyLevel", "N/A"),
            "Status": record.get("status", "N/A"),
        }

        for label, value in mission_summary.items():
            st.markdown(f"**{label}:** {value}")

    with score_col:
        st.subheader("Final Score")
        final_score = float(record.get("finalScore", 0.0))
        st.metric("Final Score Percentage", _as_percent(final_score))
        st.progress(min(0.0, 0.0), text="")
        st.progress(final_score, text="Mission score")

    with correctness_col:
        st.subheader("Correctness Panel")
        classification_ok = bool(record.get("classificationCorrect", False))
        response_ok = bool(record.get("responseCorrect", False))

        if classification_ok:
            st.success("Classification Correct")
        else:
            st.error("Classification Incorrect")

        if response_ok:
            st.success("Response Correct")
        else:
            st.error("Response Incorrect")

    breakdown = record.get("scoreBreakdown", {})
    breakdown_df = pd.DataFrame(
        [
            {"Category": "Detection", "Score": float(breakdown.get("detection", 0.0))},
            {"Category": "Classification", "Score": float(breakdown.get("classification", 0.0))},
            {"Category": "Response", "Score": float(breakdown.get("response", 0.0))},
            {"Category": "Protocol", "Score": float(breakdown.get("protocol", 0.0))},
        ]
    )

    st.subheader("Score Breakdown")
    st.bar_chart(breakdown_df.set_index("Category"), use_container_width=True)

    recommendation = record.get("trainingRecommendation", "No recommendation available.")
    st.subheader("Training Recommendation")
    st.info(recommendation)

    st.caption(f"Scenario Environment: {record.get('scenarioEnvironment', 'N/A')} | Scenario ID: {record.get('scenarioId', 'N/A')}")


if __name__ == "__main__":
    render_page()
