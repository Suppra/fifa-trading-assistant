"""
EA FC 26 Trading Bot - Main Application Package
MVC Architecture
"""

__version__ = "2.0.0"
__author__ = "Suppra"

from .models.database import DatabaseManager, Player, Transaction, PriceHistory
from .controllers.market_controller import MarketAnalyzer
from .controllers.prediction_controller import PricePredictor
from .controllers.trading_controller import TradingEngine
from .views.desktop_ui import TradingBotApp

__all__ = [
    'DatabaseManager',
    'Player',
    'Transaction',
    'PriceHistory',
    'MarketAnalyzer',
    'PricePredictor',
    'TradingEngine',
    'TradingBotApp',
]
