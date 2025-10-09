import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.connection = None

    def get_connection(self):
        if not self.connection or not self.connection.open:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        return self.connection

    def init_db(self):
        connection = self.get_connection()
        with connection.cursor() as cursor:
            # Tabla de compras
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compras (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    evento_id INT NOT NULL,
                    cantidad_entradas INT NOT NULL,
                    total DECIMAL(10, 2) NOT NULL,
                    estado ENUM('pendiente', 'pagada', 'cancelada') DEFAULT 'pendiente',
                    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de detalles de compra (para tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compra_detalles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    compra_id INT NOT NULL,
                    evento_nombre VARCHAR(255) NOT NULL,
                    evento_fecha DATETIME NOT NULL,
                    evento_lugar VARCHAR(255) NOT NULL,
                    precio_unitario DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE
                )
            ''')
            
            connection.commit()

db = Database()