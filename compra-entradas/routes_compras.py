from flask import request, jsonify
import uuid
from auth_service import validar_jwt
from event_service import obtener_evento_por_id
from database import get_db_connection

def configurar_rutas_compras(app):
    """Configurar rutas relacionadas con compras"""
    
    @app.route('/comprar', methods=['POST'])
    def comprar_entradas():
        # 1️⃣ Verificar autenticación
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token JWT requerido en header Authorization"}), 401

        token = auth_header.split(" ")[1]
        
        # 2️⃣ Validar token JWT
        usuario_payload = validar_jwt(token)
        if not usuario_payload:
            return jsonify({"error": "Token inválido o expirado"}), 401

        # 3️⃣ Obtener datos de la compra
        data = request.json
        evento_id = data.get("evento_id")
        cantidad = data.get("cantidad")

        if not evento_id:
            return jsonify({"error": "evento_id es obligatorio"}), 400

        if not cantidad or cantidad <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400

        # 4️⃣ Obtener información del evento para el precio
        try:
            evento = obtener_evento_por_id(evento_id)
            precio_unitario = evento.get('price', 0)
            total = cantidad * precio_unitario
            
            print(f"💰 Evento: {evento.get('name')}, Precio: {precio_unitario}, Cantidad: {cantidad}, Total: {total}")
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # 5️⃣ Registrar la compra en MySQL
        compra_id = str(uuid.uuid4())
        user_id = usuario_payload.get('sub')  # ID del usuario desde el JWT
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a MySQL"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                INSERT INTO compras (id, evento_id, cantidad, user_id, precio_unitario, total)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                compra_id,
                evento_id,
                cantidad,
                user_id,
                precio_unitario,
                total
            ))
            
            connection.commit()
            
            cursor.execute('SELECT * FROM compras WHERE id = %s', (compra_id,))
            compra = cursor.fetchone()
            
            return jsonify({
                "message": "✅ Compra registrada exitosamente", 
                "compra": compra,
                "usuario": {
                    "id": user_id,
                    "role": usuario_payload.get('role')
                },
                "evento_info": {
                    "nombre": evento.get('name'),
                    "precio_unitario": precio_unitario,
                    "total": total
                }
            }), 201
            
        except Exception as e:
            connection.rollback()
            return jsonify({"error": f"Error al guardar la compra: {str(e)}"}), 500
        finally:
            cursor.close()
            connection.close()

    @app.route('/mis-compras', methods=['GET'])
    def mis_compras():
        # 1️⃣ Verificar autenticación
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token JWT requerido en header Authorization"}), 401

        token = auth_header.split(" ")[1]
        
        # 2️⃣ Validar token JWT
        usuario_payload = validar_jwt(token)
        if not usuario_payload:
            return jsonify({"error": "Token inválido o expirado"}), 401

        # 3️⃣ Obtener compras del usuario
        user_id = usuario_payload.get('sub')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM compras WHERE user_id = %s ORDER BY id DESC', (user_id,))
        compras_db = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            "usuario": user_id,
            "total_compras": len(compras_db),
            "compras": compras_db
        })

    @app.route('/compras', methods=['GET'])
    def listar_compras():
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM compras ORDER BY id DESC')
        compras_db = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            "total_compras": len(compras_db),
            "compras": compras_db
        })
    
