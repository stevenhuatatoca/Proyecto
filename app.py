from flask import Flask, render_template, request, redirect, url_for, flash
from conexion.conexion import conexion, cerrar_conexion
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from models import Usuario

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# -------------------------------
# Login Manager
# -------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = None  # No duplicar mensaje en formulario

@login_manager.user_loader
def load_user(user_id):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    data = cursor.fetchone()
    cerrar_conexion(conn)

    if data:
        return Usuario(data[0], data[1], data[2])
    return None

@login_manager.unauthorized_handler
def unauthorized():
    # Redirige al login si no está autenticado (mensaje global se muestra en base.html)
    flash("Debes iniciar sesión para acceder a esta página", "info")
    return redirect(url_for('login'))

# -------------------------------
# Rutas principales
# -------------------------------
@app.route('/')
def inicio():
    return render_template('index.html', title="Inicio")

@app.route('/about')
def about():
    return render_template('about.html', title="Acerca de")

# -------------------------------
# Productos
# -------------------------------
@app.route('/productos')
@login_required
def listar_productos():
    conn = conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, precio FROM productos")
    productos = cursor.fetchall()
    cerrar_conexion(conn)
    return render_template('productos/list.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, precio) VALUES (%s, %s)", (nombre, precio))
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_productos'))
    
    return render_template('productos/form.html', title="Nuevo Producto")

@app.route('/productos/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def editar_producto(pid):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s WHERE id=%s", (nombre, precio, pid))
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_productos'))
    
    cursor.execute("SELECT id, nombre, precio FROM productos WHERE id=%s", (pid,))
    producto = cursor.fetchone()
    cerrar_conexion(conn)
    return render_template('productos/edit.html', producto=producto)

@app.route('/productos/eliminar/<int:pid>', methods=['POST'])
@login_required
def eliminar_producto(pid):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s", (pid,))
    conn.commit()
    cerrar_conexion(conn)
    return redirect(url_for('listar_productos'))

# -------------------------------
# Clientes
# -------------------------------
@app.route('/clientes')
@login_required
def listar_clientes():
    conn = conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, mail FROM clientes")
    clientes = cursor.fetchall()
    cerrar_conexion(conn)
    return render_template('clientes/list.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def crear_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, mail) VALUES (%s, %s)", (nombre, mail))
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_clientes'))
    
    return render_template('clientes/form.html', title="Nuevo Cliente")

@app.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cid):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']
        cursor.execute("UPDATE clientes SET nombre=%s, mail=%s WHERE id_usuario=%s", (nombre, mail, cid))
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_clientes'))
    
    cursor.execute("SELECT id_usuario, nombre, mail FROM clientes WHERE id_usuario=%s", (cid,))
    cliente = cursor.fetchone()
    cerrar_conexion(conn)
    return render_template('clientes/edit.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:cid>', methods=['POST'])
@login_required
def eliminar_cliente(cid):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_usuario=%s", (cid,))
    conn.commit()
    cerrar_conexion(conn)
    return redirect(url_for('listar_clientes'))

# -------------------------------
# Registro de usuarios
# -------------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validación servidor
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for('registro'))

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", 
                       (usuario, generate_password_hash(password)))
        conn.commit()
        cerrar_conexion(conn)

        flash("Usuario registrado correctamente", "success")
        return redirect(url_for('login'))

    return render_template('usuarios/registro.html')

# -------------------------------
# Login
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        data = cursor.fetchone()
        cerrar_conexion(conn)

        if not data:
            flash("Usuario no existe", "danger")
            return redirect(url_for('login'))

        if data and check_password_hash(data[2], password):
            user = Usuario(data[0], data[1], data[2])
            login_user(user)
            flash("Sesión iniciada correctamente", "success")
            return redirect(url_for('inicio'))
        else:
            flash("Usuario o contraseña inválida", "danger")
            return redirect(url_for('login'))
    
    return render_template('usuarios/login.html')

# -------------------------------
# Perfil
# -------------------------------
@app.route('/perfil')
@login_required
def perfil():
    return f'Bienvenido, {current_user.usuario}'

# -------------------------------
# Dashboard
# -------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return "Bienvenido al panel de control"

# -------------------------------
# Logout
# -------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('inicio'))

# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
