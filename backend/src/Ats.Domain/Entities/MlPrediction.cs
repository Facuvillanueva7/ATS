namespace Ats.Domain.Entities;

public class MlPrediction
{
    public Guid Id { get; set; }
    public Guid CandidateId { get; set; }
    public Guid JobId { get; set; }
    public string ModelName { get; set; } = string.Empty;
    public string Version { get; set; } = "v1";
    public double Yhat { get; set; }
    public string FeaturesJson { get; set; } = "{}";
    public string ShapTopFactorsJson { get; set; } = "[]";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
