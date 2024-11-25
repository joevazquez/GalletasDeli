import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "GalletasDeliAdmin1234#$%"

# Ruta de la base de datos
DATABASE = "Database/GalletasDeliDB.db"


def get_db_connection():
    """Conecta a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a las filas como diccionarios
    return conn


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET"])
def login():
    # Renderiza el HTML del inicio de sesión
    return render_template("Inicio_sesion/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Procesar el registro de cliente
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        user = request.form["user"]
        estado = request.form["estado"]
        ciudad = request.form["ciudad"]
        calle_numero = request.form["calle_numero"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Concatenar los campos de dirección
        direccion = f"{calle_numero}, {ciudad}, {estado}"

        # Validar si el nombre de usuario ya existe
        conn = get_db_connection()
        usuario_existente = conn.execute(
            "SELECT 1 FROM Clientes WHERE User = ?", (user,)
        ).fetchone()

        if usuario_existente:
            flash(
                "El nombre de usuario ya está en uso. Por favor elige otro.", "danger"
            )
            conn.close()
            return redirect(url_for("register"))

        # Insertar los datos del cliente
        conn.execute(
            """
            INSERT INTO Clientes (User, Nombre, Direccion, Telefono, Contrasena)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user, f"{nombre} {apellido}", direccion, telefono, contrasena),
        )
        conn.commit()
        conn.close()

        flash("Registro de cliente exitoso. Por favor, inicie sesión.", "success")
        return redirect(url_for("login"))

    # Renderizar el formulario de registro inicial
    return render_template("Inicio_sesion/register.html")


@app.route("/register_empleado", methods=["GET", "POST"])
def register_empleado():
    if request.method == "POST":
        # Procesar el registro de empleado
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        user = request.form["user"]
        estado = request.form["estado"]
        ciudad = request.form["ciudad"]
        calle_numero = request.form["calle_numero"]
        rol = request.form["rol"]
        contrasena = request.form["contrasena"]

        # Concatenar los campos de dirección
        direccion = f"{calle_numero}, {ciudad}, {estado}"

        # Validar si el nombre de usuario ya existe
        conn = get_db_connection()
        usuario_existente = conn.execute(
            "SELECT 1 FROM Empleado WHERE User = ?", (user,)
        ).fetchone()

        if usuario_existente:
            flash(
                "El nombre de usuario ya está en uso. Por favor elige otro.", "danger"
            )
            conn.close()
            return redirect(url_for("register_empleado"))

        # Insertar los datos del empleado
        conn.execute(
            """
            INSERT INTO Empleado (User, Direccion, Rol, Contrasena)
            VALUES (?, ?, ?, ?)
        """,
            (user, direccion, rol, contrasena),
        )
        conn.commit()
        conn.close()

        flash("Registro de empleado exitoso. Por favor, inicie sesión.", "success")
        return redirect(url_for("login"))

    # Renderizar el formulario de registro de empleados
    return render_template("Inicio_sesion/register_empleado.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form.get("username")
    contrasena = request.form.get("password")
    es_empleado = request.form.get("es_empleado")  # Valor enviado como '0' o '1'

    print("Datos recibidos:")
    print(f"Usuario: {username}, Contraseña: {contrasena}, Es empleado: {es_empleado}")

    conn = get_db_connection()

    if (
        es_empleado == "1"
    ):  # Si el checkbox está marcado, verificar en la tabla de empleados
        print("Consultando en tabla Empleado...")
        user = conn.execute(
            """
            SELECT ID_empleado AS id, Rol AS role
            FROM Empleado
            WHERE User = ? AND Contrasena = ?
        """,
            (username, contrasena),
        ).fetchone()
        print("Resultado:", user)

        if user:
            # Usuario autenticado como empleado
            session["user_type"] = "empleado"
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]
            conn.close()
            return render_template(
                "hola_mundo.html", role=user["role"]
            )  # Mostrar "Hola mundo"
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
            conn.close()
            return redirect(url_for("login"))
    elif (
        es_empleado == "0"
    ):  # Si el checkbox no está marcado, verificar en la tabla de clientes
        print("Consultando en tabla Clientes...")
        user = conn.execute(
            """
            SELECT ID_cliente AS id, Nombre AS name
            FROM Clientes
            WHERE User = ? AND Contrasena = ?
        """,
            (username, contrasena),
        ).fetchone()
        print("Resultado:", user)

        if user:
            # Usuario autenticado como cliente
            session["user_type"] = "cliente"
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            conn.close()
            return render_template(
                "Catalogo/catalogo-productos.html", user_name=user["name"]
            )
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
            conn.close()
            return redirect(url_for("login"))
    else:
        # Caso inesperado
        flash("Error al determinar el tipo de usuario.", "danger")
        return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("user_type") != "empleado":
        flash("Acceso no autorizado. Por favor, inicie sesión como empleado.", "danger")
        return redirect(url_for("login"))

    user_role = session.get("user_role")
    return f"Bienvenido al panel de empleados. Rol: {user_role}."


@app.route("/catalogo_productos")
def catalogo_productos():
    # Verifica si el usuario está autenticado y es cliente
    if "user_id" not in session or session.get("user_type") != "cliente":
        flash("Acceso no autorizado. Por favor, inicie sesión como cliente.", "danger")
        return redirect(url_for("login"))

    # Recupera el nombre del cliente de la sesión
    user_name = session.get("user_name", "Usuario")  # Valor por defecto: 'Usuario'

    # Renderiza la página del catálogo y pasa el nombre del usuario
    return render_template("Catalogo/catalogo-productos.html", user_name=user_name)


@app.route("/dashboard-ventas")
def dashboard_ventas():
    return render_template("dashboard_ventas.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
