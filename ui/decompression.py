import os
import pyzipper
import pyodbc
import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
from datetime import datetime
import configparser

# Cargar configuraciones desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

class DecompressionTab:
    def __init__(self, frame, db_password, config):
        """
        Inicializa la pestaña de descompresión.
        Recibe el frame de la tarjeta y la contraseña de la base de datos (db_password).
        """
        self.frame = frame
        self.db_password = db_password

        # Configuración de conexión a la base de datos
        self.db_server = config['database']['server']
        self.db_database = config['database']['database']
        self.db_user = config['database']['user']
        self.table_control_descompression = config['decompression'].get('table_control_descompression', 'ControlDescompresionDatafonos')
        self.base_folder = config['decompression'].get('base_folder', '')

        # Crear los elementos de la interfaz
        self.create_widgets()

    def create_widgets(self):
        """Crea los elementos de la interfaz de usuario en la pestaña de descompresión"""
        # Título de la sección
        title_label = ctk.CTkLabel(self.frame, text="Descompresión de Archivos", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Etiqueta de entrada de la ruta de descompresión
        folder_label = ctk.CTkLabel(self.frame, text="Ruta de Carpeta Base para Descompresión:", font=("Arial", 14))
        folder_label.pack(pady=5)

        # Campo de entrada para la ruta de descompresión
        self.decompression_path = ctk.CTkEntry(self.frame, width=700)
        self.decompression_path.insert(0, self.base_folder)  # Cargar ruta desde config.ini
        self.decompression_path.pack(pady=5)
        
        # Botón para seleccionar carpeta
        select_button = ctk.CTkButton(
            self.frame, 
            text="Seleccionar Carpeta", 
            command=self.select_decompression_path,            
            font=("Arial", 12, "bold"),
            fg_color="#c00063",
            hover_color="#b0005c",
            width=200
        )
        select_button.pack(pady=5)
        

        # Botón para iniciar la descompresión
        extract_button = ctk.CTkButton(
        self.frame,
        text="Descomprimir Archivos",
        command=self.run_extraction,
        font=("Arial", 14, "bold"),
        fg_color="#c00063",
        hover_color="#b0005c",
        width=200        
        )
        extract_button.pack(pady=20)

    def select_decompression_path(self):
        """Permite al usuario seleccionar una carpeta base para la descompresión"""
        path = filedialog.askdirectory()
        if path:
            self.decompression_path.delete(0, ctk.END)
            self.decompression_path.insert(0, path)

    def run_extraction(self):
        """Ejecuta el proceso de extracción de archivos ZIP encriptados"""
        folder_selected = self.decompression_path.get()
        
        # Confirmar que la carpeta es válida
        if not os.path.isdir(folder_selected):
            messagebox.showerror("Error", "La ruta especificada no es válida o no existe.")
            return

        # Solicitar la contraseña para los archivos ZIP (solo una vez)
        zip_password = simpledialog.askstring("Contraseña ZIP", "Introduce la contraseña para los archivos ZIP:", show='*')
        if not zip_password:
            messagebox.showwarning("Advertencia", "No se ingresó ninguna contraseña para el ZIP. Operación cancelada.")
            return
        
        zip_password_bytes = zip_password.encode('utf-8')
        
        try:
            # Iniciar la extracción y contar archivos extraídos
            archivos_descomprimidos = self.extract_all_encrypted_zips(folder_selected, zip_password_bytes)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Proceso Completado", f"Se han descomprimido correctamente {archivos_descomprimidos} archivo(s) que comienzan con 'J'.")
        except Exception as e:
            # Mostrar error si ocurre algún problema
            messagebox.showerror("Error de Extracción", f"Ha ocurrido un error: {e}")

    def get_db_connection(self):
        """Crea y devuelve una conexión a la base de datos usando la contraseña obtenida del inicio de sesión."""
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_database};"
            f"UID={self.db_user};"
            f"PWD={self.db_password}"
        )
        print(f"Intentando conectar a la base de datos con el usuario {self.db_user}...")
        return pyodbc.connect(connection_string)

    def is_already_processed(self, zip_file_path):
        """Verifica si el archivo ya ha sido procesado, consultando la base de datos"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM [{self.table_control_descompression}] WHERE NombreArchivo = ?", zip_file_path)
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def update_database(self, zip_file_path):
        """Registra el archivo procesado en la base de datos con la fecha y hora actual"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        fecha_carga = datetime.now()
        cursor.execute(f"INSERT INTO [{self.table_control_descompression}] (NombreArchivo, FechaCarga) VALUES (?, ?)", zip_file_path, fecha_carga)
        conn.commit()
        conn.close()

    def extract_encrypted_zip(self, zip_file_path, output_folder, password):
        """Extrae un archivo ZIP encriptado, si no ha sido procesado previamente"""
        if self.is_already_processed(zip_file_path):
            print(f"El archivo ya ha sido procesado: {zip_file_path}. Se omite.")
            return False  # No se descomprimió el archivo
        
        try:
            with pyzipper.AESZipFile(zip_file_path) as zf:
                zf.pwd = password
                zf.extractall(output_folder)
                print(f"Archivos extraídos correctamente: {zip_file_path}")
                self.update_database(zip_file_path)
                return True  # El archivo se descomprimió correctamente
        except Exception as e:
            print(f"Error al extraer {zip_file_path}: {e}")
            return False

    def extract_all_encrypted_zips(self, base_folder, password):
        """Extrae todos los archivos ZIP encriptados en una carpeta que comiencen con 'J'"""
        archivos_descomprimidos = 0
        
        for root, _, files in os.walk(base_folder):
            for file in files:
                # Verificar que el archivo sea un ZIP y que comience con "J"
                if file.lower().endswith('.zip') and file.lower().startswith('j'):
                    zip_file_path = os.path.join(root, file)
                    output_folder = root
                    
                    # Intentar extraer el archivo
                    if self.extract_encrypted_zip(zip_file_path, output_folder, password):
                        archivos_descomprimidos += 1
                        print(f"Archivo descomprimido correctamente: {zip_file_path}")
                    else:
                        print(f"No se pudo descomprimir o ya fue procesado: {zip_file_path}")
        
        return archivos_descomprimidos
