namespace Ats.Domain.Entities;

public class Embedding
{
    public Guid Id { get; set; }
    public string OwnerType { get; set; } = string.Empty;
    public Guid OwnerId { get; set; }
    public float[] Vector { get; set; } = Array.Empty<float>();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
