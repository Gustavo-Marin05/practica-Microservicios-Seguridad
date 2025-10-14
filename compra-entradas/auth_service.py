import jwt
import base64
import json
from config import JWT_SECRET_ENCODED, JWT_ALGORITHM

# --- Función para extraer el secreto real del JWT codificado ---
def get_jwt_secret():
    try:
        jwt_parts = JWT_SECRET_ENCODED.split('.')
        if len(jwt_parts) == 3:
            payload_b64 = jwt_parts[1]
            # Añadir padding si es necesario
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload_json = base64.b64decode(payload_b64)
            payload = json.loads(payload_json)
            real_secret = payload.get('secretkey')
            print(f"🔑 Secreto real extraído: {real_secret}")
            return real_secret
    except Exception as e:
        print(f"❌ Error extrayendo secreto: {e}")
    
    return JWT_SECRET_ENCODED

# Obtener el secreto real
JWT_SECRET_REAL = get_jwt_secret()

def validar_jwt(token):
    """Validar token JWT y devolver el payload"""
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_REAL, 
            algorithms=[JWT_ALGORITHM],
            options={"verify_aud": False, "verify_iss": False}
        )
        print(f"✅ Token válido. Usuario: {payload.get('sub')}, Rol: {payload.get('role')}")
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {e}")
        return None