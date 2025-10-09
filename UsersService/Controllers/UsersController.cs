using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using UsersService.Data;
using UsersService.DTOs;

namespace UsersService.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        private readonly UsersDbContext _db;

        public UsersController(UsersDbContext db)
        {
            _db = db;
        }

        [HttpGet]
        [Authorize(Roles = "user,admin")]
        public async Task<IActionResult> GetAll()
        {
            var users = await _db.Users.Select(u => new UserDto(u.Id, u.Email, u.Role, u.CreatedAt)).ToListAsync();
            return Ok(users);
        }

        [HttpGet("{id}")]
        [Authorize(Roles = "user,admin")]
        public async Task<IActionResult> GetById(Guid id)
        {
            var u = await _db.Users.FindAsync(id);
            if (u == null) return NotFound();
            return Ok(new UserDto(u.Id, u.Email, u.Role, u.CreatedAt));
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "admin")]
        public async Task<IActionResult> Update(Guid id, [FromBody] SignupRequest req)
        {
            var u = await _db.Users.FindAsync(id);
            if (u == null) return NotFound();

            u.Email = req.Email ?? u.Email;
            if (!string.IsNullOrWhiteSpace(req.Password))
                u.PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.Password);
            u.Role = string.IsNullOrWhiteSpace(req.Role) ? u.Role : req.Role;

            await _db.SaveChangesAsync();
            return NoContent();
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "admin")]
        public async Task<IActionResult> Delete(Guid id)
        {
            var u = await _db.Users.FindAsync(id);
            if (u == null) return NotFound();
            _db.Users.Remove(u);
            await _db.SaveChangesAsync();
            return NoContent();
        }
    }
}
