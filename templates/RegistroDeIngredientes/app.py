from flask import Flask, render_template, redirect, url_for, request, flash
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Proveedores, Materias_Primas


# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/isaac/Desktop/RegistroDeIngredientes/Database/GalletasDeliDB.db"
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)

from models import Proveedores
# Variable global para rastrear si ya se ejecutó la lógica inicial
first_request_done = False

@app.before_request
def before_first_request_logic():
    global first_request_done
    if not first_request_done:
        # Código que quieres que se ejecute antes de la primera solicitud
        print("Esto se ejecuta antes de procesar la primera solicitud.")
        # Ejemplo: Crear tablas si no existen
        db.create_all()
        first_request_done = True


@app.route('/')
def registro_de_producto():

    proveedores = Proveedores.query.all()
   
    return render_template('RegistroDeIngredientes.html', proveedores=proveedores)

@app.route("/GuardarProducto", methods=['POST'])
def guardar_producto():
    nombre_producto = request.form['nombre_producto']
    numero_lote = request.form['numero_lote']
    proveedor = request.form['proveedor']
    cantidad = request.form['cantidad']
    unidad = request.form['unidad']
    ubicacion = request.form['ubicacion']
    detalles = request.form['detalles']

    # Validación de campos vacíos
    if not nombre_producto or not numero_lote or not proveedor or not cantidad or not unidad or not ubicacion:
        error_message = "Todos los campos son obligatorios."
        return render_template('RegistroDeIngredientes.html', error_message=error_message)
    
    # Validación de cantidad positiva
    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            error_message = "La cantidad debe ser un número positivo."
            return render_template('RegistroDeIngredientes.html', error_message=error_message)
    except ValueError:
        error_message = "La cantidad debe ser un número válido."
        return render_template('RegistroDeIngredientes.html', error_message=error_message)
    
    # Validación de proveedor seleccionado
    if proveedor == "Proveedor":
        error_message = "Debe seleccionar un proveedor."
        return render_template('RegistroDeIngredientes.html', error_message=error_message)
    
    # Validación de unidad seleccionada
    if unidad == "Unidad":
        error_message = "Debe seleccionar una unidad."
        return render_template('RegistroDeIngredientes.html', error_message=error_message)

    proveedorEntero = int(proveedor)

    nuevaMateriaPrima = Materias_Primas(
        Nombre=nombre_producto,
        Descripcion=detalles,
        Stock_minimo=cantidad,
        Proveedor_ID=proveedorEntero
    )
    db.session.add(nuevaMateriaPrima)
    db.session.commit()

    return render_template('GuardarProducto.html')



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)