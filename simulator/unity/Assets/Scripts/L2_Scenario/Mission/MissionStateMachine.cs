using System;

namespace AeroVeda.Scenario;

public enum MissionState
{
    NotStarted,
    Active,
    ThreatDetected,
    ResponsePending,
    Completed,
    Failed
}

public sealed class MissionStateMachine
{
    public event Action<MissionState> StateChanged;

    public MissionState CurrentState { get; private set; } = MissionState.NotStarted;

    public void TransitionTo(MissionState nextState)
    {
        if (nextState == CurrentState)
        {
            return;
        }

        if (!IsValidTransition(CurrentState, nextState))
        {
            throw new InvalidOperationException($"Illegal mission transition: {CurrentState} -> {nextState}");
        }

        CurrentState = nextState;
        StateChanged?.Invoke(CurrentState);
    }

    private static bool IsValidTransition(MissionState current, MissionState next)
    {
        return current switch
        {
            MissionState.NotStarted => next == MissionState.Active || next == MissionState.Failed,
            MissionState.Active => next == MissionState.ThreatDetected || next == MissionState.Completed || next == MissionState.Failed,
            MissionState.ThreatDetected => next == MissionState.ResponsePending || next == MissionState.Completed || next == MissionState.Failed,
            MissionState.ResponsePending => next == MissionState.Completed || next == MissionState.Failed,
            MissionState.Completed => false,
            MissionState.Failed => false,
            _ => false
        };
    }
}
