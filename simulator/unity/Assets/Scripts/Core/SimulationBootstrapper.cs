using UnityEngine;

namespace AeroVeda.Core;

public sealed class SimulationBootstrapper : MonoBehaviour
{
    private SimulationContext _context;

    private void Awake()
    {
        var eventBus = new AeroVeda.Platform.EventBus();
        _context = new SimulationContext(eventBus);
        _context.Initialize();
    }

    private void Update()
    {
        _context?.Tick(Time.deltaTime);
    }

    private void OnDestroy()
    {
        _context?.Shutdown();
    }
}
