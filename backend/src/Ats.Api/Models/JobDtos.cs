using Ats.Domain.Enums;

namespace Ats.Api.Models;

public record JobResponse(Guid Id, string Title, string? Team, string? HiringManager, JobStatus Status, JobPriority Priority, int HeadcountRequested, int HeadcountFilled, int OpeningsRemaining, int AgeDays, bool SlaBreach);

public record JobOverviewResponse(JobResponse Job, IDictionary<string, int> Funnel, IEnumerable<string> TopReasonsRejection, IEnumerable<StageTimeMetric> AvgTimeInStage);

public record StageTimeMetric(string Stage, double Days);

public record LinkCandidateRequest(Guid CandidateId);

public record AdvanceApplicationRequest(string ToStage, string? Reason);

public record JobsQuery(string? Status, string? Team, string? Owner, string? Priority);
