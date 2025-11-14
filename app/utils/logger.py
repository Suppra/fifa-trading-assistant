"""
Logging configuration for EA FC 26 Trading Bot
Includes notifications and alerts
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Try to import winsound for Windows notifications
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

class NotificationHandler(logging.Handler):
    """
    Custom handler for important notifications
    Plays sound and shows alerts for critical events
    """
    
    def __init__(self, enable_sound: bool = True):
        super().__init__()
        self.enable_sound = enable_sound and SOUND_AVAILABLE
        
    def emit(self, record):
        """Emit notification for important messages"""
        if self.enable_sound and record.levelno >= logging.WARNING:
            # Play beep for warnings and errors
            try:
                if os.name == 'nt':  # Windows
                    winsound.Beep(1000, 200)  # 1000Hz, 200ms
            except:
                pass
        
        # Add visual separator for important messages
        if record.levelno >= logging.WARNING:
            print("\n" + "="*70)
            print(f"⚠️  {record.getMessage()}")
            print("="*70 + "\n")

def setup_logger(name: str = "TradingBot", level: str = "INFO", enable_sound: bool = True) -> logging.Logger:
    """
    Setup and configure logger for the trading bot
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_sound: Enable sound notifications
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Notification handler for important alerts
    if enable_sound:
        notification_handler = NotificationHandler(enable_sound=True)
        notification_handler.setLevel(logging.WARNING)
        logger.addHandler(notification_handler)
    
    return logger

def log_trade_opportunity(logger: logging.Logger, opportunity_type: str, 
                         player_name: str, price: int, profit_pct: float, 
                         confidence: float):
    """
    Log a trading opportunity with special formatting
    
    Args:
        logger: Logger instance
        opportunity_type: 'BUY' or 'SELL'
        player_name: Player name
        price: Price in coins
        profit_pct: Profit percentage
        confidence: Confidence level (0-1)
    """
    emoji = "🟢" if opportunity_type == "BUY" else "🔴"
    
    logger.info("\n" + "━"*70)
    logger.info(f"{emoji} {opportunity_type} OPPORTUNITY: {player_name}")
    logger.info(f"💵 Price: {price:,} coins")
    logger.info(f"📊 Profit potential: {profit_pct:.1f}%")
    logger.info(f"🎯 Confidence: {confidence*100:.0f}%")
    logger.info("━"*70 + "\n")
    
    # Play sound for very good opportunities
    if profit_pct >= 15 and confidence >= 0.75:
        if SOUND_AVAILABLE and os.name == 'nt':
            try:
                winsound.Beep(1500, 300)  # Higher pitch for good opportunities
            except:
                pass
