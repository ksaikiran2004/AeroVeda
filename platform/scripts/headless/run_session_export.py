#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCENARIO_ID = "urban-day-counter-uav"
OUTPUT_PATH = Path("frontend/dashboard/data/exports/session_record_demo.json")


def compute_detection(sensor_quality: float, operator_alertness: float, range_to_threat: float) -> tuple[float, bool, float]:
    confidence = (sensor_quality * 0.5) + (operator_alertness * 0.3) + ((1.0 - (range_to_threat / 1000.0)) * 0.2)
    confidence = max(0.0, min(1.0, confidence))
    detected = confidence >= 0.55
    time_to_detect = 5.0 - (confidence * 3.0) if detected else 0.0
    return confidence, detected, time_to_detect


def classify_threat(threat_label: str, confidence: float, observer_confirmed: bool, radar_confirmed: bool) -> tuple[str, bool, float]:
    adjusted = confidence
    if observer_confirmed:
        adjusted += 0.15
    if radar_confirmed:
        adjusted += 0.15
    adjusted = max(0.0, min(1.0, adjusted))
    is_hostile = threat_label in {"FPV Drone", "Recon UAV"} or adjusted >= 0.7
    category = "Hostile FPV drone" if threat_label == "FPV Drone" else "Hostile recon UAV"
    return category, is_hostile, adjusted


def select_response(threat_label: str, is_hostile: bool, time_to_impact: float) -> str:
    if threat_label == "FPV Drone" and time_to_impact <= 12.0:
        return "Jam"
    if threat_label == "Recon UAV" and time_to_impact <= 18.0:
        return "Monitor"
    if is_hostile and time_to_impact <= 15.0:
        return "Intercept"
    return "Jam" if is_hostile else "Monitor"


def adjudicate(detection_confidence: float, classification_confidence: float, response: str) -> tuple[float, bool, str]:
    response_weight = {
        "Monitor": 0.15,
        "Jam": 0.25,
        "Intercept": 0.35,
        "Kinetic": 0.45,
    }.get(response, 0.0)
    score = (detection_confidence * 0.3) + (classification_confidence * 0.4) + (response_weight * 1.0)
    score = max(0.0, min(1.0, score))
    success = score >= 0.6
    summary = (
        "Threat was accurately detected, classified, and neutralized with an appropriate response."
        if success
        else "Threat response did not exceed the adjudication threshold."
    )
    return score, success, summary


def build_demo_record() -> dict:
    start_time = datetime(2026, 10, 4, 9, 0, 0, tzinfo=timezone.utc)
    end_time = start_time + timedelta(minutes=3, seconds=40)

    threat_label = "FPV Drone"
    recommended_response = "Jam"
    sensor_quality = 0.9
    operator_alertness = 0.8
    range_to_threat = 220.0
    detection_confidence, detected, detection_time = compute_detection(sensor_quality, operator_alertness, range_to_threat)
    classification_label, is_hostile, classification_confidence = classify_threat(
        threat_label, detection_confidence, observer_confirmed=True, radar_confirmed=True
    )
    selected_response = select_response(threat_label, is_hostile, time_to_impact=12.0)
    score, success, summary = adjudicate(detection_confidence, classification_confidence, selected_response)
    classification_correct = classification_label == "Hostile FPV drone"
    response_correct = selected_response == recommended_response
    breakdown = {
        "detection": 35,
        "classification": 30,
        "response": 25,
        "protocol": 10,
    }

    record = {
        "sessionId": "sess-urban-day-demo-001",
        "scenarioId": SCENARIO_ID,
        "operatorId": "ops-demo",
        "startTimeUtc": start_time.isoformat().replace("+00:00", "Z"),
        "endTimeUtc": end_time.isoformat().replace("+00:00", "Z"),
        "status": "Completed" if success else "NeedsReview",
        "actualThreatType": threat_label,
        "classifiedThreatType": threat_label,
        "classificationCorrect": classification_correct,
        "recommendedResponse": recommended_response,
        "selectedResponse": selected_response,
        "responseCorrect": response_correct,
        "difficultyLevel": "Easy",
        "scenarioEnvironment": "Urban Day",
        "trainingRecommendation": "Continue FPV engagement drills.",
        "threatType": threat_label,
        "detectionTimeSeconds": round(detection_time, 2),
        "classification": classification_label,
        "response": selected_response,
        "finalScore": round(score, 4),
        "scoreBreakdown": breakdown,
        "events": [
            {
                "timestampUtc": start_time.isoformat().replace("+00:00", "Z"),
                "eventType": "MissionStarted",
                "details": "Urban Day Counter-UAS mission initialized.",
            },
            {
                "timestampUtc": (start_time + timedelta(seconds=12)).isoformat().replace("+00:00", "Z"),
                "eventType": "ThreatDetected",
                "details": "Rising FPV signature observed and confirmed by radar.",
            },
            {
                "timestampUtc": (start_time + timedelta(seconds=18)).isoformat().replace("+00:00", "Z"),
                "eventType": "ThreatClassified",
                "details": "Threat classified as hostile FPV attack drone.",
            },
            {
                "timestampUtc": (start_time + timedelta(seconds=24)).isoformat().replace("+00:00", "Z"),
                "eventType": "ResponseSelected",
                "details": "Jam response selected due to short time-to-impact window.",
            },
            {
                "timestampUtc": end_time.isoformat().replace("+00:00", "Z"),
                "eventType": "MissionCompleted",
                "details": summary,
            },
        ],
    }

    return record


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = build_demo_record()
    OUTPUT_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Exported demo session record to {OUTPUT_PATH}")
    print(f"Final score: {record['finalScore']} | status: {record['status']}")
    print(f"Classification correct: {record['classificationCorrect']} | response correct: {record['responseCorrect']}")


if __name__ == "__main__":
    main()
