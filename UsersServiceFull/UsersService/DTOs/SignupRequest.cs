using System.ComponentModel.DataAnnotations;

namespace UsersService.DTOs
{
    public class SignupRequest
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        [MaxLength(100)]
        public string Names { get; set; }

        [Required]
        [MaxLength(100)]
        public string Surnames { get; set; }

        [Required]
        [MaxLength(20)]
        public string PhoneNumber { get; set; }

        [Required]
        [MinLength(6)]
        public string Password { get; set; }

        // Opcionalmente permitir role (por seguridad dejar "user" por defecto en producción)
        public string Role { get; set; } = "user";
    }
}
