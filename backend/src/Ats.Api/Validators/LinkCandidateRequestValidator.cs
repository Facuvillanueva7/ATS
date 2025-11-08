using Ats.Api.Models;
using FluentValidation;

namespace Ats.Api.Validators;

public class LinkCandidateRequestValidator : AbstractValidator<LinkCandidateRequest>
{
    public LinkCandidateRequestValidator()
    {
        RuleFor(x => x.CandidateId).NotEmpty();
    }
}
