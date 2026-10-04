using UnityEngine;
using AeroVeda.Content;

namespace AeroVeda.Entities;

public sealed class ThreatEntity : BaseEntity
{
    [SerializeField] private ThreatDefinition threatDefinition;

    public ThreatDefinition ThreatDefinition => threatDefinition;

    public void Initialize(ThreatDefinition definition)
    {
        if (definition == null)
        {
            Debug.LogWarning("ThreatEntity initialized with null ThreatDefinition.");
            return;
        }

        threatDefinition = definition;
        Name = definition.DisplayName;
        Type = EntityType.Threat;
    }
}
