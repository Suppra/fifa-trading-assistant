"""
Servicio de feed de precios en tiempo real
Polling cada 30 segundos para actualización automática
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from collections import deque

logger = logging.getLogger(__name__)


class RealTimePriceFeed:
    """
    Feed de precios en tiempo real con polling cada 30 segundos
    Actualización automática sin reiniciar app
    """
    
    def __init__(self, db_manager, futbin_service):
        self.db_manager = db_manager
        self.futbin_service = futbin_service
        
        self.is_running = False
        self.polling_thread = None
        self.polling_interval = 30  # segundos
        
        # Watchlist de jugadores a monitorear
        self.watchlist = set()
        
        # Callbacks para notificar cambios
        self.price_change_callbacks = []
        
        # Historial reciente de cambios (últimos 100)
        self.recent_changes = deque(maxlen=100)
        
        # Estadísticas
        self.stats = {
            'polls': 0,
            'updates': 0,
            'errors': 0,
            'started_at': None
        }
    
    def add_to_watchlist(self, player_id: str):
        """
        Añade jugador a la watchlist
        
        Args:
            player_id: ID del jugador a monitorear
        """
        self.watchlist.add(player_id)
        logger.info(f"➕ Añadido {player_id} a watchlist ({len(self.watchlist)} jugadores)")
    
    def remove_from_watchlist(self, player_id: str):
        """
        Elimina jugador de la watchlist
        
        Args:
            player_id: ID del jugador
        """
        self.watchlist.discard(player_id)
        logger.info(f"➖ Eliminado {player_id} de watchlist ({len(self.watchlist)} jugadores)")
    
    def clear_watchlist(self):
        """Limpia toda la watchlist"""
        count = len(self.watchlist)
        self.watchlist.clear()
        logger.info(f"🗑️ Watchlist limpiada ({count} jugadores)")
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Registra callback para cambios de precio
        
        Args:
            callback: Función que recibe dict con cambio de precio
        """
        self.price_change_callbacks.append(callback)
        logger.info(f"📞 Callback registrado ({len(self.price_change_callbacks)} total)")
    
    def start_polling(self):
        """Inicia polling en background"""
        if self.is_running:
            logger.warning("⚠️ Polling ya está en ejecución")
            return
        
        if not self.watchlist:
            logger.warning("⚠️ Watchlist vacía, no hay jugadores para monitorear")
            return
        
        self.is_running = True
        self.stats['started_at'] = datetime.now().isoformat()
        
        def poll_loop():
            logger.info(f"🚀 Iniciando polling cada {self.polling_interval}s para {len(self.watchlist)} jugadores")
            
            while self.is_running:
                try:
                    self.stats['polls'] += 1
                    iteration = self.stats['polls']
                    
                    logger.info(f"📊 Poll #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Obtener precios de todos los jugadores en watchlist
                    for player_id in list(self.watchlist):
                        try:
                            change = self._check_price_change(player_id)
                            
                            if change:
                                self.stats['updates'] += 1
                                self.recent_changes.append(change)
                                
                                # Notificar a callbacks
                                for callback in self.price_change_callbacks:
                                    try:
                                        callback(change)
                                    except Exception as e:
                                        logger.error(f"Error en callback: {e}")
                            
                            # Rate limiting entre jugadores
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Error polling {player_id}: {e}")
                            self.stats['errors'] += 1
                    
                    logger.info(f"✅ Poll completado - {self.stats['updates']} cambios detectados")
                    
                    # Esperar intervalo antes del siguiente poll
                    for _ in range(self.polling_interval):
                        if not self.is_running:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error en poll loop: {e}")
                    self.stats['errors'] += 1
                    time.sleep(self.polling_interval)
            
            logger.info("🛑 Polling detenido")
        
        self.polling_thread = threading.Thread(target=poll_loop, daemon=True)
        self.polling_thread.start()
    
    def stop_polling(self):
        """Detiene polling"""
        if self.is_running:
            logger.info("🛑 Deteniendo polling...")
            self.is_running = False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del feed
        
        Returns:
            Dict con stats de polling
        """
        uptime = None
        if self.stats['started_at']:
            started = datetime.fromisoformat(self.stats['started_at'])
            uptime_delta = datetime.now() - started
            uptime = str(uptime_delta).split('.')[0]  # Sin microsegundos
        
        return {
            'is_running': self.is_running,
            'watchlist_size': len(self.watchlist),
            'polls': self.stats['polls'],
            'updates': self.stats['updates'],
            'errors': self.stats['errors'],
            'uptime': uptime,
            'polling_interval': self.polling_interval,
            'callbacks_registered': len(self.price_change_callbacks)
        }
    
    def get_recent_changes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Obtiene cambios recientes de precio
        
        Args:
            limit: Número máximo de cambios a retornar
            
        Returns:
            Lista de cambios recientes
        """
        # Convertir deque a lista y retornar últimos N
        changes = list(self.recent_changes)
        return changes[-limit:] if len(changes) > limit else changes
    
    def set_polling_interval(self, seconds: int):
        """
        Cambia intervalo de polling
        
        Args:
            seconds: Nuevos segundos entre polls
        """
        if seconds < 10:
            logger.warning("⚠️ Intervalo mínimo: 10 segundos")
            seconds = 10
        
        self.polling_interval = seconds
        logger.info(f"⏱️ Intervalo de polling cambiado a {seconds}s")
    
    def _check_price_change(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Verifica cambio de precio de un jugador
        
        Args:
            player_id: ID del jugador
            
        Returns:
            Dict con cambio si existe, None si no hay cambio
        """
        try:
            # Obtener precio actual de la BD
            session = self.db_manager.get_session()
            
            last_price_record = session.query(self.db_manager.PriceHistory).filter_by(
                player_id=player_id
            ).order_by(self.db_manager.PriceHistory.timestamp.desc()).first()
            
            old_price = last_price_record.price if last_price_record else 0
            
            # Obtener precio nuevo de FUTBIN
            player_data = self.futbin_service.get_player_by_id(player_id)
            
            if not player_data or 'price' not in player_data:
                return None
            
            new_price = player_data['price']
            
            # Detectar cambio significativo (>1%)
            if old_price > 0:
                change = new_price - old_price
                change_pct = (change / old_price) * 100
                
                if abs(change_pct) >= 1:  # Solo cambios >= 1%
                    # Guardar nuevo precio
                    self.db_manager.add_price_history(
                        player_id=player_id,
                        price=new_price
                    )
                    
                    # Determinar dirección
                    if change > 0:
                        direction = '📈 SUBIÓ'
                        color = 'green'
                    else:
                        direction = '📉 BAJÓ'
                        color = 'red'
                    
                    logger.info(f"{direction} {player_data.get('name', player_id)}: {old_price:,} → {new_price:,} ({change_pct:+.2f}%)")
                    
                    return {
                        'player_id': player_id,
                        'player_name': player_data.get('name', 'Unknown'),
                        'old_price': old_price,
                        'new_price': new_price,
                        'change': change,
                        'change_pct': round(change_pct, 2),
                        'direction': direction,
                        'color': color,
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                # Primer precio (no hay anterior)
                self.db_manager.add_price_history(
                    player_id=player_id,
                    price=new_price
                )
                
                logger.info(f"📌 Primer precio para {player_data.get('name', player_id)}: {new_price:,}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error verificando cambio de precio: {e}")
            return None
        finally:
            if 'session' in locals():
                session.close()
    
    def get_live_price(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene precio en vivo de FUTBIN (sin cache)
        
        Args:
            player_id: ID del jugador
            
        Returns:
            Dict con precio actual
        """
        try:
            player_data = self.futbin_service.get_player_by_id(player_id)
            
            if not player_data or 'price' not in player_data:
                return None
            
            return {
                'player_id': player_id,
                'player_name': player_data.get('name', 'Unknown'),
                'price': player_data['price'],
                'rating': player_data.get('rating', 0),
                'position': player_data.get('position', ''),
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo precio en vivo: {e}")
            return None
    
    def auto_populate_watchlist_from_inventory(self):
        """
        Llena watchlist automáticamente desde inventario
        Monitorea todas las cartas owned/listed
        """
        try:
            session = self.db_manager.get_session()
            
            inventory = session.query(self.db_manager.Inventory).filter(
                self.db_manager.Inventory.status.in_(['owned', 'listed'])
            ).all()
            
            for item in inventory:
                self.watchlist.add(item.player_id)
            
            logger.info(f"✅ Watchlist poblada desde inventario: {len(self.watchlist)} jugadores")
            
        except Exception as e:
            logger.error(f"Error poblando watchlist: {e}")
        finally:
            session.close()
