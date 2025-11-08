namespace Ats.Domain.Entities;

public class JobSource
{
    public Guid Id { get; set; }
    public Guid JobId { get; set; }
    public Job Job { get; set; } = default!;
    public string SourceName { get; set; } = string.Empty;
    public string? SourceRef { get; set; }
}
