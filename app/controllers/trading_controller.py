"""
Trading engine for EA FC 26 Trading Bot
Executes buy/sell decisions based on analysis and predictions
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import schedule

class TradingEngine:
    """
    Executes trading strategies for EA FC 26
    """
    
    def __init__(self, config, db_manager, market_analyzer, price_predictor):
        """Initialize trading engine"""
        self.config = config
        self.db_manager = db_manager
        self.market_analyzer = market_analyzer
        self.price_predictor = price_predictor
        self.logger = logging.getLogger("TradingBot.TradingEngine")
        
        # Get configuration
        self.auto_trading_enabled = config.get('trading.auto_trading_enabled', False)
        self.min_profit_percentage = config.get('trading.min_profit_percentage', 5)
        self.max_buy_price = config.get('trading.max_buy_price', 50000)
        self.max_cards_owned = config.get('trading.max_cards_owned', 50)
        self.trade_interval_minutes = config.get('trading.trade_interval_minutes', 30)
        
        self.owned_cards = []
        self.pending_transactions = []
        
    def record_buy(self, player_id: str, price: int, strategy: str = 'manual') -> bool:
        """
        Record a manual buy transaction (user executed it in-game)
        
        Args:
            player_id: Player ID bought
            price: Buy price
            strategy: Trading strategy used
            
        Returns:
            True if recorded successfully
        """
        self.logger.info(f"📝 Recording BUY for player {player_id} at {price} coins")
        
        # Check max cards limit
        if len(self.owned_cards) >= self.max_cards_owned:
            self.logger.warning("⚠️ Max cards owned limit reached")
            return False
        
        # Record transaction in database
        self.db_manager.add_transaction({
            'player_id': player_id,
            'transaction_type': 'buy',
            'price': price,
            'timestamp': datetime.now(),
            'status': 'completed'
        })
        
        # Add to owned cards
        self.owned_cards.append({
            'player_id': player_id,
            'buy_price': price,
            'buy_date': datetime.now(),
            'strategy': strategy
        })
        
        self.logger.info(f"✅ Buy recorded: {player_id} @ {price} coins")
        return True
    
    def execute_buy(self, player_id: str, price: int, strategy: str = 'manual') -> bool:
        """
        Legacy method - redirects to record_buy
        El bot NO ejecuta compras automáticamente
        """
        self.logger.warning("⚠️ Auto-trading is disabled. Use record_buy() instead.")
        return self.record_buy(player_id, price, strategy)
    
    def record_sell(self, player_id: str, price: int) -> bool:
        """
        Record a manual sell transaction (user executed it in-game)
        
        Args:
            player_id: Player ID sold
            price: Sell price
            
        Returns:
            True if recorded successfully
        """
        self.logger.info(f"📝 Recording SELL for player {player_id} at {price} coins")
        
        # Find owned card
        owned_card = next((c for c in self.owned_cards if c['player_id'] == player_id), None)
        
        if not owned_card:
            self.logger.warning(f"⚠️ Player {player_id} not in owned cards")
            self.logger.info("Tip: Use record_buy() first to track your purchases")
            return False
        
        # Calculate profit (after EA FC 26 5% tax)
        ea_tax = 0.05
        profit_after_tax = int(price * (1 - ea_tax) - owned_card['buy_price'])
        profit_pct = (profit_after_tax / owned_card['buy_price'] * 100)
        
        # Record transaction in database
        self.db_manager.add_transaction({
            'player_id': player_id,
            'transaction_type': 'sell',
            'price': price,
            'profit': profit_after_tax,
            'timestamp': datetime.now(),
            'status': 'completed'
        })
        
        # Remove from owned cards
        self.owned_cards = [c for c in self.owned_cards if c['player_id'] != player_id]
        
        emoji = "💰" if profit_after_tax > 0 else "📉"
        self.logger.info(f"✅ {emoji} Sell recorded: {player_id} @ {price} coins")
        self.logger.info(f"   Profit: {profit_after_tax:+d} coins ({profit_pct:+.1f}%)")
        return True
    
    def execute_sell(self, player_id: str, price: int) -> bool:
        """
        Legacy method - redirects to record_sell
        El bot NO ejecuta ventas automáticamente
        """
        self.logger.warning("⚠️ Auto-trading is disabled. Use record_sell() instead.")
        return self.record_sell(player_id, price)
    
    def run_trading_cycle(self):
        """Run one analysis cycle - check for opportunities and show recommendations"""
        self.logger.info("=" * 60)
        self.logger.info("🔍 Running market analysis cycle...")
        self.logger.info(f"📦 Owned cards: {len(self.owned_cards)}/{self.max_cards_owned}")
        
        try:
            # Generate recommendations
            self.logger.info("")
            self.logger.info("📊 Generating recommendations...")
            
            # Check for sell recommendations
            sell_recs = self._generate_sell_recommendations()
            
            # Check for buy recommendations
            buy_recs = self._generate_buy_recommendations()
            
            # Display recommendations
            self._display_recommendations(buy_recs, sell_recs)
            
            # Display summary
            total_profit = self.db_manager.get_total_profit()
            self.logger.info("")
            self.logger.info(f"💰 Total profit: {total_profit:+d} coins")
            self.logger.info("")
            self.logger.info("💡 Tip: Check the dashboard at http://localhost:5000 for detailed analysis")
            
        except Exception as e:
            self.logger.error(f"Error in analysis cycle: {e}", exc_info=True)
        
        self.logger.info("=" * 60)
    
    def _generate_buy_recommendations(self) -> List[Dict[str, Any]]:
        """Generate buy recommendations based on market analysis"""
        self.logger.info("📈 Analyzing buy opportunities...")
        
        recommendations = []
        
        # Get opportunities from market analyzer
        buy_opportunities = self.market_analyzer.find_buy_opportunities(max_results=10)
        
        # Get predictions
        for opp in buy_opportunities:
            prediction = self.price_predictor.predict_price(opp['player_id'])
            
            if prediction and prediction['confidence'] >= 0.6:
                # Calculate profit potential
                profit_analysis = self.market_analyzer.calculate_profit_potential(
                    opp['player_id'],
                    opp['current_price']
                )
                
                if profit_analysis['recommended'] and opp['current_price'] <= self.max_buy_price:
                    recommendations.append({
                        **opp,
                        'prediction': prediction,
                        'profit_analysis': profit_analysis
                    })
        
        return recommendations
    
    def _generate_sell_recommendations(self) -> List[Dict[str, Any]]:
        """Generate sell recommendations for owned cards"""
        if not self.owned_cards:
            return []
        
        self.logger.info("💰 Analyzing sell opportunities...")
        
        recommendations = []
        owned_player_ids = [c['player_id'] for c in self.owned_cards]
        sell_opportunities = self.market_analyzer.find_sell_opportunities(owned_player_ids)
        
        for opp in sell_opportunities:
            # Find owned card
            owned_card = next((c for c in self.owned_cards if c['player_id'] == opp['player_id']), None)
            
            if owned_card:
                # Calculate profit
                ea_tax = 0.05
                profit_after_tax = opp['current_price'] * (1 - ea_tax) - owned_card['buy_price']
                profit_pct = (profit_after_tax / owned_card['buy_price'] * 100)
                
                if profit_pct >= self.min_profit_percentage:
                    recommendations.append({
                        **opp,
                        'owned_card': owned_card,
                        'profit_after_tax': profit_after_tax,
                        'profit_percentage': profit_pct
                    })
        
        return recommendations
    
    def _display_recommendations(self, buy_recs: List[Dict], sell_recs: List[Dict]):
        """Display recommendations in console"""
        
        if buy_recs:
            self.logger.info("")
            self.logger.info("🛒 BUY RECOMMENDATIONS:")
            self.logger.info("━" * 60)
            for i, rec in enumerate(buy_recs[:5], 1):
                self.logger.info(f"{i}. {rec.get('name', rec['player_id'])} (Rating: {rec.get('rating', 'N/A')})")
                self.logger.info(f"   💵 Buy at: {rec['current_price']:,} coins")
                self.logger.info(f"   📊 Potential profit: {rec['profit_analysis']['profit_percentage']:.1f}%")
                self.logger.info(f"   🎯 Confidence: {rec['prediction']['confidence']*100:.0f}%")
                self.logger.info(f"   ⚠️  Risk: {rec['profit_analysis']['risk_level']}")
                self.logger.info("")
        else:
            self.logger.info("")
            self.logger.info("🛒 No strong buy opportunities at the moment")
        
        if sell_recs:
            self.logger.info("")
            self.logger.info("💰 SELL RECOMMENDATIONS:")
            self.logger.info("━" * 60)
            for i, rec in enumerate(sell_recs, 1):
                self.logger.info(f"{i}. Player ID: {rec['player_id']}")
                self.logger.info(f"   💵 Sell at: {rec['current_price']:,} coins")
                self.logger.info(f"   📈 Profit: {rec['profit_after_tax']:+,} coins ({rec['profit_percentage']:+.1f}%)")
                self.logger.info(f"   📅 Held for: {(datetime.now() - rec['owned_card']['buy_date']).days} days")
                self.logger.info("")
        elif self.owned_cards:
            self.logger.info("")
            self.logger.info("💰 No sell opportunities yet - hold your cards")
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        Get trading recommendations without executing
        
        Returns:
            Dict with buy and sell recommendations
        """
        # Validar que market_analyzer existe
        if not self.market_analyzer:
            self.logger.warning("MarketAnalyzer no disponible - creando instancia temporal")
            from app.controllers.analyzer import MarketAnalyzer
            self.market_analyzer = MarketAnalyzer(self.db_manager)
        
        if not self.price_predictor:
            self.logger.warning("PricePredictor no disponible - creando instancia temporal")
            from app.controllers.price_predictor import PricePredictor
            self.price_predictor = PricePredictor(self.db_manager)
        
        buy_opportunities = self.market_analyzer.find_buy_opportunities(max_results=20)
        investment_opportunities = self.price_predictor.identify_investment_opportunities()
        
        owned_player_ids = [c['player_id'] for c in self.owned_cards]
        sell_opportunities = self.market_analyzer.find_sell_opportunities(owned_player_ids)
        
        return {
            'buy_recommendations': buy_opportunities,
            'investment_opportunities': investment_opportunities,
            'sell_recommendations': sell_opportunities,
            'owned_cards': len(self.owned_cards),
            'total_profit': self.db_manager.get_total_profit()
        }
    
    def start(self):
        """Start the trading engine with scheduled tasks"""
        self.logger.info("Starting trading engine...")
        self.logger.info(f"Auto-trading: {'ENABLED' if self.auto_trading_enabled else 'DISABLED'}")
        self.logger.info(f"Trade interval: {self.trade_interval_minutes} minutes")
        
        # Schedule trading cycle
        schedule.every(self.trade_interval_minutes).minutes.do(self.run_trading_cycle)
        
        # Run first cycle immediately
        self.run_trading_cycle()
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Trading engine stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in trading engine: {e}", exc_info=True)
                time.sleep(60)
