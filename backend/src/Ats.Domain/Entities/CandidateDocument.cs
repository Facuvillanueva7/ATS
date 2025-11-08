namespace Ats.Domain.Entities;

public class CandidateDocument
{
    public Guid Id { get; set; }
    public Guid CandidateId { get; set; }
    public Candidate Candidate { get; set; } = default!;
    public string BlobUrl { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string MimeType { get; set; } = string.Empty;
    public string Sha256 { get; set; } = string.Empty;
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
}
