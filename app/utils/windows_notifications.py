"""
Windows Toast Notifications for Trading Bot
Provides push notifications for price alerts, ROI milestones, and predictions
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WindowsNotifier:
    """Manage Windows toast notifications for trading events"""
    
    def __init__(self):
        """Initialize Windows notifier with win10toast if available"""
        self.toaster = None
        self.enabled = False
        
        try:
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
            self.enabled = True
            logger.info("✅ Windows notifier initialized")
        except ImportError:
            logger.warning("⚠️ win10toast not installed. Notifications disabled.")
            logger.info("Install with: pip install win10toast")
        except Exception as e:
            logger.error(f"Error initializing Windows notifier: {e}")
    
    def show_notification(
        self, 
        title: str, 
        message: str, 
        duration: int = 5,
        icon_path: Optional[str] = None,
        threaded: bool = True
    ) -> bool:
        """
        Show a Windows toast notification
        
        Args:
            title: Notification title
            message: Notification message
            duration: How long to show (seconds)
            icon_path: Path to .ico file (optional)
            threaded: Run in background thread (default True)
            
        Returns:
            True if notification shown, False otherwise
        """
        if not self.enabled or not self.toaster:
            logger.debug(f"Notification skipped (disabled): {title}")
            return False
        
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon_path,
                threaded=threaded
            )
            logger.info(f"📢 Notification shown: {title}")
            return True
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            return False
    
    # --- Trading Event Notifications ---
    
    def notify_price_drop(self, player_name: str, old_price: int, new_price: int, drop_pct: float):
        """Notify when a watched card drops in price significantly"""
        title = f"💰 Precio Bajó - {player_name}"
        message = (
            f"Precio cayó {drop_pct:.1f}%\n"
            f"{old_price:,} → {new_price:,} coins\n"
            f"¡Oportunidad de compra!"
        )
        self.show_notification(title, message, duration=8)
    
    def notify_price_spike(self, player_name: str, old_price: int, new_price: int, spike_pct: float):
        """Notify when a owned card spikes in price"""
        title = f"📈 Precio Subió - {player_name}"
        message = (
            f"Precio subió {spike_pct:.1f}%\n"
            f"{old_price:,} → {new_price:,} coins\n"
            f"¡Considera vender!"
        )
        self.show_notification(title, message, duration=8)
    
    def notify_roi_milestone(self, portfolio_roi: float, total_profit: int):
        """Notify when portfolio reaches ROI milestone"""
        if portfolio_roi >= 10:
            emoji = "🎉"
            milestone = "excelente"
        elif portfolio_roi >= 5:
            emoji = "✨"
            milestone = "muy bueno"
        else:
            emoji = "💪"
            milestone = "sólido"
        
        title = f"{emoji} ROI Milestone Alcanzado"
        message = (
            f"Portfolio ROI: {portfolio_roi:+.1f}%\n"
            f"Ganancia total: {total_profit:,} coins\n"
            f"¡Rendimiento {milestone}!"
        )
        self.show_notification(title, message, duration=10)
    
    def notify_lstm_prediction(self, player_name: str, current_price: int, predicted_price: int, days: int):
        """Notify about LSTM price prediction"""
        change_pct = ((predicted_price - current_price) / current_price) * 100
        
        if change_pct > 5:
            emoji = "🚀"
            action = "¡Compra recomendada!"
        elif change_pct < -5:
            emoji = "📉"
            action = "¡Vende si tienes!"
        else:
            emoji = "📊"
            action = "Precio estable"
        
        title = f"{emoji} Predicción {days}d - {player_name}"
        message = (
            f"Precio actual: {current_price:,}\n"
            f"Predicción: {predicted_price:,} ({change_pct:+.1f}%)\n"
            f"{action}"
        )
        self.show_notification(title, message, duration=8)
    
    def notify_peak_hours(self, action: str, time_window: str, savings_or_profit: float):
        """Notify about optimal trading hours"""
        if action == "COMPRAR":
            emoji = "🛒"
            metric = f"Ahorro promedio: {savings_or_profit:.1f}%"
        elif action == "VENDER":
            emoji = "💰"
            metric = f"Ganancia promedio: {savings_or_profit:.1f}%"
        else:
            emoji = "⏸️"
            metric = "Espera mejor momento"
        
        title = f"{emoji} Hora Óptima - {action}"
        message = (
            f"Ventana: {time_window}\n"
            f"{metric}\n"
            f"¡Aprovecha el momento!"
        )
        self.show_notification(title, message, duration=7)
    
    def notify_sbc_requirement(self, sbc_name: str, required_rating: int, required_cards: int):
        """Notify about SBC requirements detected"""
        title = f"📋 Nuevo SBC Detectado"
        message = (
            f"{sbc_name}\n"
            f"Rating: {required_rating}+\n"
            f"Cartas: {required_cards}\n"
            f"¡Precios pueden subir!"
        )
        self.show_notification(title, message, duration=10)
    
    def notify_inventory_full(self, total_items: int, total_value: int):
        """Notify when inventory reaches capacity"""
        title = "📦 Inventario Casi Lleno"
        message = (
            f"Tienes {total_items} cartas\n"
            f"Valor total: {total_value:,} coins\n"
            f"Considera vender algunas"
        )
        self.show_notification(title, message, duration=8)
    
    def notify_profit_target(self, player_name: str, buy_price: int, sell_price: int, profit: int):
        """Notify when a card reaches target profit"""
        title = f"🎯 Target Alcanzado - {player_name}"
        message = (
            f"Compra: {buy_price:,}\n"
            f"Venta: {sell_price:,}\n"
            f"Ganancia: +{profit:,} coins"
        )
        self.show_notification(title, message, duration=8)
    
    def notify_market_trend(self, trend_type: str, avg_change_pct: float):
        """Notify about overall market trend changes"""
        if trend_type == "ALCISTA":
            emoji = "📈"
            action = "Buenos precios de venta"
        elif trend_type == "BAJISTA":
            emoji = "📉"
            action = "Buenos precios de compra"
        else:
            emoji = "➡️"
            action = "Mercado estable"
        
        title = f"{emoji} Tendencia del Mercado"
        message = (
            f"Tendencia: {trend_type}\n"
            f"Cambio promedio: {avg_change_pct:+.1f}%\n"
            f"{action}"
        )
        self.show_notification(title, message, duration=7)
    
    # --- Utility Methods ---
    
    def test_notification(self):
        """Show a test notification"""
        title = "🤖 EA FC 26 Trading Bot"
        message = (
            f"Notificaciones funcionando correctamente\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )
        return self.show_notification(title, message, duration=5)
    
    def is_enabled(self) -> bool:
        """Check if notifications are enabled"""
        return self.enabled


# Global singleton instance
_notifier_instance = None

def get_notifier() -> WindowsNotifier:
    """Get global notifier instance (singleton)"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = WindowsNotifier()
    return _notifier_instance
