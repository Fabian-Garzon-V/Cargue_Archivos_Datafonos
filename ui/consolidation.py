import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config import cargar_configuracion, guardar_rutas
import pyodbc
import shutil

class ConsolidationTab:
    def __init__(self, frame, db_password, config):
        print("Inicializando ConsolidationTab...")  # Debug
        self.frame = frame
        self.db_password = db_password
        
        # Usa directamente el config cargado desde config.py
        self.config = config
        self.server = self.config['database']['server']
        self.database = self.config['database']['database']
        self.username = self.config['database']['user']
        
        # Rutas de origen y destino
        self.carpeta_origen = self.config['paths']['consolidation_origin']
        self.carpeta_destino = self.config['paths']['consolidation_dest']
        
        # Nombre de las tablas para el control y la consolidación de datos
        self.table_control_cargue = self.config['consolidation']['table_control_cargue']
        self.table_datafonos = self.config['consolidation']['table_datafonos']

        self.create_widgets()

    def create_widgets(self):
        print("Creando widgets en ConsolidationTab...")  # Debug
        title_label = ctk.CTkLabel(self.frame, text="Consolidación de Archivos", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))

        select_origin_button = ctk.CTkButton(
            self.frame, 
            text="Seleccionar Carpeta Origen", 
            command=self.seleccionar_carpeta_origen,
            font=("Arial", 12),
            fg_color="#c00063",
            hover_color="#b0005c",
            width=200 
        )
        select_origin_button.pack(pady=5)

        self.label_origen = ctk.CTkLabel(
            self.frame,
            text=f"Origen: {self.carpeta_origen if self.carpeta_origen else 'No seleccionado'}",
            font=("Arial", 10)
        )
        self.label_origen.pack()

        select_dest_button = ctk.CTkButton(
            self.frame, 
            text="Seleccionar Carpeta Destino", 
            command=self.seleccionar_carpeta_destino,
            font=("Arial", 12),
            fg_color="#c00063",
            hover_color="#b0005c",
            width=200 
        )
        select_dest_button.pack(pady=5)

        self.label_destino = ctk.CTkLabel(
            self.frame,
            text=f"Destino: {self.carpeta_destino if self.carpeta_destino else 'No seleccionado'}",
            font=("Arial", 10)
        )
        self.label_destino.pack()

        save_button = ctk.CTkButton(
            self.frame, 
            text="Guardar Configuración", 
            command=self.guardar_configuracion, 
            font=("Arial", 12),
            fg_color="#c00063",
            hover_color="#b0005c",
            width=200 
        )
        save_button.pack(pady=10)

        process_button = ctk.CTkButton(
            self.frame, 
            text="Cargar Archivos",
            command=self.procesar_carga,
            font=("Arial", 14, "bold"),
            fg_color="#b11c5a",
            hover_color="#d23e76",
            width=200
        )
        process_button.pack(pady=(20, 10))

    def seleccionar_carpeta_origen(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta de origen")
        if carpeta:
            self.carpeta_origen = carpeta
            self.label_origen.configure(text=f"Origen: {self.carpeta_origen}")

    def seleccionar_carpeta_destino(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta de destino")
        if carpeta:
            self.carpeta_destino = carpeta
            self.label_destino.configure(text=f"Destino: {self.carpeta_destino}")

    def guardar_configuracion(self):
        """
        Guarda las rutas de origen y destino en config.py.
        """
        guardar_rutas(self.carpeta_origen, self.carpeta_destino)
        messagebox.showinfo("Configuración guardada", "Las rutas han sido guardadas correctamente.")

    def connect_to_db(self):
        """
        Conecta a la base de datos usando pyodbc.
        """
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
        """
        Procesa los archivos desde la carpeta de origen y los mueve a la carpeta de destino.
        Recarga dinámicamente las configuraciones actualizadas desde config.py.
        """
        # Recarga la configuración actualizada
        self.config = cargar_configuracion()
        self.server = self.config['database']['server']
        self.database = self.config['database']['database']
        self.username = self.config['database']['user']
        self.carpeta_origen = self.config['paths']['consolidation_origin']
        self.carpeta_destino = self.config['paths']['consolidation_dest']
        self.table_control_cargue = self.config['consolidation']['table_control_cargue']
        self.table_datafonos = self.config['consolidation']['table_datafonos']

        # Validar las rutas antes de proceder
        if not self.carpeta_origen or not self.carpeta_destino:
            messagebox.showwarning("Advertencia", "Debe seleccionar carpetas de origen y destino.")
            return

        # Conectar a la base de datos
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

                    if self.procesar_archivo(source_path, conn):
                        shutil.move(source_path, dest_path)
                        archivos_cargados += 1
                    else:
                        errores.append(f"Error en el archivo: {file}")

        conn.close()
        if errores:
            messagebox.showerror("Errores de procesamiento", f"Hubo {len(errores)} errores:\n" + "\n".join(errores))
        else:
            messagebox.showinfo("Proceso finalizado", f"Se cargaron correctamente {archivos_cargados} archivos.")


    def procesar_archivo(self, source_path, conn):
        """
        Procesa un archivo individual y lo carga en la base de datos.
        """
        try:
            # Aquí va la lógica de procesamiento del archivo
            print(f"Procesando archivo: {source_path}")  # Debug
            return True
        except Exception as e:
            print(f"Error al procesar el archivo {source_path}: {e}")
            return False
