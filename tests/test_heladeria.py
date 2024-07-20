import unittest
from app import es_ingrediente_sano, contar_calorias, calcular_costo, calcular_rentabilidad, producto_mas_rentable, vender_producto
from app import app, mysql
from flask import json

class TestHeladeria(unittest.TestCase):

    def setUp(self):
        # Configurar la aplicación para pruebas
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.testing = True

        # Crear el contexto de la aplicación
        self.app_context = app.app_context()
        self.app_context.push()

        # Conectar a la base de datos de prueba
        self.conn = mysql.connect
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()
        # Quitar el contexto de la aplicación
        self.app_context.pop()

    def test_es_ingrediente_sano(self):
        self.assertTrue(es_ingrediente_sano(50, False))
        self.assertTrue(es_ingrediente_sano(150, True))
        self.assertFalse(es_ingrediente_sano(150, False))

    def test_abastecer_ingrediente(self):
        self.cursor.execute("UPDATE ingredientes SET cantidad = 0 WHERE nombre = 'Leche'")
        self.conn.commit()
        self.cursor.execute("SELECT cantidad FROM ingredientes WHERE nombre = 'Leche'")
        cantidad = self.cursor.fetchone()[0]
        self.assertEqual(cantidad, 0)
        
        # Abastecer el ingrediente
        self.cursor.execute("UPDATE ingredientes SET cantidad = 10 WHERE nombre = 'Leche'")
        self.conn.commit()
        self.cursor.execute("SELECT cantidad FROM ingredientes WHERE nombre = 'Leche'")
        cantidad = self.cursor.fetchone()[0]
        self.assertEqual(cantidad, 10)

    def test_renovar_inventario(self):
        # Supongamos que renovar inventario simplemente restablece las cantidades a 10
        self.cursor.execute("UPDATE ingredientes SET cantidad = 0")
        self.conn.commit()
        self.cursor.execute("UPDATE ingredientes SET cantidad = 10")
        self.conn.commit()
        self.cursor.execute("SELECT cantidad FROM ingredientes")
        cantidades = self.cursor.fetchall()
        for cantidad in cantidades:
            self.assertEqual(cantidad[0], 10)

    def test_contar_calorias(self):
        self.assertEqual(contar_calorias([150, 100, 50]), 285.0)
        self.assertEqual(contar_calorias([200, 100]), 285.0)

    def test_calcular_costo(self):
        ingredientes = [{'nombre': 'Leche', 'precio': 0.5}, {'nombre': 'Azúcar', 'precio': 0.2}, {'nombre': 'Fresa', 'precio': 0.3}]
        self.assertEqual(calcular_costo(ingredientes), 1.0)

    def test_calcular_rentabilidad(self):
        ingredientes = [{'nombre': 'Leche', 'precio': 0.5}, {'nombre': 'Azúcar', 'precio': 0.2}, {'nombre': 'Fresa', 'precio': 0.3}]
        self.assertEqual(calcular_rentabilidad(5.0, ingredientes), 4.0)

    def test_producto_mas_rentable(self):
        productos = [
            {'nombre': 'Producto A', 'rentabilidad': 10.0},
            {'nombre': 'Producto B', 'rentabilidad': 20.0},
            {'nombre': 'Producto C', 'rentabilidad': 15.0},
            {'nombre': 'Producto D', 'rentabilidad': 5.0}
        ]
        self.assertEqual(producto_mas_rentable(productos)['nombre'], 'Producto B')

    def test_vender_producto(self):
        # Abastecer el inventario para la prueba
        self.cursor.execute("UPDATE ingredientes SET cantidad = 10")
        self.conn.commit()

        # Intentar vender un producto
        response = self.app.post('/vender/1')
        self.assertEqual(response.data.decode(), '¡Vendido!')

        # Vaciar el inventario de un ingrediente y probar la venta fallida
        self.cursor.execute("UPDATE ingredientes SET cantidad = 0 WHERE nombre = 'Leche'")
        self.conn.commit()
        response = self.app.post('/vender/1')
        self.assertTrue("¡Oh no! Nos hemos quedado sin Leche" in response.data.decode())

if __name__ == '__main__':
    unittest.main()
