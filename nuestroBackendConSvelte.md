# Tutorial: Cómo usar nuestro Backend con Svelte

## 📋 Introducción
Nuestro sistema tiene 4 microservicios funcionando a través de NGINX. Aquí te explico cómo usar cada endpoint desde tu frontend Svelte.

## 🔐 Autenticación (JWT en Headers)

### 1. Registro de Usuario
**Endpoint:** `POST http://localhost:8080/api/auth/signup`

```javascript
// En tu componente Svelte
async function registrarUsuario() {
  try {
    const response = await fetch('http://localhost:8080/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        names: "Antonio",
        surnames: "Calderon", 
        phoneNumber: "70323-2",
        email: "usuario@ejemplo.com",
        password: "miPassword123"
      })
    });
    
    const data = await response.json();
    console.log('Usuario registrado:', data);
  } catch (error) {
    console.error('Error en registro:', error);
  }
}
```

### 2. Inicio de Sesión
**Endpoint:** `POST http://localhost:8080/api/auth/signin`

```javascript
async function iniciarSesion(email, password) {
  try {
    const response = await fetch('http://localhost:8080/api/auth/signin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // 🔑 GUARDAR EL TOKEN EN LOCALSTORAGE
      localStorage.setItem('jwtToken', data.token);
      console.log('Login exitoso, token guardado');
      
      return data;
    } else {
      throw new Error('Credenciales incorrectas');
    }
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
}
```

## 🎭 Gestión de Eventos

### 3. Obtener Todos los Eventos
**Endpoint:** `GET http://localhost:8080/events`

```javascript
async function obtenerEventos() {
  try {
    // 📥 OBTENER TOKEN DEL LOCALSTORAGE
    const token = localStorage.getItem('jwtToken');
    
    const response = await fetch('http://localhost:8080/events', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const eventos = await response.json();
      return eventos;
    } else {
      throw new Error('Error al obtener eventos');
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

### 4. Obtener un Evento Específico
**Endpoint:** `GET http://localhost:8080/events/:id`

```javascript
async function obtenerEvento(id) {
  const token = localStorage.getItem('jwtToken');
  
  const response = await fetch(`http://localhost:8080/events/${id}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

### 5. Crear un Evento (Solo Admin)
**Endpoint:** `POST http://localhost:8080/events`

```javascript
async function crearEvento(eventoData) {
  const token = localStorage.getItem('jwtToken');
  
  const response = await fetch('http://localhost:8080/events', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: "Concierto de Rock",
      date: "2025-11-01T21:00:00Z",
      location: "Teatro Gran Rex", 
      capacity: 500,
      price: 50.0
    })
  });
  
  return await response.json();
}
```

## 🎫 Sistema de Compras

### 6. Ver Tickets Disponibles
**Endpoint:** `GET http://localhost:8080/purchases/api/purchases/event/:id/remaining`

```javascript
async function verTicketsDisponibles(eventoId) {
  const response = await fetch(
    `http://localhost:8080/purchases/api/purchases/event/${eventoId}/remaining`, 
    {
      method: 'GET'
      // No necesita autenticación
    }
  );
  
  return await response.json();
}
```

### 7. Realizar una Compra
**Endpoint:** `POST http://localhost:8080/purchases/api/purchases`

```javascript
async function realizarCompra(eventoId, cantidad) {
  const token = localStorage.getItem('jwtToken');
  
  const response = await fetch('http://localhost:8080/purchases/api/purchases', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      event_id: eventoId,
      quantity: cantidad
    })
  });
  
  return await response.json();
}
```

### 8. Ver Mis Compras
**Endpoint:** `GET http://localhost:8080/purchases/api/purchases`

```javascript
async function obtenerMisCompras() {
  const token = localStorage.getItem('jwtToken');
  
  const response = await fetch('http://localhost:8080/purchases/api/purchases', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

## 👥 Gestión de Usuarios (Admin)

### 9. Obtener Todos los Usuarios (Solo Admin)
**Endpoint:** `GET http://localhost:8080/api/users`

```javascript
async function obtenerTodosUsuarios() {
  const token = localStorage.getItem('jwtToken');
  
  const response = await fetch('http://localhost:8080/api/users', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

## 🛠️ Utilidades para Svelte

### Store para Manejar Autenticación
```javascript
// stores/auth.js
import { writable } from 'svelte/store';

export const user = writable(null);
export const isAuthenticated = writable(false);

export function initAuth() {
  // Verificar si hay token al cargar la app
  const token = localStorage.getItem('jwtToken');
  if (token) {
    isAuthenticated.set(true);
    // Opcional: decodificar token para obtener info del usuario
  }
}

export function logout() {
  localStorage.removeItem('jwtToken');
  user.set(null);
  isAuthenticated.set(false);
}
```

### Función Helper para Requests Autenticados
```javascript
// utils/api.js
export async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('jwtToken');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  };
  
  const response = await fetch(url, config);
  
  if (response.status === 401) {
    // Token expirado o inválido
    localStorage.removeItem('jwtToken');
    window.location.href = '/login';
    throw new Error('Sesión expirada');
  }
  
  return response;
}
```

## 📱 Ejemplo de Componente Svelte

```svelte
<script>
  import { onMount } from 'svelte';
  import { authenticatedFetch } from '../utils/api.js';
  
  let eventos = [];
  let loading = true;
  
  onMount(async () => {
    try {
      const response = await authenticatedFetch('http://localhost:8080/events');
      eventos = await response.json();
    } catch (error) {
      console.error('Error cargando eventos:', error);
    } finally {
      loading = false;
    }
  });
  
  async function comprarEntrada(eventoId) {
    try {
      const response = await authenticatedFetch(
        'http://localhost:8080/purchases/api/purchases',
        {
          method: 'POST',
          body: JSON.stringify({
            event_id: eventoId,
            quantity: 1
          })
        }
      );
      
      const resultado = await response.json();
      alert('Compra exitosa!');
    } catch (error) {
      alert('Error en la compra: ' + error.message);
    }
  }
</script>

{#if loading}
  <p>Cargando eventos...</p>
{:else}
  <div class="eventos">
    {#each eventos as evento}
      <div class="evento">
        <h3>{evento.name}</h3>
        <p>Lugar: {evento.location}</p>
        <p>Precio: ${evento.price}</p>
        <button on:click={() => comprarEntrada(evento.id)}>
          Comprar Entrada
        </button>
      </div>
    {/each}
  </div>
{/if}
```

## 🔄 Flujo Completo de Ejemplo

1. **Usuario se registra** → `POST /api/auth/signup`
2. **Usuario inicia sesión** → `POST /api/auth/signin` → Guarda token
3. **Ve eventos disponibles** → `GET /events` (con token)
4. **Consulta disponibilidad** → `GET /purchases/api/purchases/event/1/remaining`
5. **Realiza compra** → `POST /purchases/api/purchases` (con token)
6. **Ve sus compras** → `GET /purchases/api/purchases` (con token)

## ⚠️ Notas Importantes

- **Siempre incluir** el header `Authorization: Bearer {token}`
- **Guardar el token** en `localStorage` después del login
- **El token expira** en 1 hora (3600 segundos)
- **Solo admins** pueden crear eventos y ver todos los usuarios
- **Los usuarios normales** solo pueden ver sus propias compras

¡Listo! Tu equipo puede usar estos ejemplos para integrar el backend con Svelte. 🚀