"""
PDF Components module - Reusable table and component builders
"""

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from config import (
    COLOR_HEADER, COLOR_ROW, COLOR_TOTAL, COLOR_TEXT,
    COLOR_BAR, COLOR_BAR_EXCEED, COLOR_BG_CONTRIB
)


def get_main_table_style(with_conditional_coloring=True):
    """
    Get the standard table style for main data tables
    
    Args:
        with_conditional_coloring: Whether to check for rate>target conditional coloring
    
    Returns:
        TableStyle object
    """
    return TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_ROW)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),

        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor(COLOR_HEADER)),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])


def get_contributors_table_style():
    """Get table style for contributors/top defects tables"""
    return TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_BAR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_BG_CONTRIB)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Description column left-aligned
    ])


def apply_rate_conditional_coloring(table_style, data, rate_col_idx=7, target_col_idx=8):
    """
    Apply conditional coloring to table rows where rate > target
    
    Args:
        table_style: TableStyle object to modify
        data: List of lists with table data
        rate_col_idx: Index of the Rate column (default 7)
        target_col_idx: Index of the Target Rate column (default 8)
    """
    for i in range(1, len(data) - 1):  # Excluir header (0) y total (-1)
        try:
            rate_str = str(data[i][rate_col_idx])
            target_str = str(data[i][target_col_idx])
            
            # Convertir a float (remover $ si existe)
            rate = float(rate_str.replace('$', '').replace(',', ''))
            target = float(target_str.replace('$', '').replace(',', ''))
            
            # Si el rate excede el target, colorear la fila
            if rate > target:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor(COLOR_BAR_EXCEED))
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
        except (ValueError, IndexError):
            pass


def apply_contributors_cumulative_coloring(table_style, data, cumulative_col_idx=5, threshold=80.0):
    """
    Apply red tint to contributors rows until cumulative % reaches threshold
    
    Args:
        table_style: TableStyle object to modify
        data: List of lists with contributor data
        cumulative_col_idx: Index of cumulative % column (default 5 = % Acumulado)
        threshold: Cumulative percentage threshold (default 80.0%)
    """
    # Iterate through data rows, excluding header (0) and total row (last)
    for i in range(1, len(data) - 1):
        try:
            cumulative_str = str(data[i][cumulative_col_idx]).replace('%', '').strip()
            cumulative = float(cumulative_str)
            if cumulative <= threshold:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFCCCC'))
        except (ValueError, IndexError, AttributeError) as e:
            # Skip rows that can't be parsed
            pass
