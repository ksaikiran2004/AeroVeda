using UnityEngine;

namespace AeroVeda.Scenario;

[CreateAssetMenu(fileName = "ScenarioDefinition", menuName = "AeroVeda/Scenario Definition")]
public class ScenarioDefinition : ScriptableObject
{
    [SerializeField] private string scenarioId;
    [SerializeField] private string displayName;
    [SerializeField] private string environment;
    [SerializeField] private string objective;
    [SerializeField] private float timeLimitSeconds;

    public string ScenarioId => scenarioId;
    public string DisplayName => displayName;
    public string Environment => environment;
    public string Objective => objective;
    public float TimeLimitSeconds => timeLimitSeconds;
}
