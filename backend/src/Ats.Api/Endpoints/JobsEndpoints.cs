using Ats.Api.Models;
using Ats.Api.Services;
using Ats.Domain.Enums;
using Ats.Api.Validators;
using FluentValidation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Ats.Api.Endpoints;

public static class JobsEndpoints
{
    public static void MapJobsEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/jobs").RequireAuthorization();

        group.WithTags("Jobs");

        group.MapGet("", async ([FromServices] JobService jobService, [AsParameters] JobsQuery query, CancellationToken ct) =>
        {
            var jobs = await jobService.GetJobsAsync(query, ct);
            return Results.Ok(jobs);
        }).WithName("Jobs_List").WithSummary("List jobs with filters").WithOpenApi();

        group.MapGet("/{id:guid}/overview", async ([FromServices] JobService jobService, Guid id, CancellationToken ct) =>
        {
            var overview = await jobService.GetOverviewAsync(id, ct);
            return overview is null ? Results.NotFound() : Results.Ok(overview);
        }).WithName("Jobs_Overview").WithSummary("Get job overview funnel and KPIs").WithOpenApi();

        group.MapPost("/{id:guid}/candidates/link", async (
            [FromServices] JobService jobService,
            [FromServices] IValidator<LinkCandidateRequest> validator,
            Guid id,
            [FromBody] LinkCandidateRequest request,
            CancellationToken ct) =>
        {
            await validator.ValidateAndThrowAsync(request, ct);
            try
            {
                var application = await jobService.LinkCandidateAsync(id, request.CandidateId, ct);
                return Results.Ok(new { application.Id, application.Stage });
            }
            catch (InvalidOperationException ex)
            {
                return Results.BadRequest(new { error = ex.Message });
            }
        }).WithName("Jobs_LinkCandidate").WithSummary("Link candidate to job").WithOpenApi();
    }

    public static void MapApplicationsEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/applications").RequireAuthorization();
        group.WithTags("Applications");

        group.MapPost("/{id:guid}/advance", async (
            [FromServices] JobService jobService,
            [FromServices] IValidator<AdvanceApplicationRequest> validator,
            Guid id,
            [FromBody] AdvanceApplicationRequest request,
            CancellationToken ct) =>
        {
            await validator.ValidateAndThrowAsync(request, ct);
            var targetStage = Enum.Parse<ApplicationStage>(request.ToStage, true);
            var updated = await jobService.AdvanceStageAsync(id, targetStage, request.Reason, ct);
            return updated is null ? Results.NotFound() : Results.Ok(new { updated.Id, updated.Stage, updated.StageUpdatedAt });
        }).WithName("Applications_Advance").WithSummary("Advance application stage").WithOpenApi();
    }
}
