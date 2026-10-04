using System;
using AeroVeda.Content;

namespace AeroVeda.Evaluation.Adjudication;

public enum ResponseType
{
    Monitor,
    Jam,
    Intercept,
    Kinetic
}

public sealed class ResponseSelectionWorkflow
{
    public ResponseDecision Select(ThreatDefinition threat, ClassificationResult classification, float timeToImpactSeconds)
    {
        if (threat == null)
        {
            throw new ArgumentNullException(nameof(threat));
        }

        if (classification == null)
        {
            throw new ArgumentNullException(nameof(classification));
        }

        var response = ResponseType.Monitor;
        if (threat.Category == ThreatCategory.FPVAttackDrone || threat.Category == ThreatCategory.ReconUAV)
        {
            response = timeToImpactSeconds <= 12f ? ResponseType.Jam : ResponseType.Monitor;
        }
        else if (threat.Category == ThreatCategory.FixedWingUAV || threat.Category == ThreatCategory.SwarmNode)
        {
            response = timeToImpactSeconds <= 15f ? ResponseType.Intercept : ResponseType.Jam;
        }
        else if (threat.Category == ThreatCategory.HumanIntruder || threat.Category == ThreatCategory.VehicleThreat)
        {
            response = ResponseType.Intercept;
        }

        if (classification.IsHostile && response == ResponseType.Monitor && threat.RiskScore >= 75f)
        {
            response = ResponseType.Intercept;
        }

        return new ResponseDecision
        {
            Response = response,
            Confidence = classification.Confidence,
            Justification = $"Selected {response} for {threat.DisplayName} based on category, timing, and hostile confidence."
        };
    }
}

public sealed class ResponseDecision
{
    public ResponseType Response { get; set; }
    public float Confidence { get; set; }
    public string Justification { get; set; }
}
