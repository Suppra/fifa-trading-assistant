"""
Market scraper for EA FC 26
Collects player data and prices from FUTBIN API
"""

import logging
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

class MarketScraper:
    """
    Scrapes market data from FUTBIN API
    Provides real-time price data for EA FC 26 players
    """
    
    def __init__(self, config, db_manager):
        """Initialize market scraper"""
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger("TradingBot.MarketScraper")
        
        # Get configuration
        self.top_players_count = config.get('market_analysis.top_players_count', 100)
        self.leagues = config.get('market_analysis.leagues', [])
        self.min_rating = config.get('market_analysis.min_rating', 75)
        
        # FUTBIN API configuration
        self.futbin_base_url = "https://www.futbin.com/26/playerPrices"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        # Cache to avoid excessive requests
        self.price_cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def _get_futbin_prices(self, player_ids: List[str]) -> Dict[str, Any]:
        """
        Get prices from FUTBIN API
        
        Args:
            player_ids: List of player IDs
            
        Returns:
            Dictionary with price data
        """
        try:
            # FUTBIN uses comma-separated player IDs
            ids_param = ','.join(player_ids)
            url = f"{self.futbin_base_url}?player={ids_param}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"FUTBIN API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching FUTBIN prices: {e}")
            return {}
    
    def scrape_player_prices(self, player_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape current prices for players from FUTBIN
        
        Args:
            player_ids: List of player IDs to scrape (None for top players)
            
        Returns:
            List of player price data
        """
        self.logger.info("Starting price scraping from FUTBIN...")
        
        if not player_ids:
            # Get top meta players (hardcoded list of popular players)
            player_ids = self._get_popular_player_ids()
        
        scraped_data = []
        
        # Process in batches to avoid rate limiting
        batch_size = 30
        for i in range(0, len(player_ids), batch_size):
            batch = player_ids[i:i + batch_size]
            
            # Check cache first
            now = datetime.now()
            cached_batch = []
            uncached_batch = []
            
            for pid in batch:
                if pid in self.price_cache:
                    cache_time, cache_data = self.price_cache[pid]
                    if (now - cache_time).seconds < self.cache_duration:
                        cached_batch.append(cache_data)
                        continue
                uncached_batch.append(pid)
            
            # Fetch uncached data
            if uncached_batch:
                prices = self._get_futbin_prices(uncached_batch)
                
                for pid in uncached_batch:
                    if pid in prices:
                        price_data = prices[pid]
                        player_data = {
                            'player_id': pid,
                            'name': price_data.get('name', f'Player {pid}'),
                            'rating': price_data.get('rating', 0),
                            'position': price_data.get('position', 'Unknown'),
                            'league': price_data.get('league', 'Unknown'),
                            'club': price_data.get('club', 'Unknown'),
                            'nationality': price_data.get('nation', 'Unknown'),
                            'current_price': price_data.get('prices', {}).get('pc', {}).get('LCPrice', 0),
                            'supply': price_data.get('supply', 0),
                            'demand': 0  # FUTBIN doesn't provide demand directly
                        }
                        
                        # Cache the data
                        self.price_cache[pid] = (now, player_data)
                        scraped_data.append(player_data)
            
            # Add cached data
            scraped_data.extend(cached_batch)
            
            # Respect rate limits
            if i + batch_size < len(player_ids):
                time.sleep(2)
        
        self.logger.info(f"Scraped prices for {len(scraped_data)} players")
        return scraped_data
    
    def _get_popular_player_ids(self) -> List[str]:
        """
        Get list of popular/meta player IDs for EA FC 26
        Enfocado en jugadores de bajo presupuesto (< 10k coins)
        
        Returns:
            List of player IDs
        """
        # JUGADORES RENTABLES PARA BAJO PRESUPUESTO (Rating 82-84)
        # Estos son jugadores comúnmente usados en SBCs y con buena rotación
        
        popular_players = [
            # Premier League (Siempre demandados)
            "239085",  # Erling Haaland - 89 (si baja de 11k en crash)
            "231747",  # Kylian Mbappé - 91 (monitor para crash)
            "192985",  # Kevin De Bruyne - 91
            "188567",  # Cristiano Ronaldo - 88
            "158023",  # Lionel Messi - 88
            
            # Rating 84 (MUY RENTABLES para SBCs - presupuesto perfecto)
            "200104",  # Casemiro - 84
            "201535",  # Ederson - 85
            "212198",  # Bruno Fernandes - 88
            "202126",  # Rúben Dias - 88
            "181291",  # Toni Kroos - 86
            
            # Rating 83 (Bajo presupuesto, alta rotación)
            "246104",  # Nico Williams - 83
            "251805",  # Pedri - 85
            "243812",  # Tchouaméni - 85
            "234906",  # Frenkie de Jong - 87
            "225508",  # Trent Alexander-Arnold - 87
            
            # Rating 82 (Inicio perfecto con 11k)
            "224293",  # Jamal Musiala - 84
            "256630",  # Jude Bellingham - 90
            "247695",  # Vinícius Jr - 90
            "241096",  # João Cancelo - 84
        ]
        
        self.logger.info(f"Monitoring {len(popular_players)} budget-friendly players")
        return popular_players
    
    def scrape_top_players(self) -> List[Dict[str, Any]]:
        """
        Scrape data for top players based on configuration
        Uses FUTBIN's most popular players
        
        Returns:
            List of top player data
        """
        self.logger.info(f"Scraping top {self.top_players_count} players...")
        
        # Get popular players from database or default list
        session = self.db_manager.get_session()
        try:
            from database.db_manager import Player, PriceHistory
            
            # Get players we've been tracking
            existing_players = session.query(Player).all()
            
            if existing_players:
                player_ids = [p.player_id for p in existing_players[:self.top_players_count]]
                players = self.scrape_player_prices(player_ids)
            else:
                # First run - use popular players
                players = self._scrape_popular_by_rating()
            
            return players[:self.top_players_count]
            
        finally:
            session.close()
    
    def _scrape_popular_by_rating(self) -> List[Dict[str, Any]]:
        """
        Scrape popular players by rating ranges (83-86 for SBCs)
        
        Returns:
            List of player data
        """
        # Estos ratings son muy demandados para SBCs
        target_ratings = self.config.get('market_analysis.focus_ratings', [83, 84, 85, 86])
        
        self.logger.info(f"Focusing on ratings: {target_ratings}")
        
        # En una implementación real, consultarías FUTBIN por rating
        # Por ahora retornamos lista vacía
        return []
    
    def scrape_special_cards(self) -> List[Dict[str, Any]]:
        """
        Scrape special cards (TOTW, Icons, etc.)
        
        Returns:
            List of special card data
        """
        self.logger.info("Scraping special cards...")
        
        # FUTBIN tiene endpoints específicos para:
        # - TOTW: /26/totw
        # - Icons: /26/icons
        # - Heroes: /26/heroes
        
        special_cards = []
        
        try:
            # Scrape TOTW
            totw_url = "https://www.futbin.com/26/totw"
            # Aquí iría la lógica de scraping HTML o API
            
            self.logger.info("Special cards scraping requires HTML parsing")
            self.logger.info("Tip: Check FUTBIN manually for current TOTW and special cards")
            
        except Exception as e:
            self.logger.error(f"Error scraping special cards: {e}")
        
        return special_cards
    
    def get_player_details(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific player
        
        Args:
            player_id: Player ID
            
        Returns:
            Player details or None
        """
        # TODO: Implement player detail retrieval
        
        return None
    
    def update_market_data(self):
        """
        Main method to update all market data
        Should be called periodically
        """
        self.logger.info("=" * 50)
        self.logger.info("Updating market data...")
        
        try:
            # Scrape top players
            players = self.scrape_top_players()
            
            # Save to database
            for player_data in players:
                # Save player info
                self.db_manager.add_player({
                    'player_id': player_data['player_id'],
                    'name': player_data['name'],
                    'rating': player_data['rating'],
                    'position': player_data.get('position'),
                    'league': player_data.get('league'),
                    'club': player_data.get('club'),
                    'nationality': player_data.get('nationality')
                })
                
                # Save price history
                self.db_manager.add_price_history(
                    player_id=player_data['player_id'],
                    price=player_data['current_price'],
                    supply=player_data.get('supply'),
                    demand=player_data.get('demand')
                )
            
            self.logger.info(f"Updated data for {len(players)} players")
            
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}", exc_info=True)
        
        self.logger.info("=" * 50)
    
    def get_player_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a player by name using FUTBIN
        
        Args:
            name: Player name to search
            
        Returns:
            Player data or None
        """
        try:
            # FUTBIN search endpoint
            search_url = f"https://www.futbin.com/search?year=26&term={name}"
            
            self.logger.info(f"Searching for player: {name}")
            self.logger.info(f"Manual search: {search_url}")
            
            # Para búsquedas, es más fácil dirigir al usuario a FUTBIN
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching player: {e}")
            return None
