using Ats.Domain.Enums;

namespace Ats.Domain.Entities;

public class Job
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string? Team { get; set; }
    public string? HiringManager { get; set; }
    public string DescriptionMd { get; set; } = string.Empty;
    public string MustHaveJson { get; set; } = "[]";
    public string NiceToHaveJson { get; set; } = "[]";
    public string? EnglishReq { get; set; }
    public JobStatus Status { get; set; } = JobStatus.Draft;
    public JobPriority Priority { get; set; } = JobPriority.Medium;
    public int HeadcountRequested { get; set; } = 1;
    public int HeadcountFilled { get; set; }
    public DateTime? TargetHireDate { get; set; }
    public int? SlaDays { get; set; }
    public LocationMode LocationMode { get; set; } = LocationMode.Hybrid;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public Guid? RecruiterOwnerUserId { get; set; }
    public Guid? HmOwnerUserId { get; set; }
    public ICollection<Application> Applications { get; set; } = new List<Application>();
    public ICollection<JobTag> Tags { get; set; } = new List<JobTag>();
    public ICollection<JobSource> Sources { get; set; } = new List<JobSource>();
}
