"""
Sistema de Estrategias de Actualización Inteligente

Gestiona cuándo y cómo actualizar la base de datos desde FUTBIN:
- Primera vez: Descarga inicial 50 páginas paralelas
- Uso normal: Actualización incremental solo jugadores existentes
- Background: Descarga progresiva en segundo plano
- Manual: Actualización completa bajo demanda

Created by xSuppra
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path


class UpdateStrategy:
    """Gestiona las estrategias de actualización de datos FUTBIN"""
    
    def __init__(self):
        self.config_dir = Path("data")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "update_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Carga configuración de actualización"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Configuración por defecto
        return {
            "first_run": True,
            "last_full_update": None,
            "last_incremental_update": None,
            "total_players": 0,
            "update_history": []
        }
    
    def _save_config(self):
        """Guarda configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def is_first_run(self) -> bool:
        """Verifica si es la primera ejecución"""
        return self.config.get("first_run", True)
    
    def needs_full_update(self) -> bool:
        """Determina si se necesita actualización completa"""
        last_full = self.config.get("last_full_update")
        
        if not last_full:
            return True
        
        # Actualización completa cada 7 días
        last_date = datetime.fromisoformat(last_full)
        days_since = (datetime.now() - last_date).days
        
        return days_since >= 7
    
    def get_update_mode(self, force_full: bool = False) -> str:
        """
        Determina el modo de actualización
        
        Returns:
            'initial': Primera ejecución (50 páginas paralelas)
            'incremental': Actualización solo jugadores existentes
            'full': Actualización completa (100 páginas)
        """
        if force_full:
            return 'full'
        
        if self.is_first_run():
            return 'initial'
        
        if self.needs_full_update():
            return 'full'
        
        return 'incremental'
    
    def get_initial_pages(self) -> int:
        """Número de páginas para descarga inicial"""
        return 30  # ~900 jugadores, balance velocidad/datos
    
    def get_full_pages(self) -> int:
        """Número de páginas para actualización completa"""
        return 50  # ~1500 jugadores total
    
    def mark_first_run_complete(self, total_players: int):
        """Marca primera ejecución como completada"""
        self.config["first_run"] = False
        self.config["last_full_update"] = datetime.now().isoformat()
        self.config["total_players"] = total_players
        self.config["update_history"].append({
            "type": "initial",
            "date": datetime.now().isoformat(),
            "players": total_players
        })
        self._save_config()
    
    def mark_incremental_update(self, players_updated: int):
        """Marca actualización incremental como completada"""
        self.config["last_incremental_update"] = datetime.now().isoformat()
        self.config["update_history"].append({
            "type": "incremental",
            "date": datetime.now().isoformat(),
            "players": players_updated
        })
        # Mantener solo últimos 30 registros
        if len(self.config["update_history"]) > 30:
            self.config["update_history"] = self.config["update_history"][-30:]
        self._save_config()
    
    def mark_full_update(self, total_players: int):
        """Marca actualización completa como completada"""
        self.config["last_full_update"] = datetime.now().isoformat()
        self.config["total_players"] = total_players
        self.config["update_history"].append({
            "type": "full",
            "date": datetime.now().isoformat(),
            "players": total_players
        })
        if len(self.config["update_history"]) > 30:
            self.config["update_history"] = self.config["update_history"][-30:]
        self._save_config()
    
    def get_last_update_info(self) -> dict:
        """Obtiene información de última actualización"""
        return {
            "is_first_run": self.is_first_run(),
            "last_full_update": self.config.get("last_full_update"),
            "last_incremental_update": self.config.get("last_incremental_update"),
            "total_players": self.config.get("total_players", 0),
            "needs_full_update": self.needs_full_update()
        }
    
    def reset(self):
        """Resetea configuración (útil para pruebas)"""
        self.config = {
            "first_run": True,
            "last_full_update": None,
            "last_incremental_update": None,
            "total_players": 0,
            "update_history": []
        }
        self._save_config()


if __name__ == "__main__":
    # Test
    strategy = UpdateStrategy()
    print("Estado actual:", strategy.get_last_update_info())
    print("Modo sugerido:", strategy.get_update_mode())
