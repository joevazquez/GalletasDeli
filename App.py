import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Procesar el registro de cliente
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        user = request.form['user']
        estado = request.form['estado']
        ciudad = request.form['ciudad']
        calle_numero = request.form['calle_numero']
        telefono = request.form['telefono']
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

        # Insertar los datos del cliente
        conn.execute('''
            INSERT INTO Clientes (User, Nombre, Direccion, Telefono, Contrasena)
            VALUES (?, ?, ?, ?, ?)
        ''', (user, f"{nombre} {apellido}", direccion, telefono, contrasena))
        conn.commit()
        conn.close()

        flash('Registro de cliente exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('login'))

    # Renderizar el formulario de registro inicial
    return render_template('Inicio_sesion/register.html')


@app.route('/register_empleado', methods=['GET', 'POST'])
def register_empleado():
    if request.method == 'POST':
        # Procesar el registro de empleado
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        user = request.form['user']
        estado = request.form['estado']
        ciudad = request.form['ciudad']
        calle_numero = request.form['calle_numero']
        telefono = request.form['telefono']
        rol = request.form['rol']
        contrasena = request.form['contrasena']

        # Concatenar los campos de dirección
        direccion = f"{calle_numero}, {ciudad}, {estado}"

        # Validar si el nombre de usuario ya existe
        conn = get_db_connection()
        usuario_existente = conn.execute('SELECT 1 FROM Empleado WHERE User = ?', (user,)).fetchone()

        if usuario_existente:
            flash('El nombre de usuario ya está en uso. Por favor elige otro.', 'danger')
            conn.close()
            return redirect(url_for('register_empleado'))

        # Insertar los datos del empleado
        conn.execute('''
            INSERT INTO Empleado (User, Direccion, Rol, Contrasena)
            VALUES (?, ?, ?, ?)
        ''', (user, direccion, rol, contrasena))
        conn.commit()
        conn.close()

        flash('Registro de empleado exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('login'))

    # Renderizar el formulario de registro de empleados
    return render_template('Inicio_sesion/register_empleado.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
