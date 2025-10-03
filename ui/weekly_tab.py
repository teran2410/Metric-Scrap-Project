"""
weekly_tab.py - Pestaña para reportes semanales
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from ui.base_tab import BaseTab
from src.processors.data_processor import load_data, process_weekly_data
from src.reports.pdf_weekly_generator import generate_weekly_pdf_report
from src.analysis.top_contributors_by_week import export_contributors_to_console


class WeeklyTab(BaseTab):
    """Pestaña para generación de reportes semanales"""
    
    def __init__(self, parent_frame, root_app):
        """
        Inicializa la pestaña semanal
        
        Args:
            parent_frame: Frame padre
            root_app: Referencia a la aplicación principal
        """
        super().__init__(parent_frame)
        self.root_app = root_app
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña semanal"""
        
        # Selector de año
        self.year_combobox = self.create_year_selector(command=self.on_year_change)
        
        # Selector de semana
        week_label = ctk.CTkLabel(
            self.frame,
            text="Semana:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        week_label.pack(pady=(15, 5))
        
        self.week_combobox = ctk.CTkComboBox(
            self.frame,
            values=[],
            width=200,
            justify="center",
            state="readonly"
        )
        self.week_combobox.pack(pady=5)
        
        # Actualizar semanas disponibles
        self.update_weeks_for_year(self.current_year)
        
        # Barra de progreso
        self.progress_bar, self.status_label = self.create_progress_bar()
        
        # Botón generar PDF
        self.pdf_button = ctk.CTkButton(
            self.frame,
            text="Generar Reporte PDF",
            command=self.start_pdf_generation,
            width=250,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E8CFF",
            hover_color="#0049A3"
        )
        self.pdf_button.pack(pady=20)
    
    def on_year_change(self, selected_year):
        """Callback cuando cambia el año seleccionado"""
        self.update_weeks_for_year(int(selected_year))
    
    def update_weeks_for_year(self, year):
        """Actualiza las semanas disponibles según el año"""
        current_date = datetime.now()
        current_year = current_date.year
        current_week = int(current_date.strftime('%U'))
        
        if year < current_year:
            max_week = 53
        elif year == current_year:
            max_week = current_week
        else:
            max_week = 0
        
        weeks_list = [str(week) for week in range(1, max_week + 1)]
        self.week_combobox.configure(values=weeks_list)
        
        if weeks_list:
            self.week_combobox.set(str(max_week))
        else:
            self.week_combobox.set("")
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un hilo separado"""
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()
    
    def generate_pdf(self):
        """Genera el PDF semanal con todos los datos"""
        try:
            # Obtener valores
            year = int(self.year_combobox.get())
            week_str = self.week_combobox.get()
            
            if not week_str:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Seleccione una semana válida"))
                return
            
            week = int(week_str) - 1  # Ajustar a 0-indexado
            
            # Validaciones
            if week < 0 or week > 52:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "La semana debe estar entre 1 y 53"))
                return
            
            if year < 2000 or year > 2100:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese un año válido"))
                return
            
            # Paso 1: Cargar datos
            self.root_app.after(0, lambda: self.show_progress(
                self.progress_bar, self.status_label, self.pdf_button, "⌛ Cargando datos..."
            ))
            
            scrap_df, ventas_df, horas_df = load_data()
            
            if scrap_df is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'"
                ))
                return
            
            # Paso 2: Procesar datos
            self.root_app.after(0, lambda: self.status_label.configure(text="⚙️ Procesando datos..."))
            
            result = process_weekly_data(scrap_df, ventas_df, horas_df, week, year)
            
            if result is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showwarning(
                    "Sin datos", 
                    f"No se encontraron datos para:\n\nSemana: {week + 1}\nAño: {year}"
                ))
                return
            
            # Paso 3: Analizar contribuidores
            self.root_app.after(0, lambda: self.status_label.configure(text="🔍 Analizando contribuidores..."))
            
            contributors = export_contributors_to_console(scrap_df, week, year, top_n=10)
            
            # Paso 4: Generar PDF
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))
            
            week += 1  # Ajustar a 1-indexado para el reporte
            
            filepath = generate_weekly_pdf_report(
                result,
                contributors,
                week, 
                year,
                scrap_df
            )
            
            # Ocultar progreso
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            
            if filepath:
                folder_path = os.path.dirname(filepath)
                
                self.root_app.after(0, lambda: messagebox.showinfo(
                    "PDF Generado",
                    f"PDF generado exitosamente:\n\n{os.path.basename(filepath)}\n\nUbicación: {folder_path}"
                ))
                
                # Abrir PDF
                try:
                    if os.name == 'nt':
                        os.startfile(filepath)
                    elif os.name == 'posix':
                        os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
                except:
                    pass
            else:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "No se pudo generar el PDF"))
                
        except ValueError:
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese valores numéricos válidos"))
        except Exception as e:
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            self.root_app.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error:\n\n{str(e)}"))