"""
EA FC 26 Trading Bot
Main entry point for the trading bot application
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger
from src.database.db_manager import DatabaseManager
from src.data_collection.market_scraper import MarketScraper
from src.market_analysis.analyzer import MarketAnalyzer
from src.prediction.price_predictor import PricePredictor
from src.trading.trading_engine import TradingEngine
from src.api.dashboard import DashboardAPI

def main():
    """Main function to run the trading bot"""
    
    # Setup logging
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("EA FC 26 Trading Bot Starting...")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = ConfigLoader()
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize()
        logger.info("Database initialized")
        
        # Initialize components
        scraper = MarketScraper(config, db_manager)
        analyzer = MarketAnalyzer(config, db_manager)
        predictor = PricePredictor(config, db_manager)
        trading_engine = TradingEngine(config, db_manager, analyzer, predictor)
        
        logger.info("All components initialized successfully")
        
        # Start dashboard API (if enabled)
        if config.get('api.enabled', True):
            dashboard = DashboardAPI(config, db_manager, analyzer, predictor, trading_engine)
            logger.info(f"Dashboard API starting on port {config.get('api.port', 5000)}")
            dashboard.run()
        else:
            # Run in CLI mode
            logger.info("Running in CLI mode (no dashboard)")
            
            # Main trading loop
            logger.info("Starting trading loop...")
            trading_engine.start()
            
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
        logger.info("Stopping trading bot...")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        logger.info("EA FC 26 Trading Bot stopped")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
