using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using UsersService.Data;
using UsersService.Services;

var builder = WebApplication.CreateBuilder(args);
var configuration = builder.Configuration;

// Connection string from env or fallback
var connectionString = configuration["CONNECTION_STRING"] ?? "Host=localhost;Port=5432;Database=usersdb;Username=myuser;Password=mypassword";
builder.Services.AddDbContext<UsersDbContext>(options =>
    options.UseNpgsql(connectionString)
);

// JWT config
var jwtSecret = configuration["JWT_SECRET"] ?? throw new Exception("JWT_SECRET is required");
var issuer = configuration["JWT_ISSUER"] ?? "users-service";
var audience = configuration["JWT_AUDIENCE"] ?? "users-service-clients";
var keyBytes = Encoding.UTF8.GetBytes(jwtSecret);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.RequireHttpsMetadata = false; // dev only
    options.SaveToken = true;
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = issuer,
        ValidAudience = audience,
        IssuerSigningKey = new SymmetricSecurityKey(keyBytes),
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();
builder.Services.AddSingleton<JwtTokenService>();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();


var app = builder.Build();

// Run migrations on startup (dev convenience)
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<UsersDbContext>();
    db.Database.Migrate();

    // Seed admin if not exists (opcional)
    if (!db.Users.Any(u => u.Email == "admin@example.com"))
    {
        db.Users.Add(new UsersService.Models.User
        {
            Email = "admin@example.com",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
            Role = "admin"
        });
        db.SaveChanges();
    }
}



app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
