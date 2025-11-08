namespace Ats.Domain.Entities;

public class JobTag
{
    public Guid Id { get; set; }
    public Guid JobId { get; set; }
    public Job Job { get; set; } = default!;
    public string Tag { get; set; } = string.Empty;
}
