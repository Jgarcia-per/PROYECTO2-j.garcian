from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import math

app = Flask(__name__)
app.config.from_object('config.Config')

# Configuración de MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1027150930Juan*'
app.config['MYSQL_DB'] = 'heladeria'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

# Función para determinar si un ingrediente es sano
def es_ingrediente_sano(calorias, vegetariano):
    return calorias < 100 or vegetariano

# Función para contar las calorías de un producto
def contar_calorias(ingredientes):
    total_calorias = sum(ingredientes) * 0.95
    return round(total_calorias, 2)

# Función para calcular el costo de un producto
def calcular_costo(ingredientes):
    return round(sum(ingrediente['precio'] for ingrediente in ingredientes), 2)

# Función para calcular la rentabilidad de un producto
def calcular_rentabilidad(precio_venta, ingredientes):
    costo = calcular_costo(ingredientes)
    return round(precio_venta - costo, 2)

# Función para encontrar el producto más rentable
def producto_mas_rentable(productos):
    return max(productos, key=lambda x: x['rentabilidad'])

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.nombre AS producto, GROUP_CONCAT(i.nombre) AS ingredientes
        FROM productos p
        JOIN producto_ingredientes pi ON p.id = pi.producto_id
        JOIN ingredientes i ON pi.ingrediente_id = i.id
        GROUP BY p.id
    """)
    productos = cursor.fetchall()
    return render_template('index.html', productos=productos)

@app.route('/seleccionar_ingredientes')
def seleccionar_ingredientes():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, calorias, vegetariano, costo FROM ingredientes")
    ingredientes = cursor.fetchall()
    return render_template('seleccionar_ingredientes.html', ingredientes=ingredientes)

@app.route('/verificar_ingredientes', methods=['POST'])
def verificar_ingredientes():
    ingredientes_ids = request.form.getlist('ingredientes')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT calorias, vegetariano FROM ingredientes WHERE id IN (%s)" % ','.join(ingredientes_ids))
    ingredientes = cursor.fetchall()
    
    total_calorias = sum(i[0] for i in ingredientes)
    es_vegetariano = any(i[1] for i in ingredientes)
    
    sano = es_ingrediente_sano(total_calorias, es_vegetariano)
    
    return render_template('resultado_ingredientes.html', sano=sano)

@app.route('/contar_calorias', methods=['POST'])
def contar_calorias_route():
    ingredientes_ids = request.form.getlist('ingredientes')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT calorias FROM ingredientes WHERE id IN (%s)" % ','.join(ingredientes_ids))
    ingredientes = cursor.fetchall()
    
    calorias_list = [i[0] for i in ingredientes]
    total_calorias = contar_calorias(calorias_list)
    
    return render_template('resultado_calorias.html', total_calorias=total_calorias)

@app.route('/calcular_costo', methods=['POST'])
def calcular_costo_route():
    ingredientes_ids = request.form.getlist('ingredientes')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, costo FROM ingredientes WHERE id IN (%s)" % ','.join(ingredientes_ids))
    ingredientes = cursor.fetchall()
    
    ingredientes_dict = [{'nombre': i[0], 'precio': float(i[1])} for i in ingredientes]
    total_costo = calcular_costo(ingredientes_dict)
    
    return render_template('resultado_costo.html', total_costo=total_costo)

@app.route('/calcular_rentabilidad', methods=['POST'])
def calcular_rentabilidad_route():
    precio_venta = float(request.form.get('precio_venta'))
    ingredientes_ids = request.form.getlist('ingredientes')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, costo FROM ingredientes WHERE id IN (%s)" % ','.join(ingredientes_ids))
    ingredientes = cursor.fetchall()
    
    ingredientes_dict = [{'nombre': i[0], 'precio': float(i[1])} for i in ingredientes]
    rentabilidad = calcular_rentabilidad(precio_venta, ingredientes_dict)
    
    return render_template('resultado_rentabilidad.html', rentabilidad=rentabilidad)

@app.route('/producto_mas_rentable', methods=['POST'])
def producto_mas_rentable_route():
    productos = request.form.getlist('productos')
    productos_dict = [{'nombre': p.split(',')[0], 'rentabilidad': float(p.split(',')[1])} for p in productos]
    mas_rentable = producto_mas_rentable(productos_dict)
    
    return render_template('resultado_mas_rentable.html', producto=mas_rentable['nombre'])

if __name__ == '__main__':
    app.run(debug=True)