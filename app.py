from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, identity_changed
from models.model import db, User, Ingrediente, Producto, ProductoIngrediente
import bcrypt

app = Flask(__name__)
app.config.from_object('config.Config')

# Inicializar SQLAlchemy
db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configuración de Flask-Principals
principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))

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

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if isinstance(current_user, User):
        identity.provides.add(UserNeed(current_user.id))
        if current_user.rol:
            identity.provides.add(RoleNeed(current_user.rol))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        email = request.form['email']
        rol = request.form['rol']
        
        # Cifrar la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Crear nuevo usuario
        new_user = User(nombre=nombre, password=hashed_password.decode('utf-8'), email=email, rol=rol)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        user = User.query.filter_by(nombre=nombre).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            identity_changed.send(app, identity=Identity(user.id))
            return redirect(url_for('index'))  # Redirigir a la página de inicio
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(app, identity=AnonymousIdentity())
    return redirect(url_for('index'))

# Ruta para la página de inicio
@app.route('/index')
@login_required
def index():
    ingredientes = Ingrediente.query.all()
    return render_template('index.html', ingredientes=ingredientes, user=current_user)

# Ruta para seleccionar ingredientes
@app.route('/seleccionar_ingredientes')
def seleccionar_ingredientes():
    ingredientes = Ingrediente.query.all()
    return render_template('seleccionar_ingredientes.html', ingredientes=ingredientes)

# Ruta para verificar ingredientes
@app.route('/verificar_ingredientes', methods=['POST'])
def verificar_ingredientes():
    ingredientes_ids = request.form.getlist('ingredientes')
    ingredientes = Ingrediente.query.filter(Ingrediente.id.in_(ingredientes_ids)).all()
    
    total_calorias = sum(i.calorias for i in ingredientes)
    es_vegetariano = any(i.vegetariano for i in ingredientes)
    
    sano = es_ingrediente_sano(total_calorias, es_vegetariano)
    
    return render_template('resultado_ingredientes.html', sano=sano)

# Ruta para contar calorías
@app.route('/contar_calorias', methods=['POST'])
def contar_calorias_route():
    ingredientes_ids = request.form.getlist('ingredientes')
    ingredientes = Ingrediente.query.filter(Ingrediente.id.in_(ingredientes_ids)).all()
    
    calorias_list = [i.calorias for i in ingredientes]
    total_calorias = contar_calorias(calorias_list)
    
    return render_template('resultado_calorias.html', total_calorias=total_calorias)

# Ruta para calcular el costo
@app.route('/calcular_costo', methods=['POST'])
def calcular_costo_route():
    ingredientes_ids = request.form.getlist('ingredientes')
    ingredientes = Ingrediente.query.filter(Ingrediente.id.in_(ingredientes_ids)).all()
    
    ingredientes_dict = [{'nombre': i.nombre, 'precio': float(i.costo)} for i in ingredientes]
    total_costo = calcular_costo(ingredientes_dict)
    
    return render_template('resultado_costo.html', total_costo=total_costo)

# Ruta para calcular rentabilidad
@app.route('/calcular_rentabilidad', methods=['POST'])
def calcular_rentabilidad_route():
    precio_venta = float(request.form.get('precio_venta'))
    ingredientes_ids = request.form.getlist('ingredientes')
    ingredientes = Ingrediente.query.filter(Ingrediente.id.in_(ingredientes_ids)).all()
    
    ingredientes_dict = [{'nombre': i.nombre, 'precio': float(i.costo)} for i in ingredientes]
    rentabilidad = calcular_rentabilidad(precio_venta, ingredientes_dict)
    
    return render_template('resultado_rentabilidad.html', rentabilidad=rentabilidad)

# Ruta para encontrar el producto más rentable
@app.route('/producto_mas_rentable', methods=['POST'])
def producto_mas_rentable_route():
    productos = request.form.getlist('productos')
    productos_dict = [{'nombre': p.split(',')[0], 'rentabilidad': float(p.split(',')[1])} for p in productos]
    mas_rentable = producto_mas_rentable(productos_dict)
    
    return render_template('resultado_mas_rentable.html', producto=mas_rentable['nombre'])

# Ruta para vender producto
@app.route('/vender/<int:producto_id>', methods=['POST'])
def vender_route(producto_id):
    try:
        vender_producto(producto_id)
        return "¡Vendido!"
    except ValueError as e:
        return f"¡Oh no! Nos hemos quedado sin {e}"

# Ruta protegida para administradores
@app.route('/admin')
@login_required
@admin_permission.require(http_exception=403)
def admin():
    return "¡Bienvenido, Admin!"

# Ruta protegida para usuarios
@app.route('/user')
@login_required
@user_permission.require(http_exception=403)
def user():
    return "¡Bienvenido, Usuario!"

# Define otras rutas de tu aplicación aquí

if __name__ == '__main__':
    app.run(debug=True)
