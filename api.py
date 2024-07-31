from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models.model import db, Ingrediente, Producto, ProductoIngrediente, User

app = Flask(__name__)
api = Api(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1027150930Juan*@localhost/heladeria'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Cambia esto por una clave secreta más segura

db.init_app(app)
jwt = JWTManager(app)

# Funciones necesarias
def es_ingrediente_sano(calorias, vegetariano):
    return calorias < 100 or vegetariano

def contar_calorias(ingredientes):
    total_calorias = sum(ingrediente.calorias for ingrediente in ingredientes) * 0.95
    return round(total_calorias, 2)

def calcular_costo(ingredientes):
    return round(sum(ingrediente.costo for ingrediente in ingredientes), 2)

def calcular_rentabilidad(precio_venta, ingredientes):
    costo = calcular_costo(ingredientes)
    return round(precio_venta - costo, 2)

def producto_mas_rentable(productos):
    return max(productos, key=lambda x: x['rentabilidad'])

def vender_producto(producto_id):
    producto_ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto_id).all()
    for pi in producto_ingredientes:
        ingrediente = Ingrediente.query.get(pi.ingrediente_id)
        if ingrediente.cantidad <= 0:
            raise ValueError(f"{ingrediente.nombre}")
    
    for pi in producto_ingredientes:
        ingrediente = Ingrediente.query.get(pi.ingrediente_id)
        ingrediente.cantidad -= 1
        db.session.commit()

class IngredienteResource(Resource):
    @jwt_required()
    def get(self, id=None, nombre=None):
        if id:
            ingrediente = Ingrediente.query.get(id)
            if ingrediente:
                return jsonify({
                    'id': ingrediente.id,
                    'nombre': ingrediente.nombre,
                    'calorias': ingrediente.calorias,
                    'vegetariano': ingrediente.vegetariano,
                    'costo': ingrediente.costo,
                    'cantidad': ingrediente.cantidad
                })
            return {'message': 'Ingrediente no encontrado'}, 404
        if nombre:
            ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
            if ingrediente:
                return jsonify({
                    'id': ingrediente.id,
                    'nombre': ingrediente.nombre,
                    'calorias': ingrediente.calorias,
                    'vegetariano': ingrediente.vegetariano,
                    'costo': ingrediente.costo,
                    'cantidad': ingrediente.cantidad
                })
            return {'message': 'Ingrediente no encontrado'}, 404
        ingredientes = Ingrediente.query.all()
        return jsonify([{
            'id': ingrediente.id,
            'nombre': ingrediente.nombre,
            'calorias': ingrediente.calorias,
            'vegetariano': ingrediente.vegetariano,
            'costo': ingrediente.costo,
            'cantidad': ingrediente.cantidad
        } for ingrediente in ingredientes])

    @jwt_required()
    def post(self):
        data = request.get_json()
        nuevo_ingrediente = Ingrediente(
            nombre=data['nombre'],
            calorias=data['calorias'],
            vegetariano=data['vegetariano'],
            costo=data['costo'],
            cantidad=data['cantidad']
        )
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return {'message': 'Ingrediente creado con éxito'}, 201

    @jwt_required()
    def put(self, id):
        data = request.get_json()
        ingrediente = Ingrediente.query.get(id)
        if not ingrediente:
            return {'message': 'Ingrediente no encontrado'}, 404
        ingrediente.nombre = data['nombre']
        ingrediente.calorias = data['calorias']
        ingrediente.vegetariano = data['vegetariano']
        ingrediente.costo = data['costo']
        ingrediente.cantidad = data['cantidad']
        db.session.commit()
        return {'message': 'Ingrediente actualizado con éxito'}, 200

    @jwt_required()
    def delete(self, id):
        ingrediente = Ingrediente.query.get(id)
        if not ingrediente:
            return {'message': 'Ingrediente no encontrado'}, 404
        db.session.delete(ingrediente)
        db.session.commit()
        return {'message': 'Ingrediente eliminado con éxito'}, 200

class ProductoResource(Resource):
    @jwt_required()
    def get(self, id=None, nombre=None):
        if id:
            producto = Producto.query.get(id)
            if producto:
                ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto.id).all()
                return jsonify({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'ingredientes': [{
                        'id': i.ingrediente_id,
                        'nombre': Ingrediente.query.get(i.ingrediente_id).nombre
                    } for i in ingredientes]
                })
            return {'message': 'Producto no encontrado'}, 404
        if nombre:
            producto = Producto.query.filter_by(nombre=nombre).first()
            if producto:
                ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto.id).all()
                return jsonify({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'ingredientes': [{
                        'id': i.ingrediente_id,
                        'nombre': Ingrediente.query.get(i.ingrediente_id).nombre
                    } for i in ingredientes]
                })
            return {'message': 'Producto no encontrado'}, 404
        productos = Producto.query.all()
        return jsonify([{
            'id': producto.id,
            'nombre': producto.nombre,
            'ingredientes': [{
                'id': i.ingrediente_id,
                'nombre': Ingrediente.query.get(i.ingrediente_id).nombre
            } for i in ProductoIngrediente.query.filter_by(producto_id=producto.id).all()]
        } for producto in productos])

    @jwt_required()
    def post(self):
        data = request.get_json()
        nuevo_producto = Producto(nombre=data['nombre'])
        db.session.add(nuevo_producto)
        db.session.commit()
        for ingrediente_id in data['ingredientes']:
            nuevo_producto_ingrediente = ProductoIngrediente(
                producto_id=nuevo_producto.id,
                ingrediente_id=ingrediente_id
            )
            db.session.add(nuevo_producto_ingrediente)
        db.session.commit()
        return {'message': 'Producto creado con éxito'}, 201

    @jwt_required()
    def put(self, id):
        data = request.get_json()
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        producto.nombre = data['nombre']
        db.session.commit()
        ProductoIngrediente.query.filter_by(producto_id=producto.id).delete()
        for ingrediente_id in data['ingredientes']:
            nuevo_producto_ingrediente = ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ingrediente_id
            )
            db.session.add(nuevo_producto_ingrediente)
        db.session.commit()
        return {'message': 'Producto actualizado con éxito'}, 200

    @jwt_required()
    def delete(self, id):
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        ProductoIngrediente.query.filter_by(producto_id=producto.id).delete()
        db.session.delete(producto)
        db.session.commit()
        return {'message': 'Producto eliminado con éxito'}, 200

class ProductoCaloriasResource(Resource):
    @jwt_required()
    def get(self, id):
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto.id).all()
        calorias = contar_calorias([Ingrediente.query.get(i.ingrediente_id) for i in ingredientes])
        return jsonify({'id': producto.id, 'nombre': producto.nombre, 'calorias': calorias})

class ProductoRentabilidadResource(Resource):
    @jwt_required()
    def get(self, id):
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto.id).all()
        ingredientes_obj = [Ingrediente.query.get(i.ingrediente_id) for i in ingredientes]
        precio_venta = float(request.args.get('precio_venta', 0))
        rentabilidad = calcular_rentabilidad(precio_venta, ingredientes_obj)
        return jsonify({'id': producto.id, 'nombre': producto.nombre, 'rentabilidad': rentabilidad})

class ProductoCostoResource(Resource):
    @jwt_required()
    def get(self, id):
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        ingredientes = ProductoIngrediente.query.filter_by(producto_id=producto.id).all()
        costo = calcular_costo([Ingrediente.query.get(i.ingrediente_id) for i in ingredientes])
        return jsonify({'id': producto.id, 'nombre': producto.nombre, 'costo': costo})

class ProductoVenderResource(Resource):
    @jwt_required()
    def post(self, id):
        try:
            vender_producto(id)
            return {'message': 'Producto vendido con éxito'}, 200
        except ValueError as e:
            return {'message': f'No se pudo vender el producto: {e}'}, 400

class IngredienteSanoResource(Resource):
    @jwt_required()
    def get(self, id):
        ingrediente = Ingrediente.query.get(id)
        if not ingrediente:
            return {'message': 'Ingrediente no encontrado'}, 404
        sano = es_ingrediente_sano(ingrediente.calorias, ingrediente.vegetariano)
        return jsonify({'id': ingrediente.id, 'nombre': ingrediente.nombre, 'sano': sano})

class ProductoReabastecerResource(Resource):
    @jwt_required()
    def post(self, id):
        data = request.get_json()
        cantidad = data.get('cantidad', 0)
        producto_ingredientes = ProductoIngrediente.query.filter_by(producto_id=id).all()
        for pi in producto_ingredientes:
            ingrediente = Ingrediente.query.get(pi.ingrediente_id)
            ingrediente.cantidad += cantidad
        db.session.commit()
        return {'message': 'Producto reabastecido con éxito'}, 200

class ProductoRenovarResource(Resource):
    @jwt_required()
    def post(self, id):
        data = request.get_json()
        nuevo_nombre = data.get('nombre')
        nuevo_ingredientes = data.get('ingredientes')
        producto = Producto.query.get(id)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        if nuevo_nombre:
            producto.nombre = nuevo_nombre
        ProductoIngrediente.query.filter_by(producto_id=id).delete()
        if nuevo_ingredientes:
            for ingrediente_id in nuevo_ingredientes:
                nuevo_producto_ingrediente = ProductoIngrediente(
                    producto_id=id,
                    ingrediente_id=ingrediente_id
                )
                db.session.add(nuevo_producto_ingrediente)
        db.session.commit()
        return {'message': 'Producto renovado con éxito'}, 200

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        nombre = data.get('nombre')
        password = data.get('password')
        user = User.query.filter_by(nombre=nombre).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token)
        return {'message': 'Nombre de usuario o contraseña incorrectos'}, 401

api.add_resource(LoginResource, '/login')
api.add_resource(IngredienteResource, '/ingredientes', '/ingredientes/<int:id>')
api.add_resource(ProductoResource, '/productos', '/productos/<int:id>')
api.add_resource(ProductoCaloriasResource, '/productos/<int:id>/calorias')
api.add_resource(ProductoRentabilidadResource, '/productos/<int:id>/rentabilidad')
api.add_resource(ProductoCostoResource, '/productos/<int:id>/costo')
api.add_resource(ProductoVenderResource, '/productos/<int:id>/vender')
api.add_resource(IngredienteSanoResource, '/ingredientes/<int:id>/sano')
api.add_resource(ProductoReabastecerResource, '/productos/<int:id>/reabastecer')
api.add_resource(ProductoRenovarResource, '/productos/<int:id>/renovar')

if __name__ == '__main__':
    app.run(debug=True)
