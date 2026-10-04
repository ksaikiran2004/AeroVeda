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


def _to_percentage(value: float) -> float:
    if 0.0 <= value <= 1.0:
        return value * 100.0
    return float(value)


def build_breakdown_frame(raw_breakdown: dict) -> pd.DataFrame:
    labels = {
        "detection": "Detection",
        "classification": "Classification",
        "response": "Response",
        "protocol": "Protocol",
    }
    rows = [
        {"Category": labels.get(str(key).lower(), str(key).title()), "Score": float(value)}
        for key, value in raw_breakdown.items()
    ]
    if not rows:
        return pd.DataFrame(columns=["Category", "Score"])
    return pd.DataFrame(rows).sort_values("Score", ascending=True).reset_index(drop=True)


def compute_recommendations(df: pd.DataFrame, overall_score: float) -> list[str]:
    recommendations: list[str] = []
    weakest = df.loc[df["Score"].idxmin()]
    strongest = df.loc[df["Score"].idxmax()]
    spread = float(df["Score"].max() - df["Score"].min())

    if weakest["Score"] < 70:
        recommendations.append(
            f"Prioritize additional training in {weakest['Category']} to reduce the current skill gap and improve consistency under operational pressure."
        )
    else:
        recommendations.append(
            f"{weakest['Category']} is stable; continue periodic reinforcement to maintain the current performance baseline."
        )

    if strongest["Score"] >= 85:
        recommendations.append(
            f"{strongest['Category']} is a clear strength. Use advanced scenario repetition to sustain excellence and translate this competency into broader mission readiness."
        )

    if spread >= 20:
        recommendations.append(
            "The score spread is significant. Focus on balancing the weaker competency against the stronger one so mission execution remains consistent across the full decision cycle."
        )

    if overall_score < 80:
        recommendations.append(
            "Overall performance is below the target threshold. Increase scenario repetition with realistic time-pressure and uncertainty conditions."
        )
    elif overall_score >= 90:
        recommendations.append(
            "Overall performance is strong. Maintain the current standard and challenge the operator with more complex multi-threat scenarios to sharpen edge-case judgment."
        )
    else:
        recommendations.append(
            "Performance is operationally acceptable. Maintain current training rhythm while targeted drills should continue on the weakest competency area."
        )

    return recommendations


def render_assessment() -> None:
    st.set_page_config(page_title="Competency Assessment", page_icon="📊", layout="wide")

    record = load_session_record()
    breakdown_df = build_breakdown_frame(record.get("scoreBreakdown", {}))
    if breakdown_df.empty:
        st.warning("No scoreBreakdown data is available for assessment.")
        return

    overall_score = float(record.get("finalScore", breakdown_df["Score"].mean() / 100.0))
    overall_percent = _to_percentage(overall_score)
    weakest = breakdown_df.loc[breakdown_df["Score"].idxmin()]
    strongest = breakdown_df.loc[breakdown_df["Score"].idxmax()]

    st.title("Competency Assessment")
    st.caption(
        f"Session: {record.get('sessionId', 'N/A')} | "
        f"Scenario: {record.get('scenarioId', 'N/A')}"
    )

    overall_col, weakest_col, strongest_col = st.columns(3)
    overall_col.metric("Overall Score", f"{overall_percent:.1f}%")
    weakest_col.metric("Weakest Area", weakest["Category"], delta=f"{weakest['Score']:.0f}%")
    strongest_col.metric("Strongest Area", strongest["Category"], delta=f"{strongest['Score']:.0f}%")

    st.subheader("Score Distribution")
    st.bar_chart(breakdown_df.set_index("Category"), use_container_width=True)

    st.subheader("Recommendations")
    for recommendation in compute_recommendations(breakdown_df, overall_percent):
        st.markdown(f"- {recommendation}")


if __name__ == "__main__":
    render_assessment()