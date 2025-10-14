using System.ComponentModel.DataAnnotations;

namespace UsersService.DTOs
{
    public class SignupRequest
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        [MinLength(6)]
        public string Password { get; set; }

        // Opcionalmente permitir role (por seguridad dejar "user" por defecto en producción)
        public string Role { get; set; } = "user";
    }
}
