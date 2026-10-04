namespace AeroVeda.Entities;

public sealed class FriendlyEntity : BaseEntity
{
    public void SetOperationalRole(string role)
    {
        Name = role;
    }
}
