"""
Price predictor for EA FC 26 Trading Bot
Uses advanced machine learning to predict future player prices

Features:
- Multiple ML models (Prophet, Random Forest, XGBoost)
- SBC-aware predictions
- Event-based predictions (Weekend League, TOTW, Promos)
- Anomaly detection
- Confidence intervals
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, time as datetime_time
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PricePredictor:
    """
    Advanced price predictor with ML models and market intelligence
    """
    
    def __init__(self, config, db_manager):
        """Initialize enhanced price predictor"""
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger("TradingBot.PricePredictor")
        
        # Get configuration
        self.model_type = config.get('prediction.model_type', 'enhanced')
        self.training_window_days = config.get('prediction.training_window_days', 30)
        self.prediction_horizon_days = config.get('prediction.prediction_horizon_days', 7)
        self.enable_sbc_features = config.get('prediction.enable_sbc_features', True)
        self.enable_event_features = config.get('prediction.enable_event_features', True)
        self.anomaly_threshold = config.get('prediction.anomaly_threshold', 2.5)
        
        self.models = {}
        self.models_dir = Path('models')
        self.models_dir.mkdir(exist_ok=True)
        
        # Event calendar
        self.events = self._init_event_calendar()
    
    def _init_event_calendar(self) -> Dict[str, List[datetime]]:
        """Initialize EA FC 26 event calendar"""
        current_year = datetime.now().year
        
        return {
            'weekend_league': self._get_weekend_league_dates(current_year),
            'totw': self._get_totw_dates(current_year),
            'toty': [datetime(current_year, 1, 12), datetime(current_year, 1, 26)],
            'tots': [datetime(current_year, 4, 26), datetime(current_year, 6, 7)],
            'futties': [datetime(current_year, 7, 14), datetime(current_year, 8, 18)],
            'rttk': [datetime(current_year, 10, 6), datetime(current_year, 10, 20)],
            'black_friday': [datetime(current_year, 11, 24), datetime(current_year, 11, 28)],
        }
    
    def _get_weekend_league_dates(self, year: int) -> List[datetime]:
        """Generate Weekend League dates (Fridays)"""
        dates = []
        start_date = datetime(year, 9, 1)
        end_date = datetime(year + 1, 6, 30)
        
        current = start_date
        while current <= end_date:
            if current.weekday() == 4:  # Friday
                dates.append(current)
            current += timedelta(days=1)
        
        return dates
    
    def _get_totw_dates(self, year: int) -> List[datetime]:
        """Generate TOTW dates (Wednesdays)"""
        dates = []
        start_date = datetime(year, 9, 1)
        end_date = datetime(year + 1, 6, 30)
        
        current = start_date
        while current <= end_date:
            if current.weekday() == 2:  # Wednesday
                dates.append(current)
            current += timedelta(days=1)
        
        return dates
    
    def _get_active_events(self, date: datetime) -> List[str]:
        """Get active events for a date"""
        active = []
        
        for event_name, event_dates in self.events.items():
            for event_date in event_dates:
                if abs((date - event_date).days) <= 3:
                    active.append(event_name)
        
        return active
    
    def _get_sbc_impact_score(self, player_rating: int, player_position: str) -> float:
        """Calculate SBC impact score"""
        try:
            from app.utils.sbc_tracker import SBCTracker
            
            sbc_tracker = SBCTracker()
            active_sbcs = sbc_tracker.get_active_sbcs()
            
            if not active_sbcs:
                return 0.0
            
            impact_score = 0.0
            
            for sbc in active_sbcs:
                requirements = sbc.get('requirements', {})
                min_rating = requirements.get('min_rating', 0)
                
                if isinstance(min_rating, int):
                    if player_rating == min_rating or player_rating == min_rating + 1:
                        impact_score += 0.3
                    elif abs(player_rating - min_rating) <= 2:
                        impact_score += 0.1
            
            return min(impact_score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Error calculating SBC impact: {e}")
            return 0.0
    
    def detect_price_anomaly(self, player_id: str, current_price: int) -> Dict[str, Any]:
        """Detect price anomalies (crash/spike)"""
        try:
            price_history = self.db_manager.get_price_history(player_id, 30)
            
            if not price_history or len(price_history) < 14:
                return {'is_anomaly': False, 'type': None, 'severity': 0}
            
            prices = [p.price for p in price_history]
            mean_price = np.mean(prices)
            std_price = np.std(prices)
            
            if std_price == 0:
                return {'is_anomaly': False, 'type': None, 'severity': 0}
            
            z_score = (current_price - mean_price) / std_price
            is_anomaly = abs(z_score) > self.anomaly_threshold
            anomaly_type = 'spike' if z_score > 0 else 'crash' if is_anomaly else None
            severity = min(abs(z_score) / 3, 1.0) if is_anomaly else 0
            
            return {
                'is_anomaly': is_anomaly,
                'type': anomaly_type,
                'severity': severity,
                'z_score': z_score,
                'mean_price': int(mean_price),
                'std_price': int(std_price)
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting anomaly: {e}")
            return {'is_anomaly': False, 'type': None, 'severity': 0}
        
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
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add price-based features
        df['price_ma_7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['price_ma_14'] = df['price'].rolling(window=14, min_periods=1).mean()
        df['price_std_7'] = df['price'].rolling(window=7, min_periods=1).std()
        df['price_change'] = df['price'].diff()
        df['price_change_pct'] = df['price'].pct_change()
        df['price_momentum'] = df['price'].diff(periods=3)  # 3-day momentum
        
        # Volatility features
        df['volatility_7'] = df['price'].rolling(window=7).std() / df['price'].rolling(window=7).mean()
        df['price_range_7'] = (df['price'].rolling(window=7).max() - df['price'].rolling(window=7).min()) / df['price']
        
        # Supply/demand features
        if 'supply' in df.columns and 'demand' in df.columns:
            df['supply_demand_ratio'] = df['supply'] / (df['demand'] + 1)
            df['market_pressure'] = (df['demand'] - df['supply']) / (df['demand'] + df['supply'] + 1)
        
        # Event-based features (if enabled)
        if self.enable_event_features:
            df['is_weekend_league'] = df['timestamp'].apply(
                lambda x: 1 if 'weekend_league' in self._get_active_events(x) else 0
            )
            df['is_totw'] = df['timestamp'].apply(
                lambda x: 1 if 'totw' in self._get_active_events(x) else 0
            )
            df['event_count'] = df['timestamp'].apply(
                lambda x: len(self._get_active_events(x))
            )
        
        # SBC-based features (if enabled)
        if self.enable_sbc_features:
            try:
                # Get player info
                session = self.db_manager.get_session()
                from app.models.database import Player
                player = session.query(Player).filter(Player.player_id == player_id).first()
                
                if player:
                    sbc_impact = self._get_sbc_impact_score(player.rating, player.position)
                    df['sbc_impact'] = sbc_impact
                
                session.close()
            except Exception as e:
                self.logger.warning(f"Could not add SBC features: {e}")
                df['sbc_impact'] = 0.0
        
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
    
    def predict_price_enhanced(self, player_id: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """
        Enhanced prediction using multiple features and ensemble approach
        
        Args:
            player_id: Player ID
            days_ahead: Days into the future to predict
            
        Returns:
            Enhanced prediction data
        """
        df = self.prepare_features(player_id)
        
        if df is None or len(df) < 14:
            return self.predict_price_simple(player_id, days_ahead)
        
        # Get current state
        current_price = df['price'].iloc[-1]
        
        # Get player info for SBC and event analysis
        session = self.db_manager.get_session()
        try:
            from app.models.database import Player
            player = session.query(Player).filter(Player.player_id == player_id).first()
            
            if not player:
                return self.predict_price_simple(player_id, days_ahead)
            
            # Multiple prediction methods
            predictions = []
            
            # 1. Trend-based prediction
            recent_prices = df['price'].tail(14).values
            trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            trend_pred = current_price + (trend * days_ahead)
            predictions.append(trend_pred)
            
            # 2. Moving average prediction
            ma_7 = df['price_ma_7'].iloc[-1]
            ma_14 = df['price_ma_14'].iloc[-1]
            ma_pred = (ma_7 * 0.7 + ma_14 * 0.3)
            predictions.append(ma_pred)
            
            # 3. Momentum-based prediction
            momentum = df['price_momentum'].iloc[-1]
            momentum_pred = current_price + (momentum * days_ahead / 3)
            predictions.append(momentum_pred)
            
            # 4. SBC-adjusted prediction
            sbc_impact = self._get_sbc_impact_score(player.rating, player.position)
            sbc_multiplier = 1 + (sbc_impact * 0.15)  # Up to 15% increase
            sbc_pred = current_price * sbc_multiplier
            predictions.append(sbc_pred)
            
            # 5. Event-adjusted prediction
            target_date = datetime.now() + timedelta(days=days_ahead)
            active_events = self._get_active_events(target_date)
            event_multiplier = 1 + (len(active_events) * 0.05)  # 5% per event
            event_pred = current_price * event_multiplier
            predictions.append(event_pred)
            
            # Ensemble prediction (weighted average)
            weights = [0.25, 0.20, 0.15, 0.25, 0.15]  # Trend and SBC weighted more
            predicted_price = sum(p * w for p, w in zip(predictions, weights))
            
            # Calculate confidence
            volatility = df['volatility_7'].iloc[-1] if 'volatility_7' in df.columns else 0.1
            confidence = max(0.4, min(0.95, 1 - volatility))
            
            # Adjust confidence based on data quality
            if len(df) < 21:
                confidence *= 0.8
            
            # Detect anomaly
            anomaly = self.detect_price_anomaly(player_id, current_price)
            
            # Determine trend
            if trend > 50:
                trend_direction = 'strongly_rising'
            elif trend > 10:
                trend_direction = 'rising'
            elif trend < -50:
                trend_direction = 'strongly_falling'
            elif trend < -10:
                trend_direction = 'falling'
            else:
                trend_direction = 'stable'
            
            # Generate recommendation
            price_change_pct = ((predicted_price - current_price) / current_price) * 100
            
            if anomaly['is_anomaly'] and anomaly['type'] == 'crash':
                recommendation = 'BUY'  # Buy the dip
                reason = f"Precio en crash ({anomaly['severity']*100:.0f}% anomalía)"
            elif anomaly['is_anomaly'] and anomaly['type'] == 'spike':
                recommendation = 'SELL'  # Sell the spike
                reason = f"Precio en spike ({anomaly['severity']*100:.0f}% anomalía)"
            elif price_change_pct > 5:
                recommendation = 'BUY'
                reason = f"Predicción de subida ({price_change_pct:.1f}%)"
            elif price_change_pct < -5:
                recommendation = 'SELL'
                reason = f"Predicción de bajada ({price_change_pct:.1f}%)"
            else:
                recommendation = 'HOLD'
                reason = "Precio estable esperado"
            
            # Add SBC/Event context
            if sbc_impact > 0.2:
                reason += f" | SBC Impact: {sbc_impact*100:.0f}%"
            if active_events:
                reason += f" | Eventos: {', '.join(active_events)}"
            
            return {
                'player_id': player_id,
                'current_price': int(current_price),
                'predicted_price': int(predicted_price),
                'price_change': int(predicted_price - current_price),
                'price_change_pct': price_change_pct,
                'days_ahead': days_ahead,
                'confidence': confidence,
                'trend': trend_direction,
                'trend_value': trend,
                'recommendation': recommendation,
                'reason': reason,
                'sbc_impact': sbc_impact,
                'active_events': active_events,
                'anomaly': anomaly,
                'prediction_date': datetime.now(),
                'target_date': target_date,
                'method': 'enhanced_ensemble'
            }
            
        except Exception as e:
            self.logger.error(f"Error in enhanced prediction: {e}")
            return self.predict_price_simple(player_id, days_ahead)
        finally:
            session.close()
    
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
        if self.model_type == 'enhanced':
            prediction = self.predict_price_enhanced(player_id, days_ahead)
        elif self.model_type == 'prophet':
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
