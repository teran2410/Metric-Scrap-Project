"""
Interfaz gráfica de usuario con customtkinter
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from src.data_processor import load_data, process_weekly_data
from src.pdf_generator import generate_pdf_report
from src.top_contributors import export_contributors_to_console
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_THEME, APP_COLOR_THEME, APP_ICON_PATH

class ScrapRateApp(ctk.CTk):
    """Aplicación principal para análisis de Scrap Rate"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT + 50}")  # Aumentar altura para tabs
        
        # Configurar el tema
        ctk.set_appearance_mode(APP_THEME)
        ctk.set_default_color_theme(APP_COLOR_THEME)
        
        # Configurar ícono de la aplicación
        if os.path.exists(APP_ICON_PATH):
            try:
                self.iconbitmap(APP_ICON_PATH)
            except:
                pass  # No hacer nada si falla (puede pasar en macOS/Linux)
            
        # Configurar ícono de la taskbar
        if os.path.exists(APP_ICON_PATH):
            try:
                self.iconphoto(True, APP_ICON_PATH)
            except:
                pass  # No hacer nada si falla (puede pasar en macOS/Linux)
            
        # icon = ctk.PhotoImage(file="assets/icon.ico")  # También puedes usar .ico
        # self.iconphoto(True, icon)
        
        # Obtener año y semana actual
        current_date = datetime.now()
        self.current_year = current_date.year
        self.current_week = int(current_date.strftime('%U'))
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Título principal
        title_label = ctk.CTkLabel(
            self, 
            text="Análisis del Métrico de Scrap",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 5))
        
        # Subtitulo principal
        title_label = ctk.CTkLabel(
            self, 
            text="Desarrollado por Oscar Teran",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray"
        )
        title_label.pack(pady=(0, 10))
        
        # Crear TabView (pestañas)
        self.tabview = ctk.CTkTabview(self, width=360, height=320)
        self.tabview.pack(pady=10, padx=40)
        
        # Agregar pestañas
        self.tabview.add("Semanal")
        self.tabview.add("Mensual") # Pestaña futura
        self.tabview.add("Trimestral")  # Pestaña futura
        self.tabview.add("Anual")  # Pestaña futura
        
        # Crear contenido de cada pestaña
        self.create_weekly_tab()
        self.create_monthly_tab()
        self.create_trimestral_tab()
        self.create_anual_tab()
        
    def create_weekly_tab(self):
        """Crea el contenido de la pestaña Semanal"""
        weekly_frame = self.tabview.tab("Semanal")
        
        # Label y Dropdown para Año
        year_label = ctk.CTkLabel(
            weekly_frame,
            text="Año:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        year_label.pack(pady=(20, 5))
        
        # Dropdown para Año (2023 hasta año actual)
        current_year = datetime.now().year
        years_list = [str(year) for year in range(2023, current_year + 1)]
        
        self.year_combobox = ctk.CTkComboBox(
            weekly_frame,
            values=years_list,
            width=200,
            justify="center",
            command=self.on_year_change,
            state="readonly"
        )
        self.year_combobox.set(str(self.current_year))
        self.year_combobox.pack(pady=5)
        
        # Label y Dropdown para Semana
        week_label = ctk.CTkLabel(
            weekly_frame,
            text="Semana:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        week_label.pack(pady=(15, 5))
        
        # Dropdown para Semana (se actualiza según el año)
        self.week_combobox = ctk.CTkComboBox(
            weekly_frame,
            values=[],
            width=200,
            justify="center",
            state="readonly"
        )
        self.week_combobox.pack(pady=5)
        
        # Actualizar semanas disponibles para el año actual
        self.update_weeks_for_year(self.current_year)
        
        # Barra de progreso (inicialmente oculta)
        self.weekly_progress_bar = ctk.CTkProgressBar(
            weekly_frame,
            width=250,
            height=15,
            mode="indeterminate"
        )
        
        # Label de estado (inicialmente oculto)
        self.weekly_status_label = ctk.CTkLabel(
            weekly_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        
        # Botón para generar PDF semanal
        self.weekly_pdf_button = ctk.CTkButton(
            weekly_frame,
            text="Generar Reporte PDF",
            command=self.start_weekly_pdf_generation,
            width=250,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.weekly_pdf_button.pack(pady=20)
    
    def create_monthly_tab(self):
        """Crea el contenido de la pestaña Mensual (en preparación)"""
        monthly_frame = self.tabview.tab("Mensual")
        
        # Label informativo
        info_label = ctk.CTkLabel(
            monthly_frame,
            text="Módulo en desarrollo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        info_label.pack(pady=60)
        
        description_label = ctk.CTkLabel(
            monthly_frame,
            text="Esta funcionalidad estará disponible próximamente.\nPermitirá generar reportes mensuales consolidados.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        description_label.pack(pady=10)
        
    def create_trimestral_tab(self):
        """Crea el contenido de la pestaña Trimestral (en preparación)"""
        monthly_frame = self.tabview.tab("Trimestral")
        
        # Label informativo
        info_label = ctk.CTkLabel(
            monthly_frame,
            text="Módulo en desarrollo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        info_label.pack(pady=60)
        
        description_label = ctk.CTkLabel(
            monthly_frame,
            text="Esta funcionalidad estará disponible próximamente.\nPermitirá generar reportes trimestrales consolidados.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        description_label.pack(pady=10)
    
    def create_anual_tab(self):
        """Crea el contenido de la pestaña Anual (en preparación)"""
        monthly_frame = self.tabview.tab("Anual")
        
        # Label informativo
        info_label = ctk.CTkLabel(
            monthly_frame,
            text="Módulo en desarrollo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        info_label.pack(pady=60)
        
        description_label = ctk.CTkLabel(
            monthly_frame,
            text="Esta funcionalidad estará disponible próximamente.\nPermitirá generar reportes anuales consolidados.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        description_label.pack(pady=10)
    
    def on_year_change(self, selected_year):
        """Actualiza las semanas disponibles cuando cambia el año"""
        self.update_weeks_for_year(int(selected_year))
    
    def update_weeks_for_year(self, year):
        """Actualiza el dropdown de semanas según el año seleccionado"""
        current_date = datetime.now()
        current_year = current_date.year
        current_week = int(current_date.strftime('%U'))
        
        if year < current_year:
            # Año pasado: mostrar todas las 52 semanas
            max_week = 52
        elif year == current_year:
            # Año actual: solo semanas transcurridas
            max_week = current_week
        else:
            # Año futuro: no debería llegar aquí
            max_week = 0
        
        # Crear lista de semanas
        weeks_list = [str(week) for week in range(0, max_week + 1)]
        
        # Actualizar el combobox
        self.week_combobox.configure(values=weeks_list)
        
        # Seleccionar la penúltima semana disponible
        if weeks_list:
            self.week_combobox.set(str(max_week - 1))
        else:
            self.week_combobox.set("")
        
    def show_weekly_progress(self, message):
        """Muestra la barra de progreso semanal"""
        self.weekly_status_label.configure(text=message)
        self.weekly_status_label.pack(pady=(5, 0))
        self.weekly_progress_bar.pack(pady=(10, 20))
        self.weekly_progress_bar.start()
        self.weekly_pdf_button.configure(state="disabled")
        
    def hide_weekly_progress(self):
        """Oculta la barra de progreso semanal"""
        self.weekly_progress_bar.stop()
        self.weekly_progress_bar.pack_forget()
        self.weekly_status_label.pack_forget()
        self.weekly_pdf_button.configure(state="normal")
        
    def start_weekly_pdf_generation(self):
        """Inicia la generación del PDF semanal en un hilo separado"""
        thread = threading.Thread(target=self.generate_weekly_pdf, daemon=True)
        thread.start()
        
    def generate_weekly_pdf(self):
        """Genera el PDF semanal directamente con todos los datos"""
        try:
            # Obtener valores de los comboboxes
            year = int(self.year_combobox.get())
            week_str = self.week_combobox.get()
            
            if not week_str:
                self.after(0, lambda: messagebox.showerror("Error", "Seleccione una semana válida"))
                return
                
            week = int(week_str)
            
            # Validar semana
            if week < 0 or week > 53:
                self.after(0, lambda: messagebox.showerror("Error", "La semana debe estar entre 0 y 53"))
                return
            
            # Validar año
            if year < 2000 or year > 2100:
                self.after(0, lambda: messagebox.showerror("Error", "Ingrese un año válido"))
                return
            
            # Mostrar progreso - Paso 1: Cargando datos
            self.after(0, lambda: self.show_weekly_progress("⌛ Cargando datos..."))
            
            # Cargar datos
            scrap_df, ventas_df, horas_df = load_data()
            
            if scrap_df is None:
                self.after(0, self.hide_weekly_progress)
                self.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'"
                ))
                return
            
            # Paso 2: Procesando datos
            self.after(0, lambda: self.weekly_status_label.configure(text="⚙️ Procesando datos..."))
            
            # Procesar datos del reporte semanal
            result = process_weekly_data(scrap_df, ventas_df, horas_df, week, year)
            
            if result is None:
                self.after(0, self.hide_weekly_progress)
                self.after(0, lambda: messagebox.showwarning(
                    "Sin datos", 
                    f"No se encontraron datos para:\n\nSemana: {week}\nAño: {year}"
                ))
                return
            
            # Paso 3: Analizando contribuidores
            self.after(0, lambda: self.weekly_status_label.configure(text="🔍 Analizando contribuidores..."))
            
            # Generar top contribuidores
            contributors = export_contributors_to_console(scrap_df, week, year, top_n=10)
            
            # Paso 4: Generando PDF
            self.after(0, lambda: self.weekly_status_label.configure(text="📄 Generando PDF..."))
            
            # Generar PDF con ambas tablas y scrap_df para análisis de locations
            filepath = generate_pdf_report(
                result,
                contributors,
                week, 
                year,
                scrap_df  # Agregar scrap_df para el gráfico de Pareto de celdas
            )
            
            # Ocultar progreso
            self.after(0, self.hide_weekly_progress)
            
            if filepath:
                # Abrir la carpeta donde se guardó el PDF
                folder_path = os.path.dirname(filepath)
                
                self.after(0, lambda: messagebox.showinfo(
                    "PDF Generado",
                    f"PDF generado exitosamente:\n\n{os.path.basename(filepath)}\n\nUbicación: {folder_path}"
                ))
                
                # # Abrir la carpeta automáticamente
                # try:
                #     if os.name == 'nt':  # Windows
                #         os.startfile(folder_path)
                #     elif os.name == 'posix':  # macOS y Linux
                #         os.system(f'open "{folder_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{folder_path}"')
                # Abrir el archivo PDF directamente
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(filepath)
                    elif os.name == 'posix':  # macOS y Linux
                        os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
                except:
                    pass
            else:
                self.after(0, lambda: messagebox.showerror("Error", "No se pudo generar el PDF"))
                
        except ValueError:
            self.after(0, self.hide_weekly_progress)
            self.after(0, lambda: messagebox.showerror("Error", "Ingrese valores numéricos válidos"))
        except Exception as e:
            self.after(0, self.hide_weekly_progress)
            self.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error:\n\n{str(e)}"))


def run_app():
    """Ejecuta la aplicación"""
    app = ScrapRateApp()
    app.mainloop()