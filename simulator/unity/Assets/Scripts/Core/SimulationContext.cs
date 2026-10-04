using System;
using UnityEngine;

namespace AeroVeda.Core;

public interface IAppLifecycle
{
    void Initialize();
    void Tick(float deltaTime);
    void Shutdown();
}

public interface IEventBus
{
    void Publish<T>(T payload);
    void Subscribe<T>(Action<T> handler);
    void Unsubscribe<T>(Action<T> handler);
}

public sealed class SimulationContext : IAppLifecycle
{
    private readonly IEventBus _eventBus;

    public SimulationContext(IEventBus eventBus)
    {
        _eventBus = eventBus ?? throw new ArgumentNullException(nameof(eventBus));
    }

    public IEventBus EventBus => _eventBus;

    public void Initialize()
    {
        Debug.Log("AeroVeda simulation initialized.");
    }

    public void Tick(float deltaTime)
    {
        // Used by the simulation loop for per-frame update logic.
    }

    public void Shutdown()
    {
        Debug.Log("AeroVeda simulation shutdown.");
    }
}
