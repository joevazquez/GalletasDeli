"""

Este es el archivo que se va a ejecutar para que la aplicación Flask se cree,
lo que va a hacer es iniciar en modo depuración la aplicación create_app(), inicializar
los módulos de registro y almacén

"""

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Ruta a la base de datos
db_path = os.path.join('Database', 'GalletasDeliDB.db')

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# Cargar usuario por ID
@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nombre, Email FROM Clientes WHERE ID = ?", (user_id,))
        user_data = cursor.fetchone()
    if user_data:
        return User(id=user_data[0], username=user_data[1], email=user_data[2])
    return None

# Página de inicio
@app.route('/')
def index():
    return redirect(url_for('catalogo_productos'))
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username)
    return redirect(url_for('/LoginRegisterService/login.html'))

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Nombre, Email, Contraseña FROM Clientes WHERE Email = ?", (email,))
            user_data = cursor.fetchone()

        if user_data and check_password_hash(user_data[3], password):
            user = User(id=user_data[0], username=user_data[1], email=user_data[2])
            login_user(user)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos", "error")
    
    return render_template('/LoginRegisterService/login.html')

# Página de registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['username']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Clientes (Nombre, Direccion, Telefono, Email, Contraseña) VALUES (?, ?, ?, ?, ?)",
                           (nombre, direccion, telefono, email, hashed_password))
            conn.commit()
            flash("Usuario registrado exitosamente. Por favor, inicia sesión.", "success")
            return redirect(url_for('login'))
    
    return render_template('/LoginRegisterService/register.html')

# Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for('login'))

# Página protegida para usuarios autenticados
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# Página del catálogo de productos
@app.route('/catalogo_productos')
#@login_required
def catalogo_productos():    
    products = [
        {
            "name": "Besos de Nuez",
            "image": "galletas-besos-nuez.jpg"
        },
        {
            "name": "Naranja",
            "image": "galletas-naranja.jpg"
        },
        {
            "name": "Coco",
            "image": "galletas-coco.jpg"
        },
        {
            "name": "Chocolate",
            "image": "galletas-chocolate.jpg"
        },
        {
            "name": "Avena",
            "image": "galletas-avena.jpg"
        },
        {
            "name": "Surtido",
            "image": "galletas-surtido.jpg"
        },
    ]
    return render_template('Catalogo/catalogo-productos.html', products=products)

@app.route('/crear_orden', methods=['POST'])
#@login_required
def crear_orden():
    try:
        # Obtiene el resumen del pedido enviado desde el formulario
        order_summary = request.form.get('order_summary')
        if not order_summary:
            flash("No se recibió ningún pedido.", "error")
            return redirect(url_for('catalogo_productos'))
        
        order_summary = json.loads(order_summary)  # Decodifica el JSON
        print(order_summary)
                
        # Conecta con la base de datos
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Crea la nueva orden en la tabla `Ordenes`
            cursor.execute(
                "INSERT INTO Ordenes (id_cliente, Fecha_orden) VALUES (?, datetime('now'))",
                (current_user.id,)
            )
            order_id = cursor.lastrowid  # Obtiene el ID de la orden recién creada

            # Itera sobre los productos en el resumen del pedido
            for product_name, quantities in order_summary.items():
                half_kilo = quantities.get('halfKilo', 0)
                six_pieces = quantities.get('sixPieces', 0)

                # Maneja las cajas de medio kilo
                if half_kilo > 0:
                    cursor.execute(
                        """
                        SELECT Id_producto_terminado, Cantidad_disponible
                        FROM Productos_terminados
                        WHERE Nombre = ? AND Presentacion = 'halfKilo' AND Cantidad_disponible >= ?
                        """,
                        (product_name, half_kilo)
                    )
                    half_kilo_data = cursor.fetchone()

                    if not half_kilo_data:
                        flash(f"No hay suficiente stock para {product_name} (medio kilo).", "error")
                        return redirect(url_for('catalogo_productos'))
                    
                    half_kilo_id, half_kilo_stock = half_kilo_data

                    # Actualiza el stock del producto terminado
                    cursor.execute(
                        "UPDATE Productos_terminados SET Cantidad_disponible = Cantidad_disponible - ? WHERE ID = ?",
                        (half_kilo, half_kilo_id)
                    )

                    # Añade un detalle de orden para la presentación de medio kilo
                    cursor.execute(
                        """
                        INSERT INTO Orden_detalles (id_orden, id_producto, Cantidad, Precio_total)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, half_kilo_id, half_kilo, half_kilo * 100)
                    )

                # Maneja las cajas de 6 piezas
                if six_pieces > 0:
                    cursor.execute(
                        """
                        SELECT ID, Cantidad_disponible
                        FROM Productos_terminados
                        WHERE Nombre = ? AND Presentacion = 'sixPieces' AND Cantidad_disponible >= ?
                        """,
                        (product_name, six_pieces)
                    )
                    six_pieces_data = cursor.fetchone()

                    if not six_pieces_data:
                        flash(f"No hay suficiente stock para {product_name} (6 piezas).", "error")
                        return redirect(url_for('catalogo_productos'))
                    
                    six_pieces_id, six_pieces_stock = six_pieces_data

                    # Actualiza el stock del producto terminado
                    cursor.execute(
                        "UPDATE Productos_terminados SET Cantidad_disponible = Cantidad_disponible - ? WHERE ID = ?",
                        (six_pieces, six_pieces_id)
                    )

                    # Añade un detalle de orden para la presentación de 6 piezas
                    cursor.execute(
                        """
                        INSERT INTO Orden_detalles (id_orden, id_producto, Cantidad, Precio_total)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, six_pieces_id, six_pieces, six_pieces * 100)
                    )
            
            conn.commit()
            flash("Orden creada exitosamente.", "success")
            return redirect(url_for('rastreo_ordenes'))         
    except Exception as e:
        flash(f"Ocurrió un error al procesar la orden: {str(e)}", "error")
        return redirect(url_for('catalogo_productos'))


# Página de rastreo de órdenes
@app.route('/rastreo_ordenes')
#@login_required
def rastreo_ordenes(): 
    '''
    # Obtener las órdenes del cliente autenticado
    user_id = current_user.id
    orders = []
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Consulta SQL para obtener las órdenes
        cursor.execute("""
            SELECT 
                o.id AS id_orden, 
                o.Fecha_orden, 
                e.Fecha_estimada, 
                e.Fecha_entrega, 
                e.Status
            FROM Ordenes o
            JOIN Orden_detalles od ON o.id = od.id_orden
            LEFT JOIN Entregas e ON od.id = e.id_detalle_orden
            WHERE o.id_cliente = ?
            ORDER BY o.Fecha_orden DESC
        """, (user_id,))
        
        orders_data = cursor.fetchall()
    
    # Formatear los datos para enviarlos al template
    for order in orders_data:
        orders.append({
            "id": f"#{order[0]}",
            "creation_date": order[1],
            "delivery_date": order[3] if order[3] else "Pendiente",
            "status": order[4] if order[4] else "En preparación",
            "details": f"/rastreo_detalle/{order[0]}"
        })
    '''

    # Ejemplo de orders, eliminar cuando esté listo el login
    orders = [
        {
            "id": "#1564",
            "creation_date": "10/10/24",
            "delivery_date": "20/10/24",
            "status": "En preparación",
            "details": "link_details"
        },
        {
            "id": "#1560",
            "creation_date": "10/05/24",
            "delivery_date": "10/10/24",
            "status": "Entregado",
            "details": "link_details"
        },             
    ]
    return render_template('Rastreo/rastreo-ordenes.html', orders=orders)


#Pruebas de salida de ingredientes a produccion 
@app.route('/pagina-principal-salida')
def pagina_principal_salida():
    return render_template('salida-ingredientes1.html')

@app.route('/filtro')
def filtro():
    return render_template('salida-ingredientes2.html')

@app.route('/checkbox')
def checkbox():
    return render_template('salida-ingredientes3.html')

@app.route('/datos-operacion')
def datos_operacion():
    return render_template('salida-ingredientes4.html')

@app.route('/detalles-salida')
def detalles_salida():
    return render_template('salida-ingredientes5.html')

@app.route('/salida')
def salida():
    return render_template('salida-ingredientes6.html')



if __name__ == '__main__':
    app.run(debug=True)
