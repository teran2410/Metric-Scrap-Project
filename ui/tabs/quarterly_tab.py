"""
quarterly_tab.py - Pestaña para reportes trimestrales
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from ui.tabs.base_tab import BaseTab
from src.processors.data_loader import load_data
from src.processors.quarterly_processor import process_quarterly_data
from src.pdf_quarterly_generator import generate_quarterly_pdf_report
from src.analysis.quarterly_contributors import export_quarterly_contributors_to_console

class QuarterlyTab(BaseTab):
    """Pestaña para generación de reportes trimestrales"""
    
    QUARTERS = {
        1: "Q1 - Enero a Marzo",
        2: "Q2 - Abril a Junio",
        3: "Q3 - Julio a Septiembre",
        4: "Q4 - Octubre a Diciembre"
    }
    
    def __init__(self, parent_frame, root_app):
        super().__init__(parent_frame)
        self.root_app = root_app
        self.current_quarter = (datetime.now().month - 1) // 3 + 1
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña trimestral"""
        
        self.year_combobox = self.create_year_selector(command=self.on_year_change)
        
        quarter_label = ctk.CTkLabel(
            self.frame,
            text="Trimestre:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quarter_label.pack(pady=(15, 5))
        
        self.quarter_combobox = ctk.CTkComboBox(
            self.frame,
            values=[],
            width=200,
            justify="center",
            state="readonly"
        )
        self.quarter_combobox.pack(pady=5)
        
        self.update_quarters_for_year(self.current_year)
        
        self.progress_bar, self.status_label = self.create_progress_bar()
        
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
        self.update_quarters_for_year(int(selected_year))
    
    def update_quarters_for_year(self, year):
        """Actualiza los trimestres disponibles según el año"""
        current_date = datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1
        
        if year < current_year:
            max_quarter = 4
        elif year == current_year:
            max_quarter = current_quarter
        else:
            max_quarter = 0
        
        quarters_list = [self.QUARTERS[q] for q in range(1, max_quarter + 1)]
        self.quarter_combobox.configure(values=quarters_list)
        
        if quarters_list:
            self.quarter_combobox.set(self.QUARTERS[max_quarter])
        else:
            self.quarter_combobox.set("")
    
    def start_pdf_generation(self):
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()
    
    def generate_pdf(self):
        """Genera el PDF trimestral con todos los datos"""
        try:
            year = int(self.year_combobox.get())
            quarter_str = self.quarter_combobox.get()
            
            if not quarter_str:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Seleccione un trimestre válido"))
                return
            
            quarter = int(quarter_str.split(" - ")[0][1])
            
            if quarter < 1 or quarter > 4:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "El trimestre debe estar entre 1 y 4"))
                return
            
            if year < 2000 or year > 2100:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese un año válido"))
                return
            
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
            
            self.root_app.after(0, lambda: self.status_label.configure(text="⚙️ Procesando datos..."))

            service = getattr(self.root_app, 'report_service_quarterly', None)
            if service:
                filepath = service.run_report({'quarter': quarter, 'year': year})
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
                    result = None
            else:
                result = process_quarterly_data(scrap_df, ventas_df, horas_df, quarter, year)

            if result is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showwarning(
                    "Sin datos", 
                    f"No se encontraron datos para:\n\nTrimestre: Q{quarter}\nAño: {year}"
                ))
                return

            self.root_app.after(0, lambda: self.status_label.configure(text="🔍 Analizando contribuidores..."))
            
            contributors = export_quarterly_contributors_to_console(scrap_df, quarter, year, top_n=10)
            
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))
            
            filepath = generate_quarterly_pdf_report(
                result,
                contributors,
                quarter, 
                year,
                scrap_df
            )
            
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            
            if filepath:
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