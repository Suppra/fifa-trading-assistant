"""
Script de prueba para las nuevas features avanzadas
Testa: Tendencias históricas, Portfolio, Horas pico, LSTM, Real-time feed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import DatabaseManager
from app.services.futbin_service import FUTBINScraper
from app.services.historical_trends_service import HistoricalTrendsService
from app.services.portfolio_service import PortfolioService
from app.services.peak_hours_service import PeakHoursService
from app.services.lstm_predictor_service import LSTMPricePredictor
from app.services.realtime_feed_service import RealTimePriceFeed

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_historical_trends():
    """Test 1: Análisis de Tendencias Históricas"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: ANÁLISIS DE TENDENCIAS HISTÓRICAS")
    logger.info("="*60)
    
    try:
        db = DatabaseManager()
        trends_service = HistoricalTrendsService(db)
        
        # Obtener un jugador de ejemplo
        session = db.get_session()
        player = session.query(db.Player).filter(
            db.Player.rating >= 85
        ).first()
        session.close()
        
        if not player:
            logger.warning("No hay jugadores en la BD para probar")
            return
        
        logger.info(f"\n📊 Analizando tendencias de: {player.name} (Rating {player.rating})")
        
        # Analizar patrón semanal
        weekly_pattern = trends_service.analyze_weekly_pattern(player.player_id)
        
        if 'error' not in weekly_pattern:
            logger.info("\n✅ Patrón Semanal:")
            for day, stats in weekly_pattern.get('analysis', {}).items():
                logger.info(f"  {day}: {stats['avg_price']:,} coins (promedio)")
            
            rec = weekly_pattern.get('recommendation', {})
            logger.info(f"\n💡 Recomendación:")
            logger.info(f"  Comprar: {rec.get('buy_day')} ({rec.get('buy_avg'):,} coins)")
            logger.info(f"  Vender: {rec.get('sell_day')} ({rec.get('sell_avg'):,} coins)")
            logger.info(f"  Ganancia esperada: {rec.get('avg_profit'):,} coins ({rec.get('profit_pct')}%)")
        else:
            logger.warning(f"Error: {weekly_pattern['error']}")
        
        # Detectar tendencia
        trend = trends_service.detect_price_trends(player.player_id, days=7)
        
        if 'error' not in trend:
            logger.info(f"\n✅ Tendencia 7 días:")
            logger.info(f"  {trend['trend_color']} Tendencia: {trend['trend'].upper()}")
            logger.info(f"  Cambio: {trend['change']:,} coins ({trend['change_pct']:+.2f}%)")
            logger.info(f"  Volatilidad: {trend['volatility_pct']:.2f}%")
        
        logger.info("\n✅ Test de Tendencias Históricas COMPLETADO")
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")


def test_portfolio():
    """Test 2: Dashboard de Portfolio"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: DASHBOARD DE PORTFOLIO")
    logger.info("="*60)
    
    try:
        db = DatabaseManager()
        portfolio_service = PortfolioService(db)
        
        # Obtener resumen
        summary = portfolio_service.get_portfolio_summary()
        
        logger.info("\n💼 Resumen del Portfolio:")
        logger.info(f"  Inversión total: {summary['total_investment']:,} coins")
        logger.info(f"  Valor actual: {summary['total_value']:,} coins")
        logger.info(f"  Profit no realizado: {summary['unrealized_profit']:,} coins")
        logger.info(f"  Profit realizado: {summary['realized_profit']:,} coins")
        logger.info(f"  ROI: {summary['roi_pct']:.2f}%")
        logger.info(f"  Cartas owned: {summary['cards_owned']}")
        logger.info(f"  Cartas vendidas: {summary['cards_sold']}")
        
        # Top performers
        top = portfolio_service.get_top_performers(limit=5)
        
        if top:
            logger.info("\n🏆 Top 5 Inversiones (ROI):")
            for i, inv in enumerate(top, 1):
                logger.info(f"  {i}. {inv['player_name']}: {inv['roi_pct']:+.2f}% "
                           f"({inv['purchase_price']:,} → {inv['current_price']:,})")
        
        # Worst performers
        worst = portfolio_service.get_worst_performers(limit=3)
        
        if worst:
            logger.info("\n📉 Peores 3 Inversiones:")
            for i, inv in enumerate(worst, 1):
                logger.info(f"  {i}. {inv['player_name']}: {inv['roi_pct']:+.2f}% "
                           f"({inv['purchase_price']:,} → {inv['current_price']:,})")
        
        logger.info("\n✅ Test de Portfolio COMPLETADO")
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")


def test_peak_hours():
    """Test 3: Análisis de Horas Pico"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: ANÁLISIS DE HORAS PICO")
    logger.info("="*60)
    
    try:
        db = DatabaseManager()
        futbin = FUTBINScraper()
        peak_service = PeakHoursService(db, futbin)
        
        # Obtener recomendaciones generales
        recommendations = peak_service.get_hourly_recommendations()
        
        logger.info("\n⏰ Recomendaciones Horarias:")
        for rec in recommendations['recommendations']:
            logger.info(f"\n  {rec['time_range']}")
            logger.info(f"    Actividad: {rec['activity']}")
            logger.info(f"    Acción: {rec['action']}")
            logger.info(f"    Razón: {rec['reason']}")
        
        logger.info(f"\n💡 Mejores ventanas:")
        logger.info(f"  Comprar: {recommendations['best_buy_window']}")
        logger.info(f"  Vender: {recommendations['best_sell_window']}")
        
        # Analizar horas pico de un jugador (si hay datos)
        session = db.get_session()
        price_with_hour = session.query(db.PriceHistory).filter(
            db.PriceHistory.hour_of_day.isnot(None)
        ).first()
        session.close()
        
        if price_with_hour:
            analysis = peak_service.analyze_peak_hours(price_with_hour.player_id)
            
            if 'error' not in analysis:
                logger.info(f"\n✅ Análisis de horas pico:")
                rec = analysis['recommendation']
                logger.info(f"  Mejor hora compra: {rec['best_buy_hour']} ({rec['best_buy_price']:,} coins)")
                logger.info(f"  Mejor hora venta: {rec['best_sell_hour']} ({rec['best_sell_price']:,} coins)")
                logger.info(f"  Ganancia potencial: {rec['potential_profit']:,} coins ({rec['profit_pct']:.2f}%)")
        
        logger.info("\n✅ Test de Horas Pico COMPLETADO")
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")


def test_lstm():
    """Test 4: Deep Learning LSTM"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: DEEP LEARNING LSTM")
    logger.info("="*60)
    
    try:
        db = DatabaseManager()
        lstm_service = LSTMPricePredictor(db)
        
        # Verificar si TensorFlow está disponible
        from app.services.lstm_predictor_service import TENSORFLOW_AVAILABLE
        
        if not TENSORFLOW_AVAILABLE:
            logger.warning("⚠️ TensorFlow no instalado. Instalar con: pip install tensorflow")
            logger.info("✅ Test de LSTM SALTADO (TensorFlow no disponible)")
            return
        
        # Buscar jugador con suficientes datos
        session = db.get_session()
        from sqlalchemy import func
        
        # Jugador con más historial
        result = session.query(
            db.PriceHistory.player_id,
            func.count(db.PriceHistory.id).label('count')
        ).group_by(db.PriceHistory.player_id).order_by(
            func.count(db.PriceHistory.id).desc()
        ).first()
        
        if result and result.count >= 90:
            player_id = result.player_id
            
            player = session.query(db.Player).filter_by(player_id=player_id).first()
            logger.info(f"\n🤖 Entrenando modelo LSTM para: {player.name if player else player_id}")
            logger.info(f"   Datos disponibles: {result.count} días")
            
            # Entrenar modelo (solo 10 epochs para test rápido)
            train_result = lstm_service.train_model(player_id, epochs=10, batch_size=16)
            
            if 'error' not in train_result:
                logger.info(f"\n✅ Modelo entrenado:")
                logger.info(f"  Épocas: {train_result['epochs_trained']}")
                logger.info(f"  MAE entrenamiento: {train_result['train_mae']:.4f}")
                logger.info(f"  MAE validación: {train_result['test_mae']:.4f}")
                
                # Predecir precios
                pred_1_day = lstm_service.predict_price(player_id, days_ahead=1)
                pred_7_days = lstm_service.predict_price(player_id, days_ahead=7)
                
                if 'error' not in pred_1_day:
                    logger.info(f"\n📊 Predicciones:")
                    logger.info(f"  Precio actual: {pred_1_day['current_price']:,} coins")
                    logger.info(f"  En 1 día: {pred_1_day['final_prediction']:,} coins ({pred_1_day['change_pct']:+.2f}%)")
                
                if 'error' not in pred_7_days:
                    logger.info(f"  En 7 días: {pred_7_days['final_prediction']:,} coins ({pred_7_days['change_pct']:+.2f}%)")
            else:
                logger.warning(f"Error entrenando: {train_result['error']}")
        else:
            logger.warning("No hay suficientes datos históricos (mínimo 90 días)")
        
        session.close()
        logger.info("\n✅ Test de LSTM COMPLETADO")
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")


def test_realtime_feed():
    """Test 5: Real-Time Price Feed"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: REAL-TIME PRICE FEED")
    logger.info("="*60)
    
    try:
        db = DatabaseManager()
        futbin = FUTBINScraper()
        feed = RealTimePriceFeed(db, futbin)
        
        # Auto-poblar desde inventario
        feed.auto_populate_watchlist_from_inventory()
        
        stats = feed.get_stats()
        
        logger.info(f"\n⚡ Real-Time Feed:")
        logger.info(f"  Estado: {'🟢 Activo' if stats['is_running'] else '⚪ Detenido'}")
        logger.info(f"  Watchlist: {stats['watchlist_size']} jugadores")
        logger.info(f"  Intervalo: {stats['polling_interval']} segundos")
        logger.info(f"  Callbacks registrados: {stats['callbacks_registered']}")
        
        if stats['watchlist_size'] > 0:
            logger.info("\n📋 Jugadores en watchlist:")
            session = db.get_session()
            for i, player_id in enumerate(list(feed.watchlist)[:5], 1):
                player = session.query(db.Player).filter_by(player_id=player_id).first()
                if player:
                    logger.info(f"  {i}. {player.name} ({player.rating})")
            
            if stats['watchlist_size'] > 5:
                logger.info(f"  ... y {stats['watchlist_size'] - 5} más")
            
            session.close()
            
            logger.info("\n💡 Para probar el feed en vivo:")
            logger.info("  1. Ejecuta la app: python launcher.py")
            logger.info("  2. Ve al tab '⚡ Live Prices'")
            logger.info("  3. Click en '▶️ INICIAR FEED'")
            logger.info("  4. Observa los cambios en tiempo real")
        else:
            logger.info("\n⚠️ No hay jugadores en inventario para monitorear")
        
        logger.info("\n✅ Test de Real-Time Feed COMPLETADO")
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")


def main():
    """Ejecutar todos los tests"""
    logger.info("\n" + "="*60)
    logger.info("🧪 PRUEBAS DE FEATURES AVANZADAS")
    logger.info("="*60)
    logger.info("\nEste script prueba las 5 nuevas features:")
    logger.info("1. Análisis de Tendencias Históricas")
    logger.info("2. Dashboard de Portfolio")
    logger.info("3. Análisis de Horas Pico")
    logger.info("4. Deep Learning LSTM")
    logger.info("5. Real-Time Price Feed")
    
    # Ejecutar tests
    test_historical_trends()
    test_portfolio()
    test_peak_hours()
    test_lstm()
    test_realtime_feed()
    
    logger.info("\n" + "="*60)
    logger.info("✅ TODOS LOS TESTS COMPLETADOS")
    logger.info("="*60)
    logger.info("\nPara usar las features:")
    logger.info("  • Tendencias: Disponibles en tab 'Mercado' (próxima actualización)")
    logger.info("  • Portfolio: Visible en sidebar (inversión, profit, ROI)")
    logger.info("  • Horas Pico: Recomendaciones en 'Plan de Acción'")
    logger.info("  • LSTM: Predicciones avanzadas en 'Comprar'")
    logger.info("  • Live Prices: Tab '⚡ Live Prices' en la app")
    
    input("\n\nPresiona ENTER para salir...")


if __name__ == '__main__':
    main()
