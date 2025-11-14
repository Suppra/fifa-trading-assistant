"""
Market analyzer for EA FC 26 Trading Bot
Analyzes market trends, identifies opportunities, and provides insights
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

class MarketAnalyzer:
    """
    Analyzes EA FC 26 market data to identify trading opportunities
    """
    
    def __init__(self, config, db_manager):
        """Initialize market analyzer"""
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger("TradingBot.MarketAnalyzer")
        
        # Get configuration
        self.min_profit_percentage = config.get('trading.min_profit_percentage', 5)
        self.max_buy_price = config.get('trading.max_buy_price', 50000)
        
    def analyze_player_trend(self, player_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze price trend for a specific player
        
        Args:
            player_id: Player ID
            days: Number of days to analyze
            
        Returns:
            Trend analysis data
        """
        # Get price history
        price_history = self.db_manager.get_price_history(player_id, days)
        
        if not price_history or len(price_history) < 2:
            return {
                'trend': 'unknown',
                'confidence': 0,
                'avg_price': 0,
                'volatility': 0
            }
        
        # Convert to pandas DataFrame
        df = pd.DataFrame([
            {'timestamp': p.timestamp, 'price': p.price}
            for p in price_history
        ])
        
        # Calculate metrics
        avg_price = df['price'].mean()
        current_price = df['price'].iloc[-1]
        min_price = df['price'].min()
        max_price = df['price'].max()
        volatility = df['price'].std() / avg_price if avg_price > 0 else 0
        
        # Determine trend
        recent_prices = df['price'].tail(3).values
        if len(recent_prices) >= 2:
            if recent_prices[-1] > recent_prices[0] * 1.05:
                trend = 'rising'
            elif recent_prices[-1] < recent_prices[0] * 0.95:
                trend = 'falling'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'trend': trend,
            'current_price': int(current_price),
            'avg_price': int(avg_price),
            'min_price': int(min_price),
            'max_price': int(max_price),
            'volatility': float(volatility),
            'price_change_pct': ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
        }
    
    def find_buy_opportunities(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Find players that are good buy opportunities
        
        Args:
            max_results: Maximum number of opportunities to return
            
        Returns:
            List of buy opportunities
        """
        self.logger.info("Searching for buy opportunities...")
        
        opportunities = []
        
        # TODO: Implement logic to find opportunities based on:
        # - Price below historical average
        # - Upcoming events (TOTW, SBC requirements)
        # - Market trends
        # - Supply/demand analysis
        
        # Placeholder logic
        session = self.db_manager.get_session()
        try:
            from database.db_manager import Player
            players = session.query(Player).limit(50).all()
            
            for player in players:
                analysis = self.analyze_player_trend(player.player_id)
                
                if analysis['trend'] == 'falling' and analysis['volatility'] < 0.15:
                    # Potential buy opportunity
                    opportunities.append({
                        'player_id': player.player_id,
                        'name': player.name,
                        'rating': player.rating,
                        'current_price': analysis['current_price'],
                        'avg_price': analysis['avg_price'],
                        'potential_profit_pct': ((analysis['avg_price'] - analysis['current_price']) 
                                                / analysis['current_price'] * 100),
                        'reason': 'Price below average, low volatility',
                        'confidence': 0.7
                    })
            
        finally:
            session.close()
        
        # Sort by potential profit
        opportunities.sort(key=lambda x: x['potential_profit_pct'], reverse=True)
        
        return opportunities[:max_results]
    
    def find_sell_opportunities(self, owned_players: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find owned players that should be sold
        
        Args:
            owned_players: List of owned player IDs
            
        Returns:
            List of sell opportunities
        """
        self.logger.info("Searching for sell opportunities...")
        
        opportunities = []
        
        if not owned_players:
            # Get owned players from transaction history
            session = self.db_manager.get_session()
            try:
                from database.db_manager import Transaction
                buy_transactions = session.query(Transaction)\
                    .filter(Transaction.transaction_type == 'buy')\
                    .all()
                
                owned_players = list(set(t.player_id for t in buy_transactions))
                
            finally:
                session.close()
        
        for player_id in owned_players:
            analysis = self.analyze_player_trend(player_id)
            
            # Check if price is rising and above purchase price
            if analysis['trend'] == 'rising':
                opportunities.append({
                    'player_id': player_id,
                    'current_price': analysis['current_price'],
                    'avg_price': analysis['avg_price'],
                    'reason': 'Price rising, good time to sell',
                    'confidence': 0.75
                })
        
        return opportunities
    
    def get_market_state(self) -> Dict[str, Any]:
        """
        Get overall market state
        
        Returns:
            Market state information
        """
        self.logger.info("Analyzing market state...")
        
        # TODO: Implement comprehensive market analysis
        # - Overall market trend (bull/bear)
        # - Active player count
        # - Average prices
        # - Market volatility
        
        return {
            'state': 'neutral',
            'trend': 'stable',
            'volatility': 'medium',
            'recommended_action': 'hold',
            'timestamp': datetime.now()
        }
    
    def analyze_sbc_impact(self, sbc_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze impact of Squad Building Challenges on player prices
        
        Args:
            sbc_requirements: SBC requirements (rating, league, etc.)
            
        Returns:
            List of players likely to increase in price
        """
        self.logger.info("Analyzing SBC impact...")
        
        # TODO: Implement SBC analysis
        # - Find players matching requirements
        # - Predict demand increase
        # - Recommend investment opportunities
        
        return []
    
    def calculate_profit_potential(self, player_id: str, buy_price: int, 
                                   holding_days: int = 7) -> Dict[str, Any]:
        """
        Calculate potential profit for a player
        
        Args:
            player_id: Player ID
            buy_price: Proposed buy price
            holding_days: Days to hold before selling
            
        Returns:
            Profit potential analysis
        """
        analysis = self.analyze_player_trend(player_id)
        
        # EA FC 26 tax is 5%
        ea_tax = 0.05
        
        # Estimate sell price based on trend
        if analysis['trend'] == 'rising':
            estimated_sell_price = analysis['current_price'] * 1.1
        elif analysis['trend'] == 'falling':
            estimated_sell_price = analysis['current_price'] * 0.95
        else:
            estimated_sell_price = analysis['avg_price']
        
        # Calculate profit after tax
        profit_after_tax = estimated_sell_price * (1 - ea_tax) - buy_price
        profit_percentage = (profit_after_tax / buy_price * 100) if buy_price > 0 else 0
        
        return {
            'buy_price': buy_price,
            'estimated_sell_price': int(estimated_sell_price),
            'profit_after_tax': int(profit_after_tax),
            'profit_percentage': profit_percentage,
            'recommended': profit_percentage >= self.min_profit_percentage,
            'risk_level': 'low' if analysis['volatility'] < 0.1 else 'medium' if analysis['volatility'] < 0.2 else 'high'
        }
