from database import db
from datetime import datetime
import requests
import os
import json

class Compra:
    def __init__(self, usuario_id, evento_id, cantidad_entradas, total, estado='pendiente', id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.evento_id = evento_id
        self.cantidad_entradas = cantidad_entradas
        self.total = total
        self.estado = estado

    def save(self):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            if self.id:
                cursor.execute('''
                    UPDATE compras 
                    SET usuario_id=%s, evento_id=%s, cantidad_entradas=%s, total=%s, estado=%s
                    WHERE id=%s
                ''', (self.usuario_id, self.evento_id, self.cantidad_entradas, self.total, self.estado, self.id))
            else:
                cursor.execute('''
                    INSERT INTO compras (usuario_id, evento_id, cantidad_entradas, total, estado)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (self.usuario_id, self.evento_id, self.cantidad_entradas, self.total, self.estado))
                self.id = cursor.lastrowid
            
            connection.commit()
            return self.id

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'evento_id': self.evento_id,
            'cantidad_entradas': self.cantidad_entradas,
            'total': float(self.total) if self.total else 0.0,
            'estado': self.estado
        }

    @staticmethod
    def get_by_id(compra_id):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM compras WHERE id = %s', (compra_id,))
            result = cursor.fetchone()
            if result:
                return Compra(
                    id=result['id'],
                    usuario_id=result['usuario_id'],
                    evento_id=result['evento_id'],
                    cantidad_entradas=result['cantidad_entradas'],
                    total=result['total'],
                    estado=result['estado']
                )
            return None

    @staticmethod
    def get_by_usuario(usuario_id):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM compras WHERE usuario_id = %s ORDER BY fecha_compra DESC', (usuario_id,))
            results = cursor.fetchall()
            compras = []
            for result in results:
                compra = Compra(
                    id=result['id'],
                    usuario_id=result['usuario_id'],
                    evento_id=result['evento_id'],
                    cantidad_entradas=result['cantidad_entradas'],
                    total=result['total'],
                    estado=result['estado']
                )
                compras.append(compra.to_dict())
            return compras

class CompraManager:
    @staticmethod
    def obtener_evento(evento_id):
        """Obtiene información del evento desde el servicio de eventos"""
        try:
            eventos_url = os.getenv('EVENTOS_SERVICE_URL')
            response = requests.get(f"{eventos_url}/eventos/{evento_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con servicio de eventos: {e}")
            return None

    @staticmethod
    def notificar_compra(compra_data, usuario_email):
        """Envía notificación al servicio de notificaciones"""
        try:
            notificaciones_url = os.getenv('NOTIFICACIONES_SERVICE_URL')
            payload = {
                'email': usuario_email,
                'asunto': 'Confirmación de Compra de Entradas',
                'mensaje': f'''
                    ¡Gracias por tu compra!
                    
                    Detalles de tu compra:
                    - ID de Compra: {compra_data['id']}
                    - Evento: {compra_data['evento_nombre']}
                    - Cantidad de entradas: {compra_data['cantidad_entradas']}
                    - Total: ${compra_data['total']}
                    - Estado: {compra_data['estado']}
                    
                    ¡Esperamos que disfrutes del evento!
                '''
            }
            response = requests.post(f"{notificaciones_url}/notificaciones/email", json=payload)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con servicio de notificaciones: {e}")
            return False

    @staticmethod
    def crear_compra_detalle(compra_id, evento_info, cantidad_entradas, total):
        """Crea el detalle de la compra para mantener información histórica"""
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO compra_detalles (compra_id, evento_nombre, evento_fecha, evento_lugar, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
            ''', (compra_id, evento_info['nombre'], evento_info['fecha'], evento_info['lugar'], evento_info['precio']))
            connection.commit()