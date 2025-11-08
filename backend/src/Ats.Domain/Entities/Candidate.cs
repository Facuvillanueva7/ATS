namespace Ats.Domain.Entities;

public class Candidate
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public string? Location { get; set; }
    public string? Seniority { get; set; }
    public string? EnglishLevel { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public string? Source { get; set; }
    public string? NotesPiiRedacted { get; set; }
    public ICollection<CandidateDocument> Documents { get; set; } = new List<CandidateDocument>();
    public ICollection<CandidateSkill> Skills { get; set; } = new List<CandidateSkill>();
    public ICollection<Application> Applications { get; set; } = new List<Application>();
}
