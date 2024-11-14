import customtkinter as ctk
from tkinter import messagebox
import sys
import os

def get_resource_path(relative_path):
    # Obtiene la ruta del directorio de ejecución del .exe o script
    if getattr(sys, 'frozen', False):  # Verifica si está empaquetado
        dir_actual = os.path.dirname(sys.executable)
    else:
        dir_actual = os.path.abspath(".")
    return os.path.join(dir_actual, relative_path)

class ConfigTab:
    def __init__(self, frame, config):
        """
        Inicializa la pestaña de configuración.
        Recibe el frame donde se mostrarán los widgets.
        """
        self.frame = frame
        self.config = config  # Usa directamente el config pasado como argumento

        # Mapeo para mostrar nombres amigables
        self.label_mapping = {
            'database.server': 'Servidor',
            'database.database': 'Base de Datos',
            'database.user': 'Usuario',
            # 'paths.decompression_origin': 'Ruta de Descompresión',
            'decompression.base_folder': 'Ruta de archivos descomprensión',
            'paths.consolidation_origin': 'Ruta de Consolidación Origen',
            'paths.consolidation_dest': 'Ruta de Consolidación Destino',
            'decompression.table_control_descompression': 'SQL - Tabla control archivos descomprimidos',
            'consolidation.table_control_cargue': 'SQL - Tabla Control Carga Archivos Datafonos',
            'consolidation.table_datafonos': 'SQL - Tabla Consolidado Archivos Datafonos'
        }

        # Crear widgets para modificar configuraciones
        self.create_widgets()

    def create_widgets(self):
        """Crea campos de entrada en la pestaña usando nombres amigables"""
        self.entries = {}  # Para almacenar las entradas y acceder a los valores
        row = 0

        # Título de la sección de configuración
        title_label = ctk.CTkLabel(self.frame, text="Configuración de la Aplicación", font=("Arial", 20, "bold"))
        title_label.grid(row=row, column=0, columnspan=2, pady=(10, 20))

        row += 1

        for section in self.config.sections():
            for key in self.config[section]:
                # Formato: section.key
                config_key = f"{section}.{key}"
                # Obtener etiqueta amigable o usar la clave del config.ini
                label_text = self.label_mapping.get(config_key, config_key)
                
                # Crear y organizar el campo en la interfaz
                label = ctk.CTkLabel(self.frame, text=label_text, font=("Arial", 12))
                label.grid(row=row, column=0, padx=10, pady=5, sticky='w')

                entry = ctk.CTkEntry(self.frame, width=510, font=("Arial", 12))
                entry.insert(0, self.config[section][key])
                entry.grid(row=row, column=1, padx=10, pady=5)
                
                self.entries[config_key] = entry
                row += 1

        # Botón para guardar cambios
        save_button = ctk.CTkButton(self.frame, text="Guardar Cambios", command=self.save_changes, font=("Arial", 14, "bold"))
        save_button.grid(row=row, column=0, columnspan=2, pady=(20, 10))

    def save_changes(self):
        """Guarda los valores actualizados en el archivo config.ini"""
        config_path = get_resource_path("config.ini")  # Usa get_resource_path para obtener la ruta correcta

        for config_key, entry in self.entries.items():
            section, key = config_key.split('.')
            self.config[section][key] = entry.get()

        with open(config_path, 'w') as configfile:
            self.config.write(configfile)

        messagebox.showinfo("Configuración Guardada", "Los cambios han sido guardados en config.ini.")
