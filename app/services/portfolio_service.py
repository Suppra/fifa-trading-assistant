"""
Servicio de tracking de portfolio
Análisis de inversión total, profit/loss, ROI
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from sqlalchemy import func

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Gestión y análisis de portfolio de inversiones
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Resumen completo del portfolio
        
        Returns:
            Dict con inversión total, profit, ROI, etc.
        """
        try:
            session = self.db_manager.get_session()
            
            # Obtener todas las entradas de inventario
            inventory = session.query(self.db_manager.Inventory).all()
            
            if not inventory:
                return {
                    'total_investment': 0,
                    'total_value': 0,
                    'unrealized_profit': 0,
                    'realized_profit': 0,
                    'total_profit': 0,
                    'roi_pct': 0,
                    'cards_owned': 0,
                    'cards_sold': 0,
                    'total_cards': 0
                }
            
            total_investment = 0
            total_value = 0
            realized_profit = 0
            cards_owned = 0
            cards_sold = 0
            
            for item in inventory:
                if item.status == 'sold':
                    # Carta vendida
                    cards_sold += item.quantity
                    realized_profit += (item.profit or 0)
                else:
                    # Carta owned o listed
                    cards_owned += item.quantity
                    total_investment += item.purchase_price * item.quantity
                    
                    # Obtener precio actual para calcular valor no realizado
                    current_price = self._get_current_price(item.player_id, session)
                    if current_price:
                        total_value += current_price * item.quantity
                    else:
                        # Si no hay precio actual, asumir precio de compra
                        total_value += item.purchase_price * item.quantity
            
            # Calcular profit no realizado
            unrealized_profit = total_value - total_investment
            
            # Profit total
            total_profit = realized_profit + unrealized_profit
            
            # ROI
            roi_pct = (total_profit / total_investment) * 100 if total_investment > 0 else 0
            
            return {
                'total_investment': total_investment,
                'total_value': total_value,
                'unrealized_profit': unrealized_profit,
                'realized_profit': realized_profit,
                'total_profit': total_profit,
                'roi_pct': round(roi_pct, 2),
                'cards_owned': cards_owned,
                'cards_sold': cards_sold,
                'total_cards': cards_owned + cards_sold,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de portfolio: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Jugadores con mejor ROI
        
        Args:
            limit: Número de jugadores a retornar
            
        Returns:
            Lista de mejores inversiones
        """
        try:
            session = self.db_manager.get_session()
            
            inventory = session.query(self.db_manager.Inventory).filter(
                self.db_manager.Inventory.status.in_(['owned', 'listed'])
            ).all()
            
            performers = []
            
            for item in inventory:
                current_price = self._get_current_price(item.player_id, session)
                
                if current_price and current_price > 0:
                    profit_per_card = current_price - item.purchase_price
                    total_profit = profit_per_card * item.quantity
                    roi_pct = (profit_per_card / item.purchase_price) * 100
                    
                    performers.append({
                        'player_name': item.player_name,
                        'player_id': item.player_id,
                        'purchase_price': item.purchase_price,
                        'current_price': current_price,
                        'quantity': item.quantity,
                        'profit_per_card': profit_per_card,
                        'total_profit': total_profit,
                        'roi_pct': round(roi_pct, 2),
                        'purchase_date': item.purchase_date.isoformat()
                    })
            
            # Ordenar por ROI descendente
            performers.sort(key=lambda x: x['roi_pct'], reverse=True)
            
            return performers[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo top performers: {e}")
            return []
        finally:
            session.close()
    
    def get_worst_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Jugadores con peor ROI (pérdidas)
        
        Args:
            limit: Número de jugadores a retornar
            
        Returns:
            Lista de peores inversiones
        """
        try:
            session = self.db_manager.get_session()
            
            inventory = session.query(self.db_manager.Inventory).filter(
                self.db_manager.Inventory.status.in_(['owned', 'listed'])
            ).all()
            
            performers = []
            
            for item in inventory:
                current_price = self._get_current_price(item.player_id, session)
                
                if current_price and current_price > 0:
                    profit_per_card = current_price - item.purchase_price
                    total_profit = profit_per_card * item.quantity
                    roi_pct = (profit_per_card / item.purchase_price) * 100
                    
                    performers.append({
                        'player_name': item.player_name,
                        'player_id': item.player_id,
                        'purchase_price': item.purchase_price,
                        'current_price': current_price,
                        'quantity': item.quantity,
                        'profit_per_card': profit_per_card,
                        'total_profit': total_profit,
                        'roi_pct': round(roi_pct, 2),
                        'purchase_date': item.purchase_date.isoformat()
                    })
            
            # Ordenar por ROI ascendente (peores primero)
            performers.sort(key=lambda x: x['roi_pct'])
            
            return performers[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo worst performers: {e}")
            return []
        finally:
            session.close()
    
    def get_capital_evolution(self, days: int = 30) -> Dict[str, Any]:
        """
        Evolución del capital en el tiempo
        
        Args:
            days: Días de historial a analizar
            
        Returns:
            Dict con evolución diaria del capital
        """
        try:
            session = self.db_manager.get_session()
            
            # Fecha de inicio
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener todas las transacciones desde start_date
            transactions = session.query(self.db_manager.Transaction).filter(
                self.db_manager.Transaction.timestamp >= start_date
            ).order_by(self.db_manager.Transaction.timestamp).all()
            
            # También obtener compras del inventario
            inventory_purchases = session.query(self.db_manager.Inventory).filter(
                self.db_manager.Inventory.purchase_date >= start_date
            ).order_by(self.db_manager.Inventory.purchase_date).all()
            
            # Construir evolución día a día
            daily_capital = defaultdict(lambda: {'invested': 0, 'profit': 0, 'total': 0})
            
            # Procesar transacciones
            for trans in transactions:
                date_key = trans.timestamp.date().isoformat()
                
                if trans.transaction_type == 'buy':
                    daily_capital[date_key]['invested'] += trans.price
                elif trans.transaction_type == 'sell':
                    daily_capital[date_key]['profit'] += (trans.profit or 0)
            
            # Procesar inventario
            for inv in inventory_purchases:
                date_key = inv.purchase_date.date().isoformat()
                daily_capital[date_key]['invested'] += inv.purchase_price * inv.quantity
                
                if inv.status == 'sold' and inv.sell_date:
                    sell_date_key = inv.sell_date.date().isoformat()
                    daily_capital[sell_date_key]['profit'] += (inv.profit or 0)
            
            # Calcular total acumulado
            cumulative_invested = 0
            cumulative_profit = 0
            evolution = []
            
            # Generar todos los días en el rango
            current_date = start_date.date()
            end_date = datetime.now().date()
            
            while current_date <= end_date:
                date_key = current_date.isoformat()
                
                # Actualizar acumulados
                cumulative_invested += daily_capital[date_key]['invested']
                cumulative_profit += daily_capital[date_key]['profit']
                
                total_capital = cumulative_invested + cumulative_profit
                
                evolution.append({
                    'date': date_key,
                    'invested': cumulative_invested,
                    'profit': cumulative_profit,
                    'total': total_capital
                })
                
                current_date += timedelta(days=1)
            
            return {
                'days': days,
                'evolution': evolution,
                'final_capital': evolution[-1]['total'] if evolution else 0,
                'final_profit': evolution[-1]['profit'] if evolution else 0,
                'final_invested': evolution[-1]['invested'] if evolution else 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo evolución de capital: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def get_investment_distribution(self) -> Dict[str, Any]:
        """
        Distribución de inversión por rating, posición, liga
        
        Returns:
            Dict con distribución de inversiones
        """
        try:
            session = self.db_manager.get_session()
            
            # Obtener inventario activo
            inventory = session.query(self.db_manager.Inventory).filter(
                self.db_manager.Inventory.status.in_(['owned', 'listed'])
            ).all()
            
            by_rating = defaultdict(lambda: {'count': 0, 'investment': 0})
            by_position = defaultdict(lambda: {'count': 0, 'investment': 0})
            by_league = defaultdict(lambda: {'count': 0, 'investment': 0})
            
            for item in inventory:
                investment = item.purchase_price * item.quantity
                
                # Obtener datos del jugador
                player = session.query(self.db_manager.Player).filter_by(
                    player_id=item.player_id
                ).first()
                
                if player:
                    # Por rating (agrupado en rangos)
                    if player.rating >= 88:
                        rating_range = '88+'
                    elif player.rating >= 86:
                        rating_range = '86-87'
                    elif player.rating >= 84:
                        rating_range = '84-85'
                    elif player.rating >= 82:
                        rating_range = '82-83'
                    else:
                        rating_range = '<82'
                    
                    by_rating[rating_range]['count'] += item.quantity
                    by_rating[rating_range]['investment'] += investment
                    
                    # Por posición
                    if player.position:
                        by_position[player.position]['count'] += item.quantity
                        by_position[player.position]['investment'] += investment
                    
                    # Por liga
                    if player.league:
                        by_league[player.league]['count'] += item.quantity
                        by_league[player.league]['investment'] += investment
            
            return {
                'by_rating': dict(by_rating),
                'by_position': dict(by_position),
                'by_league': dict(by_league)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo distribución de inversión: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def _get_current_price(self, player_id: str, session) -> Optional[int]:
        """
        Obtiene el precio actual de un jugador
        
        Args:
            player_id: ID del jugador
            session: Sesión de BD activa
            
        Returns:
            Precio actual o None
        """
        try:
            # Obtener último precio de price_history
            last_price = session.query(self.db_manager.PriceHistory).filter_by(
                player_id=player_id
            ).order_by(self.db_manager.PriceHistory.timestamp.desc()).first()
            
            if last_price:
                return last_price.price
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo precio actual: {e}")
            return None
