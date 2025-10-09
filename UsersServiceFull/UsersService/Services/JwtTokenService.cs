using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace UsersService.Services
{
    public class JwtTokenService
    {
        private readonly string _secret;
        private readonly string _issuer;
        private readonly string _audience;
        private readonly int _expiresMinutes;

        public JwtTokenService()
        {
            // Hardcodeado para el lab - mismo secret que en Program.cs
            _secret = "eyJzZWNyZXRrZXkiOiJTdXBlclNlY3JldDEyMyEhQCMiLCJhbGciOiJIUzI1NiJ9";
            _issuer = "users-service";
            _audience = "users-service-clients";
            _expiresMinutes = 60;
        }

        public string GenerateToken(Guid userId, string role)
        {
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secret));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var claims = new[]
            {
                new Claim(JwtRegisteredClaimNames.Sub, userId.ToString()),
                new Claim(ClaimTypes.Role, role),
                new Claim("role", role),
                new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
            };

            var token = new JwtSecurityToken(
                issuer: _issuer,
                audience: _audience,
                claims: claims,
                expires: DateTime.UtcNow.AddMinutes(_expiresMinutes),
                signingCredentials: creds
            );

            return new JwtSecurityTokenHandler().WriteToken(token);
        }
    }
}