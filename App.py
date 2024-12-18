import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import json
from datetime import datetime, timedelta
import pandas as pd
import io
import xlsxwriter
import random
import string

app = Flask(__name__)
app.secret_key = "GalletasDeliAdmin1234#$%"

# Ruta de la base de datos
DATABASE = "Database/GalletasDeliDB.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a los resultados como diccionarios
    return conn

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/login", methods=["GET"])
def login():
    # Renderiza el HTML del inicio de sesión
    return render_template("Inicio_sesion/login.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/register_empleado", methods=["GET", "POST"])
def register_empleado():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        user = request.form["user"]
        estado = request.form["estado"]
        ciudad = request.form["ciudad"]
        calle_numero = request.form["calle_numero"]
        rol = request.form["rol"]
        contrasena = request.form.get("contrasena")  # Capturar contraseña correctamente

        # Depurar
        print(f"Contraseña recibida: {contrasena}")

        direccion = f"{calle_numero}, {ciudad}, {estado}"
        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO Empleado (Nombre, Direccion, User, Rol, Contrasena)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f"{nombre} {apellido}", direccion, user, rol, contrasena),
            )
            conn.commit()
            flash("Registro de empleado exitoso. Por favor, inicie sesión.", "success")
        except sqlite3.Error as e:
            print(f"Error al insertar en la base de datos: {e}")
            flash("Ocurrió un error al registrar el empleado.", "danger")
        finally:
            conn.close()

        return redirect(url_for("login"))

    return render_template("Inicio_sesion/register_empleado.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form.get("username")
    contrasena = request.form.get("password")
    es_empleado = request.form.get("es_empleado")

    print("Datos recibidos:")
    print(f"Usuario: {username}, Contraseña: {contrasena}, Es empleado: {es_empleado}")

    conn = get_db_connection()

    if es_empleado == 'on':  # Si el checkbox está marcado, verificar en la tabla de empleados
        print("Consultando en tabla Empleado...")
        user = conn.execute(
            """
            SELECT ID_empleado AS id, Rol AS role, Nombre AS name
            FROM Empleado
            WHERE User = ? AND Contrasena = ?
            """,
            (username, contrasena),
        ).fetchone()

        if user:
            print("Resultado en tabla Empleado:", dict(user))
            # Usuario autenticado como empleado
            session["user_type"] = "empleado"
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]
            session["user_name"] = user["name"]
            conn.close()

            # Redirigir según el rol
            if user["role"].lower() == "almacenista":
                return redirect(url_for("almacenista_dashboard"))
            elif user["role"].lower() == "administrador":
                return redirect(url_for("admin_dashboard"))
            elif user["role"].lower() == "produccion":
                return redirect(url_for("produccion_dashboard"))
            elif user["role"].lower() == "qa":
                return redirect(url_for("qa_dashboard"))
            elif user["role"].lower() == "ventas":
                return redirect(url_for("ventas_inventario"))
            else:
                flash("Rol no reconocido.", "warning")
                return redirect(url_for("login"))
        else:
            print("Empleado no encontrado.")
            print("Error login empleado")
            flash("Usuario o contraseña incorrectos.", "danger")
            conn.close()
            return redirect(url_for("login"))

    else:  # Si el checkbox no está marcado, verificar en la tabla de clientes
        print("Consultando en tabla Clientes...")
        user = conn.execute(
            """
            SELECT ID_cliente AS id, Nombre AS name
            FROM Clientes
            WHERE User = ? AND Contrasena = ?
            """,
            (username, contrasena),
        ).fetchone()

        if user:
            print("Resultado en tabla Clientes:", dict(user))
            # Usuario autenticado como cliente
            session["user_type"] = "cliente"
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            conn.close()
            return redirect(url_for("catalogo_productos"))
        else:
            print("Cliente no encontrado.")
            flash("Usuario o contraseña incorrectos.", "danger")
            conn.close()
            return redirect(url_for("login"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/catalogo_productos', methods=['GET', 'POST'])
def catalogo_productos():
    if request.method == 'POST':
        # Recibe los datos del formulario
        resumen_pedido = request.form.get('resumenPedido', 'Sin resumen disponible')
        total_pedido = request.form.get('totalPedido', 0)
        
        # Guarda los datos en la sesión
        session['resumen_pedido'] = resumen_pedido
        session['total_pedido'] = total_pedido
        
        # Redirige a la página de direcciones
        return redirect(url_for('direcciones'))
    
    # Carga el catálogo de productos
    return render_template(
        'Catalogo/catalogo-productos.html',
        user_pedido=session.get('resumen_pedido', 'Sin resumen disponible'),
        total_pedido=session.get('total_pedido', 0),
        user_name=session.get('user_name', 'Usuario')
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/direcciones', methods=['GET', 'POST'])
def direcciones():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    resumen_pedido = session.get('resumen_pedido', '{}')  # JSON vacío como valor predeterminado
    try:
        resumen_pedido = json.loads(resumen_pedido)  # Convertir el string JSON a un dict de Python
    except json.JSONDecodeError:
        resumen_pedido = {}

    total_pedido = session.get('total_pedido', 0)

    conn = get_db_connection()
    direccion = conn.execute(
        "SELECT Direccion FROM Clientes WHERE ID_cliente = ?",
        (user_id,)
    ).fetchone()
    direccion = direccion["Direccion"] if direccion and direccion["Direccion"] else None
    conn.close()

    return render_template(
        'direcciones/direcciones.html',
        direccion=direccion,
        resumen_pedido=resumen_pedido,
        total_pedido=total_pedido,
        user_name=session.get('user_name', 'Usuario')
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/actualizar_direccion', methods=['POST'])
def actualizar_direccion():
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400

    nueva_direccion = f"{data['estado']}, {data['ciudad']}, {data['delegacion']}, {data['colonia']}, {data['calle_numero']}"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Clientes SET Direccion = ? WHERE ID_cliente = ?",
            (nueva_direccion, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'No se encontró el usuario en la base de datos'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en la base de datos: {str(e)}'}), 500
    finally:
        conn.close()

    return jsonify({'success': True, 'updated_direccion': nueva_direccion, 'message': 'Dirección actualizada exitosamente'})

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/pago', methods=['POST'])
def pago():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    # Recuperar datos del pedido desde la sesión
    resumen_pedido = session.get('resumen_pedido', {})
    total_pedido = session.get('total_pedido', 0)

    if not resumen_pedido or total_pedido == 0:
        flash("No hay productos en el pedido o el total es inválido.", "warning")
        return redirect(url_for('catalogo_productos'))

    # Recuperar el historial de pedidos
    historial_pedidos = session.get('historial_pedidos', [])

    # Generar un ID único para el pedido
    new_id = str(len(historial_pedidos) + 1) + "-" + datetime.now().strftime('%H%M%S')

    # Crear un nuevo pedido
    nuevo_pedido = {
        "id": new_id,
        "products": resumen_pedido,
        "total": total_pedido,
        "creation_date": datetime.now().strftime('%Y-%m-%d'),
        "delivery_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        "status": "Procesando"
    }

    # Agregar el nuevo pedido al historial
    historial_pedidos.append(nuevo_pedido)
    session['historial_pedidos'] = historial_pedidos
    session.modified = True

    # Redirigir a la página de rastreo de órdenes
    flash("Pago realizado con éxito. Tu pedido está en proceso.", "success")
    return redirect(url_for('rastreo_pedidos'))  # No necesita ajuste si la ruta es /rastreo-pedidos

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    resumen_pedido = session.get('resumen_pedido', {})
    total_pedido = session.get('total_pedido', 0)

    # Validar que haya un pedido válido
    if not resumen_pedido or total_pedido == 0:
        flash("No hay productos en el pedido o el total es inválido.", "warning")
        return redirect(url_for('catalogo_productos'))

    # Generar un nuevo ID para el pedido
    historial_pedidos = session.get('historial_pedidos', [])
    new_id = str(len(historial_pedidos) + 1) + "-" + datetime.now().strftime('%H%M%S')

    # Crear el nuevo pedido
    nuevo_pedido = {
        "id": new_id,
        "products": resumen_pedido,  # Asegurarse de que es un diccionario
        "total": total_pedido,
        "creation_date": datetime.now().strftime('%Y-%m-%d'),
        "delivery_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        "status": "Procesando"
    }

    # Guardar el pedido en el historial
    historial_pedidos.append(nuevo_pedido)
    session['historial_pedidos'] = historial_pedidos
    session.modified = True

    flash("Pago procesado exitosamente. Tu pedido está en proceso.", "success")
    return redirect(url_for('rastreo_pedidos'))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/rastreo-pedidos')
def rastreo_pedidos():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    # Recuperar el historial de pedidos desde la sesión
    historial_pedidos = session.get('historial_pedidos', [])

    # Depuración: Imprimir el historial de pedidos en la consola
    print("Historial de Pedidos en /rastreo-pedidos:", historial_pedidos)

    # Renderizar la página con el historial de pedidos
    return render_template(
        'rastreo/rastreo-ordenes.html',  # Cambia aquí el nombre del archivo
        historial_pedidos=historial_pedidos,
        user_name=session.get('user_name', 'Usuario')
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/get-order-details/<order_id>', methods=['GET'])
def get_order_details(order_id):
    historial_pedidos = session.get('historial_pedidos', [])

    # Debug: muestra el historial de pedidos
    print("Historial de Pedidos en get-order-details:", historial_pedidos)

    # Buscar el pedido por ID
    pedido = next((p for p in historial_pedidos if p['id'] == order_id), None)

    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    # Convertir los productos de JSON a un diccionario de Python
    try:
        productos = json.loads(pedido['products'])
    except json.JSONDecodeError:
        return jsonify({"error": "Formato de productos inválido"}), 500

    # Transformar los datos de productos al formato requerido
    productos_detalle = []
    for producto, cantidades in productos.items():
        productos_detalle.append({
            "name": producto,
            "quantity": cantidades.get('half-kilo', 0) + cantidades.get('six-pieces', 0),
            "price": cantidades.get('half-kilo', 0) * 100 + cantidades.get('six-pieces', 0) * 50
        })

    return jsonify({
        "products": productos_detalle,
        "total": pedido['total']
    })

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/finalizar-pedido', methods=['POST'])
def finalizar_pedido():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    # Recuperar datos del pedido desde la sesión
    resumen_pedido = session.get('resumen_pedido', {})
    total_pedido = session.get('total_pedido', 0)

    if not resumen_pedido:
        flash("No hay productos en el pedido.", "warning")
        return redirect(url_for('catalogo_productos'))

    historial_pedidos = session.get('historial_pedidos', [])
    new_id = str(len(historial_pedidos) + 1) + "-" + datetime.now().strftime('%H%M%S')

    # Crear un nuevo pedido
    nuevo_pedido = {
        "id": new_id,
        "products": resumen_pedido,
        "total": total_pedido,
        "creation_date": datetime.now().strftime('%Y-%m-%d'),
        "delivery_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        "status": "Procesando"
    }

    # Agregar el nuevo pedido al historial
    historial_pedidos.append(nuevo_pedido)
    session['historial_pedidos'] = historial_pedidos
    session.modified = True

    flash("Pedido realizado exitosamente.", "success")
    return redirect(url_for('rastreo_pedidos'))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("user_type") != "empleado":
        flash("Acceso no autorizado. Por favor, inicie sesión como empleado.", "danger")
        return redirect(url_for("login"))

    user_role = session.get("user_role")
    return f"Bienvenido al panel de empleados. Rol: {user_role}."

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/almacenista_dashboard")
def almacenista_dashboard():
    # Verifica que el usuario esté autenticado como empleado y que sea almacenista
    if "user_id" not in session or session.get("user_role") != "Almacenista":
        flash("Acceso no autorizado. Por favor, inicie sesión como almacenista.", "danger")
        return redirect(url_for("login"))

    # Aquí puedes incluir lógica adicional para cargar datos como proveedores, etc.
    conn = get_db_connection()
    proveedores = conn.execute("SELECT ID, Nombre FROM Proveedores").fetchall()
    conn.close()

    return render_template("registro-ingedientes/registro-ingedientes.html", proveedores=proveedores)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/guardar_ingrediente", methods=["POST"])
def guardar_ingrediente():
    try:
        # Obtener los datos del formulario
        nombre_producto = request.form.get("nombre_producto")
        numero_lote = request.form.get("numero_lote")
        proveedor = request.form.get("proveedor")
        cantidad = request.form.get("cantidad")
        unidad = request.form.get("unidad")
        ubicacion = request.form.get("ubicacion")
        detalles = request.form.get("detalles")
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha actual
        materia_prima_id = 1  # Suponiendo que el ID de materia prima sea fijo por ahora
        fecha_caducidad = None  # Si no tienes este dato en el formulario

        # Validar campos obligatorios
        if not (nombre_producto and numero_lote and proveedor and cantidad and unidad and ubicacion):
            return jsonify({"success": False, "error": "Todos los campos son obligatorios."}), 400

        # Convertir cantidad a entero
        try:
            cantidad = int(cantidad)
        except ValueError:
            return jsonify({"success": False, "error": "La cantidad debe ser un número entero válido."}), 400

        # Guardar en la base de datos
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO Lotes (Fecha_ingreso, Materia_prima_ID, Cantidad, Fecha_caducidad, Nombre, Numero_lote, Proveedor, Unidad, Ubicacion, Detalles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (fecha_ingreso, materia_prima_id, cantidad, fecha_caducidad, nombre_producto, numero_lote, proveedor, unidad, ubicacion, detalles),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error al guardar ingrediente: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/salida_ingredientes", methods=["GET"])
def salida_ingredientes():
    # Verifica que el usuario esté autenticado como empleado y que sea almacenista
    if "user_id" not in session or session.get("user_role") != "Almacenista":
        flash("Acceso no autorizado. Por favor, inicie sesión como almacenista.", "danger")
        return redirect(url_for("login"))

    # Consulta los ingredientes de la base de datos
    conn = get_db_connection()
    ingredientes = conn.execute(
        """
        SELECT ID, Fecha_ingreso, Nombre, Proveedor, Numero_lote, Cantidad, Unidad
        FROM Lotes
        """
    ).fetchall()
    conn.close()

    # Renderiza la página con los datos obtenidos
    return render_template("salida_ingredientes/salida_ingredientes.html", ingredientes=ingredientes)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/registrar_salida/<int:lote_id>", methods=["POST"])
def registrar_salida(lote_id):
    try:
        # Obtener la cantidad del json de la petición
        data = request.get_json()
        cantidad_retirar = data.get("cantidad")

        # Verificar que la cantidad sea válida
        if cantidad_retirar is None or cantidad_retirar <= 0:
            return jsonify({"success": False, "error": "Cantidad no válida"}), 400

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener la cantidad actual del lote
        cursor.execute("SELECT Cantidad FROM Lotes WHERE ID = ?", (lote_id,))
        lote = cursor.fetchone()

        if not lote:
            return jsonify({"success": False, "error": "Lote no encontrado"}), 404

        cantidad_actual = lote["Cantidad"]

        # Verificar que haya suficiente cantidad en el lote
        if cantidad_retirar > cantidad_actual:
            return jsonify({"success": False, "error": "Cantidad insuficiente en el lote"}), 400

        # Calcular la cantidad restante
        cantidad_restante = cantidad_actual - cantidad_retirar

        if cantidad_restante == 0:
            # Eliminar el lote si no queda cantidad
            cursor.execute("DELETE FROM Lotes WHERE ID = ?", (lote_id,))
        else:
            # Actualizar el lote con la cantidad restante
            cursor.execute("UPDATE Lotes SET Cantidad = ? WHERE ID = ?", (cantidad_restante, lote_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/registro_lote", methods=["GET", "POST"])
def registro_lote():
    # Verifica que el usuario esté autenticado y sea un empleado autorizado
    if "user_id" not in session or session.get("user_role") not in ["Almacenista", "Administrador"]:
        flash("Acceso no autorizado. Por favor, inicie sesión como usuario autorizado.", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            tipo_lote = request.form.get("tipo_lote")
            cantidad = request.form.get("cantidad")
            fecha_ingreso = request.form.get("fecha_ingreso")
            fecha_caducidad = request.form.get("fecha_caducidad")
            ubicacion = request.form.get("ubicacion")
            detalles = request.form.get("detalles")
            
            # Validar datos obligatorios
            if not all([tipo_lote, cantidad, fecha_ingreso, ubicacion]):
                return jsonify({"success": False, "error": "Todos los campos obligatorios deben estar llenos."}), 400
            
            # Guardar datos en la base de datos
            conn = get_db_connection()
            conn.execute(
                """
                INSERT INTO Lotes (Fecha_ingreso, Fecha_caducidad, Materia_prima_ID, Cantidad, Ubicacion, Detalles, Nombre)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (fecha_ingreso, fecha_caducidad, None, cantidad, ubicacion, detalles, tipo_lote)
            )
            conn.commit()
            conn.close()
            
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Renderizar el HTML para registro de lotes
    return render_template("registro-lotes/registro-lotes.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/guardar_lote", methods=["POST"])
def guardar_lote():
    try:
        # Obtener datos del formulario
        tipo_lote = request.form.get("tipo_lote")  # Nombre de la materia prima
        cantidad = request.form.get("cantidad")
        fecha_ingreso = request.form.get("fecha_ingreso")
        fecha_caducidad = request.form.get("fecha_caducidad")
        ubicacion = request.form.get("ubicacion")
        detalles = request.form.get("detalles")

        # Validar campos obligatorios
        if not all([tipo_lote, cantidad, fecha_ingreso, ubicacion]):
            return jsonify({"success": False, "error": "Todos los campos obligatorios deben completarse."})

        # Conexión a la base de datos
        conn = get_db_connection()

        # Generar automáticamente un nuevo ID para Materia_prima_ID
        last_id_row = conn.execute("SELECT MAX(Materia_prima_ID) FROM Lotes").fetchone()
        materia_prima_id = (last_id_row[0] or 0) + 1  # Incrementar el último ID encontrado
        print(f"Nuevo Materia_prima_ID generado: {materia_prima_id}")  # Depuración

        # Insertar el lote en la tabla Lotes
        conn.execute(
            """
            INSERT INTO Lotes (Fecha_ingreso, Fecha_caducidad, Cantidad, Ubicacion, Detalles, Materia_prima_ID)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fecha_ingreso, fecha_caducidad, cantidad, ubicacion, detalles, materia_prima_id),
        )
        conn.commit()
        conn.close()

        print(f"Lote insertado correctamente: Materia_prima_ID={materia_prima_id}")
        return jsonify({"success": True, "message": "¡El lote se registró con éxito!"})

    except Exception as e:
        print(f"Error al registrar el lote: {e}")
        return jsonify({"success": False, "error": str(e)})

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/salida_lotes", methods=["GET"])
def salida_lotes():
    # Verifica que el usuario esté autenticado como empleado y que sea almacenista
    if "user_id" not in session or session.get("user_role") != "Almacenista":
        flash("Acceso no autorizado. Por favor, inicie sesión como almacenista.", "danger")
        return redirect(url_for("login"))

    # Consulta los lotes de la base de datos
    conn = get_db_connection()
    lotes = conn.execute(
        """
        SELECT ID, Fecha_ingreso, Nombre AS Tipo, Cantidad, Unidad, Ubicacion
        FROM Lotes
        """
    ).fetchall()
    conn.close()

    # Renderiza la página con los datos obtenidos
    return render_template("salida_lotes/salida_lotes.html", lotes=lotes)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/registrar_salida_lotes/<int:lote_id>", methods=["POST"])
def registrar_salida_lotes(lote_id):
    try:
        # Conectar a la base de datos
        conn = get_db_connection()

        # Verificar si el lote existe antes de eliminarlo
        lote_existente = conn.execute("SELECT * FROM Lotes WHERE ID = ?", (lote_id,)).fetchone()
        if not lote_existente:
            return jsonify({"success": False, "error": "El lote no existe"}), 404

        # Eliminar el lote correspondiente
        conn.execute("DELETE FROM Lotes WHERE ID = ?", (lote_id,))
        conn.commit()
        conn.close()

        # Devolver una respuesta JSON de éxito
        return jsonify({"success": True}), 200
    except Exception as e:
        # En caso de error, devolver un mensaje JSON de error
        return jsonify({"success": False, "error": str(e)}), 500

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/inventario", methods=["GET"])
def inventario():
    # Verifica que el usuario esté autenticado como empleado y que sea almacenista
    if "user_id" not in session or session.get("user_role") != "Almacenista":
        flash("Acceso no autorizado. Por favor, inicie sesión como almacenista.", "danger")
        return redirect(url_for("login"))

    try:
        # Consulta los datos del inventario en la base de datos
        conn = get_db_connection()
        ingredientes = conn.execute(
            """
            SELECT 
                ID, 
                Fecha_ingreso, 
                Nombre, 
                Proveedor, 
                Numero_lote, 
                Cantidad, 
                Unidad
            FROM Lotes
            """
        ).fetchall()
        conn.close()

        # Convertir los resultados en una lista de diccionarios para facilitar el uso en Jinja
        ingredientes = [
            {
                "ID": row[0],
                "Fecha_ingreso": row[1],
                "Nombre": row[2],
                "Proveedor": row[3],
                "Numero_lote": row[4],
                "Cantidad": row[5],
                "Unidad": row[6],
            }
            for row in ingredientes
        ]

        # Renderiza la página de inventario con los datos obtenidos
        return render_template("inventario/inventario.html", ingredientes=ingredientes)
    except Exception as e:
        # Manejo de errores
        print(f"Error al obtener el inventario: {e}")
        flash("Hubo un error al cargar el inventario. Intente más tarde.", "danger")
        return redirect(url_for("almacenista_dashboard"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/dashboard-ventas")
def dashboard_ventas():
    return render_template("Dashboard_ventas/dashboard_ventas.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/ventas_inventario")
def ventas_inventario():
    # Asegúrate de que el usuario tenga el rol adecuado
    if "user_id" not in session or session.get("user_role") != "Ventas":
        flash("Acceso no autorizado. Por favor, inicie sesión.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    ingredientes = conn.execute(
        """
        SELECT ID, Fecha_ingreso, Nombre, Numero_lote, Cantidad, Unidad
        FROM Lotes
        """
    ).fetchall()
    conn.close()

    return render_template("inventario/inventario_ventas.html", ingredientes=ingredientes)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/generar_reporte_inventario", methods=["GET"])
def generar_reporte_inventario():
    # Conecta a la base de datos y recupera los datos del inventario
    conn = get_db_connection()
    inventario = conn.execute(
        """
        SELECT Nombre, Numero_lote, Proveedor, Cantidad, Unidad
        FROM Lotes
        """
    ).fetchall()
    conn.close()

    # Crea un archivo Excel en memoria
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Inventario Lotes")

    # Agrega encabezados a la hoja de cálculo
    headers = ["Nombre", "Número de Lote", "Proveedor", "Cantidad", "Unidad"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Agrega los datos del inventario
    for row_num, row in enumerate(inventario, start=1):
        worksheet.write(row_num, 0, row["Nombre"])
        worksheet.write(row_num, 1, row["Numero_lote"])
        worksheet.write(row_num, 2, row["Proveedor"])
        worksheet.write(row_num, 3, row["Cantidad"])
        worksheet.write(row_num, 4, row["Unidad"])

    # Cierra el archivo Excel
    workbook.close()
    output.seek(0)

    # Obtén la fecha actual para el nombre del archivo
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"Inventario_Lotes_Terminados_{fecha_actual}.xlsx"

    # Devuelve el archivo como una descarga
    return send_file(
        output,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/catalogo_productos_ventas', methods=['GET', 'POST'])
def catalogo_productos_ventas():
    resumen_pedido = session.get('resumen_pedido', {})
    total_pedido = session.get('total_pedido', 0)

    return render_template(
        'Catalogo/catalogo-productos-ventas.html',
        user_name=session.get('user_name', 'Usuario'),
        resumen_pedido=resumen_pedido,
        total_pedido=total_pedido
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/guardar_pedido_ventas', methods=['POST'])
def guardar_pedido_ventas():
    # Obtiene los datos del formulario
    cliente_grande = request.form.get('cliente')
    resumen_pedido = request.form.get('resumenPedido')
    total_pedido = request.form.get('totalPedido')

    # Guarda los datos en la sesión
    session['cliente_grande_nombre'] = cliente_grande
    session['resumen_pedido'] = resumen_pedido
    session['total_pedido'] = total_pedido

    # Redirige a la página de direcciones ventas
    return redirect(url_for('direcciones_ventas'))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/direcciones_ventas', methods=['GET', 'POST'])
def direcciones_ventas():
    resumen_pedido = session.get('resumen_pedido', '{}')
    if isinstance(resumen_pedido, str):
        resumen_pedido = json.loads(resumen_pedido)
    total_pedido = session.get('total_pedido', 0)
    cliente_grande = session.get('cliente_grande_nombre', 'Cliente no seleccionado')

    return render_template(
        'direcciones/direcciones_ventas.html',
        resumen_pedido=resumen_pedido,
        total_pedido=total_pedido,
        cliente_grande=cliente_grande
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/guardar_direccion_ventas', methods=['POST'])
def guardar_direccion_ventas():
    try:
        # Verificar si el Content-Type es JSON
        if request.content_type == 'application/json':
            data = request.json
        else:
            data = request.form

        cliente_grande = session.get('cliente_grande_nombre')
        calle = data.get('calle')
        delegacion = data.get('delegacion')
        colonia = data.get('colonia')
        ciudad = data.get('ciudad')
        estado = data.get('estado')
        cp = data.get('cp')

        # Validar datos
        if not cliente_grande:
            return jsonify({'success': False, 'message': 'No se ha seleccionado un cliente grande.'}), 400
        if not all([calle, delegacion, colonia, ciudad, estado, cp]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios.'}), 400

        direccion_completa = f"{calle}, {delegacion}, {colonia}, {ciudad}, {estado}, {cp}"

        # Guardar en la base de datos
        conn = get_db_connection()
        try:
            conn.execute(
                """
                UPDATE Clientes
                SET Direccion = ?
                WHERE Nombre = ?
                """,
                (direccion_completa, cliente_grande)
            )
            conn.commit()
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al guardar la dirección: {str(e)}'}), 500
        finally:
            conn.close()

        # Actualizar sesión con la nueva dirección
        session['direccion_completa'] = direccion_completa

        return jsonify({'success': True, 'message': f'Dirección guardada correctamente: {direccion_completa}'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Simular días hábiles (lunes a viernes)
def calcular_fecha_envio(fecha_inicial, dias_habiles):
    dias_agregados = 0
    while dias_habiles > 0:
        fecha_inicial += timedelta(days=1)
        # Saltar fines de semana
        if fecha_inicial.weekday() < 5:  # 0: lunes, ..., 4: viernes
            dias_habiles -= 1
    return fecha_inicial

# Generar un ID único
def generar_id_unico():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/generar-pedido')
def generar_pedido():
    import json
    from datetime import datetime, timedelta
    import random
    import string

    def calcular_fecha_envio(fecha_inicial, dias_habiles):
        dias_agregados = 0
        while dias_habiles > 0:
            fecha_inicial += timedelta(days=1)
            if fecha_inicial.weekday() < 5:  # 0: lunes, ..., 4: viernes
                dias_habiles -= 1
        return fecha_inicial

    def generar_id_unico():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    resumen_pedido = session.get('resumen_pedido', '{}')
    if isinstance(resumen_pedido, str):
        resumen_pedido = json.loads(resumen_pedido)

    if not isinstance(resumen_pedido, dict):
        resumen_pedido = {}

    cliente = session.get('cliente_grande_nombre', 'Cliente Desconocido')

    if not resumen_pedido:
        flash("No hay productos en el resumen de compra.", "danger")
        return redirect(url_for('catalogo_productos_ventas'))

    fecha_creacion = datetime.now()
    fecha_envio = calcular_fecha_envio(fecha_creacion, 15)
    id_unico = generar_id_unico()

    pedido = {
        'id': id_unico,
        'cliente': cliente,
        'creation_date': fecha_creacion.strftime('%d/%m/%Y'),
        'delivery_date': fecha_envio.strftime('%d/%m/%Y'),
        'status': 'Preparando',
        'details': [
            {
                'name': producto,
                'quantity': cantidades.get('half-kilo', 0) + cantidades.get('six-pieces', 0),
                'price': 50 if 'six-pieces' in cantidades else 100
            }
            for producto, cantidades in resumen_pedido.items()
        ]
    }

    historial_pedidos_ventas = session.get('historial_pedidos_ventas', [])
    historial_pedidos_ventas.append(pedido)
    session['historial_pedidos_ventas'] = historial_pedidos_ventas

    print("Pedido generado:", pedido)

    return render_template(
        'rastreo/rastreo-ordenes-ventas.html',
        historial_pedidos_ventas=historial_pedidos_ventas,
        user_name=session.get('user_name', 'Usuario')
    )


#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/rastreo-ordenes-ventas')
def rastreo_ordenes_ventas():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, inicia sesión.", "danger")
        return redirect(url_for('login'))

    # Recuperar datos correctamente
    historial_pedidos_ventas = session.get('historial_pedidos_ventas', [])

    # Validar si es una lista de diccionarios
    if not isinstance(historial_pedidos_ventas, list):
        historial_pedidos_ventas = json.loads(historial_pedidos_ventas)  # Si viene como JSON string

    return render_template(
        'rastreo/rastreo-ordenes-ventas.html',
        historial_pedidos_ventas=historial_pedidos_ventas,
        user_name=session.get('user_name', 'Usuario')
    )

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/get-order-details-ventas/<order_id>', methods=['GET'])
def get_order_details_ventas(order_id):
    # Recuperar el historial de pedidos de la sesión
    historial_pedidos_ventas = session.get('historial_pedidos_ventas', [])

    # Buscar el pedido por ID
    pedido = next((order for order in historial_pedidos_ventas if order['id'] == order_id), None)

    if pedido:
        # Calcular el total del pedido
        total = sum(item['quantity'] * item.get('price', 0) for item in pedido['details'])

        # Preparar los datos para el JSON de respuesta
        detalles = {
            'id': pedido['id'],
            'client_name': pedido['cliente'],
            'creation_date': pedido['creation_date'],
            'delivery_date': pedido['delivery_date'],
            'status': pedido['status'],
            'products': pedido['details'],  # Lista de productos con cantidad y nombre
            'total': total
        }
        return jsonify({'success': True, 'details': detalles}), 200

    return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404

#----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

