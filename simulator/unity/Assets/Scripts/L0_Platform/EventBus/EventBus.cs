using System;
using System.Collections.Generic;

namespace AeroVeda.Platform;

public interface IEventBus
{
    void Publish<T>(T payload);
    void Subscribe<T>(Action<T> handler);
    void Unsubscribe<T>(Action<T> handler);
}

public sealed class EventBus : AeroVeda.Core.IEventBus
{
    private readonly Dictionary<Type, Delegate> _handlers = new();

    public void Publish<T>(T payload)
    {
        if (_handlers.TryGetValue(typeof(T), out var handler))
        {
            ((Action<T>)handler)?.Invoke(payload);
        }
    }

    public void Subscribe<T>(Action<T> handler)
    {
        if (_handlers.TryGetValue(typeof(T), out var currentHandler))
        {
            _handlers[typeof(T)] = (Action<T>)currentHandler + handler;
        }
        else
        {
            _handlers[typeof(T)] = handler;
        }
    }

    public void Unsubscribe<T>(Action<T> handler)
    {
        if (_handlers.TryGetValue(typeof(T), out var currentHandler))
        {
            _handlers[typeof(T)] = ((Action<T>)currentHandler) - handler;
        }
    }
}
