using System;
using AeroVeda.Content;

namespace AeroVeda.Evaluation.Adjudication;

public sealed class AdjudicationLogic
{
    public AdjudicationResult Evaluate(ThreatDefinition threat, DetectionResult detection, ClassificationResult classification, ResponseDecision response)
    {
        if (threat == null)
        {
            throw new ArgumentNullException(nameof(threat));
        }

        if (detection == null)
        {
            throw new ArgumentNullException(nameof(detection));
        }

        if (classification == null)
        {
            throw new ArgumentNullException(nameof(classification));
        }

        if (response == null)
        {
            throw new ArgumentNullException(nameof(response));
        }

        var detectionFactor = detection.Detected ? 0.4f : -0.15f;
        var classificationFactor = classification.IsHostile ? 0.35f : -0.1f;
        var responseFactor = response.Response switch
        {
            ResponseType.Monitor => 0.15f,
            ResponseType.Jam => 0.25f,
            ResponseType.Intercept => 0.35f,
            ResponseType.Kinetic => 0.45f,
            _ => 0f
        };

        var score = Math.Clamp((detection.Confidence * 0.3f) + (classification.Confidence * 0.4f) + response.Confidence * 0.2f + detectionFactor + classificationFactor + responseFactor, 0f, 1f);
        var wasSuccessful = detection.Detected && classification.IsHostile && score >= 0.6f;

        return new AdjudicationResult
        {
            ThreatId = threat.ThreatId,
            Score = score,
            Success = wasSuccessful,
            Summary = wasSuccessful
                ? "Threat was accurately detected, classified, and neutralized with an appropriate response."
                : "Threat response did not meet the desired adjudication threshold."
        };
    }
}

public sealed class AdjudicationResult
{
    public string ThreatId { get; set; }
    public float Score { get; set; }
    public bool Success { get; set; }
    public string Summary { get; set; }
}
