"""
Update player prices from FUTBIN
Run this to refresh prices with real data
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager
from src.data_collection.futbin_scraper import FUTBINScraper, FUTBINAPIClient
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_prices_from_futbin():
    """Update all player prices from FUTBIN"""
    
    print("\n" + "="*70)
    print("  🌐 ACTUALIZANDO PRECIOS DESDE FUTBIN")
    print("="*70 + "\n")
    
    # Initialize database
    db = DatabaseManager()
    
    # Get all players
    session = db.get_session()
    players = session.query(db.Player).all()
    session.close()
    
    if not players:
        print("❌ No hay jugadores en la base de datos")
        print("   Ejecuta primero: py setup_database.py")
        return
    
    print(f"📊 Jugadores en DB: {len(players)}")
    print(f"⏰ Esto tomará aproximadamente {len(players) * 2} segundos...\n")
    
    # Initialize scraper
    scraper = FUTBINScraper()
    
    updated_count = 0
    failed_count = 0
    
    for i, player in enumerate(players, 1):
        print(f"[{i}/{len(players)}] Actualizando {player.name} ({player.player_id})...", end=' ')
        
        try:
            # Get latest price from FUTBIN
            price_data = scraper.get_player_price(player.player_id)
            
            if price_data and price_data['price'] > 0:
                # Add to price history
                db.add_price_history(
                    player.player_id,
                    price_data['price']
                )
                
                print(f"✅ {price_data['price']:,} coins")
                updated_count += 1
            else:
                print("❌ Sin datos")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1
    
    print("\n" + "="*70)
    print("  📊 RESUMEN DE ACTUALIZACIÓN")
    print("="*70)
    print(f"✅ Actualizados: {updated_count}")
    print(f"❌ Fallidos: {failed_count}")
    print(f"📈 Tasa de éxito: {(updated_count/(updated_count+failed_count)*100):.1f}%")
    print("="*70 + "\n")
    
    if updated_count > 0:
        print("🎯 MEJORES OPORTUNIDADES ACTUALIZADAS:")
        print("-" * 70)
        
        # Get updated recommendations
        session = db.get_session()
        
        for player in players[:5]:
            latest_price = session.query(db.PriceHistory)\
                .filter(db.PriceHistory.player_id == player.player_id)\
                .order_by(db.PriceHistory.timestamp.desc())\
                .first()
            
            if latest_price:
                profit = int(latest_price.price * 0.12)
                roi = int((profit / latest_price.price) * 100)
                
                print(f"  {player.name} ({player.rating})")
                print(f"    Precio: {latest_price.price:,} coins")
                print(f"    Ganancia estimada: +{profit:,} coins ({roi}% ROI)")
                print()
        
        session.close()
        print("="*70)


def quick_update_top_5():
    """Quick update for top 5 budget-friendly players"""
    
    print("\n" + "="*70)
    print("  ⚡ ACTUALIZACIÓN RÁPIDA - TOP 5 JUGADORES")
    print("="*70 + "\n")
    
    db = DatabaseManager()
    scraper = FUTBINScraper()
    
    # Top 5 budget-friendly players
    top_players = [
        ("199556", "Memphis Depay"),
        ("243780", "Gavi"),
        ("210514", "Serge Gnabry"),
        ("212622", "João Félix"),
        ("241464", "Pedri"),
    ]
    
    for player_id, name in top_players:
        print(f"Actualizando {name}...", end=' ')
        
        try:
            price_data = scraper.get_player_price(player_id)
            
            if price_data and price_data['price'] > 0:
                db.add_price_history(player_id, price_data['price'])
                
                profit = int(price_data['price'] * 0.12)
                roi = int((profit / price_data['price']) * 100)
                
                print(f"✅ {price_data['price']:,} coins (+{profit:,} | {roi}% ROI)")
            else:
                print("❌ Sin datos")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*70 + "\n")


def test_futbin_connection():
    """Test FUTBIN connection with a single player"""
    
    print("\n" + "="*70)
    print("  🔍 TEST DE CONEXIÓN FUTBIN")
    print("="*70 + "\n")
    
    scraper = FUTBINScraper()
    
    test_players = [
        ("199556", "Memphis Depay"),
        ("243780", "Gavi"),
        ("20801", "Cristiano Ronaldo"),
    ]
    
    print("Probando con 3 jugadores populares...\n")
    
    for player_id, name in test_players:
        print(f"Buscando {name} ({player_id})...", end=' ')
        
        try:
            data = scraper.get_player_price(player_id)
            
            if data:
                print(f"✅")
                print(f"  Nombre: {data['name']}")
                print(f"  Rating: {data['rating']}")
                print(f"  Posición: {data['position']}")
                print(f"  Precio: {data['price']:,} coins")
                print()
            else:
                print("❌ No se encontró")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_futbin_connection()
        elif command == "quick":
            quick_update_top_5()
        elif command == "full":
            update_prices_from_futbin()
        else:
            print("Uso: py update_prices.py [test|quick|full]")
    else:
        # Default: quick update
        quick_update_top_5()
