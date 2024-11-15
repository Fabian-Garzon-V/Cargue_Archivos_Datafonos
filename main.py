import customtkinter as ctk
from tkinter import messagebox
from ui.decompression import DecompressionTab
from ui.consolidation import ConsolidationTab
from ui.config_tab import ConfigTab
from database import connect_to_db
from config import cargar_configuracion, recargar_configuracion  # Importa la función del módulo config.py

# Configuración de customtkinter
ctk.set_appearance_mode("dark")  # Tema oscuro
ctk.set_default_color_theme("dark-blue")  # Color de acento

# Cargar la configuración usando config.py
config = cargar_configuracion()

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación Descompresión-Cargue archivos - Datafonos")
        self.root.geometry("1196x600")
        self.db_connection = None
        self.db_password = None
        self.show_login_screen()

    def refresh_ui(self):
        """Recarga la configuración desde config.ini y actualiza la interfaz."""
        global config  # Actualiza la variable global config
        config = recargar_configuracion()  # Recarga la configuración desde config.ini

        # Actualiza los campos de inicio de sesión si existen
        if hasattr(self, 'username_entry') and self.username_entry.winfo_exists():
            self.username_entry.delete(0, ctk.END)
            self.username_entry.insert(0, config['database']['user'])
            print("Usuario actualizado en la pantalla de inicio de sesión.")

        # Puedes agregar más actualizaciones según sea necesario
        print("La interfaz se ha actualizado con la nueva configuración.")

    def show_login_screen(self):
        self.login_frame = ctk.CTkFrame(self.root)
        self.login_frame.pack(pady=100, padx=50)

        title_label = ctk.CTkLabel(self.login_frame, text="Inicio de Sesión", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        user_label = ctk.CTkLabel(self.login_frame, text="Usuario:", font=("Arial", 14))
        user_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")
        
        self.username_entry = ctk.CTkEntry(self.login_frame, font=("Arial", 12))
        # Leer el usuario desde la configuración
        self.username_entry.insert(0, config['database']['user'])
        self.username_entry.grid(row=1, column=1, pady=5, padx=10)
        
        password_label = ctk.CTkLabel(self.login_frame, text="Contraseña:", font=("Arial", 14))
        password_label.grid(row=2, column=0, pady=5, padx=10, sticky="w")

        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=2, column=1, pady=5, padx=10)

        login_button = ctk.CTkButton(self.login_frame, text="Iniciar Sesión", command=self.attempt_login, font=("Arial", 14, "bold"))
        login_button.grid(row=3, column=0, columnspan=2, pady=(20, 10))

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        self.db_connection = connect_to_db(username, password)
        
        if self.db_connection:
            self.db_password = password
            self.login_frame.destroy()
            messagebox.showinfo("Inicio de Sesión Exitoso", "Bienvenido a la aplicación.")
            self.show_main_interface()
        else:
            messagebox.showerror("Error de Inicio de Sesión", "Usuario o contraseña incorrectos.")
            self.password_entry.delete(0, ctk.END)

    def show_main_interface(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=(20, 10), pady=20)
        
        button_texts = ["Descompresión", "Consolidación", "Configuración"]
        button_commands = [self.show_decompression_tab, self.show_consolidation_tab, self.show_config_tab]

        for i, (text, cmd) in enumerate(zip(button_texts, button_commands)):
            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=cmd,
                font=("Arial", 14, "bold"),
                fg_color="#b11c5a",       # Color de fondo del botón
                hover_color="#d23e76",    # Color al pasar el mouse
                width=200
            )
            button.pack(pady=15, padx=10, fill="x")

        self.card_container = ctk.CTkFrame(self.root, corner_radius=15)
        self.card_container.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)

        self.cards = {
            "decompression": ctk.CTkFrame(self.card_container, corner_radius=15),
            "consolidation": ctk.CTkFrame(self.card_container, corner_radius=15),
            "config": ctk.CTkFrame(self.card_container, corner_radius=15)
        }

        self.init_tabs()
        self.show_decompression_tab()

    def init_tabs(self):
        # Pasar `config` cargado y `self.db_password` a cada clase
        self.decompression_tab = DecompressionTab(self.cards["decompression"], self.db_password, config)
        self.consolidation_tab = ConsolidationTab(self.cards["consolidation"], self.db_password, config)
        self.config_tab = ConfigTab(self.cards["config"], self)

        for card in self.cards.values():
            card.pack_forget()  # Ocultamos todas las tarjetas al inicio

    def show_decompression_tab(self):
        self._show_card("decompression")

    def show_consolidation_tab(self):
        self._show_card("consolidation")

    def show_config_tab(self):
        self._show_card("config")

    def _show_card(self, card_name):
        for name, card in self.cards.items():
            if name == card_name:
                card.pack(fill="both", expand=True, padx=10, pady=10)
            else:
                card.pack_forget()

root = ctk.CTk()
app = DatabaseApp(root)
root.mainloop()
