using System;
using AeroVeda.Content;

namespace AeroVeda.Evaluation.Adjudication;

public sealed class ThreatClassificationWorkflow
{
    public ClassificationResult Classify(ThreatDefinition threat, float confidence, bool observerConfirmed, bool radarConfirmed)
    {
        if (threat == null)
        {
            throw new ArgumentNullException(nameof(threat));
        }

        var adjustedScore = confidence;
        if (observerConfirmed)
        {
            adjustedScore += 0.15f;
        }

        if (radarConfirmed)
        {
            adjustedScore += 0.15f;
        }

        adjustedScore = Math.Clamp(adjustedScore, 0f, 1f);

        return new ClassificationResult
        {
            ThreatId = threat.ThreatId,
            Category = threat.Category,
            ThreatType = threat.DisplayName,
            Confidence = adjustedScore,
            IsHostile = threat.IsHostile || adjustedScore >= 0.7f,
            Reason = "Rules-based classification aligned with threat definition and sensor corroboration."
        };
    }
}

public sealed class ClassificationResult
{
    public string ThreatId { get; set; }
    public ThreatCategory Category { get; set; }
    public string ThreatType { get; set; }
    public float Confidence { get; set; }
    public bool IsHostile { get; set; }
    public string Reason { get; set; }
}
