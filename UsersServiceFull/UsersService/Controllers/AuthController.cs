// Controllers/AuthController.cs
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using UsersService.Data;
using UsersService.DTOs;
using UsersService.Models;
using UsersService.Services;

namespace UsersService.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly UsersDbContext _db;
        private readonly JwtTokenService _jwt;

        public AuthController(UsersDbContext db, JwtTokenService jwt)
        {
            _db = db;
            _jwt = jwt;
        }

        [HttpPost("signup")]
        public async Task<IActionResult> Signup([FromBody] SignupRequest req)
        {
            if (await _db.Users.AnyAsync(u => u.Email == req.Email))
                return Conflict(new { message = "Email already registered" });

            var user = new User
            {
                Email = req.Email,
                Names = req.Names,                    // ADD THIS
                Surnames = req.Surnames,              // ADD THIS
                PhoneNumber = req.PhoneNumber,        // ADD THIS
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.Password),
                Role = string.IsNullOrWhiteSpace(req.Role) ? "user" : req.Role
            };

            _db.Users.Add(user);
            await _db.SaveChangesAsync();

            var dto = new UserDto(user.Id, user.Email, user.Role, user.CreatedAt);
            return CreatedAtAction(nameof(Signin), new { id = user.Id }, dto);
        }

        [HttpPost("signin")]
        public async Task<IActionResult> Signin([FromBody] SigninRequest req)
        {
            var user = await _db.Users.SingleOrDefaultAsync(u => u.Email == req.Email);
            if (user == null) return Unauthorized(new { message = "Invalid credentials" });

            if (!BCrypt.Net.BCrypt.Verify(req.Password, user.PasswordHash))
                return Unauthorized(new { message = "Invalid credentials" });

            var token = _jwt.GenerateToken(user.Id, user.Role);
            return Ok(new { token });
        }
    }
}