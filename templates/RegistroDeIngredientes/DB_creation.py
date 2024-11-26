import sqlite3
import os

# Crear la carpeta 'Database' si no existe
if not os.path.exists('Database'):
    os.makedirs('Database')

# Conectar a la base de datos (o crearla si no existe) dentro de la carpeta 'Database'
db_path = os.path.join('Database', 'GalletasDeliDB.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla Proveedores
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proveedores (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre VARCHAR(100) NOT NULL,
        Telefono VARCHAR(15),
        Correo VARCHAR(100)
    )
''')

# Crear la tabla Materias_Primas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Materias_Primas (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre VARCHAR(50) NOT NULL,
        Descripcion VARCHAR(255),
        Stock_minimo INT NOT NULL,
        Proveedor_ID INT,
        FOREIGN KEY (Proveedor_ID) REFERENCES Proveedores(ID)
    )
''')

# Crear la tabla Reabastecimiento
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reabastecimiento (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Proveedor_ID INT NOT NULL,
        Materia_prima_ID INT NOT NULL,
        Cantidad INT NOT NULL,
        Fecha_pedido DATETIME NOT NULL,
        FOREIGN KEY (Proveedor_ID) REFERENCES Proveedores(ID),
        FOREIGN KEY (Materia_prima_ID) REFERENCES Materias_Primas(ID)
    )
''')

# Crear la tabla Lotes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lotes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Fecha_ingreso DATETIME NOT NULL,
        Materia_prima_ID INT NOT NULL,
        Cantidad INT NOT NULL,
        Fecha_caducidad DATETIME,
        FOREIGN KEY (Materia_prima_ID) REFERENCES Materias_Primas(ID)
    )
''')

# Crear la tabla Inventario
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Inventario (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Lote_ID INT,
        Cantidad_actual INT,
        Ubicacion TEXT,
        FOREIGN KEY (Lote_ID) REFERENCES Lotes(ID)
    )
''')

# Crear la tabla Productos_Terminados
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Productos_Terminados (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Lote_ID INT NOT NULL,
        Cantidad INT NOT NULL,
        Fecha DATETIME NOT NULL,
        Nombre VARCHAR(30) NOT NULL,
        Presentacion VARCHAR(50) NOT NULL, 
        FOREIGN KEY (Lote_ID) REFERENCES Lotes(ID)
    )
''')

# Crear la tabla Control_Calidad
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Control_Calidad (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Lote_ID INT NOT NULL,
        Resultado VARCHAR(100) NOT NULL,
        Fecha_control DATETIME NOT NULL,
        FOREIGN KEY (Lote_ID) REFERENCES Lotes(ID)
    )
''')

# Crear la tabla Clientes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clientes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Nombre VARCHAR(50) NOT NULL,
        Direccion VARCHAR(200) NOT NULL,
        Telefono VARCHAR(18) NOT NULL,
        Email VARCHAR(100) NOT NULL
    )
''')

# Crear la tabla Ordenes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ordenes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Cliente_ID INT NOT NULL,
        Fecha_orden DATETIME NOT NULL,
        FOREIGN KEY (Cliente_ID) REFERENCES Clientes(ID)
    )
''')

# Crear la tabla Orden_detalles
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orden_detalles (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Orden_ID INT NOT NULL,
        Producto_terminado_ID INT NOT NULL,
        Cantidad INT NOT NULL,
        Precio_unitario INT NOT NULL,
        FOREIGN KEY (Orden_ID) REFERENCES Ordenes(ID),
        FOREIGN KEY (Producto_terminado_ID) REFERENCES Productos_Terminados(ID)
    )
''')

# Crear la tabla Entregas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Entregas (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Orden_detalles_ID INT NOT NULL,
        Fecha_estimada DATETIME NOT NULL,
        Fecha_entrega DATETIME,
        Direccion_entrega VARCHAR(200) NOT NULL,
        Status VARCHAR(15) NOT NULL,
        FOREIGN KEY (Orden_detalles_ID) REFERENCES Orden_detalles(ID)
    )
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos y tablas creadas exitosamente en la carpeta 'Database'.")