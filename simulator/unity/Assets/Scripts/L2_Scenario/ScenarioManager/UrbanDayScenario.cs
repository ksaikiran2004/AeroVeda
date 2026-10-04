using System.Collections.Generic;

namespace AeroVeda.Scenario;

public sealed class UrbanDayScenario
{
    public string ScenarioId => "urban-day-counter-uav";
    public string DisplayName => "Urban Day Counter-UAS";
    public string Environment => "Urban corridor";
    public string Objective => "Detect, classify, and neutralize hostile airborne threats while protecting civilians and infrastructure.";
    public IReadOnlyList<string> ThreatIds => new[] { "recon-uav", "fpv-drone" };
}
