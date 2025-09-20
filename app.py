from flask import Flask, render_template, request, redirect, url_for
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


@login_manager.user_loader
def load_user(user_id):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    data = cursor.fetchone()
    cerrar_conexion(conn)

    if data:
        return Usuario(data[0], data[1], data[2])  # (id_usuario, nombre, password)
    return None


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
# Listar productos
# -------------------------------
@app.route('/productos')
def listar_productos():
    conn = conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, precio FROM productos")
    productos = cursor.fetchall()
    cerrar_conexion(conn)
    return render_template('productos/list.html', productos=productos)


# -------------------------------
# Crear producto
# -------------------------------
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, precio) VALUES (%s, %s)",
            (nombre, precio)
        )
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_productos'))

    return render_template('productos/form.html', title="Nuevo Producto")


# -------------------------------
# Editar producto
# -------------------------------
@app.route('/productos/editar/<int:pid>', methods=['GET', 'POST'])
def editar_producto(pid):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']

        cursor.execute(
            "UPDATE productos SET nombre=%s, precio=%s WHERE id=%s",
            (nombre, precio, pid)
        )
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_productos'))

    cursor.execute("SELECT id, nombre, precio FROM productos WHERE id=%s", (pid,))
    producto = cursor.fetchone()
    cerrar_conexion(conn)
    return render_template('productos/edit.html', producto=producto)


# -------------------------------
# Eliminar producto
# -------------------------------
@app.route('/productos/eliminar/<int:pid>', methods=['POST'])
def eliminar_producto(pid):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s", (pid,))
    conn.commit()
    cerrar_conexion(conn)
    return redirect(url_for('listar_productos'))

#----------------------------------------------
# Rutas para clientes
#----------------------------------------------

# -------------------------------
# Listar clientes
# -------------------------------
@app.route('/clientes')
def listar_clientes():
    conn = conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, mail FROM clientes")
    clientes = cursor.fetchall()
    cerrar_conexion(conn)
    return render_template('clientes/list.html', clientes=clientes)


# -------------------------------
# Crear cliente
# -------------------------------
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def crear_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombre, mail) VALUES (%s, %s)",
            (nombre, mail)
        )
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_clientes'))

    return render_template('clientes/form.html', title="Nuevo Cliente")


# -------------------------------
# Editar cliente
# -------------------------------
@app.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
def editar_cliente(cid):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']

        cursor.execute(
            "UPDATE clientes SET nombre=%s, mail=%s WHERE id_usuario=%s",
            (nombre, mail, cid)
        )
        conn.commit()
        cerrar_conexion(conn)
        return redirect(url_for('listar_clientes'))

    cursor.execute("SELECT id_usuario, nombre, mail FROM clientes WHERE id_usuario=%s", (cid,))
    cliente = cursor.fetchone()
    cerrar_conexion(conn)
    return render_template('clientes/edit.html', cliente=cliente)


# -------------------------------
# Eliminar cliente
# -------------------------------
@app.route('/clientes/eliminar/<int:cid>', methods=['POST'])
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
        password = generate_password_hash(request.form['password'])

        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, password) VALUES (%s, %s)", (usuario, password))
        conn.commit()
        cerrar_conexion(conn)
        return "Usuario registrado exitosamente"

    return render_template('registro.html')


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
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", (usuario,))
        data = cursor.fetchone()
        cerrar_conexion(conn)

        if data and check_password_hash(data[2], password):
            user = Usuario(data[0], data[1], data[2])
            login_user(user)
            return "Login exitoso"

        return "Credenciales incorrectas"

    return render_template('login.html')


# -------------------------------
# Perfil
# -------------------------------
@app.route('/perfil')
def perfil():
    if current_user.is_authenticated:
        return f'Bienvenido, {current_user.nombre}'
    return 'Debes iniciar sesión para ver tu perfil'


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
    return "Sesión cerrada exitosamente"


if __name__ == '__main__':
    app.run(debug=True)
