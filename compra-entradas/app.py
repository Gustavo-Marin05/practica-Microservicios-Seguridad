from flask import Flask
from config import MYSQL_CONFIG, JWT_SECRET_ENCODED, JWT_ALGORITHM
from database import init_db
from routes_eventos import configurar_rutas_eventos
from routes_compras import configurar_rutas_compras
from routes_pago import configurar_rutas_pago
import os
import time

app = Flask(__name__)

def wait_for_mysql():
    """Esperar a que MySQL esté disponible"""
    max_attempts = 30
    attempt = 0
    
    print("⏳ Esperando a que MySQL esté listo...")
    
    while attempt < max_attempts:
        try:
            from database import get_db_connection
            connection = get_db_connection()
            if connection:
                connection.close()
                print("✅ MySQL está listo!")
                return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Intento {attempt}/{max_attempts} - MySQL no está listo: {e}")
            time.sleep(2)
    
    print("❌ No se pudo conectar a MySQL después de varios intentos")
    return False

def main():
    print("🚀 Iniciando servicio de Compras en Docker...")
    
    # Esperar a que MySQL esté listo
    if not wait_for_mysql():
        print("❌ No se pudo conectar a MySQL. Saliendo...")
        return
    
    # Inicializar base de datos
    print("🔄 Inicializando base de datos...")
    if init_db():
        print("✅ Base de datos inicializada correctamente")
    else:
        print("❌ Error inicializando base de datos")
    
    # Configurar rutas
    configurar_rutas_eventos(app)
    configurar_rutas_compras(app)
    configurar_rutas_pago(app)

    print("🎉 Servicio de Compras iniciado correctamente")
    print(f"🔧 Configuración MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
    print("📋 Endpoints disponibles:")
    print("   GET  /eventos              - Listar todos los eventos")
    print("   GET  /eventos/<id>         - Obtener un evento por ID")
    print("   POST /comprar              - Comprar entradas (requiere JWT)")
    print("   GET  /mis-compras          - Mis compras (requiere JWT)")
    print("   GET  /compras              - Listar todas las compras")
    
    # Obtener el host y puerto de las variables de entorno para Docker
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 4000))
    
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()