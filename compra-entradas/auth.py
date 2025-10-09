import jwt
import os
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

class Auth:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id(self, token):
        payload = self.verify_token(token)
        return payload.get('user_id') if payload else None

    def get_user_role(self, token):
        payload = self.verify_token(token)
        return payload.get('role') if payload else None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token es requerido'}), 401
        
        auth = Auth()
        payload = auth.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar información del usuario al request
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        
        return f(*args, **kwargs)
    
    return decorated