"""
report_history.py - Sistema de gestión de historial de reportes generados
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ReportEntry:
    """Representa una entrada en el historial de reportes"""
    
    def __init__(self, filepath: str, report_type: str, period: str, 
                 generated_date: str, file_size: int):
        self.filepath = filepath
        self.report_type = report_type
        self.period = period
        self.generated_date = generated_date
        self.file_size = file_size
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para JSON"""
        return {
            'filepath': self.filepath,
            'report_type': self.report_type,
            'period': self.period,
            'generated_date': self.generated_date,
            'file_size': self.file_size
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ReportEntry':
        """Crea instancia desde diccionario"""
        return ReportEntry(
            filepath=data['filepath'],
            report_type=data['report_type'],
            period=data['period'],
            generated_date=data['generated_date'],
            file_size=data['file_size']
        )
    
    def exists(self) -> bool:
        """Verifica si el archivo aún existe"""
        return os.path.exists(self.filepath)
    
    def get_age_days(self) -> int:
        """Retorna la antigüedad del reporte en días"""
        try:
            gen_date = datetime.fromisoformat(self.generated_date)
            return (datetime.now() - gen_date).days
        except:
            return 0
    
    def get_size_mb(self) -> float:
        """Retorna el tamaño en MB"""
        return self.file_size / (1024 * 1024)


class ReportHistoryManager:
    """Gestor del historial de reportes generados"""
    
    def __init__(self, history_file: str = 'data/report_history.json'):
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Asegura que el archivo de historial exista"""
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            self._save_history([])
            logger.info(f"Created report history file: {self.history_file}")
    
    def _load_history(self) -> List[ReportEntry]:
        """Carga el historial desde el archivo JSON"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ReportEntry.from_dict(entry) for entry in data]
        except Exception as e:
            logger.error(f"Error loading report history: {e}")
            return []
    
    def _save_history(self, entries: List[ReportEntry]):
        """Guarda el historial al archivo JSON"""
        try:
            data = [entry.to_dict() for entry in entries]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(entries)} entries to report history")
        except Exception as e:
            logger.error(f"Error saving report history: {e}")
    
    def add_report(self, filepath: str, report_type: str, period: str):
        """
        Agrega un reporte al historial
        
        Args:
            filepath: Ruta completa del archivo PDF generado
            report_type: Tipo de reporte (Semanal, Mensual, Trimestral, Anual, Personalizado)
            period: Descripción del periodo (ej: "Semana 21/2025", "Abril 2025")
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Cannot add to history, file not found: {filepath}")
                return
            
            file_size = os.path.getsize(filepath)
            generated_date = datetime.now().isoformat()
            
            entry = ReportEntry(
                filepath=filepath,
                report_type=report_type,
                period=period,
                generated_date=generated_date,
                file_size=file_size
            )
            
            # Cargar historial existente
            history = self._load_history()
            
            # Verificar si ya existe (evitar duplicados)
            exists = any(e.filepath == filepath for e in history)
            if exists:
                # Actualizar entrada existente
                history = [e for e in history if e.filepath != filepath]
                logger.debug(f"Updated existing entry: {filepath}")
            
            # Agregar nueva entrada al inicio
            history.insert(0, entry)
            
            # Guardar
            self._save_history(history)
            logger.info(f"Added to history: {report_type} - {period}")
            
        except Exception as e:
            logger.error(f"Error adding report to history: {e}")
    
    def get_all_reports(self, filter_type: Optional[str] = None) -> List[ReportEntry]:
        """
        Obtiene todos los reportes del historial
        
        Args:
            filter_type: Filtrar por tipo de reporte (opcional)
            
        Returns:
            Lista de reportes, ordenados por fecha (más reciente primero)
        """
        history = self._load_history()
        
        if filter_type:
            history = [e for e in history if e.report_type == filter_type]
        
        return history
    
    def delete_report(self, filepath: str):
        """
        Elimina un reporte del historial (solo del registro, no el archivo)
        
        Args:
            filepath: Ruta del reporte a eliminar del historial
        """
        try:
            history = self._load_history()
            history = [e for e in history if e.filepath != filepath]
            self._save_history(history)
            logger.info(f"Removed from history: {filepath}")
        except Exception as e:
            logger.error(f"Error removing report from history: {e}")
    
    def cleanup_missing(self) -> int:
        """
        Limpia entradas del historial cuyos archivos ya no existen
        
        Returns:
            Número de entradas eliminadas
        """
        try:
            history = self._load_history()
            original_count = len(history)
            
            # Filtrar solo los que existen
            history = [e for e in history if e.exists()]
            
            removed_count = original_count - len(history)
            
            if removed_count > 0:
                self._save_history(history)
                logger.info(f"Cleaned up {removed_count} missing reports from history")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up history: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del historial
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            history = self._load_history()
            
            total = len(history)
            existing = sum(1 for e in history if e.exists())
            missing = total - existing
            
            total_size = sum(e.file_size for e in history if e.exists())
            
            by_type = {}
            for entry in history:
                by_type[entry.report_type] = by_type.get(entry.report_type, 0) + 1
            
            return {
                'total': total,
                'existing': existing,
                'missing': missing,
                'total_size_mb': total_size / (1024 * 1024),
                'by_type': by_type
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total': 0, 'existing': 0, 'missing': 0, 'total_size_mb': 0, 'by_type': {}}


# Singleton global
_report_history_manager = None

def get_report_history_manager() -> ReportHistoryManager:
    """Obtiene la instancia global del gestor de historial"""
    global _report_history_manager
    if _report_history_manager is None:
        _report_history_manager = ReportHistoryManager()
    return _report_history_manager
