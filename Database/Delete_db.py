import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join('Database', 'GalletasDeliDB.db')

def consultar_usuarios():
    """Consulta todos los usuarios en la tabla Clientes y los imprime en la consola."""
    if not os.path.exists(db_path):
        print("La base de datos no existe en la ruta especificada.")
        return

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Consulta para obtener todos los usuarios
        query = '''
            SELECT ID_cliente, User, Nombre, Direccion, Telefono, Email
            FROM Clientes
        '''
        cursor.execute(query)
        usuarios = cursor.fetchall()

        # Imprimir los resultados
        if usuarios:
            print("Usuarios en la base de datos:")
            for usuario in usuarios:
                print(f"ID: {usuario[0]}, Usuario: {usuario[1]}, Nombre: {usuario[2]}, Dirección: {usuario[3]}, Teléfono: {usuario[4]}, Email: {usuario[5]}")
        else:
            print("No hay usuarios registrados en la base de datos.")

    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()

# Ejecutar la consulta
if __name__ == "__main__":
    consultar_usuarios()
