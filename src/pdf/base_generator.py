"""
Base PDF Generator - Abstract base class for all PDF report generators
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import logging

from .styles import (
    get_title_style, get_subtitle_style,
    get_section_title_style, get_target_header_style
)

logger = logging.getLogger(__name__)


class BasePDFGenerator:
    """
    Abstract base class for PDF report generation
    
    Provides common functionality for:
    - Document creation with landscape layout
    - Style management
    - Header/subtitle creation
    - Target achievement indicators
    """
    
    def __init__(self, output_folder='reports'):
        """
        Initialize PDF generator
        
        Args:
            output_folder: Folder path to save PDF reports
        """
        self.output_folder = output_folder
        self.elements = []
        
    def _ensure_output_folder(self):
        """Create output folder if it doesn't exist"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            logger.info(f"Created output folder: {self.output_folder}")
    
    def _create_document(self, filepath):
        """
        Create SimpleDocTemplate with standard settings
        
        Args:
            filepath: Full path to output PDF file
            
        Returns:
            SimpleDocTemplate object
        """
        return SimpleDocTemplate(
            filepath,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
    
    def _add_main_title(self, title_text):
        """
        Add main title to report
        
        Args:
            title_text: Title string (e.g., "REPORTE SEMANAL DEL MÉTRICO DE SCRAP")
        """
        title_style = get_title_style()
        title = Paragraph(title_text, title_style)
        self.elements.append(title)
    
    def _add_subtitle(self, subtitle_text):
        """
        Add subtitle to report
        
        Args:
            subtitle_text: Subtitle string with period/year info
        """
        subtitle_style = get_subtitle_style()
        subtitle = Paragraph(subtitle_text, subtitle_style)
        self.elements.append(subtitle)
    
    def _add_target_header(self, within_target, header_text=None):
        """
        Add colored DENTRO/FUERA DE META header
        
        Args:
            within_target: Boolean indicating if metrics meet target
            header_text: Custom text (default: "DENTRO DE META" or "FUERA DE META")
        """
        if header_text is None:
            header_text = "DENTRO DE META" if within_target else "FUERA DE META"
        
        header_style = get_target_header_style(within_target)
        header = Paragraph(header_text, header_style)
        self.elements.append(header)
        self.elements.append(Spacer(0.5, 0.3))
    
    def _add_section_title(self, section_text):
        """
        Add section title (for contributors page, etc.)
        
        Args:
            section_text: Section title string
        """
        section_style = get_section_title_style()
        section_title = Paragraph(section_text, section_style)
        self.elements.append(section_title)
    
    def _add_spacer(self, height_inches=0.3):
        """
        Add vertical spacing
        
        Args:
            height_inches: Height in inches (default 0.3)
        """
        self.elements.append(Spacer(1, height_inches * inch))
    
    def _add_page_break(self):
        """Add page break"""
        self.elements.append(PageBreak())
    
    def _close_matplotlib_figures(self):
        """Close all open matplotlib figures to free memory"""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
            logger.debug("Closed all matplotlib figures")
        except Exception as e:
            logger.warning(f"Error closing matplotlib figures: {e}")
    
    def _calculate_target_achievement(self, df):
        """
        Calculate if period meets target rate (to be implemented by subclasses)
        
        Args:
            df: DataFrame with report data
            
        Returns:
            tuple: (within_target: bool, total_rate: float, target_rate: float)
        """
        raise NotImplementedError("Subclasses must implement _calculate_target_achievement")
    
    def _build_main_table_data(self, df):
        """
        Build data structure for main report table (to be implemented by subclasses)
        
        Args:
            df: DataFrame with report data
            
        Returns:
            list: List of lists with table data (including headers)
        """
        raise NotImplementedError("Subclasses must implement _build_main_table_data")
    
    def _build_contributors_table_data(self, contributors_df):
        """
        Build data structure for contributors table (to be implemented by subclasses)
        
        Args:
            contributors_df: DataFrame with contributors data
            
        Returns:
            list: List of lists with contributors table data (including headers)
        """
        raise NotImplementedError("Subclasses must implement _build_contributors_table_data")
    
    def build_and_save(self, doc):
        """
        Build PDF document from elements
        
        Args:
            doc: SimpleDocTemplate object
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            doc.build(self.elements)
            logger.info(f"PDF successfully built: {doc.filename}")
            return doc.filename
        except Exception as e:
            logger.error(f"Error building PDF: {e}")
            raise
