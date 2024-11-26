from flask import Flask, render_template, redirect, url_for, request, session
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/isaac/Desktop/RegistroDeDirecciones/Database/GalletasDeliDB.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)
from models import Clientes
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

@app.route("/")
def hello_world():
    return render_template('RegistroDirecciones.html')

@app.route("/RegistroGuardado", methods=['POST'])
def RegistroGuardado():
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    estado = request.form.get("estado")
    ciudad = request.form.get("ciudad")
    calle_y_numero = request.form.get("calleYnumero")
    telefono = request.form.get("telefono")
    email = request.form.get("email")
    pwd = request.form.get("contraseña")

     # Validar campos vacíos
    if not all([nombre, apellido, estado, ciudad, calle_y_numero, telefono, email, pwd]):
        return render_template('RegistroDirecciones.html', error="Todos los campos son obligatorios.")
    
    # Validar formato del correo electrónico
    if not "@" in email or not "." in email.split("@")[-1]:
        return render_template('RegistroDirecciones.html', error="El correo electrónico no tiene un formato válido.")
    
    # Validar formato del teléfono
    if not telefono.isdigit() or len(telefono) < 8 or len(telefono) > 15:
        return render_template('RegistroDirecciones.html', error="El número de teléfono debe contener solo números y tener entre 8 y 15 caracteres.")
    
    # Validar formato de la contraseña
    import re
    if not re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', pwd):
        return render_template('RegistroDirecciones.html', error="La contraseña debe tener al menos 8 caracteres, incluir una letra, un número y un carácter especial.")
    
    # Validar si el correo ya existe en la base de datos
    cliente_existente = Clientes.query.filter_by(Email=email).first()
    if cliente_existente:
        return render_template('RegistroDirecciones.html', error="El correo electrónico ya está registrado.")
    

    contraseña_encriptada = generate_password_hash(pwd, method='pbkdf2:sha256', salt_length=8)
    print(type(contraseña_encriptada))
    # Construir la dirección a partir de los campos del formulario
    direccion = f"{calle_y_numero}, {estado}, {ciudad}"

    # Crear una instancia de Cliente
    nuevo_cliente = Clientes(
        Nombre=f"{nombre} {apellido}",
        Direccion=direccion,
        Telefono=telefono,
        Email=email,
        Contraseña=contraseña_encriptada
    )
    # Guardar el cliente en la base de datos
    try:
        db.session.add(nuevo_cliente)
        db.session.commit()
        return "Cliente registrado exitosamente"
    except Exception as e:
        db.session.rollback()
        return f"Error al registrar cliente: {e}"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)