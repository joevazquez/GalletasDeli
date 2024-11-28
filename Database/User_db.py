import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join('Database', 'GalletasDeliDB.db')

def consultar_usuarios_y_empleados():
    """Consulta todos los usuarios en la tabla Clientes y Empleados y los imprime en la consola."""
    if not os.path.exists(db_path):
        print("La base de datos no existe en la ruta especificada.")
        return

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Consulta para obtener todos los clientes
        query_clientes = '''
            SELECT ID_cliente, User, Nombre, Direccion, Telefono, Email, Contrasena
            FROM Clientes
        '''
        cursor.execute(query_clientes)
        clientes = cursor.fetchall()

        # Imprimir resultados de Clientes
        if clientes:
            print("Clientes en la base de datos:")
            for cliente in clientes:
                print(f"ID: {cliente[0]}, Usuario: {cliente[1]}, Nombre: {cliente[2]}, Dirección: {cliente[3]}, Teléfono: {cliente[4]}, Email: {cliente[5]}, Contraseña: {cliente[6]}")
        else:
            print("No hay clientes registrados en la base de datos.")

        # Consulta para obtener todos los empleados con sus roles
        query_empleados = '''
            SELECT ID_empleado, User, Nombre, Direccion, Rol, Contrasena
            FROM Empleado
        '''
        cursor.execute(query_empleados)
        empleados = cursor.fetchall()

        # Imprimir resultados de Empleados
        if empleados:
            print("\nEmpleados en la base de datos:")
            for empleado in empleados:
                print(f"ID: {empleado[0]}, Usuario: {empleado[1]}, Nombre: {empleado[2]}, Dirección: {empleado[3]}, Rol: {empleado[4]}, Contraseña: {empleado[5]}")
        else:
            print("No hay empleados registrados en la base de datos.")

            # Consulta para obtener todos los empleados con sus roles
        query_empleados_todos = '''
            SELECT *
            FROM Empleado
        '''
        print(query_empleados_todos)

    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()



# Ejecutar la consulta
if __name__ == "__main__":
    consultar_usuarios_y_empleados()
