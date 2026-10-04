using System.Collections.Generic;

namespace AeroVeda.Content;

public interface IThreatLibrary
{
    ThreatDefinition GetById(string id);
    IEnumerable<ThreatDefinition> GetAll();
}

public sealed class ThreatLibrary : IThreatLibrary
{
    private readonly Dictionary<string, ThreatDefinition> _lookup = new();

    public void Load(IEnumerable<ThreatDefinition> definitions)
    {
        _lookup.Clear();

        foreach (var definition in definitions)
        {
            if (definition == null || string.IsNullOrWhiteSpace(definition.ThreatId))
            {
                continue;
            }

            _lookup[definition.ThreatId] = definition;
        }
    }

    public ThreatDefinition GetById(string id)
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            return null;
        }

        return _lookup.TryGetValue(id, out var item) ? item : null;
    }

    public IEnumerable<ThreatDefinition> GetAll()
    {
        return _lookup.Values;
    }
}
