using UnityEngine;

namespace AeroVeda.Content;

[CreateAssetMenu(fileName = "ThreatDefinition", menuName = "AeroVeda/Threat Definition")]
public class ThreatDefinition : ScriptableObject
{
    [SerializeField] private string threatId;
    [SerializeField] private string displayName;
    [SerializeField] private ThreatCategory category;
    [SerializeField] private ThreatBehavior behavior;
    [SerializeField] private float detectionDifficulty;
    [SerializeField] private float riskScore;
    [SerializeField] private bool isHostile;
    [SerializeField] private string[] tags;

    public string ThreatId => threatId;
    public string DisplayName => displayName;
    public ThreatCategory Category => category;
    public ThreatBehavior Behavior => behavior;
    public float DetectionDifficulty => detectionDifficulty;
    public float RiskScore => riskScore;
    public bool IsHostile => isHostile;
    public string[] Tags => tags;
}

public enum ThreatCategory
{
    ReconUAV,
    FPVAttackDrone,
    FixedWingUAV,
    SwarmNode,
    InterceptorDrone,
    HumanIntruder,
    VehicleThreat
}

public enum ThreatBehavior
{
    Surveillance,
    Assault,
    Coordinated,
    Loitering,
    Intrusion
}
