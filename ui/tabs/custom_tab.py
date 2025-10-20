"""
custom_tab.py - Pestaña para reportes personalizados por rango de fechas
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading
import re
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
        
        # Label para Fecha Inicial
        start_label = ctk.CTkLabel(
            self.frame,
            text="Fecha Inicial:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_label.pack(pady=(20, 5))

        # Entry para fecha inicial
        self.start_date = ctk.CTkEntry(
            self.frame,
            width=120,
            height=30,
            font=ctk.CTkFont(size=14),
            placeholder_text="dd/mm/aaaa"
        )
        self.start_date.pack(pady=5)

        # Label para Fecha Final
        end_label = ctk.CTkLabel(
            self.frame,
            text="Fecha Final:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        end_label.pack(pady=(15, 5))

        # Entry para fecha final
        self.end_date = ctk.CTkEntry(
            self.frame,
            width=120,
            height=30,
            font=ctk.CTkFont(size=14),
            placeholder_text="dd/mm/aaaa"
        )
        self.end_date.pack(pady=5)

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

    def validate_date(self, date_str):
        """
        Valida el formato de fecha dd/mm/aaaa y su validez
        Args:
            date_str: String con la fecha a validar
        Returns:
            datetime o None si la fecha es inválida
        """
        # Verificar formato
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
            return None
        
        try:
            # Convertir a datetime
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            return None

    def generate_pdf(self):
        """Genera el PDF personalizado con los datos del rango de fechas"""
        try:
            # Obtener y validar fechas
            start_str = self.start_date.get()
            end_str = self.end_date.get()
            
            # Validar formato y existencia de fechas
            start_date = self.validate_date(start_str)
            if not start_date:
                messagebox.showerror(
                    "Error", 
                    f"Fecha inicial inválida: {start_str}\nUse el formato dd/mm/aaaa"
                )
                return
                
            end_date = self.validate_date(end_str)
            if not end_date:
                messagebox.showerror(
                    "Error", 
                    f"Fecha final inválida: {end_str}\nUse el formato dd/mm/aaaa"
                )
                return
            
            # Ajustar las horas
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())

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

            # Paso 2: Procesar datos y generar reporte via ReportService si está disponible
            self.root_app.after(0, lambda: self.status_label.configure(text="⚙️ Procesando datos..."))

            service = getattr(self.root_app, 'report_service_custom', None)
            if service:
                # ReportService espera claves start_date y end_date (ya normalizamos antes)
                filepath = service.run_report({'start_date': start_date, 'end_date': end_date})
                if filepath:
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
                    # continuar con el flujo local
                    result = None
            else:
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