from flask import jsonify
from event_service import obtener_todos_eventos, obtener_evento_por_id

def configurar_rutas_eventos(app):
    """Configurar rutas relacionadas con eventos"""
    
    @app.route('/eventos', methods=['GET'])
    def listar_eventos():
        try:
            eventos = obtener_todos_eventos()
            return jsonify(eventos)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/eventos/<evento_id>', methods=['GET'])
    def obtener_evento(evento_id):
        try:
            evento = obtener_evento_por_id(evento_id)
            return jsonify(evento)
        except Exception as e:
            return jsonify({
                "error": str(e),
                "eventos_disponibles": obtener_todos_eventos() if "no encontrado" in str(e) else []
            }), 404