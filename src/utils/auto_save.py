"""
Auto-Save Manager
Guarda transacciones y configuración automáticamente cada X minutos
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoSaveManager:
    """Gestiona auto-guardado de datos"""
    
    def __init__(self, save_interval: int = 300):  # 5 minutos por defecto
        """
        Args:
            save_interval: Intervalo de guardado en segundos (default: 300 = 5 min)
        """
        self.save_interval = save_interval
        self.running = False
        self.thread = None
        self.callbacks = []  # Lista de funciones a ejecutar en cada save
        self.last_save_time = None
        
    def register_callback(self, callback):
        """
        Registra una función para ejecutar en cada auto-save
        
        Args:
            callback: Función sin parámetros que se ejecutará
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            logger.info(f"✓ Callback registrado para auto-save: {callback.__name__}")
    
    def unregister_callback(self, callback):
        """Elimina un callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start(self):
        """Inicia el auto-save en background thread"""
        if self.running:
            logger.warning("Auto-save ya está corriendo")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._save_loop, daemon=True)
        self.thread.start()
        logger.info(f"✅ Auto-save iniciado (cada {self.save_interval // 60} minutos)")
    
    def stop(self):
        """Detiene el auto-save"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("⏹️ Auto-save detenido")
    
    def force_save(self):
        """Fuerza un guardado inmediato"""
        self._execute_saves()
        logger.info("💾 Guardado forzado completado")
    
    def _save_loop(self):
        """Loop principal de auto-save"""
        while self.running:
            try:
                time.sleep(self.save_interval)
                
                if self.running:  # Check again after sleep
                    self._execute_saves()
                    
            except Exception as e:
                logger.error(f"Error en auto-save loop: {e}")
    
    def _execute_saves(self):
        """Ejecuta todos los callbacks de guardado"""
        self.last_save_time = datetime.now()
        
        for callback in self.callbacks:
            try:
                callback()
                logger.debug(f"✓ Ejecutado: {callback.__name__}")
            except Exception as e:
                logger.error(f"Error en callback {callback.__name__}: {e}")
        
        logger.info(f"💾 Auto-save completado: {len(self.callbacks)} operaciones")
    
    def get_status(self) -> dict:
        """Obtiene estado del auto-save"""
        return {
            "running": self.running,
            "interval_minutes": self.save_interval // 60,
            "callbacks_count": len(self.callbacks),
            "last_save": self.last_save_time.isoformat() if self.last_save_time else None
        }
