"""
PDF Styles module - Centralized style definitions for all PDF reports
"""

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from config import COLOR_TEXT


def get_styles():
    """Get base ReportLab styles"""
    return getSampleStyleSheet()


def get_title_style():
    """Get title paragraph style"""
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )


def get_subtitle_style():
    """Get subtitle paragraph style"""
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=10,
        alignment=TA_CENTER
    )


def get_section_title_style():
    """Get section title style (for contributors section, etc.)"""
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'ContributorsTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )


def get_target_header_style(within_target=True):
    """Get style for DENTRO/FUERA DE META header"""
    styles = getSampleStyleSheet()
    header_color = colors.HexColor("#2E8B57") if within_target else colors.red
    
    return ParagraphStyle(
        'TargetHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=header_color,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
