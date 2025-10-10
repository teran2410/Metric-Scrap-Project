"""
custom_tab.py - Pestaña para reportes personalizados por rango de fechas
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading
from tkcalendar import DateEntry
from tkinter import ttk
import tkinter as tk

from ui.tabs.base_tab import BaseTab
from src.processors.data_loader import load_data
from src.processors.custom_processor import process_custom_data
from src.pdf_custom_generator import create_custom_report
from src.analysis.custom_contributors import get_top_contributors_custom, get_scrap_reasons_custom


class CustomTab(BaseTab):
    """Pestaña para generación de reportes personalizados"""

    def __init__(self, parent_frame, root_app):
        """
        Inicializa la pestaña personalizada
        Args:
            parent_frame: Frame padre
            root_app: Referencia a la aplicación principal
        """
        super().__init__(parent_frame)
        self.root_app = root_app
        self.create_content()

    def create_content(self):
        """Crea el contenido de la pestaña personalizada"""
        # Frame para las fechas
        dates_frame = ctk.CTkFrame(self.frame)
        dates_frame.pack(pady=10, padx=20, fill="x")

        # Fecha inicial
        start_label = ctk.CTkLabel(
            dates_frame,
            text="Fecha Inicial:",
            font=ctk.CTkFont(size=14)
        )
        start_label.grid(row=0, column=0, padx=5, pady=5)

        # Crear un frame especial para el DateEntry
        start_cal_frame = ttk.Frame(dates_frame)
        start_cal_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.start_date = DateEntry(
            start_cal_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.start_date.pack()

        # Fecha final
        end_label = ctk.CTkLabel(
            dates_frame,
            text="Fecha Final:",
            font=ctk.CTkFont(size=14)
        )
        end_label.grid(row=0, column=2, padx=5, pady=5)

        # Frame para el segundo DateEntry
        end_cal_frame = ttk.Frame(dates_frame)
        end_cal_frame.grid(row=0, column=3, padx=5, pady=5)
        
        self.end_date = DateEntry(
            end_cal_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.end_date.pack()

        # Configurar grid
        dates_frame.grid_columnconfigure((1, 3), weight=1)

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

    def start_pdf_generation(self):
        """Inicia la generación del PDF en un hilo separado"""
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()

    def generate_pdf(self):
        """Genera el PDF personalizado con los datos del rango de fechas"""
        try:
            # Obtener fechas
            start_date = datetime.combine(self.start_date.get_date(), datetime.min.time())
            end_date = datetime.combine(self.end_date.get_date(), datetime.max.time())

            # Validar rango de fechas
            if start_date > end_date:
                self.root_app.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "La fecha inicial debe ser anterior a la fecha final"
                ))
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
            result = process_custom_data(scrap_df, ventas_df, horas_df, start_date, end_date)
            if result is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showwarning(
                    "Sin datos",
                    f"No se encontraron datos para el periodo:\n{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
                ))
                return

            # Paso 3: Analizar contribuidores
            self.root_app.after(0, lambda: self.status_label.configure(text="🔍 Analizando contribuidores..."))
            contributors = get_top_contributors_custom(scrap_df, start_date, end_date)
            reasons = get_scrap_reasons_custom(scrap_df, start_date, end_date)

            # Paso 4: Generar PDF
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))
            filename = f"Scrap_Rate_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join("reports", filename)
            
            create_custom_report(
                result,
                contributors,
                reasons,
                start_date,
                end_date,
                filepath
            )

            # Ocultar progreso
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))

            # Mostrar mensaje de éxito y abrir PDF
            if os.path.exists(filepath):
                self.root_app.after(0, lambda: messagebox.showinfo(
                    "Éxito",
                    f"El archivo [{filename}]\n\n se ha generado exitosamente."
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

        except Exception as e:
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            error_msg = str(e)
            self.root_app.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Ocurrió un error:\n\n{msg}"))