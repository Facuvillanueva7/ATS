namespace Ats.Domain.Entities;

public class CandidateSkill
{
    public Guid Id { get; set; }
    public Guid CandidateId { get; set; }
    public Candidate Candidate { get; set; } = default!;
    public string Skill { get; set; } = string.Empty;
    public string? NormalizedSkill { get; set; }
    public double? YearsExp { get; set; }
    public DateTime? LastUsed { get; set; }
    public double? Confidence { get; set; }
}
