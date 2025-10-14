from flask import request, jsonify
from auth_service import validar_jwt
from event_service import obtener_evento_por_id
from database import get_db_connection
from datetime import datetime

def configurar_rutas_pago(app):
    """Configurar rutas relacionadas con pagos"""
    
    @app.route('/pagar/<compra_id>', methods=['POST'])
    def pagar_compra(compra_id):
        """
        Simular confirmación de pago - Marcar compra como pagada
        """
        print(f"🔄 Iniciando pago para compra: {compra_id}")
        
        # 1️⃣ Verificar autenticación
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("❌ No hay token en el header")
            return jsonify({"error": "Token JWT requerido en header Authorization"}), 401

        token = auth_header.split(" ")[1]
        print(f"🔐 Token recibido: {token[:50]}...")
        
        # 2️⃣ Validar token JWT
        usuario_payload = validar_jwt(token)
        if not usuario_payload:
            return jsonify({"error": "Token inválido o expirado"}), 401

        user_id_token = usuario_payload.get('sub')
        print(f"👤 User ID del token: {user_id_token}")

        # 3️⃣ Buscar la compra en la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            # DEBUG: Primero buscar la compra sin filtrar por usuario
            cursor.execute('SELECT * FROM compras WHERE id = %s', (compra_id,))
            compra = cursor.fetchone()
            
            print(f"🔍 Resultado de búsqueda de compra: {compra}")
            
            if not compra:
                print(f"❌ Compra {compra_id} no encontrada en la base de datos")
                return jsonify({"error": "Compra no encontrada"}), 404
            
            user_id_compra = compra.get('user_id')
            print(f"🔍 User ID de la compra: {user_id_compra}")
            print(f"🔍 Comparación: {user_id_compra} == {user_id_token} -> {user_id_compra == user_id_token}")
            
            # Verificar si pertenece al usuario
            if user_id_compra != user_id_token:
                print(f"❌ La compra no pertenece a este usuario")
                return jsonify({
                    "error": "Compra no pertenece al usuario",
                    "detalle": f"La compra pertenece a {user_id_compra} pero el token es de {user_id_token}"
                }), 404
            
            # Verificar si ya está pagada
            if compra.get('pagada'):
                print("❌ La compra ya está pagada")
                return jsonify({"error": "La compra ya está pagada"}), 400
            
            # 4️⃣ Obtener información del evento para el payload
            try:
                evento = obtener_evento_por_id(compra['evento_id'])
                print(f"🎫 Información del evento obtenida: {evento.get('name')}")
            except Exception as e:
                print(f"⚠️ No se pudo obtener información del evento: {e}")
                evento = {"name": "Evento no disponible", "date": "Fecha no disponible"}
            
            # 5️⃣ Marcar la compra como pagada
            fecha_pago = datetime.now().isoformat()
            print(f"💳 Marcando compra como pagada...")
            
            cursor.execute('''
                UPDATE compras 
                SET pagada = TRUE, fecha_pago = %s
                WHERE id = %s
            ''', (fecha_pago, compra_id))
            
            connection.commit()
            print("✅ Compra marcada como pagada en la base de datos")
            
            # 6️⃣ Obtener la compra actualizada
            cursor.execute('SELECT * FROM compras WHERE id = %s', (compra_id,))
            compra_actualizada = cursor.fetchone()
            
            # 7️⃣ Construir el payload en el formato específico requerido
            payload_respuesta = {
                "type": "payment.confirmed",
                "data": {
                    "user": {
                        "email": f"user_{user_id_token}@example.com",
                        "name": f"Usuario {user_id_token}"
                    },
                    "event": {
                        "name": evento.get('name', 'Evento no disponible'),
                        "date": evento.get('date', 'Fecha no disponible')
                    },
                    "quantity": compra_actualizada['cantidad'],
                    "total": float(compra_actualizada['total'])
                }
            }
            
            print(f"🎉 Pago confirmado exitosamente para compra {compra_id}")
            print(f"📤 Payload enviado: {payload_respuesta}")
            
            return jsonify(payload_respuesta)
            
        except Exception as e:
            connection.rollback()
            print(f"❌ Error al procesar el pago: {str(e)}")
            return jsonify({"error": f"Error al procesar el pago: {str(e)}"}), 500
        finally:
            cursor.close()
            connection.close()

    @app.route('/compras-pagadas', methods=['GET'])
    def compras_pagadas():
        """Obtener todas las compras pagadas del usuario"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token JWT requerido"}), 401

        token = auth_header.split(" ")[1]
        usuario_payload = validar_jwt(token)
        if not usuario_payload:
            return jsonify({"error": "Token inválido o expirado"}), 401

        user_id = usuario_payload.get('sub')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM compras WHERE user_id = %s AND pagada = TRUE ORDER BY fecha_pago DESC', (user_id,))
        compras_db = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            "usuario": user_id,
            "total_compras_pagadas": len(compras_db),
            "compras": compras_db
        })

    # Endpoint adicional para debug
    @app.route('/debug/compras/<compra_id>', methods=['GET'])
    def debug_compra(compra_id):
        """Endpoint para debug - ver información de una compra específica"""
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM compras WHERE id = %s', (compra_id,))
        compra = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if compra:
            return jsonify({
                "compra": compra,
                "existe": True
            })
        else:
            return jsonify({
                "compra": None,
                "existe": False
            })