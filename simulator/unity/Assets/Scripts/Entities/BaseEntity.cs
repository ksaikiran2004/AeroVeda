using UnityEngine;

namespace AeroVeda.Entities;

public enum EntityType
{
    Friendly,
    Threat,
    Sensor,
    Asset,
    Environment
}

public interface IEntity
{
    string Id { get; }
    string Name { get; }
    EntityType Type { get; }
    Vector3 Position { get; set; }
    bool IsActive { get; set; }
}

public abstract class BaseEntity : MonoBehaviour, IEntity
{
    [SerializeField] private string id;
    [SerializeField] private string name;
    [SerializeField] private EntityType type;

    public string Id => id;
    public string Name
    {
        get => name;
        set => name = value;
    }

    public EntityType Type
    {
        get => type;
        protected set => type = value;
    }

    public Vector3 Position
    {
        get => transform.position;
        set => transform.position = value;
    }

    public bool IsActive { get; set; } = true;

    protected virtual void Awake()
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            id = System.Guid.NewGuid().ToString();
        }
    }
}
