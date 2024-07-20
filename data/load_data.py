import csv
import mysql.connector

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'heladeria',
}

# Conectar a la base de datos
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Función para cargar ingredientes desde un archivo CSV
def load_ingredientes(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO ingredientes (nombre, calorias, vegetariano, costo)
                VALUES (%s, %s, %s, %s)
            """, (row['nombre'], row['calorias'], row['vegetariano'], row['costo']))
    conn.commit()

# Función para cargar productos desde un archivo CSV
def load_productos(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO productos (nombre)
                VALUES (%s)
            """, (row['nombre'],))
    conn.commit()

if __name__ == '__main__':
    load_ingredientes('ingredientes.csv')
    load_productos('productos.csv')
    print("Datos cargados exitosamente.")
    cursor.close()
    conn.close()
