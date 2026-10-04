namespace AeroVeda.Evaluation.Adjudication;

public interface IAdjudicationManager
{
    AdjudicationResult EvaluateThreat(
        AeroVeda.Content.ThreatDefinition threat,
        float sensorQuality,
        float operatorAlertness,
        float rangeToThreat,
        bool observerConfirmed,
        bool radarConfirmed,
        float timeToImpactSeconds);
}
