namespace Ats.Domain.Entities;

public class Offer
{
    public Guid Id { get; set; }
    public Guid ApplicationId { get; set; }
    public Application Application { get; set; } = default!;
    public string AmountCurrency { get; set; } = "USD";
    public decimal AmountValue { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? AcceptedAt { get; set; }
    public string Status { get; set; } = "pending";
}
