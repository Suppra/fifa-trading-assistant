"""
Sistema de actualización automática de precios FUTBIN en tiempo real
Se ejecuta en segundo plano y actualiza precios cada hora
"""

import time
import logging
from datetime import datetime, timedelta
from threading import Thread
from app.database.db_manager import DatabaseManager
from app.data_collection.futbin_scraper import FUTBINScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimePriceUpdater:
    """Actualiza precios de FUTBIN automáticamente"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = FUTBINScraper()
        self.is_running = False
        self.update_interval = 3600  # 1 hora en segundos
        
    def start(self):
        """Inicia el actualizador en segundo plano"""
        if self.is_running:
            logger.warning("Updater ya está ejecutándose")
            return
        
        self.is_running = True
        thread = Thread(target=self._update_loop, daemon=True)
        thread.start()
        logger.info("✅ Realtime Price Updater iniciado")
        
    def stop(self):
        """Detiene el actualizador"""
        self.is_running = False
        logger.info("⏹️ Realtime Price Updater detenido")
        
    def _update_loop(self):
        """Loop principal de actualización"""
        while self.is_running:
            try:
                logger.info("🔄 Iniciando actualización de precios...")
                self._update_fodder_prices()
                logger.info(f"✅ Actualización completa. Próxima en {self.update_interval/60:.0f} minutos")
                
                # Esperar hasta la próxima actualización
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en update loop: {e}")
                time.sleep(60)  # Esperar 1 min antes de reintentar
    
    def _update_fodder_prices(self):
        """Actualiza precios de cartas fodder (82-84)"""
        session = self.db.SessionLocal()
        
        try:
            from app.database.db_manager import Player, PriceHistory
            
            # Obtener jugadores rating 82-84 (fodder)
            fodder_players = session.query(Player).filter(
                Player.rating.in_([82, 83, 84]),
                Player.is_extinct == False
            ).limit(100).all()
            
            logger.info(f"📊 Actualizando {len(fodder_players)} jugadores fodder...")
            
            updated_count = 0
            for player in fodder_players:
                try:
                    # Buscar precio en FUTBIN
                    player_data = self.scraper.search_player(player.name)
                    
                    if player_data and player_data.get('pc_price', 0) > 0:
                        pc_price = player_data['pc_price']
                        
                        # Guardar en historial
                        price_entry = PriceHistory(
                            player_id=player.player_id,
                            price=pc_price,
                            timestamp=datetime.now()
                        )
                        session.add(price_entry)
                        updated_count += 1
                        
                        logger.info(f"✅ {player.name} ({player.rating}): {pc_price:,} coins")
                    
                    # Rate limiting - 1 request cada 2 segundos
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error actualizando {player.name}: {e}")
                    continue
            
            session.commit()
            logger.info(f"💾 {updated_count} precios actualizados en BD")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error en actualización: {e}")
        finally:
            session.close()
    
    def force_update_now(self):
        """Fuerza una actualización inmediata"""
        logger.info("⚡ Forzando actualización inmediata...")
        thread = Thread(target=self._update_fodder_prices, daemon=True)
        thread.start()


if __name__ == '__main__':
    updater = RealtimePriceUpdater()
    updater.start()
    
    # Mantener vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        updater.stop()
        logger.info("👋 Updater cerrado")
