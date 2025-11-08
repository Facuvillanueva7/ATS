namespace Ats.Domain.Entities;

public class EventAudit
{
    public Guid Id { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public Guid? ActorUserId { get; set; }
    public string Entity { get; set; } = string.Empty;
    public Guid EntityId { get; set; }
    public string Action { get; set; } = string.Empty;
    public string DiffJson { get; set; } = "{}";
    public string? Ip { get; set; }
}
