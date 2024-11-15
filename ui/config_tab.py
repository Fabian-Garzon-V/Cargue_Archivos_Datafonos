import customtkinter as ctk
from tkinter import messagebox
from config import guardar_rutas, guardar_base_datos, guardar_tablas_consolidacion, recargar_configuracion

class ConfigTab:
    def __init__(self, frame, app):
        """
        Inicializa la pestaña de configuración.
        Recibe el frame donde se mostrarán los widgets y una referencia a la aplicación principal.
        """
        self.frame = frame
        self.app = app  # Referencia a la instancia de DatabaseApp
        self.config = recargar_configuracion()  # Cargar configuración inicial

        # Mapeo para mostrar nombres amigables
        self.label_mapping = {
            'database.server': 'Servidor',
            'database.database': 'Base de Datos',
            'database.user': 'Usuario',
            'paths.consolidation_origin': 'Ruta de Consolidación Origen',
            'paths.consolidation_dest': 'Ruta de Consolidación Destino',
            'decompression.base_folder': 'Ruta de archivos descompresión',
            'decompression.table_control_descompression': 'SQL - Tabla control archivos descomprimidos',
            'consolidation.table_control_cargue': 'SQL - Tabla Control Carga Archivos Datafonos',
            'consolidation.table_datafonos': 'SQL - Tabla Consolidado Archivos Datafonos'
        }

        # Crear widgets para modificar configuraciones
        self.create_widgets()

    def create_widgets(self):
        """Crea campos de entrada en la pestaña usando nombres amigables."""
        self.entries = {}  # Para almacenar las entradas y acceder a los valores
        row = 0

        # Título de la sección de configuración
        title_label = ctk.CTkLabel(self.frame, text="Configuración de la Aplicación", font=("Arial", 20, "bold"))
        title_label.grid(row=row, column=0, columnspan=2, pady=(10, 20))

        row += 1

        # Iterar sobre las configuraciones cargadas
        for section, keys in self.config.items():
            for key, value in keys.items():
                # Formato: section.key
                config_key = f"{section}.{key}"
                # Obtener etiqueta amigable o usar la clave directamente
                label_text = self.label_mapping.get(config_key, config_key)
                
                # Crear y organizar el campo en la interfaz
                label = ctk.CTkLabel(self.frame, text=label_text, font=("Arial", 12))
                label.grid(row=row, column=0, padx=10, pady=5, sticky='w')

                entry = ctk.CTkEntry(self.frame, width=510, font=("Arial", 12))
                entry.insert(0, value)  # Insertar el valor actual de la configuración
                entry.grid(row=row, column=1, padx=10, pady=5)
                
                self.entries[config_key] = entry
                row += 1

        # Botón para guardar cambios
        save_button = ctk.CTkButton(
            self.frame, 
            text="Guardar Cambios", 
            command=self.save_changes, 
            font=("Arial", 14, "bold"),
            fg_color="#b11c5a",
            hover_color="#d23e76",
            width=200
        )
        save_button.grid(row=row, column=0, columnspan=2, pady=(20, 10))

    def save_changes(self):
        """Guarda los valores actualizados en config.ini y refresca la aplicación principal."""
        rutas = {}
        db_config = {}
        tablas_consolidacion = {}
        decompression_config = {}

        # Extraer valores modificados por el usuario
        for config_key, entry in self.entries.items():
            section, key = config_key.split('.')
            value = entry.get()

            if section == 'paths':
                rutas[key] = value
            elif section == 'database':
                db_config[key] = value
            elif section == 'decompression':
                decompression_config[key] = value
            elif section == 'consolidation':
                tablas_consolidacion[key] = value

        # Guardar cada sección usando las funciones de config.py
        if rutas:
            guardar_rutas(
                rutas.get("consolidation_origin", ""), 
                rutas.get("consolidation_dest", "")
            )
        if db_config:
            guardar_base_datos(
                db_config.get("server", ""), 
                db_config.get("database", ""), 
                db_config.get("user", "")
            )
        if tablas_consolidacion:
            guardar_tablas_consolidacion(
                tablas_consolidacion.get("table_control_cargue", ""), 
                tablas_consolidacion.get("table_datafonos", "")
            )

        # Llamar a refresh_ui para actualizar la interfaz principal
        self.app.refresh_ui()

        # Mostrar mensaje de éxito
        messagebox.showinfo("Configuración Guardada", "Los cambios han sido guardados correctamente.")
