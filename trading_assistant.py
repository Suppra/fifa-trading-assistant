"""
Script de ejemplo para interactuar con el Trading Assistant
Muestra cómo registrar compras/ventas manualmente
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger
from src.database.db_manager import DatabaseManager
from src.market_analysis.analyzer import MarketAnalyzer
from src.prediction.price_predictor import PricePredictor
from src.trading.trading_engine import TradingEngine

def main():
    """Ejemplo de uso del bot"""
    
    print("=" * 70)
    print("🎮 EA FC 26 Trading Assistant - Modo Interactivo")
    print("=" * 70)
    print()
    
    # Inicializar componentes
    config = ConfigLoader()
    logger = setup_logger()
    db = DatabaseManager()
    db.initialize()
    
    analyzer = MarketAnalyzer(config, db)
    predictor = PricePredictor(config, db)
    engine = TradingEngine(config, db, analyzer, predictor)
    
    while True:
        print()
        print("📋 MENÚ PRINCIPAL")
        print("-" * 70)
        print("1. 📊 Ver recomendaciones de compra")
        print("2. 💰 Ver recomendaciones de venta")
        print("3. 🔮 Ver predicciones semanales")
        print("4. ✅ Registrar compra manual")
        print("5. ✅ Registrar venta manual")
        print("6. 📈 Ver estado del mercado")
        print("7. 💵 Ver ganancias totales")
        print("8. 🚪 Salir")
        print("-" * 70)
        
        choice = input("\nElige una opción (1-8): ").strip()
        
        if choice == "1":
            show_buy_recommendations(engine)
        elif choice == "2":
            show_sell_recommendations(engine)
        elif choice == "3":
            show_predictions(predictor)
        elif choice == "4":
            record_buy(engine)
        elif choice == "5":
            record_sell(engine)
        elif choice == "6":
            show_market_state(analyzer)
        elif choice == "7":
            show_total_profit(db)
        elif choice == "8":
            print("\n👋 ¡Gracias por usar EA FC 26 Trading Assistant!")
            print("💡 Recuerda: ¡Ejecuta los trades en el juego!")
            break
        else:
            print("\n❌ Opción no válida")

def show_buy_recommendations(engine):
    """Mostrar recomendaciones de compra"""
    print("\n" + "=" * 70)
    print("🛒 RECOMENDACIONES DE COMPRA")
    print("=" * 70)
    
    recs = engine._generate_buy_recommendations()
    
    if not recs:
        print("\n⚠️  No hay recomendaciones de compra en este momento")
        print("💡 Tip: El mercado puede estar caro. Espera a rewards o market crash.")
        return
    
    for i, rec in enumerate(recs[:10], 1):
        print(f"\n{i}. {rec.get('name', rec['player_id'])}")
        print(f"   ⭐ Rating: {rec.get('rating', 'N/A')}")
        print(f"   💵 Precio de compra: {rec['current_price']:,} coins")
        print(f"   📊 Ganancia potencial: {rec['profit_analysis']['profit_percentage']:.1f}%")
        print(f"   🎯 Confianza: {rec['prediction']['confidence']*100:.0f}%")
        print(f"   ⚠️  Riesgo: {rec['profit_analysis']['risk_level']}")
        print(f"   📈 Tendencia: {rec.get('trend', 'unknown')}")

def show_sell_recommendations(engine):
    """Mostrar recomendaciones de venta"""
    print("\n" + "=" * 70)
    print("💰 RECOMENDACIONES DE VENTA")
    print("=" * 70)
    
    if not engine.owned_cards:
        print("\n⚠️  No tienes cartas registradas en el bot")
        print("💡 Usa la opción 4 para registrar tus compras")
        return
    
    recs = engine._generate_sell_recommendations()
    
    if not recs:
        print("\n📊 Ninguna de tus cartas tiene buen momento de venta aún")
        print("💡 Tip: Mantén tus inversiones, los precios subirán")
        return
    
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. Player ID: {rec['player_id']}")
        print(f"   💵 Precio de venta: {rec['current_price']:,} coins")
        print(f"   💰 Ganancia: {rec['profit_after_tax']:+,} coins ({rec['profit_percentage']:+.1f}%)")
        print(f"   📅 Días en inventario: {(datetime.now() - rec['owned_card']['buy_date']).days}")
        print(f"   💡 Razón: {rec['reason']}")

def show_predictions(predictor):
    """Mostrar predicciones semanales"""
    print("\n" + "=" * 70)
    print("🔮 PREDICCIONES PARA LA PRÓXIMA SEMANA")
    print("=" * 70)
    
    predictions = predictor.predict_weekly_trends()
    
    if not predictions:
        print("\n⚠️  No hay suficientes datos para predicciones")
        print("💡 Tip: El bot necesita recopilar más datos históricos")
        return
    
    print("\n📈 Jugadores que SUBIRÁN:")
    rising = [p for p in predictions if p['predicted_price'] > p['current_price']][:5]
    
    for i, pred in enumerate(rising, 1):
        change = pred['predicted_price'] - pred['current_price']
        change_pct = (change / pred['current_price'] * 100)
        print(f"\n{i}. Player ID: {pred['player_id']}")
        print(f"   💵 Precio actual: {pred['current_price']:,} coins")
        print(f"   🔮 Precio predicho: {pred['predicted_price']:,} coins")
        print(f"   📈 Cambio: +{change:,} coins (+{change_pct:.1f}%)")
        print(f"   🎯 Confianza: {pred['confidence']*100:.0f}%")

def record_buy(engine):
    """Registrar una compra manual"""
    print("\n" + "=" * 70)
    print("✅ REGISTRAR COMPRA MANUAL")
    print("=" * 70)
    print("\n💡 Primero ejecuta la compra en EA FC 26, luego regístrala aquí")
    
    player_id = input("\n🔢 ID del jugador (de FUTBIN): ").strip()
    if not player_id:
        print("❌ ID inválido")
        return
    
    try:
        price = int(input("💵 Precio pagado: ").strip())
        if price <= 0:
            print("❌ Precio inválido")
            return
    except ValueError:
        print("❌ Precio debe ser un número")
        return
    
    print("\n📝 Estrategia usada:")
    print("1. Snipe (ganga rápida)")
    print("2. Mass Bidding (puja)")
    print("3. Investment (inversión)")
    print("4. Otra")
    
    strategy_choice = input("Elige (1-4): ").strip()
    strategies = {
        "1": "snipe",
        "2": "mass_bidding", 
        "3": "investment",
        "4": "manual"
    }
    strategy = strategies.get(strategy_choice, "manual")
    
    # Registrar
    success = engine.record_buy(player_id, price, strategy)
    
    if success:
        print("\n✅ ¡Compra registrada exitosamente!")
        print(f"💡 El bot monitoreará esta carta y te dirá cuándo vender")

def record_sell(engine):
    """Registrar una venta manual"""
    print("\n" + "=" * 70)
    print("✅ REGISTRAR VENTA MANUAL")
    print("=" * 70)
    
    if not engine.owned_cards:
        print("\n⚠️  No tienes cartas registradas para vender")
        return
    
    print("\n📦 Tus cartas:")
    for i, card in enumerate(engine.owned_cards, 1):
        print(f"{i}. Player ID: {card['player_id']} - Comprado por {card['buy_price']:,} coins")
    
    try:
        choice = int(input("\nElige número de carta (o 0 para cancelar): ").strip())
        if choice == 0:
            return
        if choice < 1 or choice > len(engine.owned_cards):
            print("❌ Opción inválida")
            return
        
        card = engine.owned_cards[choice - 1]
        player_id = card['player_id']
        
        sell_price = int(input(f"\n💵 Precio de venta para {player_id}: ").strip())
        if sell_price <= 0:
            print("❌ Precio inválido")
            return
        
        # Mostrar preview de ganancia
        ea_tax = 0.05
        profit = int(sell_price * (1 - ea_tax) - card['buy_price'])
        profit_pct = (profit / card['buy_price'] * 100)
        
        print(f"\n📊 Preview:")
        print(f"   Compra: {card['buy_price']:,} coins")
        print(f"   Venta: {sell_price:,} coins")
        print(f"   Tax (5%): -{int(sell_price * ea_tax):,} coins")
        print(f"   Ganancia: {profit:+,} coins ({profit_pct:+.1f}%)")
        
        confirm = input("\n¿Confirmar venta? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Venta cancelada")
            return
        
        success = engine.record_sell(player_id, sell_price)
        
        if success:
            print("\n✅ ¡Venta registrada exitosamente!")
            
    except ValueError:
        print("❌ Entrada inválida")

def show_market_state(analyzer):
    """Mostrar estado del mercado"""
    print("\n" + "=" * 70)
    print("📈 ESTADO DEL MERCADO")
    print("=" * 70)
    
    state = analyzer.get_market_state()
    
    print(f"\n📊 Estado general: {state['state'].upper()}")
    print(f"📈 Tendencia: {state['trend']}")
    print(f"⚡ Volatilidad: {state['volatility']}")
    print(f"💡 Acción recomendada: {state['recommended_action'].upper()}")

def show_total_profit(db):
    """Mostrar ganancias totales"""
    print("\n" + "=" * 70)
    print("💰 ESTADÍSTICAS DE GANANCIAS")
    print("=" * 70)
    
    total_profit = db.get_total_profit()
    
    print(f"\n💵 Ganancia total: {total_profit:+,} coins")
    
    if total_profit > 0:
        print("✅ ¡Excelente trabajo! Sigue así")
    elif total_profit < 0:
        print("📉 Pérdida temporal - sigue las recomendaciones del bot")
    else:
        print("📊 Sin operaciones completadas aún")

if __name__ == "__main__":
    from datetime import datetime
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
