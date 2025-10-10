import os
from dotenv import load_dotenv

load_dotenv()

# Configuración MySQL
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'mysql-compras'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', '123456'),
    'database': os.environ.get('MYSQL_DATABASE', 'compras_db')
}

# Configuración JWT
JWT_SECRET_ENCODED = os.environ.get('JWT_SECRET', 'eyJzZWNyZXRrZXkiOiJTdXBlclNlY3JldDEyMyEhQCMiLCJhbGciOiJIUzI1NiJ9')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

# Configuración servicios externos - usa nombre del contenedor en Docker
# En Docker: usar el nombre del servicio, en local: usar localhost
EVENTS_SERVICE_URL = os.environ.get('EVENTS_SERVICE_URL', 'http://node_app:3000/events')