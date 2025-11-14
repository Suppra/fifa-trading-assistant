"""
Database manager for EA FC 26 Trading Bot
Handles all database operations using SQLAlchemy
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

class Player(Base):
    """Player model"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    rating = Column(Integer, nullable=False)
    position = Column(String(10))
    league = Column(String(100))
    club = Column(String(100))
    nationality = Column(String(100))
    is_extinct = Column(Boolean, default=False)  # Jugador sin mercado/precio
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class PriceHistory(Base):
    """Price history model"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    supply = Column(Integer)  # Number of cards on market
    demand = Column(Integer)  # Sales velocity
    hour_of_day = Column(Integer)  # Hour when price was recorded (0-23) for peak analysis

class Transaction(Base):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'buy' or 'sell'
    price = Column(Integer, nullable=False)
    profit = Column(Integer)  # Only for sell transactions
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(20), default='completed')  # completed, pending, failed

class Prediction(Base):
    """Price prediction model"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50), nullable=False)
    predicted_price = Column(Integer, nullable=False)
    confidence = Column(Float)
    prediction_date = Column(DateTime, default=datetime.now)
    target_date = Column(DateTime, nullable=False)
    model_version = Column(String(50))

class MarketSnapshot(Base):
    """Market snapshot model"""
    __tablename__ = 'market_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_data = Column(Text, nullable=False)  # JSON data
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    market_trend = Column(String(20))  # bull, bear, neutral

class Inventory(Base):
    """Inventory model - tracks multiple purchases of same player"""
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String(50), nullable=False)
    player_name = Column(String(200), nullable=False)
    purchase_price = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, default=datetime.now, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)  # Number of cards purchased at this price
    status = Column(String(20), default='owned')  # owned, listed, sold
    sell_price = Column(Integer)  # Price sold at (if sold)
    sell_date = Column(DateTime)  # Date sold
    profit = Column(Integer)  # Total profit (sell_price - purchase_price) * quantity
    notes = Column(Text)  # Optional notes (e.g., "Weekend League snipe", "SBC investment")

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_url: str = "sqlite:///data/trading_bot.db"):
        """Initialize database manager"""
        self.logger = logging.getLogger("TradingBot.Database")
        self.db_url = db_url
        
        # Ensure data directory exists
        if db_url.startswith("sqlite:///"):
            db_path = Path(db_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Store model references
        self.Player = Player
        self.PriceHistory = PriceHistory
        self.Transaction = Transaction
        self.Prediction = Prediction
        self.MarketSnapshot = MarketSnapshot
        self.Inventory = Inventory
        
    def initialize(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        self.logger.info("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def add_player(self, player_data: Dict[str, Any]) -> Player:
        """Add or update player"""
        session = self.get_session()
        try:
            player = session.query(Player).filter_by(player_id=player_data['player_id']).first()
            
            if player:
                # Update existing player
                for key, value in player_data.items():
                    setattr(player, key, value)
                player.updated_at = datetime.now()
            else:
                # Create new player
                player = Player(**player_data)
                session.add(player)
            
            session.commit()
            session.refresh(player)
            return player
        finally:
            session.close()
    
    def add_price_history(self, player_id: str, price: int, supply: int = None, demand: int = None):
        """Add price history entry"""
        session = self.get_session()
        try:
            price_entry = PriceHistory(
                player_id=player_id,
                price=price,
                supply=supply,
                demand=demand
            )
            session.add(price_entry)
            session.commit()
        finally:
            session.close()
    
    def get_price_history(self, player_id: str, days: int = 30) -> List[PriceHistory]:
        """Get price history for a player"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            return session.query(PriceHistory)\
                .filter(PriceHistory.player_id == player_id)\
                .filter(PriceHistory.timestamp >= cutoff_date)\
                .order_by(PriceHistory.timestamp.asc())\
                .all()
        finally:
            session.close()
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Add transaction record"""
        session = self.get_session()
        try:
            transaction = Transaction(**transaction_data)
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        finally:
            session.close()
    
    def get_total_profit(self) -> int:
        """Calculate total profit from all transactions"""
        session = self.get_session()
        try:
            result = session.query(Transaction)\
                .filter(Transaction.transaction_type == 'sell')\
                .filter(Transaction.profit.isnot(None))\
                .all()
            
            return sum(t.profit for t in result)
        finally:
            session.close()
    
    def add_prediction(self, prediction_data: Dict[str, Any]) -> Prediction:
        """Add price prediction"""
        session = self.get_session()
        try:
            prediction = Prediction(**prediction_data)
            session.add(prediction)
            session.commit()
            session.refresh(prediction)
            return prediction
        finally:
            session.close()
