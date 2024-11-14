import pyodbc
import configparser
import sys
import os

def get_resource_path(relative_path):
    """ Devuelve la ruta absoluta del archivo de recurso """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Cargar configuración del archivo config.ini usando get_resource_path
config = configparser.ConfigParser()
config_path = get_resource_path("config.ini")
config.read(config_path)

def connect_to_db(username, password):
    """Intenta conectar a la base de datos con las credenciales proporcionadas."""
    try:
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['database']['server']};"
            f"DATABASE={config['database']['database']};"
            f"UID={username};"
            f"PWD={password};"
        )
        print("Conexión exitosa a la base de datos")
        return connection
    except pyodbc.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None
