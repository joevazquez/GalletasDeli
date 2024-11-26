from extensions import db


# Modelo Proveedores
class Proveedores(db.Model):
    __tablename__ = 'Proveedores'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Telefono = db.Column(db.String(15))
    Correo = db.Column(db.String(100))

    # Relación con Materias_Primas
    materias_primas = db.relationship('Materias_Primas', backref='proveedor', lazy=True)

# Modelo Reabastecimiento
class Reabastecimiento(db.Model):
    __tablename__ = 'Reabastecimiento'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Proveedor_ID = db.Column(db.Integer, db.ForeignKey('Proveedores.ID'), nullable=False)
    Materia_prima_ID = db.Column(db.Integer, db.ForeignKey('Materias_Primas.ID'), nullable=False)
    Cantidad = db.Column(db.Integer, nullable=False)
    Fecha_pedido = db.Column(db.DateTime, nullable=False)


# Modelo Materias_Primas
class Materias_Primas(db.Model):
    __tablename__ = 'Materias_Primas'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Descripcion = db.Column(db.String(255))
    Stock_minimo = db.Column(db.Integer, nullable=False)
    Proveedor_ID = db.Column(db.Integer, db.ForeignKey('Proveedores.ID'))

    # Relación con Lotes y Reabastecimiento
    lotes = db.relationship('Lotes', backref='materia_prima', lazy=True)
    reabastecimientos = db.relationship('Reabastecimiento', backref='materia_prima', lazy=True)

    # Modelo Lotes
class Lotes(db.Model):
    __tablename__ = 'Lotes'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha_ingreso = db.Column(db.DateTime, nullable=False)
    Materia_prima_ID = db.Column(db.Integer, db.ForeignKey('Materias_Primas.ID'), nullable=False)
    Cantidad = db.Column(db.Integer, nullable=False)
    Fecha_caducidad = db.Column(db.DateTime)

    # Relación con Inventario, Productos_Terminados y Control_Calidad
    inventarios = db.relationship('Inventario', backref='lote', lazy=True)
    productos_terminados = db.relationship('Productos_Terminados', backref='lote', lazy=True)
    controles_calidad = db.relationship('Control_Calidad', backref='lote', lazy=True)

# Modelo Inventario
class Inventario(db.Model):
    __tablename__ = 'Inventario'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Lote_ID = db.Column(db.Integer, db.ForeignKey('Lotes.ID'))
    Cantidad_actual = db.Column(db.Integer)
    Ubicacion = db.Column(db.Text)

# Modelo Productos_Terminados
class Productos_Terminados(db.Model):
    __tablename__ = 'Productos_Terminados'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Lote_ID = db.Column(db.Integer, db.ForeignKey('Lotes.ID'), nullable=False)
    Cantidad = db.Column(db.Integer, nullable=False)
    Fecha = db.Column(db.DateTime, nullable=False)
    Nombre = db.Column(db.String(30), nullable=False)
    Presentacion = db.Column(db.String(50), nullable=False)

# Modelo Control_Calidad
class Control_Calidad(db.Model):
    __tablename__ = 'Control_Calidad'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Lote_ID = db.Column(db.Integer, db.ForeignKey('Lotes.ID'), nullable=False)
    Resultado = db.Column(db.String(100), nullable=False)
    Fecha_control = db.Column(db.DateTime, nullable=False)

# Modelo Clientes
class Clientes(db.Model):
    __tablename__ = 'Clientes'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Direccion = db.Column(db.String(200), nullable=False)
    Telefono = db.Column(db.String(18), nullable=False)
    Email = db.Column(db.String(100), nullable=False)

    # Relación con Ordenes
    ordenes = db.relationship('Ordenes', backref='cliente', lazy=True)

# Modelo Ordenes
class Ordenes(db.Model):
    __tablename__ = 'Ordenes'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Cliente_ID = db.Column(db.Integer, db.ForeignKey('Clientes.ID'), nullable=False)
    Fecha_orden = db.Column(db.DateTime, nullable=False)

    # Relación con Orden_detalles
    detalles = db.relationship('Orden_detalles', backref='orden', lazy=True)

# Modelo Orden_detalles
class Orden_detalles(db.Model):
    __tablename__ = 'Orden_detalles'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Orden_ID = db.Column(db.Integer, db.ForeignKey('Ordenes.ID'), nullable=False)
    Producto_terminado_ID = db.Column(db.Integer, db.ForeignKey('Productos_Terminados.ID'), nullable=False)
    Cantidad = db.Column(db.Integer, nullable=False)
    Precio_unitario = db.Column(db.Integer, nullable=False)

    # Relación con Entregas
    entregas = db.relationship('Entregas', backref='orden_detalle', lazy=True)

# Modelo Entregas
class Entregas(db.Model):
    __tablename__ = 'Entregas'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Orden_detalles_ID = db.Column(db.Integer, db.ForeignKey('Orden_detalles.ID'), nullable=False)
    Fecha_estimada = db.Column(db.DateTime, nullable=False)
    Fecha_entrega = db.Column(db.DateTime)
    Direccion_entrega = db.Column(db.String(200), nullable=False)
    Status = db.Column(db.String(15), nullable=False)