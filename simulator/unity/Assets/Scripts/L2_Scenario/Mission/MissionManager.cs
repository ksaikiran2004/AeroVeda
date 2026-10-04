using System;
using System.Collections.Generic;
using AeroVeda.Content;

namespace AeroVeda.Scenario;

public sealed class MissionManager
{
    private readonly ScenarioDefinition _scenario;
    private readonly ThreatLibrary _threatLibrary;
    private readonly MissionStateMachine _stateMachine = new();
    private readonly ThreatSpawnSystem _spawnSystem = new();
    private readonly List<string> _spawnedThreatIds = new();

    public MissionManager(ScenarioDefinition scenario, ThreatLibrary threatLibrary)
    {
        _scenario = scenario ?? throw new ArgumentNullException(nameof(scenario));
        _threatLibrary = threatLibrary ?? throw new ArgumentNullException(nameof(threatLibrary));
    }

    public MissionState State => _stateMachine.CurrentState;
    public ScenarioDefinition Scenario => _scenario;
    public IReadOnlyList<string> SpawnedThreatIds => _spawnedThreatIds;

    public void Start()
    {
        _stateMachine.TransitionTo(MissionState.Active);
        _spawnSystem.Reset();

        var urbanScenario = new UrbanDayScenario();
        foreach (var threatId in urbanScenario.ThreatIds)
        {
            var definition = _threatLibrary.GetById(threatId);
            if (definition != null)
            {
                _spawnSystem.Enqueue(definition);
                _spawnedThreatIds.Add(definition.ThreatId);
            }
        }
    }

    public void Tick(float deltaTime)
    {
        if (_stateMachine.CurrentState != MissionState.Active)
        {
            return;
        }

        _spawnSystem.Tick(deltaTime);

        if (_spawnSystem.AllThreatsResolved)
        {
            _stateMachine.TransitionTo(MissionState.Completed);
        }
    }

    public void Complete()
    {
        _stateMachine.TransitionTo(MissionState.Completed);
    }
}
