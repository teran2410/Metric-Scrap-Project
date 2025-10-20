"""
weekly_tab.py - Pestaña para reportes semanales
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from ui.tabs.base_tab import BaseTab
from src.processors.data_loader import load_data
from src.processors.weekly_processor import process_weekly_data
from src.pdf_weekly_generator import generate_weekly_pdf_report
from src.analysis.weekly_contributors import export_contributors_to_console, get_weekly_location_contributors

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
        
        # Campo de entrada de semana (reemplaza al combobox)
        week_label = ctk.CTkLabel(
            self.frame,
            text="Semana:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        week_label.pack(pady=(15, 5))
        
        self.week_entry = ctk.CTkEntry(
            self.frame,
            width=200,
            justify="center",
            placeholder_text="Ingrese la semana (1-53)"
        )
        self.week_entry.pack(pady=5)
        
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
            fg_color="#2F6690",
            hover_color="#9DB4C0"
        )
        self.pdf_button.pack(pady=20)
    
    def on_year_change(self, selected_year):
        """Callback cuando cambia el año seleccionado"""
        # Ya no se requiere actualizar semanas, pero mantenemos el método por compatibilidad
        pass
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un hilo separado"""
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()
    
    def generate_pdf(self):
        """Genera el PDF semanal con todos los datos"""
        try:
            # Obtener valores
            year = int(self.year_combobox.get())
            week_str = self.week_entry.get().strip()
            
            # Validar entrada vacía
            if not week_str:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese una semana válida"))
                return
            
            # Validar que sea numérica
            if not week_str.isdigit():
                self.root_app.after(0, lambda: messagebox.showerror("Error", "La semana debe ser un número"))
                return
            
            week = int(week_str)
            
            # Validaciones de rango
            if week < 1 or week > 53:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "La semana debe estar entre 1 y 53"))
                return
            
            # Validar que la semana no sea mayor a la actual (si el año es el actual)
            current_date = datetime.now()
            try:
                current_week = int(current_date.isocalendar()[1])
            except Exception:
                current_week = int(current_date.strftime('%U'))
            current_year = current_date.year
            
            if year == current_year and week > current_week:
                self.root_app.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No se pueden generar reportes de semanas que aún no transcurren"
                ))
                return
            
            if year < 2000 or year > 2100:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese un año válido"))
                return
            
            # Ajustar semana a 0-indexado
            week -= 1
            
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
            locations = get_weekly_location_contributors(scrap_df, week, year, top_n=10)
            
            # Paso 4: Generar PDF
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))

            week += 1  # Ajustar a 1-indexado para el reporte

            # Si la aplicación principal proporcionó un ReportService/adapter, usarlo
            filepath = None
            try:
                service = getattr(self.root_app, 'report_service_weekly', None)
                if service is not None:
                    # Ejecutar servicio genérico
                    filepath = service.run_report({'week': week, 'year': year})
                else:
                    # Fallback: usar el generador directo
                    filepath = generate_weekly_pdf_report(
                        result,
                        contributors,
                        week,
                        year,
                        scrap_df,
                        locations
                    )
            except Exception:
                # En caso de fallo en el service, intentar el fallback directo
                filepath = generate_weekly_pdf_report(
                    result,
                    contributors,
                    week,
                    year,
                    scrap_df,
                    locations
                )
            
            # Ocultar progreso
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            
            # Mostrar mensaje de éxito o error
            if filepath:
                folder_path = os.path.dirname(filepath)
                
                self.root_app.after(0, lambda: messagebox.showinfo(
                    "Éxito",
                    f"El archivo [{os.path.basename(filepath)}]\n\n se ha generado exitosamente."
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
