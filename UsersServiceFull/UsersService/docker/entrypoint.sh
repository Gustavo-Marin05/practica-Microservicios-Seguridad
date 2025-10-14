#!/bin/sh
set -e

echo "Esperando a que PostgreSQL esté listo..."

# Esperar a que el puerto esté disponible
until nc -z db 5432; do
  echo "PostgreSQL no está listo todavía... esperando"
  sleep 2
done

echo "PostgreSQL está listo! Iniciando aplicación..."
exec dotnet UsersService.dll