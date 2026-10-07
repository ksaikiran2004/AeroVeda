using UnityEngine;

/// <summary>Moves the attacker from its launch point to B and reports interception.</summary>
public sealed class AttackerDroneAI : MonoBehaviour
{
    public enum FlightState
    {
        EnRoute,
        Intercepted,
        ReachedDestination
    }

    [SerializeField] private float flightSpeed = 10f;
    [SerializeField] private float interceptRadius = 5f;
    [SerializeField] private Transform interceptor;
    [SerializeField] private Transform[] propellers;
    [SerializeField] private float propellerSpeed = 2500f;

    private Vector3 destination;
    private Rigidbody body;

    public FlightState State { get; private set; } = FlightState.EnRoute;
    public Vector3 Destination => destination;

    public void Initialize(Vector3 target, Transform player, Transform[] rotors, float speed, float radius, float rotorSpeed)
    {
        destination = target;
        interceptor = player;
        propellers = rotors;
        flightSpeed = speed;
        interceptRadius = radius;
        propellerSpeed = rotorSpeed;
        body = GetComponent<Rigidbody>();
        if (body != null)
        {
            body.linearVelocity = Vector3.zero;
            body.angularVelocity = Vector3.zero;
            body.useGravity = false;
            body.isKinematic = true;
        }
    }

    private void FixedUpdate()
    {
        if (State == FlightState.Intercepted)
            return;

        // Keep checking proximity at B as well as in flight so the interceptor can
        // complete the mission even if the attacker reaches its destination first.
        if (interceptor != null && Vector3.Distance(transform.position, interceptor.position) <= interceptRadius)
        {
            State = FlightState.Intercepted;
            return;
        }

        if (State != FlightState.EnRoute)
            return;

        Vector3 toTarget = destination - transform.position;
        if (toTarget.sqrMagnitude <= 1f)
        {
            transform.position = destination;
            State = FlightState.ReachedDestination;
            return;
        }

        Vector3 direction = toTarget.normalized;
        transform.position = Vector3.MoveTowards(transform.position, destination, flightSpeed * Time.fixedDeltaTime);
        transform.rotation = Quaternion.LookRotation(direction, Vector3.up);
    }

    private void Update()
    {
        if (State != FlightState.EnRoute || propellers == null)
            return;

        for (int i = 0; i < propellers.Length; i++)
        {
            if (propellers[i] == null)
                continue;

            float direction = (i == 0 || i == 3) ? 1f : -1f;
            propellers[i].Rotate(Vector3.up, direction * propellerSpeed * Time.deltaTime);
        }
    }
}
