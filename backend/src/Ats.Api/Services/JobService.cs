using Ats.Api.Models;
using Ats.Domain.Entities;
using Ats.Domain.Enums;
using Ats.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Ats.Api.Services;

public class JobService
{
    private readonly AppDbContext _db;
    private readonly ILogger<JobService> _logger;

    public JobService(AppDbContext db, ILogger<JobService> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<IReadOnlyList<JobResponse>> GetJobsAsync(JobsQuery query, CancellationToken ct)
    {
        var jobs = _db.Jobs.AsNoTracking();

        if (!string.IsNullOrEmpty(query.Status) && Enum.TryParse<JobStatus>(query.Status, true, out var status))
        {
            jobs = jobs.Where(j => j.Status == status);
        }

        if (!string.IsNullOrEmpty(query.Team))
        {
            jobs = jobs.Where(j => j.Team == query.Team);
        }

        if (!string.IsNullOrEmpty(query.Owner))
        {
            if (Guid.TryParse(query.Owner, out var ownerId))
            {
                jobs = jobs.Where(j => j.RecruiterOwnerUserId == ownerId || j.HmOwnerUserId == ownerId);
            }
        }

        if (!string.IsNullOrEmpty(query.Priority) && Enum.TryParse<JobPriority>(query.Priority, true, out var priority))
        {
            jobs = jobs.Where(j => j.Priority == priority);
        }

        var now = DateTime.UtcNow;
        var list = await jobs.Select(job => new JobResponse(
            job.Id,
            job.Title,
            job.Team,
            job.HiringManager,
            job.Status,
            job.Priority,
            job.HeadcountRequested,
            job.HeadcountFilled,
            job.HeadcountRequested - job.HeadcountFilled,
            EF.Functions.DateDiffDay(job.CreatedAt, now),
            job.SlaDays != null && EF.Functions.DateDiffDay(job.CreatedAt, now) > job.SlaDays
        )).ToListAsync(ct);

        return list;
    }

    public async Task<JobOverviewResponse?> GetOverviewAsync(Guid jobId, CancellationToken ct)
    {
        var job = await _db.Jobs.AsNoTracking().FirstOrDefaultAsync(j => j.Id == jobId, ct);
        if (job is null)
        {
            return null;
        }

        var funnel = await _db.Applications
            .Where(a => a.JobId == jobId)
            .GroupBy(a => a.Stage)
            .Select(g => new { Stage = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.Stage.ToString().ToLowerInvariant(), x => x.Count, ct);

        var topReasons = await _db.Applications
            .Where(a => a.JobId == jobId && a.DecisionReason != null)
            .OrderByDescending(a => a.StageUpdatedAt)
            .Select(a => a.DecisionReason!)
            .Take(5)
            .ToListAsync(ct);

        var avgTime = await _db.Applications
            .Where(a => a.JobId == jobId)
            .GroupBy(a => a.Stage)
            .Select(g => new StageTimeMetric(g.Key.ToString().ToLowerInvariant(),
                g.Average(a => EF.Functions.DateDiffDay(a.StageUpdatedAt, DateTime.UtcNow))))
            .ToListAsync(ct);

        var jobResponse = new JobResponse(
            job.Id,
            job.Title,
            job.Team,
            job.HiringManager,
            job.Status,
            job.Priority,
            job.HeadcountRequested,
            job.HeadcountFilled,
            job.HeadcountRequested - job.HeadcountFilled,
            EF.Functions.DateDiffDay(job.CreatedAt, DateTime.UtcNow),
            job.SlaDays != null && EF.Functions.DateDiffDay(job.CreatedAt, DateTime.UtcNow) > job.SlaDays
        );

        return new JobOverviewResponse(jobResponse, funnel, topReasons, avgTime);
    }

    public async Task<Application?> LinkCandidateAsync(Guid jobId, Guid candidateId, CancellationToken ct)
    {
        var job = await _db.Jobs.FirstOrDefaultAsync(j => j.Id == jobId, ct);
        if (job is null)
        {
            throw new InvalidOperationException("Job not found");
        }

        var candidate = await _db.Candidates.FirstOrDefaultAsync(c => c.Id == candidateId, ct);
        if (candidate is null)
        {
            throw new InvalidOperationException("Candidate not found");
        }

        var existing = await _db.Applications.FirstOrDefaultAsync(a => a.JobId == jobId && a.CandidateId == candidateId, ct);
        if (existing != null)
        {
            return existing;
        }

        var application = new Application
        {
            Id = Guid.NewGuid(),
            CandidateId = candidateId,
            JobId = jobId,
            Stage = ApplicationStage.Screen,
            StageUpdatedAt = DateTime.UtcNow
        };

        await _db.Applications.AddAsync(application, ct);
        await _db.SaveChangesAsync(ct);
        return application;
    }

    public async Task<Application?> AdvanceStageAsync(Guid applicationId, ApplicationStage toStage, string? reason, CancellationToken ct)
    {
        var application = await _db.Applications.FirstOrDefaultAsync(a => a.Id == applicationId, ct);
        if (application is null)
        {
            return null;
        }

        application.Stage = toStage;
        application.StageUpdatedAt = DateTime.UtcNow;
        if (!string.IsNullOrWhiteSpace(reason))
        {
            application.DecisionReason = reason;
        }

        await _db.SaveChangesAsync(ct);
        return application;
    }
}
