using Ats.Domain.Enums;

namespace Ats.Domain.Entities;

public class Application
{
    public Guid Id { get; set; }
    public Guid CandidateId { get; set; }
    public Candidate Candidate { get; set; } = default!;
    public Guid JobId { get; set; }
    public Job Job { get; set; } = default!;
    public ApplicationStage Stage { get; set; } = ApplicationStage.Sourced;
    public DateTime StageUpdatedAt { get; set; } = DateTime.UtcNow;
    public double? MatchScore { get; set; }
    public string? DecisionReason { get; set; }
    public Guid? OwnerUserId { get; set; }
    public bool Shortlisted { get; set; }
    public ICollection<ApplicationNote> Notes { get; set; } = new List<ApplicationNote>();
}
