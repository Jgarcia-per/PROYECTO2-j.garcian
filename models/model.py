from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

db = SQLAlchemy()

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    calorias = db.Column(db.Integer)
    vegetariano = db.Column(db.Boolean)
    costo = db.Column(db.Float)
    cantidad = db.Column(db.Integer)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

class ProductoIngrediente(db.Model):
    __tablename__ = 'producto_ingredientes'
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), primary_key=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingredientes.id'), primary_key=True)

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    rol = db.Column(db.Enum('admin', 'user'), nullable=False)
