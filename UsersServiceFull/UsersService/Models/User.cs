using System;
using System.ComponentModel.DataAnnotations;

namespace UsersService.Models
{
    public class User
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        [MaxLength(256)]
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
        public string PasswordHash { get; set; }

        [Required]
        [MaxLength(50)]
        public string Role { get; set; } = "user";

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
