namespace Ats.Domain.Entities;

public class ApplicationNote
{
    public Guid Id { get; set; }
    public Guid ApplicationId { get; set; }
    public Application Application { get; set; } = default!;
    public string Author { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
