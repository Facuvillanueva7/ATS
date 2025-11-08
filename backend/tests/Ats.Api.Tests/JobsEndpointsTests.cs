using System.Net.Http.Json;
using System.Linq;
using Ats.Api.Models;
using Ats.Domain.Enums;
using Ats.Infrastructure.Data;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace Ats.Api.Tests;

public class JobsEndpointsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public JobsEndpointsTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                var descriptor = services.SingleOrDefault(d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("jobs-tests"));
            });
        });
    }

    [Fact]
    public async Task ListJobs_ReturnsSuccess()
    {
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        db.Jobs.Add(new Domain.Entities.Job
        {
            Id = Guid.NewGuid(),
            Title = "Backend Engineer",
            Status = JobStatus.Open,
            Priority = JobPriority.High
        });
        await db.SaveChangesAsync();

        var client = _factory.CreateClient();
        var response = await client.GetAsync("/api/jobs");
        response.EnsureSuccessStatusCode();
        var jobs = await response.Content.ReadFromJsonAsync<IEnumerable<JobResponse>>();
        jobs.Should().NotBeNull();
        jobs!.Should().HaveCount(1);
    }

    [Fact]
    public async Task LinkCandidate_PreventsDuplicates()
    {
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var job = new Domain.Entities.Job { Id = Guid.NewGuid(), Title = "Data Scientist" };
        var candidate = new Domain.Entities.Candidate { Id = Guid.NewGuid(), Name = "Jane Doe", Email = "jane@example.com" };
        db.Jobs.Add(job);
        db.Candidates.Add(candidate);
        await db.SaveChangesAsync();

        var client = _factory.CreateClient();
        var request = new LinkCandidateRequest(candidate.Id);
        var first = await client.PostAsJsonAsync($"/api/jobs/{job.Id}/candidates/link", request);
        first.EnsureSuccessStatusCode();
        var second = await client.PostAsJsonAsync($"/api/jobs/{job.Id}/candidates/link", request);
        second.EnsureSuccessStatusCode();
        var apps = db.Applications.Where(a => a.JobId == job.Id && a.CandidateId == candidate.Id).ToList();
        apps.Should().HaveCount(1);
    }
}
