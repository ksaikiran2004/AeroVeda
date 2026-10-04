using System;
using AeroVeda.Content;

namespace AeroVeda.Evaluation.Adjudication;

public sealed class DetectionWorkflow
{
    public DetectionResult Evaluate(ThreatDefinition threat, float sensorQuality, float operatorAlertness, float rangeToThreat)
    {
        if (threat == null)
        {
            throw new ArgumentNullException(nameof(threat));
        }

        var difficultyAdjustment = threat.DetectionDifficulty * 0.35f;
        var confidence = Mathf.Clamp01((sensorQuality * 0.5f) + (operatorAlertness * 0.3f) + (1f - rangeToThreat / 1000f) * 0.2f - difficultyAdjustment);
        var detected = confidence >= 0.55f;

        return new DetectionResult
        {
            ThreatId = threat.ThreatId,
            Detected = detected,
            Confidence = confidence,
            DetectionTimeSeconds = detected ? 5f - confidence * 3f : 0f,
            Reason = detected ? "Sensor and operator cues exceeded the detection threshold." : "Detection threshold not met."
        };
    }
}

public sealed class DetectionResult
{
    public string ThreatId { get; set; }
    public bool Detected { get; set; }
    public float Confidence { get; set; }
    public float DetectionTimeSeconds { get; set; }
    public string Reason { get; set; }
}

internal static class Mathf
{
    public static float Clamp01(float value)
    {
        if (value < 0f)
        {
            return 0f;
        }

        if (value > 1f)
        {
            return 1f;
        }

        return value;
    }
}
