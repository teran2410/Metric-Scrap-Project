"""
monthly_tab.py - Pestaña para reportes mensuales
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from ui.tabs.base_tab import BaseTab
from src.processors.data_loader import load_data
from src.processors.monthly_processor import process_monthly_data
from src.pdf_monthly_generator import generate_monthly_pdf_report
from src.analysis.monthly_contributors import export_monthly_contributors_to_console, get_monthly_location_contributors
from config import MONTHS_NUM_TO_ES

class MonthlyTab(BaseTab):
    """Pestaña para generación de reportes mensuales"""
    
    def __init__(self, parent_frame, root_app):
        """
        Inicializa la pestaña mensual
        
        Args:
            parent_frame: Frame padre
            root_app: Referencia a la aplicación principal
        """
        super().__init__(parent_frame)
        self.root_app = root_app
        self.current_month = datetime.now().month
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña mensual"""
        
        # Selector de año
        self.year_combobox = self.create_year_selector(command=self.on_year_change)
        
        # Selector de mes
        month_label = ctk.CTkLabel(
            self.frame,
            text="Mes:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        month_label.pack(pady=(15, 5))
        
        self.month_combobox = ctk.CTkComboBox(
            self.frame,
            values=[],
            width=200,
            justify="center",
            state="readonly"
        )
        self.month_combobox.pack(pady=5)
        
        # Actualizar meses disponibles
        self.update_months_for_year(self.current_year)
        
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
        self.update_months_for_year(int(selected_year))
    
    def update_months_for_year(self, year):
        """Actualiza los meses disponibles según el año"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        if year < current_year:
            # Año pasado: mostrar todos los meses
            max_month = 12
        elif year == current_year:
            # Año actual: solo meses transcurridos
            max_month = current_month
        else:
            # Año futuro
            max_month = 0
        
        # Crear lista de meses (nombre completo)
        months_list = [f"{month:02d} - {MONTHS_NUM_TO_ES[month]}" for month in range(1, max_month + 1)]
        self.month_combobox.configure(values=months_list)

        if months_list:
            self.month_combobox.set(f"{max_month:02d} - {MONTHS_NUM_TO_ES[max_month]}")
        else:
            self.month_combobox.set("")
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un hilo separado"""
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()
    
    def generate_pdf(self):
        """Genera el PDF mensual con todos los datos"""
        try:
            # Obtener valores
            year = int(self.year_combobox.get())
            month_str = self.month_combobox.get()
            
            if not month_str:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Seleccione un mes válido"))
                return
            
            # Extraer número de mes (formato: "01 - Enero")
            month = int(month_str.split(" - ")[0])
            
            # Validaciones
            if month < 1 or month > 12:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "El mes debe estar entre 1 y 12"))
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

            # Si la aplicación tiene un ReportService para mensual, usarlo (adapter generará el PDF)
            service = getattr(self.root_app, 'report_service_monthly', None)
            if service:
                # El servicio devuelve la ruta al PDF o None
                filepath = service.run_report({'month': month, 'year': year})
                if filepath:
                    # Ocultar progreso y notificar éxito
                    self.root_app.after(0, lambda: self.hide_progress(
                        self.progress_bar, self.status_label, self.pdf_button
                    ))
                    self.root_app.after(0, lambda: messagebox.showinfo(
                        "Éxito",
                        f"El archivo [{os.path.basename(filepath)}]\n\n se ha generado exitosamente."
                    ))
                    try:
                        if os.name == 'nt':
                            os.startfile(filepath)
                        elif os.name == 'posix':
                            os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
                    except:
                        pass
                    return
                else:
                    # Si service no generó nada, continuar con el flujo local (resultado None)
                    result = None
            else:
                result = process_monthly_data(scrap_df, ventas_df, horas_df, month, year)

            if result is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showwarning(
                    "Sin datos",
                    f"No se encontraron datos para:\n\nMes: {MONTHS_NUM_TO_ES[month]}\nAño: {year}"
                ))
                return
            
            # Paso 3: Analizar contribuidores
            self.root_app.after(0, lambda: self.status_label.configure(text="🔍 Analizando contribuidores..."))
            
            contributors = export_monthly_contributors_to_console(scrap_df, month, year, top_n=10)
            locations = get_monthly_location_contributors(scrap_df, month, year, top_n=10)
            
            # Paso 4: Generar PDF
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))
            
            filepath = generate_monthly_pdf_report(
                result,
                contributors,
                month, 
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