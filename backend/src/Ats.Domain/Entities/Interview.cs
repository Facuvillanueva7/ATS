namespace Ats.Domain.Entities;

public class Interview
{
    public Guid Id { get; set; }
    public Guid ApplicationId { get; set; }
    public Application Application { get; set; } = default!;
    public string InterviewType { get; set; } = string.Empty;
    public string Interviewer { get; set; } = string.Empty;
    public DateTime ScheduledAt { get; set; }
    public int DurationMin { get; set; }
    public string? FeedbackJson { get; set; }
    public string? OverallRecommendation { get; set; }
}
