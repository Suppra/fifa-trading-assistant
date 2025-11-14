"""
Sistema de Alertas de Precio
Notificaciones Windows Toast + Discord webhooks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
import requests

logger = logging.getLogger(__name__)

# Try to import Windows toast notifications
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    logger.warning("win10toast no disponible - instalar con: pip install win10toast")


class PriceAlertManager:
    """Gestiona alertas de precios con notificaciones"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.alerts_file = Path("data/price_alerts.json")
        self.alerts_file.parent.mkdir(exist_ok=True)
        
        # Load existing alerts
        self.alerts = self._load_alerts()
        
        # Toast notifier
        self.toaster = ToastNotifier() if TOAST_AVAILABLE else None
        
        # Discord webhook (from .env)
        self.discord_webhook = self._get_discord_webhook()
    
    def _load_alerts(self) -> Dict:
        """Carga alertas guardadas"""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando alertas: {e}")
        
        return {
            "price_drop_threshold": 10,  # % caída para alertar
            "price_rise_threshold": 15,   # % subida para alertar
            "monitored_players": {},      # player_id -> {name, last_price, threshold}
            "alert_history": []           # Historial de alertas enviadas
        }
    
    def _save_alerts(self):
        """Guarda alertas"""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando alertas: {e}")
    
    def _get_discord_webhook(self) -> Optional[str]:
        """Obtiene webhook de Discord desde .env"""
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('DISCORD_WEBHOOK_URL='):
                            return line.split('=', 1)[1].strip()
            except Exception as e:
                logger.error(f"Error leyendo .env: {e}")
        return None
    
    def add_player_alert(self, player_id: str, player_name: str, 
                        current_price: int, threshold_percent: int = 10):
        """
        Añade un jugador a monitoreo de alertas
        
        Args:
            player_id: ID del jugador
            player_name: Nombre del jugador
            current_price: Precio actual de referencia
            threshold_percent: % de cambio para alertar
        """
        self.alerts["monitored_players"][player_id] = {
            "name": player_name,
            "reference_price": current_price,
            "threshold": threshold_percent,
            "added_at": datetime.now().isoformat()
        }
        self._save_alerts()
        logger.info(f"✓ Alerta añadida: {player_name} ({threshold_percent}%)")
    
    def remove_player_alert(self, player_id: str):
        """Elimina alerta de un jugador"""
        if player_id in self.alerts["monitored_players"]:
            name = self.alerts["monitored_players"][player_id]["name"]
            del self.alerts["monitored_players"][player_id]
            self._save_alerts()
            logger.info(f"✓ Alerta eliminada: {name}")
    
    def check_price_changes(self) -> List[Dict]:
        """
        Revisa cambios de precio y genera alertas
        
        Returns:
            Lista de alertas generadas
        """
        if not self.db:
            return []
        
        alerts_triggered = []
        session = self.db.SessionLocal()
        
        try:
            from app.models.database import Player, PriceHistory
            
            for player_id, alert_data in list(self.alerts["monitored_players"].items()):
                # Get latest price
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.player_id == player_id
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                if not latest_price:
                    continue
                
                ref_price = alert_data["reference_price"]
                current_price = latest_price.price
                change_percent = ((current_price - ref_price) / ref_price) * 100
                
                # Check if threshold exceeded
                threshold = alert_data["threshold"]
                
                if abs(change_percent) >= threshold:
                    alert = {
                        "player_id": player_id,
                        "player_name": alert_data["name"],
                        "reference_price": ref_price,
                        "current_price": current_price,
                        "change_percent": change_percent,
                        "timestamp": datetime.now().isoformat(),
                        "type": "DROP" if change_percent < 0 else "RISE"
                    }
                    
                    alerts_triggered.append(alert)
                    
                    # Send notification
                    self._send_notification(alert)
                    
                    # Update reference price
                    self.alerts["monitored_players"][player_id]["reference_price"] = current_price
                    
                    # Add to history
                    self.alerts["alert_history"].append(alert)
                    
                    # Keep only last 100 alerts
                    if len(self.alerts["alert_history"]) > 100:
                        self.alerts["alert_history"] = self.alerts["alert_history"][-100:]
            
            if alerts_triggered:
                self._save_alerts()
            
        finally:
            session.close()
        
        return alerts_triggered
    
    def _send_notification(self, alert: Dict):
        """Envía notificación (Windows Toast + Discord)"""
        change = alert["change_percent"]
        emoji = "🔻" if change < 0 else "📈"
        
        # Windows Toast
        if self.toaster:
            try:
                title = f"{emoji} Alerta de Precio - {alert['player_name']}"
                message = f"{change:+.1f}%: {alert['reference_price']:,} → {alert['current_price']:,} coins"
                
                self.toaster.show_toast(
                    title,
                    message,
                    duration=10,
                    icon_path=None,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"Error en toast notification: {e}")
        
        # Discord Webhook
        if self.discord_webhook:
            try:
                color = 0xFF4444 if change < 0 else 0x00C805  # Red or Green
                
                embed = {
                    "embeds": [{
                        "title": f"{emoji} Alerta de Precio",
                        "description": f"**{alert['player_name']}**",
                        "color": color,
                        "fields": [
                            {
                                "name": "Cambio",
                                "value": f"{change:+.1f}%",
                                "inline": True
                            },
                            {
                                "name": "Precio Anterior",
                                "value": f"{alert['reference_price']:,} coins",
                                "inline": True
                            },
                            {
                                "name": "Precio Actual",
                                "value": f"{alert['current_price']:,} coins",
                                "inline": True
                            }
                        ],
                        "timestamp": alert["timestamp"],
                        "footer": {
                            "text": "EA FC 26 Trading Bot"
                        }
                    }]
                }
                
                response = requests.post(
                    self.discord_webhook,
                    json=embed,
                    timeout=5
                )
                
                if response.status_code != 204:
                    logger.warning(f"Discord webhook error: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error enviando Discord webhook: {e}")
    
    def get_monitored_players(self) -> List[Dict]:
        """Obtiene lista de jugadores monitoreados"""
        return [
            {
                "player_id": pid,
                "name": data["name"],
                "reference_price": data["reference_price"],
                "threshold": data["threshold"],
                "added_at": data["added_at"]
            }
            for pid, data in self.alerts["monitored_players"].items()
        ]
    
    def get_alert_history(self, limit: int = 20) -> List[Dict]:
        """Obtiene historial de alertas"""
        return self.alerts["alert_history"][-limit:]
    
    def set_global_threshold(self, drop_percent: int = 10, rise_percent: int = 15):
        """Configura umbrales globales de alerta"""
        self.alerts["price_drop_threshold"] = drop_percent
        self.alerts["price_rise_threshold"] = rise_percent
        self._save_alerts()
