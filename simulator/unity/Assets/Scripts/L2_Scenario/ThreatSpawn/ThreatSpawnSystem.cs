using System.Collections.Generic;
using AeroVeda.Content;

namespace AeroVeda.Scenario;

public sealed class ThreatSpawnSystem
{
    private readonly Queue<ThreatDefinition> _spawnQueue = new();
    private readonly List<ThreatDefinition> _resolvedThreats = new();
    private float _spawnTimer;

    public bool AllThreatsResolved => _spawnQueue.Count == 0 && _resolvedThreats.Count > 0;

    public void Enqueue(ThreatDefinition threat)
    {
        if (threat == null)
        {
            return;
        }

        _spawnQueue.Enqueue(threat);
    }

    public void Reset()
    {
        _spawnQueue.Clear();
        _resolvedThreats.Clear();
        _spawnTimer = 0f;
    }

    public void Tick(float deltaTime)
    {
        _spawnTimer += deltaTime;

        if (_spawnQueue.Count > 0 && _spawnTimer >= 2f)
        {
            var threat = _spawnQueue.Dequeue();
            _resolvedThreats.Add(threat);
            _spawnTimer = 0f;
        }
    }
}
