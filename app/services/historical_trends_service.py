"""
Servicio de análisis de tendencias históricas
Scraping de gráficos de precios 7/30/90 días desde FUTBIN
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class HistoricalTrendsService:
    """
    Scraper de tendencias históricas de precios desde FUTBIN
    Extrae datos de gráficos de 7/30/90 días
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.base_url = "https://www.futbin.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
        })
        
    def get_price_graph_data(self, player_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos del gráfico de precios de FUTBIN
        
        Args:
            player_id: ID de FUTBIN del jugador
            days: Días de historial (7, 30, 90, 365)
            
        Returns:
            Dict con timestamps y precios
        """
        try:
            # URL de la API de gráficos de FUTBIN
            # Ejemplo: https://www.futbin.com/26/playerGraph?type=daily_graph&year=26&player=ID
            graph_url = f"{self.base_url}/26/playerGraph"
            params = {
                'type': 'daily_graph',
                'year': '26',
                'player': player_id,
            }
            
            logger.info(f"📊 Obteniendo gráfico de {days} días para jugador {player_id}")
            
            response = self.session.get(graph_url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Error al obtener gráfico: {response.status_code}")
                return None
            
            # FUTBIN devuelve JSON con estructura:
            # { "ps": [[timestamp, price], ...], "xbox": [...], "pc": [...] }
            data = response.json()
            
            if 'pc' not in data or not data['pc']:
                logger.warning(f"No hay datos de PC para jugador {player_id}")
                return None
            
            pc_data = data['pc']
            
            # Filtrar por días solicitados
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_timestamp = int(cutoff_date.timestamp() * 1000)  # FUTBIN usa milisegundos
            
            filtered_data = [
                {'timestamp': ts, 'price': price}
                for ts, price in pc_data
                if ts >= cutoff_timestamp and price > 0
            ]
            
            logger.info(f"✅ Obtenidos {len(filtered_data)} puntos de precio")
            
            return {
                'player_id': player_id,
                'days': days,
                'data': filtered_data,
                'fetched_at': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al obtener gráfico: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON del gráfico: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return None
    
    def analyze_weekly_pattern(self, player_id: str) -> Dict[str, Any]:
        """
        Analiza patrón semanal de precios (Lun-Dom)
        
        Args:
            player_id: ID de FUTBIN del jugador
            
        Returns:
            Dict con análisis por día de la semana
        """
        try:
            # Obtener 30 días de datos (mínimo 4 semanas)
            graph_data = self.get_price_graph_data(player_id, days=30)
            
            if not graph_data or not graph_data['data']:
                return {
                    'error': 'No hay datos suficientes',
                    'player_id': player_id
                }
            
            # Agrupar por día de la semana (0=Lunes, 6=Domingo)
            day_prices = defaultdict(list)
            
            for point in graph_data['data']:
                timestamp_ms = point['timestamp']
                price = point['price']
                
                # Convertir timestamp de milisegundos a datetime
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                day_of_week = dt.weekday()  # 0=Lunes, 6=Domingo
                
                day_prices[day_of_week].append(price)
            
            # Calcular estadísticas por día
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            analysis = {}
            
            for day in range(7):
                prices = day_prices.get(day, [])
                if prices:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    
                    analysis[day_names[day]] = {
                        'avg_price': int(avg_price),
                        'min_price': min_price,
                        'max_price': max_price,
                        'samples': len(prices),
                        'volatility': max_price - min_price
                    }
            
            # Identificar mejor día para comprar/vender
            if analysis:
                best_buy_day = min(analysis.items(), key=lambda x: x[1]['avg_price'])
                best_sell_day = max(analysis.items(), key=lambda x: x[1]['avg_price'])
                
                avg_profit = best_sell_day[1]['avg_price'] - best_buy_day[1]['avg_price']
                profit_pct = (avg_profit / best_buy_day[1]['avg_price']) * 100 if best_buy_day[1]['avg_price'] > 0 else 0
                
                return {
                    'player_id': player_id,
                    'analysis': analysis,
                    'recommendation': {
                        'buy_day': best_buy_day[0],
                        'buy_avg': best_buy_day[1]['avg_price'],
                        'sell_day': best_sell_day[0],
                        'sell_avg': best_sell_day[1]['avg_price'],
                        'avg_profit': avg_profit,
                        'profit_pct': round(profit_pct, 2)
                    }
                }
            else:
                return {'error': 'No hay suficientes datos para análisis', 'player_id': player_id}
            
        except Exception as e:
            logger.error(f"Error analizando patrón semanal: {e}")
            return {'error': str(e), 'player_id': player_id}
    
    def detect_price_trends(self, player_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Detecta tendencias de precio (alcista, bajista, lateral)
        
        Args:
            player_id: ID de FUTBIN del jugador
            days: Días a analizar
            
        Returns:
            Dict con tendencia y estadísticas
        """
        try:
            graph_data = self.get_price_graph_data(player_id, days=days)
            
            if not graph_data or not graph_data['data'] or len(graph_data['data']) < 3:
                return {'error': 'Datos insuficientes', 'player_id': player_id}
            
            prices = [point['price'] for point in graph_data['data']]
            
            # Calcular cambio porcentual total
            first_price = prices[0]
            last_price = prices[-1]
            total_change = last_price - first_price
            total_change_pct = (total_change / first_price) * 100 if first_price > 0 else 0
            
            # Determinar tendencia
            if total_change_pct > 5:
                trend = 'alcista'  # Subiendo
                color = '🟢'
            elif total_change_pct < -5:
                trend = 'bajista'  # Bajando
                color = '🔴'
            else:
                trend = 'lateral'  # Estable
                color = '🟡'
            
            # Calcular volatilidad
            max_price = max(prices)
            min_price = min(prices)
            volatility = max_price - min_price
            volatility_pct = (volatility / min_price) * 100 if min_price > 0 else 0
            
            return {
                'player_id': player_id,
                'days_analyzed': days,
                'trend': trend,
                'trend_color': color,
                'first_price': first_price,
                'last_price': last_price,
                'change': total_change,
                'change_pct': round(total_change_pct, 2),
                'max_price': max_price,
                'min_price': min_price,
                'volatility': volatility,
                'volatility_pct': round(volatility_pct, 2),
                'data_points': len(prices)
            }
            
        except Exception as e:
            logger.error(f"Error detectando tendencias: {e}")
            return {'error': str(e), 'player_id': player_id}
    
    def get_historical_comparison(self, player_ids: List[str], days: int = 30) -> Dict[str, Any]:
        """
        Compara tendencias de múltiples jugadores
        
        Args:
            player_ids: Lista de IDs de FUTBIN
            days: Días a comparar
            
        Returns:
            Dict con comparación de jugadores
        """
        try:
            comparisons = {}
            
            for player_id in player_ids:
                trend_data = self.detect_price_trends(player_id, days=days)
                
                if 'error' not in trend_data:
                    comparisons[player_id] = {
                        'trend': trend_data['trend'],
                        'change_pct': trend_data['change_pct'],
                        'volatility_pct': trend_data['volatility_pct'],
                        'last_price': trend_data['last_price']
                    }
                
                time.sleep(1)  # Rate limiting
            
            # Ordenar por mejor rendimiento
            sorted_players = sorted(
                comparisons.items(),
                key=lambda x: x[1]['change_pct'],
                reverse=True
            )
            
            return {
                'days': days,
                'players_compared': len(comparisons),
                'comparisons': dict(sorted_players),
                'best_performer': sorted_players[0] if sorted_players else None,
                'worst_performer': sorted_players[-1] if sorted_players else None
            }
            
        except Exception as e:
            logger.error(f"Error en comparación histórica: {e}")
            return {'error': str(e)}
    
    def save_historical_data_to_db(self, player_id: str, days: int = 30):
        """
        Guarda datos históricos en price_history table
        
        Args:
            player_id: ID de FUTBIN del jugador
            days: Días de historial a guardar
        """
        try:
            graph_data = self.get_price_graph_data(player_id, days=days)
            
            if not graph_data or not graph_data['data']:
                logger.warning(f"No hay datos para guardar de jugador {player_id}")
                return
            
            session = self.db_manager.get_session()
            
            for point in graph_data['data']:
                timestamp_ms = point['timestamp']
                price = point['price']
                
                # Convertir timestamp
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                
                # Verificar si ya existe este punto
                existing = session.query(self.db_manager.PriceHistory).filter_by(
                    player_id=player_id,
                    timestamp=dt
                ).first()
                
                if not existing:
                    price_entry = self.db_manager.PriceHistory(
                        player_id=player_id,
                        price=price,
                        timestamp=dt
                    )
                    session.add(price_entry)
            
            session.commit()
            logger.info(f"✅ Guardados {len(graph_data['data'])} puntos históricos para {player_id}")
            
        except Exception as e:
            logger.error(f"Error guardando datos históricos: {e}")
        finally:
            session.close()
