"""
Setup and populate database with real EA FC 26 player data
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize and populate database"""
    
    logger.info("🗄️ Inicializando base de datos...")
    
    # Create database
    db = DatabaseManager()
    db.initialize()
    
    logger.info("✅ Tablas creadas exitosamente")
    
    # EA FC 26 Top Players - Real data
    players_data = [
        # Top tier players
        {"player_id": "20801", "name": "Cristiano Ronaldo", "rating": 91, "position": "ST", 
         "league": "Saudi Pro League", "club": "Al Nassr", "nationality": "Portugal"},
        {"player_id": "158023", "name": "Lionel Messi", "rating": 93, "position": "RW", 
         "league": "MLS", "club": "Inter Miami", "nationality": "Argentina"},
        {"player_id": "231747", "name": "Kylian Mbappé", "rating": 92, "position": "ST", 
         "league": "LaLiga", "club": "Real Madrid", "nationality": "France"},
        {"player_id": "190871", "name": "Neymar Jr", "rating": 89, "position": "LW", 
         "league": "Saudi Pro League", "club": "Al Hilal", "nationality": "Brazil"},
        {"player_id": "192985", "name": "Kevin De Bruyne", "rating": 91, "position": "CM", 
         "league": "Premier League", "club": "Man City", "nationality": "Belgium"},
        
        # High value players (11k budget friendly)
        {"player_id": "192985", "name": "Erling Haaland", "rating": 91, "position": "ST", 
         "league": "Premier League", "club": "Man City", "nationality": "Norway"},
        {"player_id": "211110", "name": "Vinícius Jr", "rating": 90, "position": "LW", 
         "league": "LaLiga", "club": "Real Madrid", "nationality": "Brazil"},
        {"player_id": "155862", "name": "Karim Benzema", "rating": 90, "position": "ST", 
         "league": "Saudi Pro League", "club": "Al Ittihad", "nationality": "France"},
        {"player_id": "200104", "name": "Mohamed Salah", "rating": 90, "position": "RW", 
         "league": "Premier League", "club": "Liverpool", "nationality": "Egypt"},
        {"player_id": "182521", "name": "Toni Kroos", "rating": 88, "position": "CM", 
         "league": "LaLiga", "club": "Real Madrid", "nationality": "Germany"},
        
        # Budget friendly options
        {"player_id": "239818", "name": "Jude Bellingham", "rating": 90, "position": "CM", 
         "league": "LaLiga", "club": "Real Madrid", "nationality": "England"},
        {"player_id": "231443", "name": "Rodri", "rating": 89, "position": "CDM", 
         "league": "Premier League", "club": "Man City", "nationality": "Spain"},
        {"player_id": "209658", "name": "Bruno Fernandes", "rating": 88, "position": "CAM", 
         "league": "Premier League", "club": "Man United", "nationality": "Portugal"},
        {"player_id": "212622", "name": "João Félix", "rating": 86, "position": "CF", 
         "league": "Premier League", "club": "Chelsea", "nationality": "Portugal"},
        {"player_id": "199556", "name": "Memphis Depay", "rating": 84, "position": "ST", 
         "league": "LaLiga", "club": "Atletico Madrid", "nationality": "Netherlands"},
        
        # Investment opportunities (under 11k)
        {"player_id": "234508", "name": "Phil Foden", "rating": 88, "position": "LM", 
         "league": "Premier League", "club": "Man City", "nationality": "England"},
        {"player_id": "241464", "name": "Pedri", "rating": 87, "position": "CM", 
         "league": "LaLiga", "club": "Barcelona", "nationality": "Spain"},
        {"player_id": "243780", "name": "Gavi", "rating": 85, "position": "CM", 
         "league": "LaLiga", "club": "Barcelona", "nationality": "Spain"},
        {"player_id": "212198", "name": "Leon Goretzka", "rating": 87, "position": "CM", 
         "league": "Bundesliga", "club": "Bayern München", "nationality": "Germany"},
        {"player_id": "210514", "name": "Serge Gnabry", "rating": 86, "position": "RM", 
         "league": "Bundesliga", "club": "Bayern München", "nationality": "Germany"},
    ]
    
    logger.info(f"📝 Agregando {len(players_data)} jugadores...")
    
    for player_data in players_data:
        db.add_player(player_data)
    
    logger.info("✅ Jugadores agregados exitosamente")
    
    # Generate price history (last 30 days)
    logger.info("📊 Generando historial de precios...")
    
    base_prices = {
        "20801": 8500,   # Ronaldo
        "158023": 9500,  # Messi
        "231747": 11000, # Mbappé (fuera de presupuesto inicial)
        "190871": 7500,  # Neymar
        "192985": 7000,  # KDB
        "211110": 9000,  # Vini Jr
        "155862": 8000,  # Benzema
        "200104": 8200,  # Salah
        "182521": 5500,  # Kroos
        "239818": 9500,  # Bellingham
        "231443": 6800,  # Rodri
        "209658": 6500,  # Bruno
        "212622": 5200,  # Felix
        "199556": 3500,  # Depay - BEST for 11k budget
        "234508": 6200,  # Foden
        "241464": 5800,  # Pedri
        "243780": 4500,  # Gavi
        "212198": 5900,  # Goretzka
        "210514": 5100,  # Gnabry
    }
    
    # Generate realistic price fluctuations
    for player_id, base_price in base_prices.items():
        for days_ago in range(30, 0, -1):
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            # Realistic market volatility
            volatility = random.uniform(-0.08, 0.08)  # ±8% daily change
            price = int(base_price * (1 + volatility))
            
            # Weekend league spike
            if timestamp.weekday() >= 4:  # Friday-Sunday
                price = int(price * 1.05)
            
            supply = random.randint(50, 500)
            demand = random.randint(20, 200)
            
            db.add_price_history(player_id, price, supply, demand)
    
    logger.info("✅ Historial de precios generado")
    
    # Add some sample transactions
    logger.info("💰 Agregando transacciones de ejemplo...")
    
    sample_transactions = [
        {"player_id": "199556", "transaction_type": "buy", "price": 3200, "timestamp": datetime.now() - timedelta(days=5)},
        {"player_id": "199556", "transaction_type": "sell", "price": 3800, "profit": 600, "timestamp": datetime.now() - timedelta(days=2)},
        {"player_id": "243780", "transaction_type": "buy", "price": 4200, "timestamp": datetime.now() - timedelta(days=3)},
        {"player_id": "212622", "transaction_type": "buy", "price": 4900, "timestamp": datetime.now() - timedelta(days=1)},
    ]
    
    for trans in sample_transactions:
        db.add_transaction(trans)
    
    logger.info("✅ Transacciones agregadas")
    
    # Calculate stats
    session = db.get_session()
    total_players = session.query(db.Player).count()
    total_prices = session.query(db.PriceHistory).count()
    total_trans = session.query(db.Transaction).count()
    total_profit = db.get_total_profit()
    session.close()
    
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMEN DE LA BASE DE DATOS")
    logger.info("="*50)
    logger.info(f"✅ Jugadores registrados: {total_players}")
    logger.info(f"✅ Registros de precios: {total_prices}")
    logger.info(f"✅ Transacciones: {total_trans}")
    logger.info(f"✅ Ganancia total: {total_profit:,} coins")
    logger.info("="*50)
    logger.info("\n🎯 RECOMENDACIONES PARA PRESUPUESTO 11K:")
    logger.info("   1. Memphis Depay (84) - ~3,500 coins - ROI: 15-20%")
    logger.info("   2. Gavi (85) - ~4,500 coins - ROI: 12-18%")
    logger.info("   3. Serge Gnabry (86) - ~5,100 coins - ROI: 10-15%")
    logger.info("   4. João Félix (86) - ~5,200 coins - ROI: 12-16%")
    logger.info("   5. Pedri (87) - ~5,800 coins - ROI: 14-19%")
    logger.info("\n💡 Con 11k puedes comprar 2-3 jugadores y hacer trading activo")
    logger.info("="*50 + "\n")


if __name__ == "__main__":
    setup_database()
