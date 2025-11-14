"""
Price predictor for EA FC 26 Trading Bot
Uses machine learning to predict future player prices
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pickle
from pathlib import Path

class PricePredictor:
    """
    Predicts future player prices using historical data and ML models
    """
    
    def __init__(self, config, db_manager):
        """Initialize price predictor"""
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger("TradingBot.PricePredictor")
        
        # Get configuration
        self.model_type = config.get('prediction.model_type', 'prophet')
        self.training_window_days = config.get('prediction.training_window_days', 30)
        self.prediction_horizon_days = config.get('prediction.prediction_horizon_days', 7)
        
        self.models = {}
        self.models_dir = Path('models')
        self.models_dir.mkdir(exist_ok=True)
        
    def prepare_features(self, player_id: str) -> Optional[pd.DataFrame]:
        """
        Prepare features for prediction
        
        Args:
            player_id: Player ID
            
        Returns:
            DataFrame with features
        """
        # Get price history
        price_history = self.db_manager.get_price_history(
            player_id, 
            self.training_window_days
        )
        
        if not price_history or len(price_history) < 7:
            self.logger.warning(f"Insufficient data for player {player_id}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': p.timestamp,
                'price': p.price,
                'supply': p.supply,
                'demand': p.demand
            }
            for p in price_history
        ])
        
        # Add time-based features
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour'] = df['timestamp'].dt.hour
        df['week_of_year'] = df['timestamp'].dt.isocalendar().week
        
        # Add price-based features
        df['price_ma_7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['price_std_7'] = df['price'].rolling(window=7, min_periods=1).std()
        df['price_change'] = df['price'].diff()
        df['price_change_pct'] = df['price'].pct_change()
        
        return df
    
    def predict_price_simple(self, player_id: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """
        Simple prediction using moving average and trend analysis
        
        Args:
            player_id: Player ID
            days_ahead: Days into the future to predict
            
        Returns:
            Prediction data
        """
        df = self.prepare_features(player_id)
        
        if df is None or len(df) < 7:
            return None
        
        # Calculate trend
        recent_prices = df['price'].tail(7).values
        trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        # Current price and moving average
        current_price = df['price'].iloc[-1]
        moving_avg_7 = df['price_ma_7'].iloc[-1]
        
        # Simple prediction: current trend + moving average
        predicted_price = current_price + (trend * days_ahead)
        
        # Calculate confidence based on volatility
        volatility = df['price_std_7'].iloc[-1] / moving_avg_7 if moving_avg_7 > 0 else 1
        confidence = max(0, min(1, 1 - volatility))
        
        return {
            'player_id': player_id,
            'current_price': int(current_price),
            'predicted_price': int(predicted_price),
            'days_ahead': days_ahead,
            'confidence': confidence,
            'trend': 'rising' if trend > 0 else 'falling' if trend < 0 else 'stable',
            'prediction_date': datetime.now(),
            'target_date': datetime.now() + timedelta(days=days_ahead),
            'method': 'simple_trend'
        }
    
    def predict_price_prophet(self, player_id: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """
        Predict price using Facebook Prophet
        
        Args:
            player_id: Player ID
            days_ahead: Days into the future to predict
            
        Returns:
            Prediction data
        """
        try:
            from prophet import Prophet
        except ImportError:
            self.logger.warning("Prophet not installed, using simple prediction")
            return self.predict_price_simple(player_id, days_ahead)
        
        df = self.prepare_features(player_id)
        
        if df is None or len(df) < 14:
            return self.predict_price_simple(player_id, days_ahead)
        
        # Prepare data for Prophet
        prophet_df = pd.DataFrame({
            'ds': df['timestamp'],
            'y': df['price']
        })
        
        # Train model
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        model.fit(prophet_df)
        
        # Make prediction
        future = model.make_future_dataframe(periods=days_ahead)
        forecast = model.predict(future)
        
        predicted_price = forecast['yhat'].iloc[-1]
        lower_bound = forecast['yhat_lower'].iloc[-1]
        upper_bound = forecast['yhat_upper'].iloc[-1]
        
        # Calculate confidence
        range_pct = (upper_bound - lower_bound) / predicted_price if predicted_price > 0 else 1
        confidence = max(0, min(1, 1 - (range_pct / 2)))
        
        return {
            'player_id': player_id,
            'current_price': int(df['price'].iloc[-1]),
            'predicted_price': int(predicted_price),
            'lower_bound': int(lower_bound),
            'upper_bound': int(upper_bound),
            'days_ahead': days_ahead,
            'confidence': confidence,
            'prediction_date': datetime.now(),
            'target_date': datetime.now() + timedelta(days=days_ahead),
            'method': 'prophet'
        }
    
    def predict_price(self, player_id: str, days_ahead: int = None) -> Optional[Dict[str, Any]]:
        """
        Predict player price using configured model
        
        Args:
            player_id: Player ID
            days_ahead: Days into the future (uses config if None)
            
        Returns:
            Prediction data
        """
        if days_ahead is None:
            days_ahead = self.prediction_horizon_days
        
        self.logger.info(f"Predicting price for player {player_id}, {days_ahead} days ahead")
        
        # Choose prediction method
        if self.model_type == 'prophet':
            prediction = self.predict_price_prophet(player_id, days_ahead)
        else:
            prediction = self.predict_price_simple(player_id, days_ahead)
        
        # Save prediction to database
        if prediction:
            self.db_manager.add_prediction({
                'player_id': prediction['player_id'],
                'predicted_price': prediction['predicted_price'],
                'confidence': prediction['confidence'],
                'target_date': prediction['target_date'],
                'model_version': prediction['method']
            })
        
        return prediction
    
    def predict_weekly_trends(self) -> List[Dict[str, Any]]:
        """
        Predict weekly trends for top players
        
        Returns:
            List of weekly predictions
        """
        self.logger.info("Generating weekly trend predictions...")
        
        predictions = []
        
        # Get active players
        session = self.db_manager.get_session()
        try:
            from database.db_manager import Player
            players = session.query(Player).limit(50).all()
            
            for player in players:
                prediction = self.predict_price(player.player_id, days_ahead=7)
                if prediction:
                    predictions.append(prediction)
            
        finally:
            session.close()
        
        # Sort by potential profit
        predictions.sort(
            key=lambda x: x['predicted_price'] - x['current_price'], 
            reverse=True
        )
        
        return predictions
    
    def identify_investment_opportunities(self, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        Identify best investment opportunities based on predictions
        
        Args:
            min_confidence: Minimum prediction confidence
            
        Returns:
            List of investment opportunities
        """
        self.logger.info("Identifying investment opportunities...")
        
        predictions = self.predict_weekly_trends()
        
        opportunities = []
        min_profit_pct = self.config.get('trading.min_profit_percentage', 5)
        
        for pred in predictions:
            # EA FC 26 tax is 5%
            profit_after_tax = pred['predicted_price'] * 0.95 - pred['current_price']
            profit_pct = (profit_after_tax / pred['current_price'] * 100) if pred['current_price'] > 0 else 0
            
            if pred['confidence'] >= min_confidence and profit_pct >= min_profit_pct:
                opportunities.append({
                    **pred,
                    'profit_after_tax': int(profit_after_tax),
                    'profit_percentage': profit_pct,
                    'recommended_buy_price': pred['current_price'],
                    'recommended_sell_price': pred['predicted_price']
                })
        
        return opportunities
