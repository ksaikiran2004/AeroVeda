using System;
using System.Collections.Generic;
using AeroVeda.Session;

namespace AeroVeda.Headless;

public sealed class HeadlessEntryPoint
{
    public static SessionRecord RunUrbanDayDemo()
    {
        var record = new SessionRecord
        {
            SessionId = "sess-urban-day-demo-001",
            ScenarioId = "urban-day-counter-uav",
            OperatorId = "ops-demo",
            StartTimeUtc = new DateTime(2026, 10, 4, 9, 0, 0, DateTimeKind.Utc),
            EndTimeUtc = new DateTime(2026, 10, 4, 9, 3, 40, DateTimeKind.Utc),
            Status = "Completed",
            ActualThreatType = "FPV Drone",
            ClassifiedThreatType = "FPV Drone",
            ClassificationCorrect = true,
            RecommendedResponse = "Jam",
            SelectedResponse = "Jam",
            ResponseCorrect = true,
            DifficultyLevel = "Easy",
            ScenarioEnvironment = "Urban Day",
            TrainingRecommendation = "Continue FPV engagement drills.",
            ThreatType = "FPV Drone",
            DetectionTimeSeconds = 2.46f,
            Classification = "Hostile FPV drone",
            Response = "Jam",
            FinalScore = 0.9038f,
            ScoreBreakdown = new SessionScoreBreakdown
            {
                Detection = 35f,
                Classification = 30f,
                Response = 25f,
                Protocol = 10f
            }
        };

        record.Events = new List<SessionEvent>
        {
            new SessionEvent { TimestampUtc = record.StartTimeUtc, EventType = "MissionStarted", Details = "Urban Day Counter-UAS mission initialized." },
            new SessionEvent { TimestampUtc = record.StartTimeUtc.AddSeconds(12), EventType = "ThreatDetected", Details = "Rising FPV signature observed and confirmed by radar." },
            new SessionEvent { TimestampUtc = record.StartTimeUtc.AddSeconds(18), EventType = "ThreatClassified", Details = "Threat classified as hostile FPV attack drone." },
            new SessionEvent { TimestampUtc = record.StartTimeUtc.AddSeconds(24), EventType = "ResponseSelected", Details = "Jam response selected due to short time-to-impact window." },
            new SessionEvent { TimestampUtc = record.EndTimeUtc, EventType = "MissionCompleted", Details = "Threat was accurately detected, classified, and neutralized with an appropriate response." }
        };

        return record;
    }
}
