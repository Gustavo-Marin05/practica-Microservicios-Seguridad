// DTOs/UserDto.cs
using System;

namespace UsersService.DTOs
{
    public record UserDto(Guid Id, string Email, string Role, DateTime CreatedAt);
}
