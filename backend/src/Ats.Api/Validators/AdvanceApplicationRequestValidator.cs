using Ats.Api.Models;
using Ats.Domain.Enums;
using FluentValidation;

namespace Ats.Api.Validators;

public class AdvanceApplicationRequestValidator : AbstractValidator<AdvanceApplicationRequest>
{
    public AdvanceApplicationRequestValidator()
    {
        RuleFor(x => x.ToStage).NotEmpty().Must(BeValidStage).WithMessage("Invalid stage");
        RuleFor(x => x.Reason).MaximumLength(500);
    }

    private bool BeValidStage(string stage)
    {
        return Enum.TryParse<ApplicationStage>(stage, true, out _);
    }
}
