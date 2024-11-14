import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
import configparser
import pyodbc
import pandas as pd
from datetime import datetime
import shutil
import re
import sys

def get_resource_path(relative_path):
    # Obtiene la ruta del directorio de ejecución del .exe o script
    if getattr(sys, 'frozen', False):  # Verifica si está empaquetado
        dir_actual = os.path.dirname(sys.executable)
    else:
        dir_actual = os.path.abspath(".")
    return os.path.join(dir_actual, relative_path)

class ConsolidationTab:
    def __init__(self, frame, db_password, config):
        print("Inicializando ConsolidationTab...")  # Debug
        self.frame = frame
        self.db_password = db_password
        
        # Usa directamente el config pasado como parámetro, sin volver a leer el archivo
        self.server = config['database']['server']
        self.database = config['database']['database']
        self.username = config['database']['user']
        
        # Rutas de origen y destino
        self.carpeta_origen = config['paths'].get('consolidation_origin', '')
        self.carpeta_destino = config['paths'].get('consolidation_dest', '')
        
        # Nombre de las tablas para el control y la consolidación de datos
        self.table_control_cargue = config['decompression']['table_control_descompression']
        self.table_datafonos = config['consolidation']['table_datafonos']

        self.create_widgets()

    def create_widgets(self):
        print("Creando widgets en ConsolidationTab...")  # Debug
        title_label = ctk.CTkLabel(self.frame, text="Consolidación de Archivos", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))

        select_origin_button = ctk.CTkButton(self.frame, text="Seleccionar Carpeta Origen", command=self.seleccionar_carpeta_origen)
        select_origin_button.pack(pady=5)

        self.label_origen = ctk.CTkLabel(
            self.frame,
            text=f"Origen: {self.carpeta_origen if self.carpeta_origen else 'No seleccionado'}",
            font=("Arial", 10)
        )
        self.label_origen.pack()

        select_dest_button = ctk.CTkButton(self.frame, text="Seleccionar Carpeta Destino", command=self.seleccionar_carpeta_destino)
        select_dest_button.pack(pady=5)

        self.label_destino = ctk.CTkLabel(
            self.frame,
            text=f"Destino: {self.carpeta_destino if self.carpeta_destino else 'No seleccionado'}",
            font=("Arial", 10)
        )
        self.label_destino.pack()

        save_button = ctk.CTkButton(self.frame, text="Guardar Configuración", command=self.guardar_configuracion, font=("Arial", 12))
        save_button.pack(pady=10)

        process_button = ctk.CTkButton(
            self.frame, text="Cargar Archivos",
             command=self.procesar_carga,
             font=("Arial", 14, "bold"),
             fg_color="#b11c5a",
             width=200
            )
        process_button.pack(pady=(20, 10))

    def seleccionar_carpeta_origen(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta de origen")
        if carpeta:
            self.carpeta_origen = carpeta
            self.label_origen.config(text=f"Origen: {self.carpeta_origen}")

    def seleccionar_carpeta_destino(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta de destino")
        if carpeta:
            self.carpeta_destino = carpeta
            self.label_destino.config(text=f"Destino: {self.carpeta_destino}")

    def guardar_configuracion(self):
        config_path = get_resource_path("config.ini")
        config = configparser.ConfigParser()
        config.read(config_path)
        config['paths']['consolidation_origin'] = self.carpeta_origen
        config['paths']['consolidation_dest'] = self.carpeta_destino
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Configuración guardada", "Las rutas han sido guardadas en config.ini")

    def connect_to_db(self):
        connection_string = (
            f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};'
            f'UID={self.username};PWD={self.db_password}'
        )
        try:
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")
            return None

    def procesar_carga(self):
        if not self.carpeta_origen or not self.carpeta_destino:
            messagebox.showwarning("Advertencia", "Debe seleccionar carpetas de origen y destino.")
            return

        conn = self.connect_to_db()
        if not conn:
            return

        archivos_cargados = 0
        errores = []
        for root, _, files in os.walk(self.carpeta_origen):
            for file in files:
                if file.lower().endswith('.csv') and file.startswith('J760') and 'CNCO' not in file:
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(self.carpeta_destino, file)

                    if self.procesar_carga(source_path, conn):
                        shutil.move(source_path, dest_path)
                        archivos_cargados += 1
                    else:
                        errores.append(f"Error en el archivo: {file}")

        conn.close()
        if errores:
            messagebox.showerror("Errores de procesamiento", f"Hubo {len(errores)} errores:\n" + "\n".join(errores))
        else:
            messagebox.showinfo("Proceso finalizado", f"Se cargaron correctamente {archivos_cargados} archivos.")