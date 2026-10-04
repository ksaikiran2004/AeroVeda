using System;
using AeroVeda.Content;

namespace AeroVeda.Evaluation.Adjudication;

public sealed class AdjudicationManager : IAdjudicationManager
{
    private readonly DetectionWorkflow _detectionWorkflow = new();
    private readonly ThreatClassificationWorkflow _classificationWorkflow = new();
    private readonly ResponseSelectionWorkflow _responseWorkflow = new();
    private readonly AdjudicationLogic _adjudicationLogic = new();

    public AdjudicationResult EvaluateThreat(
        ThreatDefinition threat,
        float sensorQuality,
        float operatorAlertness,
        float rangeToThreat,
        bool observerConfirmed,
        bool radarConfirmed,
        float timeToImpactSeconds)
    {
        if (threat == null)
        {
            throw new ArgumentNullException(nameof(threat));
        }

        var detection = _detectionWorkflow.Evaluate(threat, sensorQuality, operatorAlertness, rangeToThreat);
        var classification = _classificationWorkflow.Classify(threat, detection.Confidence, observerConfirmed, radarConfirmed);
        var response = _responseWorkflow.Select(threat, classification, timeToImpactSeconds);

        return _adjudicationLogic.Evaluate(threat, detection, classification, response);
    }
}
