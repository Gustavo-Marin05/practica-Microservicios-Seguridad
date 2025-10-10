import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG

def get_db_connection():
    """Obtener conexión a MySQL"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        print("✅ Conectado a MySQL")
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def init_db():
    """Crear base de datos y tabla si no existen"""
    print("🔄 Inicializando base de datos...")
    
    connection = get_db_connection()
    if not connection:
        print("❌ No se pudo inicializar la base de datos - sin conexión")
        return False
    
    cursor = connection.cursor()
    
    try:
        # Crear base de datos si no existe
        print("📁 Verificando/Creando base de datos...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS compras_db")
        cursor.execute("USE compras_db")
        print("✅ Base de datos compras_db verificada")
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'compras'")
        tabla_existe = cursor.fetchone()
        
        if tabla_existe:
            print("✅ Tabla 'compras' ya existe")
            # Verificar columnas existentes
            cursor.execute("DESCRIBE compras")
            columnas = [col[0] for col in cursor.fetchall()]
            print(f"📊 Columnas existentes: {columnas}")
            
            # Definir todas las columnas necesarias
            columnas_necesarias = {
                'precio_unitario': "ALTER TABLE compras ADD COLUMN precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0",
                'total': "ALTER TABLE compras ADD COLUMN total DECIMAL(10,2) NOT NULL DEFAULT 0",
                'pagada': "ALTER TABLE compras ADD COLUMN pagada BOOLEAN DEFAULT FALSE",
                'fecha_pago': "ALTER TABLE compras ADD COLUMN fecha_pago VARCHAR(100)"
            }
            
            # Agregar columnas si no existen
            for columna, query in columnas_necesarias.items():
                if columna not in columnas:
                    cursor.execute(query)
                    print(f"✅ Columna '{columna}' agregada")
                    
        else:
            # Crear tabla nueva con TODAS las columnas necesarias
            print("🆕 Creando nueva tabla 'compras'...")
            cursor.execute('''
                CREATE TABLE compras (
                    id VARCHAR(36) PRIMARY KEY,
                    evento_id VARCHAR(50) NOT NULL,
                    cantidad INT NOT NULL,
                    user_id VARCHAR(50),
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    pagada BOOLEAN DEFAULT FALSE,
                    fecha_pago VARCHAR(100)
                )
            ''')
            print("✅ Tabla 'compras' creada con todas las columnas")
        
        connection.commit()
        print("🎉 Estructura de la tabla verificada y actualizada correctamente")
        return True
        
    except Error as e:
        connection.rollback()
        print(f"❌ Error inicializando BD: {e}")
        return False
    finally:
        cursor.close()
        connection.close()