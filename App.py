import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'GalletasDeliAdmin1234#$%' 

# Ruta de la base de datos
DATABASE = 'Database/GalletasDeliDB.db'

def get_db_connection():
    """Conecta a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a las filas como diccionarios
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    # Renderiza el HTML del inicio de sesión
    return render_template('Inicio_sesion/login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()  # Recibir datos en formato JSON
    username = data.get('username')
    contrasena = data.get('password')

    conn = get_db_connection()

    # Verificar si el usuario es un cliente
    cliente = conn.execute('''
        SELECT c.ID_cliente AS id, c.Nombre AS name, u.Contrasena
        FROM Clientes c
        INNER JOIN Usuarios u ON c.User = u.User_cliente
        WHERE u.User_cliente = ? AND u.Contrasena = ?
    ''', (username, contrasena)).fetchone()

    # Verificar si el usuario es un empleado
    empleado = conn.execute('''
        SELECT e.ID_empleado AS id, e.Rol AS role, u.Contrasena
        FROM Empleado e
        INNER JOIN Usuarios u ON e.User = u.User_empleado
        WHERE u.User_empleado = ? AND u.Contrasena = ?
    ''', (username, contrasena)).fetchone()

    conn.close()

    if cliente:
        # Usuario es cliente
        session['user_type'] = 'cliente'
        session['user_id'] = cliente['id']
        session['user_name'] = cliente['name']
        return redirect(url_for('catalogo_productos'))
    elif empleado:
        # Usuario es empleado
        session['user_type'] = 'empleado'
        session['user_id'] = empleado['id']
        session['user_role'] = empleado['role']
        return jsonify({'message': 'Inicio de sesión exitoso', 'redirect': '/dashboard'}), 200
    else:
        # Credenciales incorrectas
        return jsonify({'message': 'Usuario o contraseña incorrectos.'}), 401

@app.route('/catalogo_productos')
def catalogo_productos():
    # Verificar si el cliente está autenticado
    if 'user_id' in session and session.get('user_type') == 'cliente':
        return render_template('Catalogo/catalogo-productos.html')
    else:
        flash('Por favor, inicie sesión para acceder al catálogo.', 'warning')
        return redirect(url_for('Catalogo/catalogo-productos.html'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor, inicie sesión para acceder al panel.', 'warning')
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    user_name = session.get('user_name')
    user_role = session.get('user_role')

    if user_type == 'cliente':
        return f"Bienvenido a Gelletas Deli, {user_name}."
    elif user_type == 'empleado':
        return f"Bienvenido al panel de Empleado."
    else:
        flash('Hubo un error al determinar el tipo de usuario.', 'danger')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capturar los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        user = request.form['user']
        estado = request.form['estado']
        ciudad = request.form['ciudad']
        calle_numero = request.form['calle_numero']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        # Concatenar los campos de dirección
        direccion = f"{calle_numero}, {ciudad}, {estado}"

        # Validar si el nombre de usuario ya existe
        conn = get_db_connection()
        usuario_existente = conn.execute('SELECT 1 FROM Clientes WHERE User = ?', (user,)).fetchone()

        if usuario_existente:
            flash('El nombre de usuario ya está en uso. Por favor elige otro.', 'danger')
            conn.close()
            return redirect(url_for('register'))

        # Insertar los datos en la base de datos
        conn.execute('''
            INSERT INTO Clientes (User, Nombre, Direccion, Telefono, Email, Contrasena)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user, f"{nombre} {apellido}", direccion, telefono, correo, contrasena))
        conn.commit()
        conn.close()

        # Confirmar el registro y redirigir al login
        flash('Registro exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('login'))

    # Renderizar el formulario de registro
    return render_template('Inicio_sesion/register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
