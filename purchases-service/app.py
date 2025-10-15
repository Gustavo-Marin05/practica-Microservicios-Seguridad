from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import jwt
import os
from functools import wraps
import requests
from dotenv import load_dotenv
import pika
import json

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración desde variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://myuser:mypassword@localhost:5432/purchasesdb')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

JWT_SECRET = os.getenv('JWT_SECRET', 'eyJzZWNyZXRrZXkiOiJTdXBlclNlY3JldDEyMyEhQCMiLCJhbGciOiJIUzI1NiJ9')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# URLs de otros microservicios
EVENTS_SERVICE_URL = os.getenv('EVENTS_SERVICE_URL', 'http://localhost:3000')
USERS_SERVICE_URL = os.getenv('USERS_SERVICE_URL', 'http://localhost:80')

# RabbitMQ Configuration
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'payments')
RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY', 'payment.confirmed')

print(f"🔧 Configuración cargada:")
print(f"   DATABASE_URL: {DATABASE_URL}")
print(f"   EVENTS_SERVICE_URL: {EVENTS_SERVICE_URL}")
print(f"   USERS_SERVICE_URL: {USERS_SERVICE_URL}")
print(f"   RABBITMQ_URL: {RABBITMQ_URL}")
print(f"   JWT_SECRET: {JWT_SECRET[:20]}...")

db = SQLAlchemy(app)

# ==========================================
# MODELO
# ==========================================
class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)  # UUID de .NET como string
    event_id = db.Column(db.BigInteger, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat()
        }

# ==========================================
# MIDDLEWARE DE AUTENTICACIÓN
# ==========================================
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=[JWT_ALGORITHM],
                options={"verify_aud": False}  # No validamos audience para simplificar
            )
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': 'Token inválido', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_user_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = request.user.get('role', '')
        if role != 'user' and role != 'admin':
            return jsonify({'error': 'Acceso denegado. Solo usuarios pueden comprar'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def get_event_by_id(event_id):
    """Obtiene un evento del microservicio de eventos"""
    try:
        url = f'{EVENTS_SERVICE_URL}/events/{event_id}'
        print(f"🔍 Consultando evento {event_id} en {url}")
        response = requests.get(url, timeout=5)
        print(f"📡 Respuesta del servicio de eventos: Status {response.status_code}")
        
        if response.status_code == 200:
            event_data = response.json()
            print(f"✅ Evento encontrado: {event_data.get('name', 'N/A')}")
            return event_data
        else:
            print(f"❌ Evento no encontrado. Status: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"💥 Error al consultar evento: {e}")
        return None

def get_user_by_id(user_id):
    """Obtiene información de un usuario del microservicio de usuarios"""
    try:
        url = f'{USERS_SERVICE_URL}/api/users/{user_id}'
        print(f"🔍 Consultando usuario {user_id} en {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Usuario encontrado: {user_data.get('email', 'N/A')}")
            return user_data
        else:
            print(f"❌ Usuario no encontrado. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"💥 Error al consultar usuario: {e}")
        return None

def calculate_remaining_tickets(event_id, capacity):
    """Calcula los tickets restantes para un evento"""
    total_purchased = db.session.query(
        db.func.sum(Purchase.quantity)
    ).filter(
        Purchase.event_id == event_id
    ).scalar() or 0
    
    return capacity - total_purchased

def publish_to_rabbitmq(message_data):
    """Publica un mensaje a RabbitMQ"""
    try:
        # Conectar a RabbitMQ
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Declarar exchange (topic)
        channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type='topic',
            durable=True
        )
        
        # Publicar mensaje
        channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=RABBITMQ_ROUTING_KEY,
            body=json.dumps(message_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
                content_type='application/json'
            )
        )
        
        print(f"📨 Mensaje publicado a RabbitMQ: {RABBITMQ_EXCHANGE}:{RABBITMQ_ROUTING_KEY}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"💥 Error al publicar a RabbitMQ: {e}")
        return False

# ==========================================
# RUTAS
# ==========================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'purchases'}), 200

# GET /api/purchases - Obtener todas las compras (admin) o las propias (user)
@app.route('/api/purchases', methods=['GET'])
@require_auth
def get_purchases():
    user_id = request.user.get('nameid') or request.user.get('sub')
    role = request.user.get('role', '')
    
    if role == 'admin':
        purchases = Purchase.query.order_by(Purchase.created_at.desc()).all()
    else:
        purchases = Purchase.query.filter_by(user_id=user_id).order_by(Purchase.created_at.desc()).all()
    
    return jsonify([p.to_dict() for p in purchases]), 200

# GET /api/purchases/:id - Obtener una compra específica
@app.route('/api/purchases/<int:purchase_id>', methods=['GET'])
@require_auth
def get_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if not purchase:
        return jsonify({'error': 'Compra no encontrada'}), 404
    
    user_id = request.user.get('nameid') or request.user.get('sub')
    role = request.user.get('role', '')
    
    # Solo puede ver su propia compra, excepto admin
    if role != 'admin' and purchase.user_id != user_id:
        return jsonify({'error': 'No autorizado'}), 403
    
    return jsonify(purchase.to_dict()), 200

# GET /api/purchases/event/:event_id/remaining - Obtener tickets restantes
@app.route('/api/purchases/event/<int:event_id>/remaining', methods=['GET'])
def get_remaining_tickets(event_id):
    # Obtener información del evento
    event = get_event_by_id(event_id)
    if not event:
        return jsonify({'error': 'Evento no encontrado'}), 404
    
    capacity = event.get('capacity', 0)
    remaining = calculate_remaining_tickets(event_id, capacity)
    
    return jsonify({
        'event_id': event_id,
        'capacity': capacity,
        'remaining': remaining,
        'sold': capacity - remaining
    }), 200

# POST /api/purchases - Crear una compra
@app.route('/api/purchases', methods=['POST'])
@require_auth
@require_user_role
def create_purchase():
    data = request.get_json()
    
    # Validaciones
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    event_id = data.get('event_id')
    quantity = data.get('quantity')
    
    if not event_id or not quantity:
        return jsonify({'error': 'event_id y quantity son requeridos'}), 400
    
    try:
        event_id = int(event_id)
        quantity = int(quantity)
    except ValueError:
        return jsonify({'error': 'event_id y quantity deben ser números'}), 400
    
    if quantity <= 0:
        return jsonify({'error': 'La cantidad debe ser mayor a 0'}), 400
    
    # Obtener información del evento
    event = get_event_by_id(event_id)
    if not event:
        return jsonify({'error': 'Evento no encontrado'}), 404
    
    capacity = event.get('capacity', 0)
    
    # Verificar disponibilidad
    remaining = calculate_remaining_tickets(event_id, capacity)
    
    if quantity > remaining:
        return jsonify({
            'error': 'No hay suficientes entradas disponibles',
            'requested': quantity,
            'available': remaining
        }), 400
    
    # Crear la compra
    user_id = request.user.get('nameid') or request.user.get('sub')
    user_email = request.user.get('email', '')
    
    purchase = Purchase(
        user_id=user_id,
        event_id=event_id,
        quantity=quantity
    )
    
    try:
        db.session.add(purchase)
        db.session.commit()
        
        # Obtener información completa del usuario (opcional, si falla usamos el email del JWT)
        user_info = None
        try:
            user_info = get_user_by_id(user_id)
        except:
            pass
        
        # Preparar mensaje para RabbitMQ
        notification_payload = {
            "type": "payment.confirmed",
            "data": {
                "user": {
                    "id": user_id,
                    "email": user_email or (user_info.get('email') if user_info else 'cliente@example.com'),
                    "name": user_info.get('email', 'Cliente') if user_info else user_email or 'Cliente'
                },
                "event": {
                    "id": event.get('id'),
                    "name": event.get('name'),
                    "date": event.get('date'),
                    "location": event.get('location')
                },
                "quantity": quantity,
                "total": event.get('price', 0) * quantity,
                "purchase_id": purchase.id,
                "created_at": purchase.created_at.isoformat()
            }
        }
        
        # Publicar a RabbitMQ (no bloqueante, si falla no afecta la compra)
        try:
            publish_to_rabbitmq(notification_payload)
            print(f"✅ Notificación enviada a RabbitMQ para compra #{purchase.id}")
        except Exception as rabbit_err:
            print(f"⚠️ Error al publicar a RabbitMQ (compra guardada): {rabbit_err}")
        
        return jsonify({
            'message': 'Compra realizada exitosamente',
            'purchase': purchase.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la compra', 'details': str(e)}), 500

# GET /api/purchases/user/:user_id - Obtener compras de un usuario (admin)
@app.route('/api/purchases/user/<user_id>', methods=['GET'])
@require_auth
def get_user_purchases(user_id):
    role = request.user.get('role', '')
    current_user_id = request.user.get('nameid') or request.user.get('sub')
    
    # Solo admin o el mismo usuario puede ver sus compras
    if role != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'No autorizado'}), 403
    
    purchases = Purchase.query.filter_by(user_id=user_id).order_by(Purchase.created_at.desc()).all()
    return jsonify([p.to_dict() for p in purchases]), 200

# GET /api/purchases/event/:event_id - Obtener compras de un evento
@app.route('/api/purchases/event/<int:event_id>', methods=['GET'])
@require_auth
def get_event_purchases(event_id):
    role = request.user.get('role', '')
    
    # Solo admin puede ver todas las compras de un evento
    if role != 'admin':
        return jsonify({'error': 'Solo administradores'}), 403
    
    purchases = Purchase.query.filter_by(event_id=event_id).order_by(Purchase.created_at.desc()).all()
    
    # Calcular estadísticas
    total_tickets = db.session.query(
        db.func.sum(Purchase.quantity)
    ).filter(
        Purchase.event_id == event_id
    ).scalar() or 0
    
    total_purchases = len(purchases)
    
    return jsonify({
        'purchases': [p.to_dict() for p in purchases],
        'statistics': {
            'total_purchases': total_purchases,
            'total_tickets_sold': int(total_tickets)
        }
    }), 200

# ==========================================
# INICIALIZACIÓN
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos inicializada")
    
    app.run(host='0.0.0.0', port=5001, debug=True)