"""
backup_manager.py - Sistema de backup automático para archivos de datos

Gestiona backups automáticos del archivo Excel con:
- Creación automática antes de cada carga
- Rotación (mantiene últimos N backups)
- Restauración desde backup
- Listado de backups disponibles
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Información de un archivo de backup"""
    filename: str
    filepath: str
    timestamp: datetime
    size_bytes: int
    
    @property
    def size_mb(self) -> float:
        """Retorna el tamaño en MB"""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def age_str(self) -> str:
        """Retorna la antigüedad en formato legible"""
        delta = datetime.now() - self.timestamp
        
        if delta.days > 0:
            return f"hace {delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace unos segundos"


class BackupManager:
    """Gestor de backups automáticos para archivos de datos"""
    
    def __init__(self, backup_folder: str = "backups", max_backups: int = 10):
        """
        Inicializa el gestor de backups.
        
        Args:
            backup_folder: Carpeta donde guardar los backups
            max_backups: Número máximo de backups a mantener
        """
        self.backup_folder = Path(backup_folder)
        self.max_backups = max_backups
        
        # Crear carpeta de backups si no existe
        if not self.backup_folder.exists():
            self.backup_folder.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Carpeta de backups creada: {self.backup_folder}")
    
    def create_backup(self, source_file: str, force: bool = False) -> Optional[str]:
        """
        Crea un backup del archivo fuente.
        
        Args:
            source_file: Ruta del archivo a respaldar
            force: Si True, crea backup aunque el archivo no haya cambiado
            
        Returns:
            str: Ruta del backup creado, o None si no se creó
        """
        source_path = Path(source_file)
        
        # Validar que el archivo existe
        if not source_path.exists():
            logger.error(f"❌ Archivo fuente no existe: {source_file}")
            return None
        
        try:
            # Verificar si ya existe un backup reciente (últimos 5 minutos)
            if not force:
                recent_backup = self._get_most_recent_backup(source_path.name)
                if recent_backup:
                    time_diff = datetime.now() - recent_backup.timestamp
                    if time_diff.total_seconds() < 300:  # 5 minutos
                        logger.info(f"ℹ️ Backup reciente ya existe ({recent_backup.age_str}), omitiendo...")
                        return recent_backup.filepath
            
            # Generar nombre de backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{timestamp}_{source_path.name}"
            backup_path = self.backup_folder / backup_name
            
            # Copiar archivo
            logger.info(f"Creando backup: {source_path.name} → {backup_name}")
            shutil.copy2(source_file, backup_path)
            
            file_size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"✓ Backup creado exitosamente ({file_size_mb:.2f} MB): {backup_path}")
            
            # Limpiar backups antiguos
            self._cleanup_old_backups(source_path.name)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}", exc_info=True)
            return None
    
    def _get_most_recent_backup(self, filename: str) -> Optional[BackupInfo]:
        """Obtiene el backup más reciente de un archivo"""
        backups = self.list_backups(filename)
        return backups[0] if backups else None
    
    def list_backups(self, filename: Optional[str] = None) -> List[BackupInfo]:
        """
        Lista todos los backups disponibles.
        
        Args:
            filename: Si se especifica, filtra por nombre de archivo original
            
        Returns:
            List[BackupInfo]: Lista de backups, ordenados por fecha (más reciente primero)
        """
        backups = []
        
        try:
            for backup_file in self.backup_folder.glob("*"):
                if not backup_file.is_file():
                    continue
                
                # Si se especificó filename, filtrar
                if filename and not backup_file.name.endswith(filename):
                    continue
                
                # Extraer timestamp del nombre
                try:
                    timestamp_str = backup_file.name.split("_")[0] + backup_file.name.split("_")[1]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                except:
                    # Si no se puede parsear, usar fecha de modificación
                    timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                backup_info = BackupInfo(
                    filename=backup_file.name,
                    filepath=str(backup_file),
                    timestamp=timestamp,
                    size_bytes=backup_file.stat().st_size
                )
                backups.append(backup_info)
            
            # Ordenar por timestamp (más reciente primero)
            backups.sort(key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error listando backups: {e}")
        
        return backups
    
    def restore_backup(self, backup_path: str, destination: str) -> bool:
        """
        Restaura un backup a la ubicación de destino.
        
        Args:
            backup_path: Ruta del backup a restaurar
            destination: Ruta de destino para la restauración
            
        Returns:
            bool: True si se restauró exitosamente
        """
        backup_file = Path(backup_path)
        dest_file = Path(destination)
        
        if not backup_file.exists():
            logger.error(f"❌ Backup no existe: {backup_path}")
            return False
        
        try:
            # Crear backup del archivo actual antes de restaurar
            if dest_file.exists():
                logger.info("Creando backup de seguridad del archivo actual...")
                safety_backup = f"{destination}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(destination, safety_backup)
                logger.info(f"✓ Backup de seguridad creado: {safety_backup}")
            
            # Restaurar backup
            logger.info(f"Restaurando backup: {backup_file.name} → {dest_file.name}")
            shutil.copy2(backup_path, destination)
            
            logger.info(f"✓ Backup restaurado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error restaurando backup: {e}", exc_info=True)
            return False
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        Elimina un backup específico.
        
        Args:
            backup_path: Ruta del backup a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            logger.warning(f"Backup no existe: {backup_path}")
            return False
        
        try:
            backup_file.unlink()
            logger.info(f"✓ Backup eliminado: {backup_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando backup: {e}")
            return False
    
    def _cleanup_old_backups(self, filename: str):
        """
        Elimina backups antiguos manteniendo solo los últimos N.
        
        Args:
            filename: Nombre del archivo original para filtrar backups
        """
        backups = self.list_backups(filename)
        
        if len(backups) <= self.max_backups:
            return
        
        # Eliminar backups más allá del límite
        backups_to_delete = backups[self.max_backups:]
        
        logger.info(f"Limpiando {len(backups_to_delete)} backup(s) antiguo(s)...")
        
        for backup in backups_to_delete:
            try:
                Path(backup.filepath).unlink()
                logger.debug(f"✓ Eliminado: {backup.filename}")
            except Exception as e:
                logger.error(f"Error eliminando {backup.filename}: {e}")
    
    def get_backup_statistics(self) -> dict:
        """
        Obtiene estadísticas de los backups.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                "total_backups": 0,
                "total_size_mb": 0,
                "oldest_backup": None,
                "newest_backup": None
            }
        
        total_size = sum(b.size_bytes for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_backup": backups[-1].timestamp,
            "newest_backup": backups[0].timestamp,
            "backups_by_file": self._count_by_file(backups)
        }
    
    def _count_by_file(self, backups: List[BackupInfo]) -> dict:
        """Cuenta backups agrupados por archivo original"""
        counts = {}
        for backup in backups:
            # Extraer nombre original del archivo
            original_name = "_".join(backup.filename.split("_")[2:])
            counts[original_name] = counts.get(original_name, 0) + 1
        return counts


# Instancia global del gestor de backups
_backup_manager = None


def get_backup_manager() -> BackupManager:
    """
    Obtiene la instancia global del gestor de backups.
    
    Returns:
        BackupManager: Instancia del gestor
    """
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
