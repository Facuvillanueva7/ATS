using Ats.Domain.Entities;
using Ats.Domain.Enums;
using Microsoft.EntityFrameworkCore;

namespace Ats.Infrastructure.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    public DbSet<Candidate> Candidates => Set<Candidate>();
    public DbSet<CandidateDocument> CandidateDocuments => Set<CandidateDocument>();
    public DbSet<CandidateSkill> CandidateSkills => Set<CandidateSkill>();
    public DbSet<Job> Jobs => Set<Job>();
    public DbSet<JobTag> JobTags => Set<JobTag>();
    public DbSet<JobSource> JobSources => Set<JobSource>();
    public DbSet<Application> Applications => Set<Application>();
    public DbSet<ApplicationNote> ApplicationNotes => Set<ApplicationNote>();
    public DbSet<Interview> Interviews => Set<Interview>();
    public DbSet<Offer> Offers => Set<Offer>();
    public DbSet<User> Users => Set<User>();
    public DbSet<EventAudit> EventsAudit => Set<EventAudit>();
    public DbSet<MlPrediction> MlPredictions => Set<MlPrediction>();
    public DbSet<Setting> Settings => Set<Setting>();
    public DbSet<Embedding> Embeddings => Set<Embedding>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Candidate>(entity =>
        {
            entity.ToTable("candidates");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Name).HasMaxLength(200);
            entity.Property(x => x.Email).HasMaxLength(200);
            entity.Property(x => x.NotesPiiRedacted).HasColumnName("notes_piiredacted");
        });

        modelBuilder.Entity<CandidateDocument>(entity =>
        {
            entity.ToTable("candidate_documents");
            entity.HasKey(x => x.Id);
            entity.HasIndex(x => x.Sha256).IsUnique();
            entity.Property(x => x.BlobUrl).HasMaxLength(500);
            entity.HasOne(x => x.Candidate).WithMany(c => c.Documents).HasForeignKey(x => x.CandidateId);
        });

        modelBuilder.Entity<CandidateSkill>(entity =>
        {
            entity.ToTable("candidate_skills");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Skill).HasMaxLength(200);
            entity.HasOne(x => x.Candidate).WithMany(c => c.Skills).HasForeignKey(x => x.CandidateId);
        });

        modelBuilder.Entity<Job>(entity =>
        {
            entity.ToTable("jobs");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Title).HasMaxLength(200);
            entity.Property(x => x.DescriptionMd).HasColumnName("description_md");
            entity.Property(x => x.MustHaveJson).HasColumnName("must_have_json");
            entity.Property(x => x.NiceToHaveJson).HasColumnName("nice_to_have_json");
            entity.Property(x => x.EnglishReq).HasColumnName("english_req");
            entity.Property(x => x.HeadcountRequested).HasColumnName("headcount_requested");
            entity.Property(x => x.HeadcountFilled).HasColumnName("headcount_filled");
            entity.Property(x => x.TargetHireDate).HasColumnName("target_hire_date");
            entity.Property(x => x.SlaDays).HasColumnName("sla_days");
            entity.Property(x => x.LocationMode).HasConversion<string>().HasColumnName("location_mode");
            entity.Property(x => x.Status).HasConversion<string>().HasColumnName("status");
            entity.Property(x => x.Priority).HasConversion<string>().HasColumnName("priority");
            entity.Property(x => x.RecruiterOwnerUserId).HasColumnName("recruiter_owner_user_id");
            entity.Property(x => x.HmOwnerUserId).HasColumnName("hm_owner_user_id");
            entity.Property(x => x.CreatedAt).HasColumnName("created_at");
            entity.Property(x => x.UpdatedAt).HasColumnName("updated_at");
            entity.HasMany(x => x.Tags).WithOne(x => x.Job).HasForeignKey(x => x.JobId);
            entity.HasMany(x => x.Sources).WithOne(x => x.Job).HasForeignKey(x => x.JobId);
        });

        modelBuilder.Entity<JobTag>(entity =>
        {
            entity.ToTable("job_tags");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<JobSource>(entity =>
        {
            entity.ToTable("job_sources");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<Application>(entity =>
        {
            entity.ToTable("applications");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Stage).HasConversion<string>().HasColumnName("stage");
            entity.Property(x => x.StageUpdatedAt).HasColumnName("stage_updated_at");
            entity.Property(x => x.MatchScore).HasColumnName("match_score");
            entity.Property(x => x.DecisionReason).HasColumnName("decision_reason");
            entity.Property(x => x.OwnerUserId).HasColumnName("owner_user_id");
            entity.Property(x => x.Shortlisted).HasColumnName("shortlisted");
            entity.HasOne(x => x.Candidate).WithMany(c => c.Applications).HasForeignKey(x => x.CandidateId);
            entity.HasOne(x => x.Job).WithMany(j => j.Applications).HasForeignKey(x => x.JobId);
            entity.HasIndex(x => new { x.JobId, x.Stage }).HasDatabaseName("IX_applications_job_stage");
            entity.HasIndex(x => new { x.CandidateId, x.JobId }).IsUnique().HasDatabaseName("IX_applications_cand_job");
        });

        modelBuilder.Entity<ApplicationNote>(entity =>
        {
            entity.ToTable("application_notes");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<Interview>(entity =>
        {
            entity.ToTable("interviews");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<Offer>(entity =>
        {
            entity.ToTable("offers");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<User>(entity =>
        {
            entity.ToTable("users");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Email).HasMaxLength(200);
            entity.Property(x => x.Role).HasMaxLength(50);
        });

        modelBuilder.Entity<EventAudit>(entity =>
        {
            entity.ToTable("events_audit");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<MlPrediction>(entity =>
        {
            entity.ToTable("ml_predictions");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<Setting>(entity =>
        {
            entity.ToTable("settings");
            entity.HasKey(x => x.Id);
        });

        modelBuilder.Entity<Embedding>(entity =>
        {
            entity.ToTable("embeddings");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Vector).HasColumnType("vector(1536)");
        });

        modelBuilder.Entity<JobOverviewView>(entity =>
        {
            entity.HasNoKey().ToView("v_job_openings");
        });

        modelBuilder.Entity<CandidateProfileView>(entity =>
        {
            entity.HasNoKey().ToView("v_candidate_profile");
        });
    }
}

public class JobOverviewView
{
    public Guid JobId { get; set; }
    public int OpeningsRemaining { get; set; }
    public int AgeDays { get; set; }
    public bool SlaBreach { get; set; }
}

public class CandidateProfileView
{
    public Guid CandidateId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Seniority { get; set; }
    public string? EnglishLevel { get; set; }
}
