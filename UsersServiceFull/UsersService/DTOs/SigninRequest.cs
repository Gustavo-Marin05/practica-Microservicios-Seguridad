using System.ComponentModel.DataAnnotations;

namespace UsersService.DTOs
{
    public class SigninRequest
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        public string Password { get; set; }
    }
}
