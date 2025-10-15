# test_purchases.py - Script para probar el microservicio
import requests
import json

BASE_URL = "http://localhost:5000"

# Primero necesitas un token JWT válido del servicio de usuarios
# Ejemplo de cómo obtenerlo (ajusta según tu servicio de usuarios):
# TOKEN = "tu_jwt_token_aqui"

def test_health():
    """Prueba el endpoint de health"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def test_get_remaining_tickets(event_id):
    """Prueba obtener tickets restantes para un evento"""
    response = requests.get(f"{BASE_URL}/api/purchases/event/{event_id}/remaining")
    print(f"\nTickets restantes para evento {event_id}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_create_purchase(token, event_id, quantity):
    """Prueba crear una compra"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "event_id": event_id,
        "quantity": quantity
    }

    response = requests.post(
        f"{BASE_URL}/api/purchases",
        headers=headers,
        json=data
    )

    print(f"\nCrear compra de {quantity} tickets para evento {event_id}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_get_my_purchases(token):
    """Prueba obtener las compras del usuario autenticado"""
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/api/purchases",
        headers=headers
    )

    print("\nMis compras:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_get_purchase_by_id(token, purchase_id):
    """Prueba obtener una compra específica"""
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/api/purchases/{purchase_id}",
        headers=headers
    )

    print(f"\nCompra {purchase_id}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    print("=== PRUEBAS DEL MICROSERVICIO DE COMPRAS ===\n")

    # 1. Health check
    test_health()

    # 2. Ver tickets restantes (sin autenticación)
    test_get_remaining_tickets(1)

    # Para las siguientes pruebas necesitas un token válido
    # TOKEN = "tu_token_jwt_aqui"
    # test_create_purchase(TOKEN, 1, 2)
    # test_get_my_purchases(TOKEN)

# ==========================================
# API_DOCUMENTATION.md
# ==========================================
"""
# API de Compras de Entradas

## Base URL
`http://localhost:5000`

## Autenticación
Todos los endpoints (excepto `/health` y `/api/purchases/event/:id/remaining`)
requieren un JWT token en el header:
```
Authorization: Bearer <tu_token_jwt>
```

## Endpoints

### 1. Health Check
**GET** `/health`

Verifica que el servicio esté funcionando.

**Respuesta:**
```json
{
  "status": "ok",
  "service": "purchases"
}
```

---

### 2. Obtener Tickets Restantes
**GET** `/api/purchases/event/:event_id/remaining`

Obtiene la cantidad de tickets disponibles para un evento.

**Parámetros:**
- `event_id` (path): ID del evento

**Respuesta:**
```json
{
  "event_id": 1,
  "capacity": 200,
  "remaining": 150,
  "sold": 50
}
```

---

### 3. Crear Compra
**POST** `/api/purchases`

Crea una nueva compra de entradas. Solo usuarios con rol `user` o `admin`.

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Body:**
```json
{
  "event_id": 1,
  "quantity": 5
}
```

**Respuesta exitosa (201):**
```json
{
  "message": "Compra realizada exitosamente",
  "purchase": {
    "id": 1,
    "user_id": "uuid-del-usuario",
    "event_id": 1,
    "quantity": 5,
    "created_at": "2025-10-15T12:00:00+00:00"
  }
}
```

**Errores posibles:**
- `400`: Datos inválidos o cantidad <= 0
- `400`: No hay suficientes entradas disponibles
- `401`: Token inválido o expirado
- `403`: Rol no autorizado
- `404`: Evento no encontrado

---

### 4. Obtener Mis Compras
**GET** `/api/purchases`

Obtiene todas las compras del usuario autenticado (o todas si es admin).

**Headers:**
- `Authorization: Bearer <token>`

**Respuesta:**
```json
[
  {
    "id": 1,
    "user_id": "uuid-del-usuario",
    "event_id": 1,
    "quantity": 5,
    "created_at": "2025-10-15T12:00:00+00:00"
  }
]
```

---

### 5. Obtener Compra por ID
**GET** `/api/purchases/:id`

Obtiene una compra específica (solo si es propia o si eres admin).

**Parámetros:**
- `id` (path): ID de la compra

**Headers:**
- `Authorization: Bearer <token>`

**Respuesta:**
```json
{
  "id": 1,
  "user_id": "uuid-del-usuario",
  "event_id": 1,
  "quantity": 5,
  "created_at": "2025-10-15T12:00:00+00:00"
}
```

---

### 6. Obtener Compras de un Usuario
**GET** `/api/purchases/user/:user_id`

Obtiene todas las compras de un usuario específico (solo admin o el mismo usuario).

**Parámetros:**
- `user_id` (path): UUID del usuario

**Headers:**
- `Authorization: Bearer <token>`

**Respuesta:**
```json
[
  {
    "id": 1,
    "user_id": "uuid-del-usuario",
    "event_id": 1,
    "quantity": 5,
    "created_at": "2025-10-15T12:00:00+00:00"
  }
]
```

---

### 7. Obtener Compras de un Evento (Admin)
**GET** `/api/purchases/event/:event_id`

Obtiene todas las compras y estadísticas de un evento. Solo administradores.

**Parámetros:**
- `event_id` (path): ID del evento

**Headers:**
- `Authorization: Bearer <token>`

**Respuesta:**
```json
{
  "purchases": [
    {
      "id": 1,
      "user_id": "uuid-del-usuario",
      "event_id": 1,
      "quantity": 5,
      "created_at": "2025-10-15T12:00:00+00:00"
    }
  ],
  "statistics": {
    "total_purchases": 10,
    "total_tickets_sold": 50
  }
}
```

---

## Códigos de Error

- `400`: Bad Request - Datos inválidos
- `401`: Unauthorized - Token inválido o no proporcionado
- `403`: Forbidden - Sin permisos suficientes
- `404`: Not Found - Recurso no encontrado
- `500`: Internal Server Error - Error del servidor

---

## Flujo de Compra

1. El usuario se autentica en el servicio de usuarios y obtiene un JWT
2. El usuario consulta eventos disponibles en el servicio de eventos
3. El usuario consulta tickets restantes: `GET /api/purchases/event/:id/remaining`
4. El usuario realiza la compra: `POST /api/purchases`
5. El sistema verifica:
   - Que el evento exista (consulta al servicio de eventos)
   - Que haya suficientes tickets disponibles
   - Que la cantidad sea válida (> 0)
6. Si todo es correcto, se crea la compra y se devuelve la confirmación

---

## Ejemplos con cURL

### Obtener tickets restantes
```bash
curl http://localhost:5000/api/purchases/event/1/remaining
```

### Crear compra
```bash
curl -X POST http://localhost:5000/api/purchases \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{"event_id": 1, "quantity": 3}'
```

### Obtener mis compras
```bash
curl http://localhost:5000/api/purchases \
  -H "Authorization: Bearer <tu_token>"
```
"""
