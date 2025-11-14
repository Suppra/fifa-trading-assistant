"""
Configuration loader for EA FC 26 Trading Bot
"""

import os
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Optional, Dict
from datetime import datetime

class BudgetManager:
    """
    Manages dynamic budget configuration
    Adapts strategies based on available coins
    """
    
    def __init__(self, config_path: str = "budget_config.json"):
        """Initialize budget manager"""
        self.config_path = Path(config_path)
        self.budget_data = self._load_budget()
    
    def _load_budget(self) -> Dict[str, Any]:
        """Load budget configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default budget configuration
            return {
                "current_budget": 11000,
                "initial_budget": 11000,
                "total_profit": 0,
                "invested": 0,
                "reserve": 2000,
                "last_updated": datetime.now().isoformat()
            }
    
    def save_budget(self):
        """Save budget configuration to file"""
        self.budget_data["last_updated"] = datetime.now().isoformat()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.budget_data, f, indent=4)
    
    def update_budget(self, new_budget: int):
        """Update current budget"""
        self.budget_data["current_budget"] = new_budget
        self.save_budget()
    
    def get_budget(self) -> int:
        """Get current available budget"""
        return self.budget_data["current_budget"]
    
    def get_budget_tier(self) -> str:
        """
        Get budget tier for strategy adaptation
        
        Returns:
            Budget tier: 'low', 'medium', 'high', 'elite'
        """
        budget = self.get_budget()
        
        if budget < 20000:
            return 'low'  # 0-20k: Focus on rating 82-84
        elif budget < 50000:
            return 'medium'  # 20-50k: Rating 84-86, some specials
        elif budget < 100000:
            return 'high'  # 50-100k: Special cards, meta players
        else:
            return 'elite'  # 100k+: Icons, high-end trading
    
    def get_strategy_config(self) -> Dict[str, Any]:
        """
        Get trading strategy configuration based on budget tier
        
        Returns:
            Dictionary with strategy parameters
        """
        tier = self.get_budget_tier()
        budget = self.get_budget()
        
        strategies = {
            'low': {
                'max_buy_price': min(int(budget * 0.8), 15000),
                'min_buy_price': 1500,
                'max_investment_per_card': min(int(budget * 0.45), 5000),
                'max_cards_owned': 3,
                'reserve_coins': 2000,
                'min_profit_percentage': 10,
                'focus_ratings': [82, 83, 84],
                'strategies': ['snipe_deals', 'mass_bidding', 'sbc_trading', 'fodder_flipping'],
                'description': 'Bajo presupuesto: Fodder y cartas accesibles'
            },
            'medium': {
                'max_buy_price': min(int(budget * 0.7), 35000),
                'min_buy_price': 5000,
                'max_investment_per_card': min(int(budget * 0.35), 15000),
                'max_cards_owned': 5,
                'reserve_coins': 5000,
                'min_profit_percentage': 8,
                'focus_ratings': [84, 85, 86],
                'strategies': ['position_trading', 'special_cards', 'meta_players', 'weekend_league'],
                'description': 'Presupuesto medio: Meta players y especiales'
            },
            'high': {
                'max_buy_price': min(int(budget * 0.6), 70000),
                'min_buy_price': 15000,
                'max_investment_per_card': min(int(budget * 0.3), 30000),
                'max_cards_owned': 7,
                'reserve_coins': 10000,
                'min_profit_percentage': 6,
                'focus_ratings': [86, 87, 88],
                'strategies': ['special_cards', 'icons', 'investment', 'promo_cards'],
                'description': 'Alto presupuesto: Special cards e inversiones'
            },
            'elite': {
                'max_buy_price': int(budget * 0.5),
                'min_buy_price': 50000,
                'max_investment_per_card': int(budget * 0.25),
                'max_cards_owned': 10,
                'reserve_coins': 20000,
                'min_profit_percentage': 5,
                'focus_ratings': [88, 89, 90, 91],
                'strategies': ['icons', 'high_end_trading', 'investment', 'market_manipulation'],
                'description': 'Elite: Icons, cartas top y trading avanzado'
            }
        }
        
        return strategies[tier]
    
    def record_transaction(self, transaction_type: str, amount: int):
        """Record a transaction and update budget"""
        if transaction_type == 'buy':
            self.budget_data["invested"] += amount
            self.budget_data["current_budget"] -= amount
        elif transaction_type == 'sell':
            self.budget_data["current_budget"] += amount
            profit = amount - self.budget_data["invested"]
            self.budget_data["total_profit"] += profit
            self.budget_data["invested"] = max(0, self.budget_data["invested"] - amount)
        
        self.save_budget()

class ConfigLoader:
    """Loads and manages configuration from YAML and environment variables"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration loader"""
        self.config_path = Path(config_path)
        self.config = {}
        self.budget_manager = BudgetManager()
        
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        self._load_yaml()
        
        # Override with budget-based settings
        self._apply_budget_config()
        
    def _load_yaml(self):
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def _apply_budget_config(self):
        """Apply budget-based configuration overrides"""
        strategy_config = self.budget_manager.get_strategy_config()
        
        # Override trading settings based on budget
        if 'trading' not in self.config:
            self.config['trading'] = {}
        
        self.config['trading']['max_buy_price'] = strategy_config['max_buy_price']
        self.config['trading']['min_buy_price'] = strategy_config['min_buy_price']
        self.config['trading']['max_investment_per_card'] = strategy_config['max_investment_per_card']
        self.config['trading']['max_cards_owned'] = strategy_config['max_cards_owned']
        self.config['trading']['reserve_coins'] = strategy_config['reserve_coins']
        self.config['trading']['min_profit_percentage'] = strategy_config['min_profit_percentage']
        
        # Override market analysis settings
        if 'market_analysis' not in self.config:
            self.config['market_analysis'] = {}
        
        self.config['market_analysis']['focus_ratings'] = strategy_config['focus_ratings']
        self.config['trading']['strategies'] = strategy_config['strategies']
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., 'trading.min_profit_percentage')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check environment variable first (uppercase and replace dots with underscores)
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Navigate nested dictionary
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_trading_config(self) -> dict:
        """Get trading configuration"""
        return self.get('trading', {})
    
    def get_market_analysis_config(self) -> dict:
        """Get market analysis configuration"""
        return self.get('market_analysis', {})
    
    def get_prediction_config(self) -> dict:
        """Get prediction configuration"""
        return self.get('prediction', {})
    
    def get_database_config(self) -> dict:
        """Get database configuration"""
        return self.get('database', {})
    
    def get_logging_config(self) -> dict:
        """Get logging configuration"""
        return self.get('logging', {})
    
    def get_budget_info(self) -> Dict[str, Any]:
        """Get current budget information"""
        tier = self.budget_manager.get_budget_tier()
        strategy_config = self.budget_manager.get_strategy_config()
        
        return {
            'current_budget': self.budget_manager.get_budget(),
            'tier': tier,
            'tier_description': strategy_config['description'],
            'max_buy_price': strategy_config['max_buy_price'],
            'max_cards': strategy_config['max_cards_owned'],
            'strategies': strategy_config['strategies'],
            'reserve': strategy_config['reserve_coins']
        }
    
    def update_budget(self, new_budget: int):
        """Update budget and reconfigure strategies"""
        self.budget_manager.update_budget(new_budget)
        self._apply_budget_config()
    
    def record_transaction(self, transaction_type: str, amount: int):
        """Record transaction in budget manager"""
        self.budget_manager.record_transaction(transaction_type, amount)
