"""
Asistente Inteligente de Fodder Flipping
Te dice exactamente qué hacer en cada momento según el mercado
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from src.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class FodderFlippingAssistant:
    """Asistente inteligente para estrategia Fodder Flipping"""
    
    def __init__(self, user_budget: int = 11000):
        self.db = DatabaseManager()
        self.user_budget = user_budget
        
        # Configuración de estrategia
        self.config = {
            'min_rating': 82,
            'max_rating': 84,
            'max_card_price': user_budget * 0.7,  # No más del 70% del presupuesto
            'min_profit_percent': 15,  # Mínimo 15% ganancia
            'reserve_budget': 2000,  # Siempre dejar 2k de reserva
        }
    
    def get_market_moment(self) -> Dict[str, any]:
        """Analiza el momento actual del mercado"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.strftime('%A')
        
        # Determinar fase del mercado
        if day_of_week in ['Monday', 'Tuesday', 'Wednesday']:
            if hour >= 19:  # Lunes-Miércoles noche (después de Rewards)
                return {
                    'phase': 'BUYING_OPTIMAL',
                    'action': 'COMPRAR',
                    'urgency': 'ALTA',
                    'reason': 'Precios en mínimo semanal después de Rewards',
                    'emoji': '🟢',
                    'confidence': 95
                }
            else:
                return {
                    'phase': 'BUYING_GOOD',
                    'action': 'COMPRAR',
                    'urgency': 'MEDIA',
                    'reason': 'Buenos precios antes del Weekend League',
                    'emoji': '🟡',
                    'confidence': 80
                }
        
        elif day_of_week == 'Thursday':
            if hour >= 19:  # Jueves después de Rewards
                return {
                    'phase': 'BUYING_BEST',
                    'action': 'COMPRAR AGRESIVO',
                    'urgency': 'MUY ALTA',
                    'reason': '¡REWARDS! Precios en MÍNIMO absoluto',
                    'emoji': '🔥',
                    'confidence': 100
                }
            else:
                return {
                    'phase': 'HOLD',
                    'action': 'ESPERAR',
                    'urgency': 'NINGUNA',
                    'reason': 'Espera a Rewards a las 19:00',
                    'emoji': '⏳',
                    'confidence': 70
                }
        
        elif day_of_week in ['Friday', 'Saturday']:
            return {
                'phase': 'SELLING_PEAK',
                'action': 'VENDER',
                'urgency': 'ALTA',
                'reason': 'Weekend League - Precios en MÁXIMO',
                'emoji': '💰',
                'confidence': 95
            }
        
        elif day_of_week == 'Sunday':
            if hour <= 18:
                return {
                    'phase': 'SELLING_LAST_CHANCE',
                    'action': 'VENDER YA',
                    'urgency': 'CRÍTICA',
                    'reason': 'Última oportunidad antes de bajada',
                    'emoji': '⚠️',
                    'confidence': 90
                }
            else:
                return {
                    'phase': 'HOLD',
                    'action': 'NO VENDER',
                    'urgency': 'NINGUNA',
                    'reason': 'Precios cayendo - mejor esperar al próximo WL',
                    'emoji': '🔒',
                    'confidence': 85
                }
        
        return {
            'phase': 'NEUTRAL',
            'action': 'MONITOREAR',
            'urgency': 'BAJA',
            'reason': 'Mercado estable',
            'emoji': '📊',
            'confidence': 60
        }
    
    def get_buy_recommendations(self) -> List[Dict[str, any]]:
        """Obtiene recomendaciones ESPECÍFICAS de compra"""
        session = self.db.SessionLocal()
        market_moment = self.get_market_moment()
        
        try:
            from src.database.db_manager import Player, PriceHistory
            from sqlalchemy import func
            
            # Solo recomendar si es momento de comprar
            if market_moment['action'] not in ['COMPRAR', 'COMPRAR AGRESIVO']:
                return []
            
            # Obtener jugadores fodder con precio actual
            subquery = session.query(
                PriceHistory.player_id,
                func.max(PriceHistory.timestamp).label('latest')
            ).group_by(PriceHistory.player_id).subquery()
            
            fodder_cards = session.query(
                Player,
                PriceHistory.price.label('current_price')
            ).join(
                PriceHistory,
                Player.player_id == PriceHistory.player_id
            ).join(
                subquery,
                (PriceHistory.player_id == subquery.c.player_id) &
                (PriceHistory.timestamp == subquery.c.latest)
            ).filter(
                Player.rating.in_([82, 83, 84]),
                Player.is_extinct == False,
                PriceHistory.price > 0,
                PriceHistory.price <= self.config['max_card_price']
            ).order_by(
                Player.rating.desc(),
                PriceHistory.price.asc()
            ).limit(10).all()
            
            recommendations = []
            
            for player, current_price in fodder_cards:
                # Calcular precio objetivo de venta
                target_price = self._calculate_sell_price(player.rating, current_price)
                profit = target_price - current_price - (target_price * 0.05)  # Tax 5%
                profit_percent = (profit / current_price) * 100
                
                if profit_percent >= self.config['min_profit_percent']:
                    recommendations.append({
                        'player_name': player.name,
                        'rating': player.rating,
                        'position': player.position,
                        'league': player.league,
                        'current_price': current_price,
                        'target_price': target_price,
                        'profit': int(profit),
                        'profit_percent': round(profit_percent, 1),
                        'when_to_sell': self._get_sell_timing(player.rating),
                        'confidence': self._calculate_confidence(player.rating, profit_percent),
                        'priority': 'ALTA' if profit_percent >= 25 else 'MEDIA'
                    })
            
            # Ordenar por profit_percent
            recommendations.sort(key=lambda x: x['profit_percent'], reverse=True)
            
            return recommendations[:5]  # Top 5
            
        finally:
            session.close()
    
    def get_sell_recommendations(self) -> List[Dict[str, any]]:
        """Obtiene recomendaciones de venta (tu inventario)"""
        market_moment = self.get_market_moment()
        
        # Solo recomendar vender si es buen momento
        if market_moment['action'] not in ['VENDER', 'VENDER YA']:
            return []
        
        session = self.db.SessionLocal()
        
        try:
            from src.database.db_manager import Player, PriceHistory, Transaction
            from sqlalchemy import func
            
            # Obtener cartas compradas y no vendidas
            bought_cards = session.query(
                Transaction.player_id,
                Transaction.price.label('buy_price'),
                Transaction.timestamp.label('buy_date')
            ).filter(
                Transaction.transaction_type == 'buy',
                Transaction.status == 'completed'
            ).all()
            
            if not bought_cards:
                return []
            
            sell_recommendations = []
            
            for card in bought_cards:
                # Obtener precio actual
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.player_id == card.player_id
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                if not latest_price:
                    continue
                
                current_price = latest_price.price
                profit = current_price - card.buy_price - (current_price * 0.05)
                profit_percent = (profit / card.buy_price) * 100
                
                # Obtener datos del jugador
                player = session.query(Player).filter(
                    Player.player_id == card.player_id
                ).first()
                
                if not player:
                    continue
                
                sell_recommendations.append({
                    'player_name': player.name,
                    'rating': player.rating,
                    'buy_price': card.buy_price,
                    'current_price': current_price,
                    'profit': int(profit),
                    'profit_percent': round(profit_percent, 1),
                    'days_held': (datetime.now() - card.buy_date).days,
                    'recommendation': 'VENDER AHORA' if profit_percent >= 15 else 'HOLD',
                    'urgency': market_moment['urgency']
                })
            
            # Ordenar por profit_percent
            sell_recommendations.sort(key=lambda x: x['profit_percent'], reverse=True)
            
            return sell_recommendations
            
        finally:
            session.close()
    
    def _calculate_sell_price(self, rating: int, buy_price: int) -> int:
        """Calcula precio objetivo de venta según rating"""
        multipliers = {
            82: 1.20,  # +20%
            83: 1.25,  # +25%
            84: 1.30   # +30%
        }
        
        multiplier = multipliers.get(rating, 1.15)
        target = int(buy_price * multiplier)
        
        # Redondear a centenas
        return (target // 100) * 100
    
    def _get_sell_timing(self, rating: int) -> str:
        """Indica cuándo vender según rating"""
        now = datetime.now()
        day = now.strftime('%A')
        
        if day in ['Friday', 'Saturday']:
            return "HOY (Weekend League)"
        elif day == 'Sunday':
            return "ANTES DE LAS 18:00"
        else:
            return "Viernes-Sábado próximo"
    
    def _calculate_confidence(self, rating: int, profit_percent: float) -> int:
        """Calcula nivel de confianza de la inversión"""
        base_confidence = {
            82: 85,
            83: 90,
            84: 92
        }.get(rating, 80)
        
        # Ajustar por profit esperado
        if profit_percent >= 30:
            base_confidence += 5
        elif profit_percent < 15:
            base_confidence -= 10
        
        return min(100, max(60, base_confidence))
    
    def get_action_plan(self) -> Dict[str, any]:
        """Plan de acción completo para AHORA"""
        market_moment = self.get_market_moment()
        buy_recs = self.get_buy_recommendations()
        sell_recs = self.get_sell_recommendations()
        
        return {
            'market_moment': market_moment,
            'current_action': market_moment['action'],
            'urgency': market_moment['urgency'],
            'buy_recommendations': buy_recs,
            'sell_recommendations': sell_recs,
            'total_investment_needed': sum(r['current_price'] for r in buy_recs[:3]),
            'potential_profit': sum(r['profit'] for r in buy_recs[:3]),
            'instructions': self._generate_instructions(market_moment, buy_recs, sell_recs)
        }
    
    def _generate_instructions(self, market, buy_recs, sell_recs) -> List[str]:
        """Genera instrucciones paso a paso con ejemplos genéricos"""
        instructions = []
        
        if market['action'] in ['COMPRAR', 'COMPRAR AGRESIVO']:
            instructions.append(f"{market['emoji']} MOMENTO: {market['reason']}")
            instructions.append(f"📝 Presupuesto disponible: {self.user_budget - self.config['reserve_budget']:,} coins")
            instructions.append("")
            instructions.append("🛒 EJEMPLOS DE QUÉ BUSCAR:")
            instructions.append("  • Rating 82: 2,000-3,500 coins (Ejemplo: Pau Torres, Koundé)")
            instructions.append("  • Rating 83: 3,500-5,500 coins (Ejemplo: Rodri, Alaba)")
            instructions.append("  • Rating 84: 5,000-8,000 coins (Ejemplo: Casemiro, Ederson)")
            instructions.append("")
            instructions.append("⏰ CUÁNDO VENDER: Viernes-Sábado (Weekend League)")
            instructions.append("💡 Al comprar una carta en el juego, haz clic en 'COMPRAR EN JUEGO' abajo")
        
        elif market['action'] in ['VENDER', 'VENDER YA']:
            instructions.append(f"{market['emoji']} MOMENTO: {market['reason']}")
            instructions.append("")
            
            if sell_recs and len(sell_recs) > 0:
                instructions.append("💰 VENDE TUS CARTAS EN INVENTARIO:")
                instructions.append("  Ve al tab 'Vender' para ver tu inventario completo")
            else:
                instructions.append("ℹ️ No tienes cartas en inventario para vender")
                instructions.append("")
                instructions.append("💡 PRÓXIMOS PASOS:")
                instructions.append("  1. Espera al Lunes-Jueves para comprar")
                instructions.append("  2. Compra rating 82-84 cuando salga la recomendación")
                instructions.append("  3. Vuelve este fin de semana para vender")
        
        else:
            instructions.append(f"{market['emoji']} {market['reason']}")
            instructions.append("")
            instructions.append("💤 MIENTRAS ESPERAS:")
            instructions.append("  • Revisa el tab 'Mercado' para ver tendencias")
            instructions.append("  • Monitorea la gráfica de precios")
            instructions.append("  • Prepárate para el próximo momento de trading")
        
        return instructions


if __name__ == '__main__':
    assistant = FodderFlippingAssistant(user_budget=11000)
    plan = assistant.get_action_plan()
    
    print("\n" + "="*60)
    print("  ASISTENTE DE FODDER FLIPPING")
    print("="*60)
    print(f"\n{plan['market_moment']['emoji']} ACCIÓN: {plan['current_action']}")
    print(f"⚡ Urgencia: {plan['urgency']}")
    print(f"📊 Confianza: {plan['market_moment']['confidence']}%")
    print(f"\n{plan['market_moment']['reason']}")
    print("\n" + "-"*60)
    print("INSTRUCCIONES:")
    for instruction in plan['instructions']:
        print(instruction)
    print("="*60 + "\n")
