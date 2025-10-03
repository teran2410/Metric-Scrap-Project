"""
base_tab.py - Clase base para las pestañas de la aplicación
"""

import customtkinter as ctk
from datetime import datetime


class BaseTab:
    """Clase base para las pestañas de la aplicación"""
    
    def __init__(self, parent_frame):
        """
        Inicializa la pestaña base
        
        Args:
            parent_frame: Frame padre donde se creará el contenido
        """
        self.frame = parent_frame
        self.current_year = datetime.now().year
        self.current_week = int(datetime.now().strftime('%U'))
        
    def create_development_message(self, title="Módulo en desarrollo"):
        """
        Crea un mensaje de desarrollo para pestañas futuras
        
        Args:
            title (str): Título del mensaje
        """
        info_label = ctk.CTkLabel(
            self.frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        info_label.pack(pady=60)
        
        description_label = ctk.CTkLabel(
            self.frame,
            text="Esta funcionalidad estará disponible próximamente.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        description_label.pack(pady=10)
    
    def create_year_selector(self, command=None):
        """
        Crea un selector de año reutilizable
        
        Args:
            command: Función callback cuando cambia el año
            
        Returns:
            CTkComboBox: ComboBox del año
        """
        year_label = ctk.CTkLabel(
            self.frame,
            text="Año:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        year_label.pack(pady=(20, 5))
        
        years_list = [str(year) for year in range(2023, self.current_year + 1)]
        
        year_combobox = ctk.CTkComboBox(
            self.frame,
            values=years_list,
            width=200,
            justify="center",
            command=command,
            state="readonly"
        )
        year_combobox.set(str(self.current_year))
        year_combobox.pack(pady=5)
        
        return year_combobox
    
    def create_progress_bar(self):
        """
        Crea una barra de progreso reutilizable
        
        Returns:
            tuple: (progress_bar, status_label)
        """
        progress_bar = ctk.CTkProgressBar(
            self.frame,
            width=250,
            height=15,
            mode="indeterminate"
        )
        
        status_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        
        return progress_bar, status_label
    
    def show_progress(self, progress_bar, status_label, button, message):
        """
        Muestra la barra de progreso
        
        Args:
            progress_bar: Barra de progreso
            status_label: Label de estado
            button: Botón a deshabilitar
            message (str): Mensaje a mostrar
        """
        status_label.configure(text=message)
        status_label.pack(pady=(5, 0))
        progress_bar.pack(pady=(10, 20))
        progress_bar.start()
        button.configure(state="disabled")
    
    def hide_progress(self, progress_bar, status_label, button):
        """
        Oculta la barra de progreso
        
        Args:
            progress_bar: Barra de progreso
            status_label: Label de estado
            button: Botón a habilitar
        """
        progress_bar.stop()
        progress_bar.pack_forget()
        status_label.pack_forget()
        button.configure(state="normal")