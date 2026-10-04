using System;
using System.Collections.Generic;

namespace AeroVeda.Session;

[Serializable]
public sealed class SessionRecord
{
    public string SessionId;
    public string ScenarioId;
    public string OperatorId;
    public DateTime StartTimeUtc;
    public DateTime EndTimeUtc;
    public string Status;
    public string ThreatType;
    public float DetectionTimeSeconds;
    public string Classification;
    public string Response;
    public float FinalScore;

    public List<SessionEvent> Events = new();
}

[Serializable]
public sealed class SessionEvent
{
    public DateTime TimestampUtc;
    public string EventType;
    public string Details;
}
