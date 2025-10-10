import requests
from config import EVENTS_SERVICE_URL

def obtener_todos_eventos():
    """Obtener todos los eventos del servicio externo"""
    try:
        response = requests.get(EVENTS_SERVICE_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"No se pudo conectar al servicio de eventos: {str(e)}")

def obtener_evento_por_id(evento_id):
    """Obtener un evento específico por ID"""
    try:
        eventos = obtener_todos_eventos()
        
        evento_encontrado = None
        for evento in eventos:
            if str(evento.get('id')) == str(evento_id):
                evento_encontrado = evento
                break
        
        if evento_encontrado:
            return evento_encontrado
        else:
            raise Exception(f"Evento con ID {evento_id} no encontrado")
            
    except Exception as e:
        raise e