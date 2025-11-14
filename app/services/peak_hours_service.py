"""
Servicio de análisis de horas pico
Scraping horario para identificar patrones de precio por hora
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class PeakHoursService:
    """
    Análisis de horas pico en precios
    Scraping cada hora durante 24h para identificar patrones
    """
    
    def __init__(self, db_manager, futbin_service):
        self.db_manager = db_manager
        self.futbin_service = futbin_service
        self.is_running = False
        self.monitoring_thread = None
    
    def start_hourly_monitoring(self, player_ids: List[str], duration_hours: int = 24):
        """
        Inicia monitoreo horario de precios
        
        Args:
            player_ids: Lista de IDs de jugadores a monitorear
            duration_hours: Duración del monitoreo en horas
        """
        if self.is_running:
            logger.warning("Monitoreo ya está en ejecución")
            return
        
        self.is_running = True
        
        def monitor():
            logger.info(f"🕐 Iniciando monitoreo de {len(player_ids)} jugadores por {duration_hours} horas")
            
            end_time = datetime.now() + timedelta(hours=duration_hours)
            iteration = 0
            
            while datetime.now() < end_time and self.is_running:
                iteration += 1
                current_hour = datetime.now().hour
                
                logger.info(f"📊 Iteración {iteration} - Hora {current_hour}:00")
                
                for player_id in player_ids:
                    try:
                        # Obtener precio actual
                        player_data = self.futbin_service.get_player_by_id(player_id)
                        
                        if player_data and 'price' in player_data:
                            # Guardar en BD con hora
                            self._save_price_with_hour(
                                player_id=player_id,
                                price=player_data['price'],
                                hour=current_hour
                            )
                            
                            logger.info(f"✅ {player_data.get('name', player_id)}: {player_data['price']:,} coins")
                        
                        time.sleep(2)  # Rate limiting entre jugadores
                        
                    except Exception as e:
                        logger.error(f"Error monitoreando {player_id}: {e}")
                
                # Esperar 1 hora (3600 segundos) o hasta que se detenga
                for _ in range(360):  # 360 * 10 segundos = 1 hora
                    if not self.is_running:
                        break
                    time.sleep(10)
            
            self.is_running = False
            logger.info("✅ Monitoreo horario completado")
        
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
    
    def stop_hourly_monitoring(self):
        """Detiene el monitoreo horario"""
        if self.is_running:
            logger.info("🛑 Deteniendo monitoreo horario...")
            self.is_running = False
    
    def analyze_peak_hours(self, player_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Analiza horas pico de un jugador
        
        Args:
            player_id: ID del jugador
            days: Días de historial a analizar
            
        Returns:
            Dict con análisis por hora
        """
        try:
            session = self.db_manager.get_session()
            
            # Fecha de inicio
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener precios con hora
            price_records = session.query(self.db_manager.PriceHistory).filter(
                self.db_manager.PriceHistory.player_id == player_id,
                self.db_manager.PriceHistory.timestamp >= start_date,
                self.db_manager.PriceHistory.hour_of_day.isnot(None)
            ).all()
            
            if not price_records:
                return {
                    'error': 'No hay datos suficientes con horas',
                    'player_id': player_id
                }
            
            # Agrupar por hora (0-23)
            hour_prices = defaultdict(list)
            
            for record in price_records:
                hour = record.hour_of_day
                price = record.price
                hour_prices[hour].append(price)
            
            # Calcular estadísticas por hora
            hourly_analysis = {}
            
            for hour in range(24):
                prices = hour_prices.get(hour, [])
                
                if prices:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    
                    hourly_analysis[hour] = {
                        'hour': f"{hour:02d}:00",
                        'avg_price': int(avg_price),
                        'min_price': min_price,
                        'max_price': max_price,
                        'samples': len(prices),
                        'volatility': max_price - min_price
                    }
            
            if not hourly_analysis:
                return {
                    'error': 'No hay datos procesables',
                    'player_id': player_id
                }
            
            # Identificar mejor hora para comprar/vender
            best_buy_hour = min(hourly_analysis.items(), key=lambda x: x[1]['avg_price'])
            best_sell_hour = max(hourly_analysis.items(), key=lambda x: x[1]['avg_price'])
            
            # Calcular ganancia potencial
            potential_profit = best_sell_hour[1]['avg_price'] - best_buy_hour[1]['avg_price']
            profit_pct = (potential_profit / best_buy_hour[1]['avg_price']) * 100 if best_buy_hour[1]['avg_price'] > 0 else 0
            
            # Identificar horas de mayor actividad (más muestras)
            peak_activity_hour = max(hourly_analysis.items(), key=lambda x: x[1]['samples'])
            
            return {
                'player_id': player_id,
                'days_analyzed': days,
                'hourly_analysis': hourly_analysis,
                'recommendation': {
                    'best_buy_hour': best_buy_hour[1]['hour'],
                    'best_buy_price': best_buy_hour[1]['avg_price'],
                    'best_sell_hour': best_sell_hour[1]['hour'],
                    'best_sell_price': best_sell_hour[1]['avg_price'],
                    'potential_profit': potential_profit,
                    'profit_pct': round(profit_pct, 2),
                    'peak_activity_hour': peak_activity_hour[1]['hour'],
                    'peak_activity_samples': peak_activity_hour[1]['samples']
                }
            }
            
        except Exception as e:
            logger.error(f"Error analizando horas pico: {e}")
            return {'error': str(e), 'player_id': player_id}
        finally:
            session.close()
    
    def get_global_peak_hours(self, days: int = 7) -> Dict[str, Any]:
        """
        Analiza horas pico globales (todos los jugadores)
        
        Args:
            days: Días de historial a analizar
            
        Returns:
            Dict con análisis global por hora
        """
        try:
            session = self.db_manager.get_session()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener todos los precios con hora
            price_records = session.query(self.db_manager.PriceHistory).filter(
                self.db_manager.PriceHistory.timestamp >= start_date,
                self.db_manager.PriceHistory.hour_of_day.isnot(None)
            ).all()
            
            if not price_records:
                return {'error': 'No hay datos suficientes'}
            
            # Agrupar por hora
            hour_activity = defaultdict(int)
            hour_prices = defaultdict(list)
            
            for record in price_records:
                hour = record.hour_of_day
                hour_activity[hour] += 1
                hour_prices[hour].append(record.price)
            
            # Calcular estadísticas
            global_analysis = {}
            
            for hour in range(24):
                activity = hour_activity.get(hour, 0)
                prices = hour_prices.get(hour, [])
                
                if activity > 0:
                    avg_price = sum(prices) / len(prices) if prices else 0
                    
                    global_analysis[hour] = {
                        'hour': f"{hour:02d}:00",
                        'activity_count': activity,
                        'avg_price': int(avg_price),
                        'unique_players': len(set(r.player_id for r in price_records if r.hour_of_day == hour))
                    }
            
            # Identificar horas de mayor actividad
            if global_analysis:
                peak_hour = max(global_analysis.items(), key=lambda x: x[1]['activity_count'])
                low_hour = min(global_analysis.items(), key=lambda x: x[1]['activity_count'])
                
                return {
                    'days_analyzed': days,
                    'global_analysis': global_analysis,
                    'peak_activity_hour': peak_hour[1]['hour'],
                    'peak_activity_count': peak_hour[1]['activity_count'],
                    'low_activity_hour': low_hour[1]['hour'],
                    'low_activity_count': low_hour[1]['activity_count'],
                    'total_records': len(price_records)
                }
            else:
                return {'error': 'No hay datos procesables'}
            
        except Exception as e:
            logger.error(f"Error analizando horas pico globales: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def get_hourly_recommendations(self) -> Dict[str, str]:
        """
        Recomendaciones generales basadas en horas pico
        
        Returns:
            Dict con recomendaciones por franja horaria
        """
        return {
            'recommendations': [
                {
                    'time_range': '00:00 - 06:00',
                    'activity': 'Muy Baja',
                    'action': '✅ COMPRAR',
                    'reason': 'Pocos jugadores activos, precios más bajos'
                },
                {
                    'time_range': '06:00 - 12:00',
                    'activity': 'Baja-Media',
                    'action': '🟡 MONITOREAR',
                    'reason': 'Mercado despertando, algunos descuentos'
                },
                {
                    'time_range': '12:00 - 18:00',
                    'activity': 'Media-Alta',
                    'action': '🟡 MONITOREAR',
                    'reason': 'Actividad creciente, precios subiendo'
                },
                {
                    'time_range': '18:00 - 23:00',
                    'activity': 'Muy Alta',
                    'action': '✅ VENDER',
                    'reason': 'Peak de jugadores conectados, precios máximos'
                },
                {
                    'time_range': '23:00 - 00:00',
                    'activity': 'Alta',
                    'action': '🔴 EVITAR',
                    'reason': 'Transición entre peak y madrugada, volátil'
                }
            ],
            'best_buy_window': '02:00 - 05:00 (madrugada)',
            'best_sell_window': '19:00 - 22:00 (noche)',
            'note': 'Estos son patrones generales. Analiza jugadores específicos para mejor precisión.'
        }
    
    def _save_price_with_hour(self, player_id: str, price: int, hour: int):
        """
        Guarda precio con hora del día
        
        Args:
            player_id: ID del jugador
            price: Precio
            hour: Hora del día (0-23)
        """
        try:
            session = self.db_manager.get_session()
            
            price_entry = self.db_manager.PriceHistory(
                player_id=player_id,
                price=price,
                timestamp=datetime.now(),
                hour_of_day=hour
            )
            
            session.add(price_entry)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error guardando precio con hora: {e}")
        finally:
            session.close()
