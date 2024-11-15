import configparser
import os
import sys

def obtener_ruta_config_ini(relative_path="config.ini"):
    """
    Obtiene la ruta del archivo config.ini dependiendo de si está empaquetado como .exe o no.
    """
    if getattr(sys, 'frozen', False):  # Si está empaquetado con PyInstaller
        dir_actual = os.path.dirname(sys.executable)
    else:  # En modo desarrollo
        dir_actual = os.path.abspath(".")
    return os.path.join(dir_actual, relative_path)

def cargar_configuracion():
    """
    Carga todas las configuraciones del archivo config.ini y las organiza en un diccionario.
    """
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini())
    
    configuraciones = {
        "database": {
            "server": config["database"]["server"],
            "database": config["database"]["database"],
            "user": config["database"]["user"]
        },
        "paths": {
            "consolidation_origin": config["paths"]["consolidation_origin"],
            "consolidation_dest": config["paths"]["consolidation_dest"]
        },
        "decompression": {
            "base_folder": config["decompression"]["base_folder"],
            "table_control_descompression": config["decompression"]["table_control_descompression"]
        },
        "consolidation": {
            "table_control_cargue": config["consolidation"]["table_control_cargue"],
            "table_datafonos": config["consolidation"]["table_datafonos"]
        }
    }
    return configuraciones

def guardar_rutas(consolidation_origin, consolidation_dest):
    """
    Guarda nuevas rutas en la sección [paths] del archivo config.ini.
    """
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini())
    
    config["paths"]["consolidation_origin"] = consolidation_origin
    config["paths"]["consolidation_dest"] = consolidation_dest

    with open(obtener_ruta_config_ini(), 'w') as configfile:
        config.write(configfile)

def guardar_base_datos(server, database, user):
    """
    Guarda nuevos parámetros en la sección [database] del archivo config.ini.
    """
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini())
    
    config["database"]["server"] = server
    config["database"]["database"] = database
    config["database"]["user"] = user

    with open(obtener_ruta_config_ini(), 'w') as configfile:
        config.write(configfile)

def obtener_tablas_consolidacion():
    """
    Obtiene las tablas de la sección [consolidation] del archivo config.ini.
    """
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini())
    
    tablas = {
        "table_control_cargue": config["consolidation"]["table_control_cargue"],
        "table_datafonos": config["consolidation"]["table_datafonos"]
    }
    return tablas

def guardar_tablas_consolidacion(table_control_cargue, table_datafonos):
    """
    Guarda las tablas en la sección [consolidation] del archivo config.ini.
    """
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini())
    
    config["consolidation"]["table_control_cargue"] = table_control_cargue
    config["consolidation"]["table_datafonos"] = table_datafonos

    with open(obtener_ruta_config_ini(), 'w') as configfile:
        config.write(configfile)

def recargar_configuracion():
    """Recarga la configuración desde config.ini."""
    config_path = obtener_ruta_config_ini()
    config = configparser.ConfigParser()
    config.read(config_path)
    return config
