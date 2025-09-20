#clase conexion a la base de datos
import mysql.connector

#metodo de conexion a la base de datos
def conexion():
    return mysql.connector.connect(
        host='localhost',
        port='3307', # Puerto modificado
        user='root',
        password='1234',
        database='desarrollo_web'
    )

#cerrar conexion
def cerrar_conexion(conn):
    if conn.is_connected():
        conn.close()
        print("Conexión cerrada")
        