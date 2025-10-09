from flask import Flask, request, jsonify
from database import db
from models import Compra, CompraManager
from auth import token_required
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Inicializar base de datos - FORMA CORREGIDA
with app.app_context():
    db.init_db()

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'service': 'compras'})

# Obtener compras del usuario
@app.route('/compras', methods=['GET'])
@token_required
def obtener_compras_usuario():
    try:
        compras = Compra.get_by_usuario(request.user_id)
        return jsonify({'compras': compras}), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener compras: {str(e)}'}), 500

# Crear nueva compra (reserva)
@app.route('/compras', methods=['POST'])
@token_required
def crear_compra():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['evento_id', 'cantidad_entradas']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        evento_id = data['evento_id']
        cantidad_entradas = data['cantidad_entradas']
        
        # Verificar disponibilidad del evento
        evento = CompraManager.obtener_evento(evento_id)
        if not evento:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        # Verificar capacidad
        if evento.get('capacidad_actual', 0) + cantidad_entradas > evento.get('capacidad', 0):
            return jsonify({'error': 'No hay suficiente capacidad disponible'}), 400
        
        # Calcular total
        total = evento['precio'] * cantidad_entradas
        
        # Crear compra
        compra = Compra(
            usuario_id=request.user_id,
            evento_id=evento_id,
            cantidad_entradas=cantidad_entradas,
            total=total,
            estado='pendiente'
        )
        
        compra_id = compra.save()
        
        # Crear detalle de compra
        CompraManager.crear_compra_detalle(compra_id, evento, cantidad_entradas, total)
        
        compra_data = compra.to_dict()
        compra_data['evento_nombre'] = evento['nombre']
        
        return jsonify({
            'mensaje': 'Compra creada exitosamente',
            'compra': compra_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear compra: {str(e)}'}), 500

# Procesar pago
@app.route('/compras/<int:compra_id>/pagar', methods=['POST'])
@token_required
def procesar_pago(compra_id):
    try:
        # Verificar que la compra existe y pertenece al usuario
        compra = Compra.get_by_id(compra_id)
        if not compra:
            return jsonify({'error': 'Compra no encontrada'}), 404
        
        if compra.usuario_id != request.user_id:
            return jsonify({'error': 'No autorizado para pagar esta compra'}), 403
        
        if compra.estado != 'pendiente':
            return jsonify({'error': f'La compra ya está {compra.estado}'}), 400
        
        # Simular procesamiento de pago
        # En un sistema real, aquí se integraría con una pasarela de pago
        
        # Actualizar estado a pagada
        compra.estado = 'pagada'
        compra.save()
        
        # Obtener información del evento para la notificación
        evento = CompraManager.obtener_evento(compra.evento_id)
        
        # Preparar datos para notificación
        compra_data = compra.to_dict()
        compra_data['evento_nombre'] = evento['nombre'] if evento else 'Evento'
        
        # Enviar notificación (asíncrono en producción)
        # En un sistema real, esto iría a una cola de mensajes
        CompraManager.notificar_compra(compra_data, "usuario@ejemplo.com")  # Email debería venir del token o BD
        
        return jsonify({
            'mensaje': 'Pago procesado exitosamente',
            'compra': compra_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al procesar pago: {str(e)}'}), 500

# Obtener compra específica
@app.route('/compras/<int:compra_id>', methods=['GET'])
@token_required
def obtener_compra(compra_id):
    try:
        compra = Compra.get_by_id(compra_id)
        if not compra:
            return jsonify({'error': 'Compra no encontrada'}), 404
        
        if compra.usuario_id != request.user_id:
            return jsonify({'error': 'No autorizado'}), 403
        
        return jsonify({'compra': compra.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener compra: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)