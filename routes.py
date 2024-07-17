from flask import Blueprint, render_template
from models import get_ingredientes, get_productos, get_producto_mas_rentable

main = Blueprint('main', __name__)

@main.route('/')
def index():
    ingredientes = get_ingredientes()
    productos = get_productos()
    producto_mas_rentable = get_producto_mas_rentable()
    return render_template('index.html', ingredientes=ingredientes, productos=productos, producto_mas_rentable=producto_mas_rentable)
