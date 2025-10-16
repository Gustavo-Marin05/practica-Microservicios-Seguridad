using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using UsersService.Data;
using UsersService.Services;

var builder = WebApplication.CreateBuilder(args);

// Forzar el puerto 80
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(80);
});

// CONEXIÓN FORZADA
var connectionString = "Host=db-users;Port=5432;Database=usersdb;Username=myuser;Password=mypassword";

builder.Services.AddDbContext<UsersDbContext>(options =>
    options.UseNpgsql(connectionString)
);

// JWT config hardcodeado
var jwtSecret = "eyJzZWNyZXRrZXkiOiJTdXBlclNlY3JldDEyMyEhQCMiLCJhbGciOiJIUzI1NiJ9";
var issuer = "users-service";
var audience = "users-service-clients";
var keyBytes = Encoding.UTF8.GetBytes(jwtSecret);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.RequireHttpsMetadata = false;
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

// Ejecutar migraciones y seed admin
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<UsersDbContext>();
    
    Console.WriteLine("Aplicando migraciones...");
    db.Database.Migrate();
    Console.WriteLine("Migraciones aplicadas.");

    if (!db.Users.Any(u => u.Email == "admin@example.com"))
    {
        Console.WriteLine("Creando usuario admin...");
        db.Users.Add(new UsersService.Models.User
        {
            Email = "admin@example.com",
            Names = "System",                   
            Surnames = "Administrator",          
            PhoneNumber = "+1-555-0100",        
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
            Role = "admin"
        });
        db.SaveChanges();
        Console.WriteLine("Usuario admin creado.");
    }
}

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();