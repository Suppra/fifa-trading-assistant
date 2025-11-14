"""
FUTBIN API Client - Uses actual FUTBIN endpoints
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class RealFUTBINClient:
    """
    Real FUTBIN API client using their actual API endpoints
    """
    
    def __init__(self):
        self.base_url = "https://www.futbin.com/26"
        self.api_url = "https://futbin.org/futbin/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.futbin.com/',
            'Origin': 'https://www.futbin.com'
        })
    
    def search_players_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Search players by name using FUTBIN search
        
        Args:
            name: Player name to search
            
        Returns:
            List of matching players
        """
        try:
            url = f"{self.base_url}/search"
            params = {'term': name}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching for '{name}': {e}")
            return []
    
    def get_popular_gold_players(self, min_rating: int = 83, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get popular gold players (most traded)
        
        Args:
            min_rating: Minimum player rating
            limit: Number of players to return
            
        Returns:
            List of player data
        """
        players_data = []
        
        # Popular budget players for trading (these are real commonly traded cards)
        popular_names = [
            "Depay",
            "Gavi", 
            "Pedri",
            "Gnabry",
            "Felix",
            "Goretzka",
            "Foden",
            "Bruno Fernandes",
            "Rodri",
            "Kroos",
            "Salah",
            "Benzema",
            "Neymar",
            "De Bruyne",
            "Vinicius",
            "Mbappe",
            "Messi",
            "Ronaldo",
            "Bellingham",
            "Williams"
        ]
        
        for name in popular_names[:limit]:
            print(f"  Buscando {name}...", end=' ')
            
            results = self.search_players_by_name(name)
            
            if results:
                # Get first result (usually the gold card)
                player = results[0]
                
                if player.get('rating', 0) >= min_rating:
                    players_data.append(player)
                    print(f"✅ {player.get('rating', '?')}")
                else:
                    print(f"⚠️ Rating {player.get('rating', '?')} < {min_rating}")
            else:
                print("❌")
            
            time.sleep(1)  # Rate limiting
        
        return players_data
    
    def get_player_price_trends(self, player_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get price trends for a player
        
        Args:
            player_id: Player ID
            days: Number of days of history
            
        Returns:
            Price trend data
        """
        try:
            url = f"{self.base_url}/player/{player_id}/prices"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting price trends for {player_id}: {e}")
            return {}


class SimplePriceGenerator:
    """
    Generate realistic prices based on player ratings
    Use this when FUTBIN is unavailable
    """
    
    def __init__(self):
        # Base prices by rating (in coins)
        self.base_prices = {
            82: 1200,
            83: 1800,
            84: 3500,
            85: 5500,
            86: 8500,
            87: 12000,
            88: 18000,
            89: 28000,
            90: 45000,
            91: 75000,
            92: 120000,
            93: 200000,
        }
    
    def generate_price(self, rating: int, position: str = None, league: str = None) -> int:
        """
        Generate realistic price based on rating and attributes
        
        Args:
            rating: Player rating
            position: Player position (ST, CAM more expensive)
            league: Player league (Premier League +20%, etc.)
            
        Returns:
            Estimated price in coins
        """
        # Get base price
        base = self.base_prices.get(rating, 1000)
        
        # Position multiplier
        position_mult = 1.0
        if position in ['ST', 'CF', 'CAM', 'LW', 'RW']:
            position_mult = 1.2
        elif position in ['CB', 'GK']:
            position_mult = 0.8
        
        # League multiplier
        league_mult = 1.0
        if league and 'Premier League' in league:
            league_mult = 1.3
        elif league and 'LaLiga' in league:
            league_mult = 1.2
        
        # Add some randomness (±15%)
        import random
        randomness = random.uniform(0.85, 1.15)
        
        price = int(base * position_mult * league_mult * randomness)
        
        return price
    
    def generate_prices_for_database(self, db_manager) -> int:
        """
        Generate realistic prices for all players in database
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Number of prices generated
        """
        session = db_manager.get_session()
        players = session.query(db_manager.Player).all()
        
        count = 0
        for player in players:
            price = self.generate_price(
                player.rating,
                player.position,
                player.league
            )
            
            db_manager.add_price_history(
                player.player_id,
                price
            )
            
            count += 1
            print(f"  {player.name} ({player.rating}): {price:,} coins")
        
        session.close()
        return count


def test_real_futbin():
    """Test the real FUTBIN client"""
    print("\n" + "="*70)
    print("  🔍 PROBANDO FUTBIN API REAL")
    print("="*70 + "\n")
    
    client = RealFUTBINClient()
    
    # Test search
    print("Buscando 'Depay'...")
    results = client.search_players_by_name("Depay")
    
    if results:
        print(f"\n✅ Encontrados {len(results)} resultados:")
        for i, player in enumerate(results[:3], 1):
            print(f"{i}. {player.get('name', 'Unknown')} - Rating: {player.get('rating', '?')}")
    else:
        print("❌ No se encontraron resultados")
    
    print("\n" + "="*70 + "\n")


def generate_realistic_prices():
    """Generate realistic prices for all database players"""
    print("\n" + "="*70)
    print("  💰 GENERANDO PRECIOS REALISTAS")
    print("="*70 + "\n")
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from src.database.db_manager import DatabaseManager
    
    db = DatabaseManager()
    generator = SimplePriceGenerator()
    
    count = generator.generate_prices_for_database(db)
    
    print(f"\n✅ Generados {count} precios")
    print("="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_real_futbin()
    else:
        generate_realistic_prices()
