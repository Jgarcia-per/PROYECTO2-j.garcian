from app import db

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    calorias = db.Column(db.Float, nullable=False)
    inventario = db.Column(db.Integer, nullable=False)
    es_vegetariano = db.Column(db.Boolean, nullable=False)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_publico = db.Column(db.Float, nullable=False)
    rentabilidad = db.Column(db.Float, nullable=False)

class ProductoIngrediente(db.Model):
    __tablename__ = 'producto_ingrediente'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingredientes.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto', backref=db.backref('producto_ingredientes', lazy=True))
    ingrediente = db.relationship('Ingrediente', backref=db.backref('producto_ingredientes', lazy=True))

# Funciones para obtener datos
def get_ingredientes():
    return Ingrediente.query.all()

def get_productos():
    return Producto.query.all()

def get_producto_mas_rentable():
    return Producto.query.order_by(Producto.rentabilidad.desc()).first()
