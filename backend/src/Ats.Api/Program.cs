using System.Text.Json.Serialization;
using Ats.Api.Endpoints;
using Ats.Api.Services;
using Ats.Api.Validators;
using Ats.Infrastructure.Data;
using FluentValidation;
using FluentValidation.AspNetCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseSerilog((context, config) =>
{
    config.ReadFrom.Configuration(context.Configuration).WriteTo.Console();
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "ATS API",
        Version = "v1",
        Description = "Enterprise ATS API"
    });
    options.AddSecurityDefinition("oauth2", new OpenApiSecurityScheme
    {
        Type = SecuritySchemeType.OAuth2,
        Flows = new OpenApiOAuthFlows
        {
            AuthorizationCode = new OpenApiOAuthFlow
            {
                AuthorizationUrl = new Uri("https://example.com/auth"),
                TokenUrl = new Uri("https://example.com/token"),
                Scopes = new Dictionary<string, string> { { "api", "Access ATS API" } }
            }
        }
    });
    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme { Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "oauth2" } },
            new[] { "api" }
        }
    });
});

builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
}).AddJwtBearer(options =>
{
    options.Authority = builder.Configuration["Auth:Authority"] ?? "https://example.com";
    options.Audience = builder.Configuration["Auth:Audience"] ?? "ats-api";
});

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("RequireRecruiter", policy => policy.RequireRole("Recruiter", "Admin"));
});

builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<LinkCandidateRequestValidator>();

builder.Services.AddDbContext<AppDbContext>(options =>
{
    var connectionString = builder.Configuration.GetConnectionString("SqlServer") ?? "Server=localhost,1433;Database=ats;User Id=sa;Password=Your_password123;TrustServerCertificate=True";
    options.UseSqlServer(connectionString);
});

builder.Services.AddScoped<JobService>();

builder.Services.AddHealthChecks().AddSqlServer(builder.Configuration.GetConnectionString("SqlServer") ?? string.Empty, name: "sqlserver");

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.Converters.Add(new JsonStringEnumConverter());
});

var app = builder.Build();

app.UseSerilogRequestLogging();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapHealthChecks("/health");
app.MapHealthChecks("/readiness");

app.MapJobsEndpoints();
app.MapApplicationsEndpoints();

app.Run();

public partial class Program { }
