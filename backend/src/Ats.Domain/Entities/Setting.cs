namespace Ats.Domain.Entities;

public class Setting
{
    public Guid Id { get; set; }
    public string Key { get; set; } = string.Empty;
    public string ValueJson { get; set; } = "{}";
}
