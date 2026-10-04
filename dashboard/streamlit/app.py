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


def render_page() -> None:
	st.set_page_config(page_title="Mission Overview", page_icon="🛩️", layout="wide")

	record = load_session_record()

	st.title("Mission Overview")
	st.caption("Source: data/exports/session_record_demo.json")

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
		st.metric("Final Score Percentage", f"{final_score * 100:.2f}%")
		st.progress(final_score, text="Mission score")

	with correctness_col:
		st.subheader("Correctness Panel")
		if bool(record.get("classificationCorrect", False)):
			st.success("Classification Correct")
		else:
			st.error("Classification Incorrect")

		if bool(record.get("responseCorrect", False)):
			st.success("Response Correct")
		else:
			st.error("Response Incorrect")

	breakdown = record.get("scoreBreakdown", {})
	breakdown_df = pd.DataFrame(
		[
			{"Category": str(category).title(), "Score": float(score)}
			for category, score in breakdown.items()
		]
	)

	if not breakdown_df.empty:
		st.subheader("Score Breakdown")
		st.bar_chart(breakdown_df.set_index("Category"), use_container_width=True)

	st.subheader("Training Recommendation")
	st.info(record.get("trainingRecommendation", "No recommendation available."))

	st.caption(
		f"Scenario Environment: {record.get('scenarioEnvironment', 'N/A')} | "
		f"Scenario ID: {record.get('scenarioId', 'N/A')}"
	)


if __name__ == "__main__":
	render_page()
