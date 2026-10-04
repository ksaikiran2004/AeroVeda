using System;
using System.Collections.Generic;
using System.Linq;
using AeroVeda.Content;

namespace AeroVeda.Scenario;

public interface IScenarioManager
{
    void RegisterScenario(ScenarioDefinition scenario);
    ScenarioDefinition GetScenario(string scenarioId);
    IEnumerable<ScenarioDefinition> GetAllScenarios();
    MissionManager CreateMission(string scenarioId, ThreatLibrary threatLibrary);
}

public sealed class ScenarioManager : IScenarioManager
{
    private readonly Dictionary<string, ScenarioDefinition> _scenarios = new();

    public void RegisterScenario(ScenarioDefinition scenario)
    {
        if (scenario == null || string.IsNullOrWhiteSpace(scenario.ScenarioId))
        {
            throw new ArgumentException("Scenario must include an identifier.", nameof(scenario));
        }

        _scenarios[scenario.ScenarioId] = scenario;
    }

    public ScenarioDefinition GetScenario(string scenarioId)
    {
        if (string.IsNullOrWhiteSpace(scenarioId))
        {
            return null;
        }

        return _scenarios.TryGetValue(scenarioId, out var scenario) ? scenario : null;
    }

    public IEnumerable<ScenarioDefinition> GetAllScenarios()
    {
        return _scenarios.Values.ToList();
    }

    public MissionManager CreateMission(string scenarioId, ThreatLibrary threatLibrary)
    {
        var scenario = GetScenario(scenarioId);
        if (scenario == null)
        {
            throw new InvalidOperationException($"Scenario {scenarioId} is not registered.");
        }

        return new MissionManager(scenario, threatLibrary ?? throw new ArgumentNullException(nameof(threatLibrary)));
    }
}
