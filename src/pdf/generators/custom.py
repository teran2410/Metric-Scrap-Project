"""
custom.py - Generador PDF para reportes de rango de fechas personalizado
"""

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import get_main_table_style, get_contributors_table_style, apply_contributors_cumulative_coloring
from src.pdf.styles import get_section_title_style
from reportlab.platypus import Table, Paragraph
from reportlab.lib.units import inch
import os
import pandas as pd


class CustomPDFGenerator(BasePDFGenerator):
    """Generador de PDF para reportes personalizados (rango de fechas)"""
    
    def _calculate_target_achievement(self, df):
        """
        Calcula si el periodo personalizado cumple con el target promedio
        
        Returns:
            tuple: (within_target: bool, total_rate: float, target_rate: float)
        """
        if df is None or df.empty:
            return False, 0.0, 0.5
        
        # Usar el rate promedio del periodo
        total_rate = pd.to_numeric(df['Rate'].mean(), errors='coerce')
        target_rate = 0.8  # Target al 80% (0.8)
        
        within = total_rate <= target_rate if not pd.isna(total_rate) else False
        return within, total_rate if not pd.isna(total_rate) else 0.0, target_rate
    
    def _build_main_table_data(self, df):
        """
        Construye los datos de la tabla principal
        
        Returns:
            list: Lista con headers y filas de datos
        """
        if df is None or df.empty:
            return [['Sin datos disponibles']]
        
        data = []
        
        # Headers
        headers = ['Fecha', 'Scrap', 'Hrs Prod.', '$ Venta (dls)', 'Rate']
        data.append(headers)
        
        # Rows (el processor ya incluye la fila TOTAL)
        for _, row in df.iterrows():
            row_data = [
                str(row.get('Date', '')),
                f"{row.get('Scrap', 0):.2f}",
                f"{row.get('Hrs Prod.', 0):.2f}",
                f"${row.get('$ Venta (dls)', 0):,.2f}",
                f"{row.get('Rate', 0):.4f}"
            ]
            data.append(row_data)
        
        return data
    
    def _build_contributors_table_data(self, contributors_df):
        """
        Construye los datos de la tabla de contribuidores
        
        Returns:
            list: Lista con headers y filas de contribuidores
        """
        if contributors_df is None or contributors_df.empty:
            return None
        
        data = []
        
        # Headers - ahora con todas las columnas
        headers = ['Lugar', 'Número de Parte', 'Descripción', 'Ubicación', 'Cantidad', 'Monto (USD)', '% Acumulado']
        data.append(headers)
        
        # Rows
        for _, row in contributors_df.iterrows():
            # Detectar fila TOTAL
            is_total = str(row.get('Lugar', '')).upper() == 'TOTAL'
            
            lugar = str(row.get('Lugar', ''))
            numero_parte = str(row.get('Número de Parte', ''))
            descripcion = str(row.get('Descripción', ''))[:40]  # Limitar descripción
            ubicacion = str(row.get('Ubicación', ''))
            cantidad = row.get('Cantidad Scrapeada', 0)
            monto = row.get('Monto (dls)', 0)
            acum = row.get('% Acumulado', '')
            
            # Formatear valores
            if is_total:
                cantidad_fmt = f"{int(cantidad):,}" if cantidad != '' else ''
                monto_fmt = f"${monto:,.2f}" if monto != '' else ''
                acum_fmt = ''
            else:
                cantidad_fmt = f"{int(cantidad):,}"
                monto_fmt = f"${monto:,.2f}"
                acum_fmt = f"{acum:.1f}%" if acum != '' else ''
            
            row_data = [
                lugar,
                numero_parte,
                descripcion,
                ubicacion,
                cantidad_fmt,
                monto_fmt,
                acum_fmt
            ]
            data.append(row_data)
        
        return data
    
    def _build_reasons_table_data(self, reasons_df):
        """
        Construye los datos de la tabla de razones de scrap
        
        Returns:
            list: Lista con headers y filas de razones
        """
        if reasons_df is None or reasons_df.empty:
            return None
        
        data = []
        
        # Headers
        headers = ['Razón', 'Total Scrap', 'Cantidad', '% del Total']
        data.append(headers)
        
        # Rows
        for _, row in reasons_df.iterrows():
            row_data = [
                str(row.get('Reason', '')),
                f"{row.get('Total Scrap', 0):.2f}",
                str(row.get('Count', 0)),
                f"{row.get('% of Total', 0):.2f}%"
            ]
            data.append(row_data)
        
        return data
    
    def generate(self, data_df, contributors_df, reasons_df, start_date, end_date, output_path=None):
        """
        Genera el reporte PDF personalizado
        
        Args:
            data_df (DataFrame): DataFrame con los datos del periodo
            contributors_df (DataFrame): DataFrame con los principales contribuidores
            reasons_df (DataFrame): DataFrame con las principales razones
            start_date (datetime): Fecha inicial del periodo
            end_date (datetime): Fecha final del periodo
            output_path (str): Ruta completa donde guardar el PDF (opcional)
            
        Returns:
            str: Ruta del archivo PDF generado
        """
        # Setup
        self._close_matplotlib_figures()
        
        # Convertir fechas a datetime si son date objects
        if hasattr(start_date, 'strftime'):
            start_str_filename = start_date.strftime('%Y%m%d')
            start_str_display = start_date.strftime('%d/%m/%Y')
        else:
            from datetime import datetime
            start_dt = datetime.combine(start_date, datetime.min.time())
            start_str_filename = start_dt.strftime('%Y%m%d')
            start_str_display = start_dt.strftime('%d/%m/%Y')
        
        if hasattr(end_date, 'strftime'):
            end_str_filename = end_date.strftime('%Y%m%d')
            end_str_display = end_date.strftime('%d/%m/%Y')
        else:
            from datetime import datetime
            end_dt = datetime.combine(end_date, datetime.min.time())
            end_str_filename = end_dt.strftime('%Y%m%d')
            end_str_display = end_dt.strftime('%d/%m/%Y')
        
        # Si no se proporciona ruta de salida, usar la carpeta predeterminada
        if output_path is None:
            self._ensure_output_folder()
            filename = f"Scrap_Rate_Custom_{start_str_filename}_{end_str_filename}.pdf"
            output_path = os.path.join(self.output_folder, filename)
        
        doc = self._create_document(output_path)
        self.elements = []
        
        # Título
        self._add_main_title("REPORTE PERSONALIZADO DE SCRAP RATE")
        
        # Subtítulo con rango de fechas
        date_range = f"{start_str_display} - {end_str_display}"
        self._add_subtitle(f"{date_range} | Reporte generado automáticamente por Metric Scrap System")
        
        # Target achievement (basado en rate promedio)
        within, avg_rate, target = self._calculate_target_achievement(data_df)
        custom_text = "DENTRO DE META" if within else "✘ FUERA DE META"
        self._add_target_header(within, custom_text)
        
        self._add_spacer()
        
        # ========== TABLA PRINCIPAL ==========
        if data_df is not None and not data_df.empty:
            self._add_section_title("DATOS DEL PERIODO")
            
            table_data = self._build_main_table_data(data_df)
            table = Table(table_data, repeatRows=1)
            table.setStyle(get_main_table_style())
            self.elements.append(table)
            
            self._add_spacer(0.4)
        
        # ========== PRINCIPALES CONTRIBUIDORES ==========
        if contributors_df is not None and not contributors_df.empty:
            self._add_section_title("PRINCIPALES CONTRIBUIDORES")
            
            contrib_data = self._build_contributors_table_data(contributors_df)
            if contrib_data:
                contrib_table = Table(contrib_data, repeatRows=1)
                contrib_table_style = get_contributors_table_style()
                apply_contributors_cumulative_coloring(contrib_table_style, contrib_data, cumulative_col_idx=6, threshold=80.0)
                contrib_table.setStyle(contrib_table_style)
                self.elements.append(contrib_table)
                
                self._add_spacer(0.4)
        
        # ========== PRINCIPALES RAZONES ==========
        if reasons_df is not None and not reasons_df.empty:
            self._add_section_title("PRINCIPALES RAZONES DE SCRAP")
            
            reasons_data = self._build_reasons_table_data(reasons_df)
            if reasons_data:
                reasons_table = Table(reasons_data, repeatRows=1)
                reasons_table.setStyle(get_contributors_table_style())
                self.elements.append(reasons_table)
        
        # Build PDF
        return self.build_and_save(doc)


# ========== FUNCIÓN LEGACY PARA COMPATIBILIDAD ==========

def create_custom_report(data_df, contributors_df, start_date=None, end_date=None, reasons_df=None, output_path=None):
    """
    Función legacy para compatibilidad con código existente
    
    Soporta dos firmas:
    1. create_custom_report(data_df, contributors_df, start_date, end_date) - UI actual
    2. create_custom_report(data_df, contributors_df, reasons_df, start_date, end_date, output_path) - Firma completa
    
    Args:
        data_df (DataFrame): DataFrame con los datos del periodo
        contributors_df (DataFrame): DataFrame con los principales contribuidores
        start_date (datetime/date): Fecha inicial del periodo
        end_date (datetime/date): Fecha final del periodo
        reasons_df (DataFrame, optional): DataFrame con las principales razones
        output_path (str, optional): Ruta donde guardar el PDF
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    generator = CustomPDFGenerator()
    return generator.generate(data_df, contributors_df, reasons_df, start_date, end_date, output_path)
