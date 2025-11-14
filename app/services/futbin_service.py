"""
FUTBIN scraper optimizado para precios de PC en EA FC 26
Extrae precios reales de jugadores desde FUTBIN
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FUTBINScraper:
    """
    Scraper de FUTBIN para precios de PC en EA FC 26
    """
    
    def __init__(self):
        self.base_url = "https://www.futbin.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
    def search_player(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca un jugador por nombre y obtiene su precio de PC
        
        Args:
            player_name: Nombre del jugador (ej: "Messi", "Ronaldo")
            
        Returns:
            Diccionario con datos del jugador y precio PC
        """
        try:
            # Búsqueda en FUTBIN
            search_url = f"{self.base_url}/26/players?page=1&search={player_name}"
            logger.info(f"🔍 Buscando '{player_name}' en FUTBIN...")
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Error en búsqueda: {response.status_code}")
                return self._get_cached_price(player_name)  # FALLBACK A CACHE
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar primera fila de jugador (clase correcta: player-row)
            player_row = soup.find('tr', {'class': 'player-row'})
            
            if not player_row:
                logger.warning(f"No se encontró jugador: {player_name}")
                return self._get_cached_price(player_name)  # FALLBACK A CACHE
            
            # Extraer enlace del jugador (clase correcta: player-row-playercard)
            player_link = player_row.find('a', {'class': 'player-row-playercard'})
            if not player_link:
                logger.warning("No se encontró enlace del jugador")
                return self._get_cached_price(player_name)  # FALLBACK A CACHE
            
            player_url = player_link.get('href')
            if not player_url.startswith('http'):
                player_url = f"{self.base_url}{player_url}"
            
            # Extraer rating del playercard en la búsqueda
            rating_elem = player_row.find('div', {'class': 'playercard-s-26-rating'})
            rating = int(rating_elem.text.strip()) if rating_elem else 0
            
            # Obtener página del jugador para precio PC
            logger.info(f"📄 Accediendo a página del jugador...")
            player_response = self.session.get(player_url, timeout=15)
            
            if player_response.status_code != 200:
                logger.warning(f"Error al cargar página del jugador: {player_response.status_code}")
                return self._get_cached_price(player_name)  # FALLBACK A CACHE
            
            player_soup = BeautifulSoup(player_response.text, 'html.parser')
            
            # Extraer precio de PC del texto
            # Buscar: "His current price on FUT is XXX on Playstation, XXX on Xbox and XXX on PC"
            price_text = player_soup.get_text()
            pc_price = 0
            
            # Patrón: "XXX on PC" o "XXX,XXX on PC"
            match = re.search(r'([\d,]+)\s+on\s+PC', price_text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                pc_price = int(price_str)
                logger.info(f"✅ Precio PC encontrado: {pc_price:,} coins")
            else:
                # Intentar con data-price-pc attribute
                price_elem = player_soup.find(attrs={'data-price-pc': True})
                if price_elem:
                    pc_price = int(price_elem.get('data-price-pc', 0))
                    logger.info(f"✅ Precio PC (data attribute): {pc_price:,} coins")
            
            if pc_price == 0:
                logger.warning("No se pudo extraer precio de PC")
            
            return {
                'player_id': player_url.split('/')[-2] if '/' in player_url else 'unknown',
                'name': player_link.text.strip(),
                'rating': rating,
                'price': pc_price,
                'platform': 'PC',
                'timestamp': datetime.now(),
                'url': player_url
            }
            
        except Exception as e:
            logger.error(f"Error buscando jugador '{player_name}': {e}", exc_info=True)
            return None
    
    def get_pc_price(self, player_id: str, player_name: str = "") -> int:
        """
        Obtiene precio PC de un jugador específico desde FUTBIN
        
        Args:
            player_id: ID del jugador en FUTBIN (ej: "239085" para Messi)
            player_name: Nombre del jugador (opcional, para slug URL)
            
        Returns:
            Precio PC del jugador (int), 0 si no se encuentra
        """
        try:
            # Construir URL del jugador
            # Formato: https://www.futbin.com/26/player/239085/lionel-messi
            slug = player_name.lower().replace(' ', '-') if player_name else str(player_id)
            player_url = f"{self.base_url}/26/player/{player_id}/{slug}"
            
            logger.debug(f"🔍 Obteniendo precio PC para player_id={player_id}")
            
            response = self.session.get(player_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Error al cargar página del jugador: {response.status_code}")
                return 0
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Método 1: Buscar en texto "XXX on PC"
            price_text = soup.get_text()
            match = re.search(r'([\d,]+)\s+on\s+PC', price_text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                price = int(price_str)
                logger.debug(f"✅ Precio encontrado: {price:,} coins")
                return price
            
            # Método 2: data-price-pc attribute
            price_elem = soup.find(attrs={'data-price-pc': True})
            if price_elem:
                price = int(price_elem.get('data-price-pc', 0))
                if price > 0:
                    logger.debug(f"✅ Precio (data attribute): {price:,} coins")
                    return price
            
            logger.warning(f"⚠️ No se pudo extraer precio PC para player_id={player_id}")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio PC para player_id={player_id}: {e}")
            return 0
    
    def get_player_price(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time price for a specific player from FUTBIN
        
        NOTE: This requires knowing the player's URL slug. 
        For searching by name, use search_player_by_name() instead.
        
        Args:
            player_id: FUTBIN player ID
            
        Returns:
            Dictionary with player price data
        """
        # This method is deprecated - use search_player_by_name instead
        logger.warning("get_player_price requires URL slug. Use search_player_by_name() instead.")
        return None
    
    def get_all_players_from_page(self, page: int = 1, max_players: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene jugadores directamente de la página de FUTBIN
        
        Args:
            page: Número de página
            max_players: Máximo de jugadores a obtener de esta página
            
        Returns:
            Lista de jugadores con precios PC
        """
        try:
            url = f"{self.base_url}/26/players?page={page}"
            logger.info(f"📄 Obteniendo jugadores de página {page}...")
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Error al obtener página: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todas las filas de jugadores
            player_rows = soup.find_all('tr', {'class': 'player-row'}, limit=max_players)
            
            logger.info(f"✅ Encontradas {len(player_rows)} filas de jugadores")
            
            players = []
            
            for row in player_rows:
                try:
                    # Extraer enlace del jugador
                    player_link = row.find('a', {'class': 'player-row-playercard'})
                    if not player_link:
                        continue
                    
                    player_url = player_link.get('href')
                    if not player_url:
                        continue
                    
                    # Extraer nombre del href (formato: /26/player/ID/nombre-jugador)
                    parts = player_url.split('/')
                    if len(parts) < 5:
                        continue
                    
                    player_id = parts[3]
                    player_slug = parts[4]
                    player_name = player_slug.replace('-', ' ').title()
                    
                    # Extraer rating
                    rating_elem = row.find('div', {'class': 'playercard-s-26-rating'})
                    rating = int(rating_elem.text.strip()) if rating_elem else 0
                    
                    players.append({
                        'player_id': player_id,
                        'name': player_name,
                        'rating': rating,
                        'url': f"{self.base_url}{player_url}"
                    })
                    
                except Exception as e:
                    logger.debug(f"Error procesando fila: {e}")
                    continue
            
            return players
            
        except Exception as e:
            logger.error(f"Error obteniendo jugadores de página {page}: {e}")
            return []
    
    def get_all_available_players(self, max_pages: int = 10, min_rating: int = 75) -> List[Dict[str, Any]]:
        """
        Obtiene TODOS los jugadores disponibles en FUTBIN
        
        Args:
            max_pages: Máximo de páginas a procesar
            min_rating: Rating mínimo de jugadores
            
        Returns:
            Lista completa de jugadores con URLs
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 OBTENIENDO TODOS LOS JUGADORES DE FUTBIN")
        logger.info(f"{'='*70}\n")
        
        all_players = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"📖 Procesando página {page}/{max_pages}...")
            
            page_players = self.get_all_players_from_page(page)
            
            if not page_players:
                logger.info(f"⚠️ No hay más jugadores en página {page}")
                break
            
            # Filtrar por rating
            filtered = [p for p in page_players if p['rating'] >= min_rating]
            all_players.extend(filtered)
            
            logger.info(f"✅ Agregados {len(filtered)} jugadores (rating >= {min_rating})")
            
            import time
            time.sleep(1)  # Rate limiting entre páginas
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ TOTAL: {len(all_players)} jugadores obtenidos")
        logger.info(f"{'='*70}\n")
        
        return all_players
    
    def get_players_by_rating(self, rating: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene jugadores de un rating específico
        Optimizado para scraping selectivo (solo ratings relevantes)
        
        Args:
            rating: Rating exacto a buscar (ej: 82, 83, 84, 85)
            max_pages: Máximo de páginas a procesar
            
        Returns:
            Lista de jugadores del rating especificado
        """
        try:
            logger.info(f"[SCRAPER] Buscando jugadores Rating {rating}...")
            
            players = []
            
            for page in range(1, max_pages + 1):
                # URL con filtro de rating en FUTBIN
                url = f"{self.base_url}/26/players?page={page}&minrating={rating}&maxrating={rating}"
                
                logger.debug(f"Pagina {page}/{max_pages}: {url}")
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"Error en pagina {page}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar todas las filas de jugadores
                player_rows = soup.find_all('tr', {'class': 'player-row'})
                
                if not player_rows:
                    logger.info(f"No hay mas jugadores en pagina {page}")
                    break
                
                page_count = 0
                for row in player_rows:
                    try:
                        # Extraer enlace del jugador
                        player_link = row.find('a', {'class': 'player-row-playercard'})
                        if not player_link:
                            continue
                        
                        player_url = player_link.get('href')
                        if not player_url:
                            continue
                        
                        # Hacer URL absoluta
                        if not player_url.startswith('http'):
                            player_url = f"{self.base_url}{player_url}"
                        
                        # Extraer player_id y nombre del URL
                        # Formato: https://www.futbin.com/26/player/18690/maradona
                        # parts: ['https:', '', 'www.futbin.com', '26', 'player', '18690', 'maradona']
                        parts = player_url.split('/')
                        player_id = parts[5] if len(parts) > 5 else 'unknown'
                        name = parts[6].replace('-', ' ').title() if len(parts) > 6 else 'Unknown'
                        
                        # Rating y posición
                        rating_elem = row.find('div', {'class': 'playercard-s-26-rating'})
                        actual_rating = int(rating_elem.text.strip()) if rating_elem else rating
                        
                        position_elem = row.find('div', {'class': 'playercard-s-26-position'})
                        position = position_elem.text.strip() if position_elem else 'Unknown'
                        
                        # Extraer liga/club/nación de las imágenes
                        league = 'Unknown'
                        club = 'Unknown'
                        nation = 'Unknown'
                        
                        league_img = row.find('img', {'class': 'player-row-league-logo'})
                        if league_img and league_img.get('alt'):
                            league = league_img.get('alt')
                        
                        nation_img = row.find('img', {'class': 'player-row-nation-logo'})
                        if nation_img and nation_img.get('alt'):
                            nation = nation_img.get('alt')
                        
                        club_img = row.find('img', {'class': 'player-row-club-logo'})
                        if club_img and club_img.get('alt'):
                            club = club_img.get('alt')
                        
                        player_data = {
                            'player_id': player_id,
                            'name': name,
                            'rating': actual_rating,
                            'position': position,
                            'league': league,
                            'club': club,
                            'nation': nation,
                            'price': 0,  # Se obtiene después con get_player_price()
                            'url': player_url,
                            'timestamp': datetime.now()
                        }
                        
                        players.append(player_data)
                        page_count += 1
                        
                    except Exception as e:
                        logger.debug(f"Error procesando jugador: {e}")
                        continue
                
                logger.info(f"[OK] Pagina {page}: {page_count} jugadores extraidos")
                
                import time
                time.sleep(1)  # Rate limiting
            
            logger.info(f"[OK] Total Rating {rating}: {len(players)} jugadores")
            return players
            
        except Exception as e:
            logger.error(f"Error obteniendo jugadores rating {rating}: {e}")
            return []
    
    def update_all_players_prices(self, db_manager, max_pages: int = 10) -> int:
        """
        Actualiza precios de TODOS los jugadores disponibles en FUTBIN
        
        Args:
            db_manager: Instancia de DatabaseManager
            max_pages: Páginas a procesar
            
        Returns:
            Número de precios actualizados
        """
        # Primero obtener lista de todos los jugadores disponibles
        all_players = self.get_all_available_players(max_pages=max_pages)
        
        if not all_players:
            logger.error("❌ No se pudieron obtener jugadores de FUTBIN")
            return 0
        
        logger.info(f"\n{'='*70}")
        logger.info(f"💰 ACTUALIZANDO PRECIOS DE {len(all_players)} JUGADORES")
        logger.info(f"{'='*70}\n")
        
        updated = 0
        failed = 0
        
        for i, player in enumerate(all_players, 1):
            try:
                logger.info(f"[{i}/{len(all_players)}] {player['name']} ({player['rating']})...")
                
                # Obtener precio usando la URL completa
                response = self.session.get(player['url'], timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ Error HTTP {response.status_code}")
                    failed += 1
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraer precio PC del texto
                price_text = soup.get_text()
                match = re.search(r'([\d,]+)\s+on\s+PC', price_text, re.IGNORECASE)
                
                # Buscar o crear jugador en DB primero
                session = db_manager.get_session()
                
                existing_player = session.query(db_manager.Player).filter_by(
                    player_id=player['player_id']
                ).first()
                
                if match:
                    price_str = match.group(1).replace(',', '')
                    pc_price = int(price_str)
                    
                    if not existing_player:
                        # Crear nuevo jugador con player_id de FUTBIN
                        new_player = db_manager.Player(
                            player_id=player['player_id'],
                            name=player['name'],
                            rating=player['rating'],
                            position='Unknown',
                            is_extinct=False
                        )
                        session.add(new_player)
                        session.commit()
                        player_id = player['player_id']
                        logger.info(f"➕ Jugador agregado a DB")
                    else:
                        # Actualizar si estaba extinto
                        if existing_player.is_extinct:
                            existing_player.is_extinct = False
                            session.commit()
                        player_id = existing_player.player_id
                    
                    session.close()
                    
                    # Agregar precio
                    db_manager.add_price_history(
                        player_id=player_id,
                        price=pc_price
                    )
                    
                    updated += 1
                    logger.info(f"✅ {player['name']}: {pc_price:,} coins (PC)")
                else:
                    # Jugador EXTINTO - Sin precio en mercado
                    if not existing_player:
                        # Crear jugador extinto
                        new_player = db_manager.Player(
                            player_id=player['player_id'],
                            name=player['name'],
                            rating=player['rating'],
                            position='Unknown',
                            is_extinct=True
                        )
                        session.add(new_player)
                        session.commit()
                        logger.info(f"🔴 {player['name']}: EXTINTO (sin mercado)")
                    else:
                        # Marcar como extinto
                        existing_player.is_extinct = True
                        session.commit()
                        logger.info(f"🔴 {player['name']}: Marcado como EXTINTO")
                    
                    session.close()
                    failed += 1
                
                import time
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                failed += 1
                continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ COMPLETADO: {updated} actualizados, {failed} fallidos")
        logger.info(f"{'='*70}\n")
        
        return updated
        """
        Obtiene jugadores populares con sus precios de PC
        
        Args:
            limit: Número de jugadores a obtener (default: 100)
            
        Returns:
            Lista de jugadores con precios PC
        """
        # Jugadores populares para scraping - Expandido a 100+ jugadores
        player_names = [
            # Icons & Top Tier (90+)
            "Cristiano Ronaldo", "Lionel Messi", "Kylian Mbappé", "Erling Haaland",
            "Kevin De Bruyne", "Vinícius Jr", "Mohamed Salah", "Karim Benzema",
            "Neymar Jr", "Jude Bellingham", "Robert Lewandowski", "Luka Modrić",
            "Thibaut Courtois", "Alisson", "Ederson", "Manuel Neuer",
            
            # High Rating (87-89)
            "Rodri", "Bruno Fernandes", "Phil Foden", "Harry Kane",
            "Bernardo Silva", "Son Heung-Min", "Joshua Kimmich", "Toni Kroos",
            "Casemiro", "N'Golo Kanté", "Virgil van Dijk", "Rúben Dias",
            "Antonio Rüdiger", "Marquinhos", "Sergio Ramos", "Raphael Varane",
            
            # Popular Mid-Tier (85-86)
            "Pedri", "Gavi", "Federico Valverde", "Eduardo Camavinga",
            "Aurélien Tchouaméni", "Leon Goretzka", "İlkay Gündoğan", "Frenkie de Jong",
            "João Félix", "Rafael Leão", "Marcus Rashford", "Bukayo Saka",
            "Jadon Sancho", "Jack Grealish", "Kai Havertz", "Mason Mount",
            "Declan Rice", "Trent Alexander-Arnold", "Andrew Robertson", "João Cancelo",
            
            # Budget Beasts (83-84)
            "Serge Gnabry", "Memphis Depay", "Nico Williams", "Ferran Torres",
            "Dani Olmo", "Mikel Oyarzabal", "Martin Ødegaard", "Gabriel Jesus",
            "Diogo Jota", "Luis Díaz", "Cody Gakpo", "Darwin Núñez",
            "Julián Álvarez", "Christopher Nkunku", "Ousmane Dembélé", "Kingsley Coman",
            "Leroy Sané", "Raheem Sterling", "Antony", "Richarlison",
            
            # Affordable Options (80-82)
            "Gabriel Martinelli", "Alejandro Garnacho", "Ansu Fati", "Florian Wirtz",
            "Jamal Musiala", "Jérémie Frimpong", "Reece James", "Ben Chilwell",
            "Achraf Hakimi", "Theo Hernández", "Alphonso Davies", "Kyle Walker",
            "Eder Militão", "Jules Koundé", "William Saliba", "Gabriel Magalhães",
            
            # Investment Targets (78-79)
            "Eberechi Eze", "Cole Palmer", "Morgan Gibbs-White", "Anthony Gordon",
            "Brennan Johnson", "Pedro Neto", "Matheus Cunha", "Matheus Nunes",
            "Adama Traoré", "Allan Saint-Maximin", "Moussa Diaby", "Jonathan Ikoné",
            
            # Budget Cards (75-77)
            "Marcus Thuram", "Randal Kolo Muani", "Gonçalo Ramos", "Victor Osimhen",
            "Khvicha Kvaratskhelia", "Dejan Kulusevski", "Ademola Lookman", "Callum Hudson-Odoi",
            "Harvey Barnes", "Wilfried Zaha", "Ismaïla Sarr", "Jarrod Bowen",
            
            # Emerging Talents
            "Jude Soonsup-Bell", "Lamine Yamal", "Warren Zaïre-Emery", "Endrick",
            "Arda Güler", "Desire Doue", "Rayan Cherki", "Mathys Tel",
        ]
        
        players = []
        
        for player_name in player_names[:limit]:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 Procesando: {player_name}")
            
            player_data = self.search_player(player_name)
            
            if player_data and player_data['price'] > 0:
                players.append(player_data)
                logger.info(f"✅ {player_data['name']} ({player_data['rating']}): {player_data['price']:,} coins (PC)")
            else:
                logger.warning(f"⚠️ No se pudo obtener precio PC para {player_name}")
            
            # Rate limiting para no saturar FUTBIN
            time.sleep(2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Total obtenido: {len(players)} jugadores con precios PC")
        
        return players
    
    def update_database_prices(self, db_manager, use_all_futbin: bool = True, max_pages: int = 5) -> int:
        """
        Actualiza precios de jugadores en la base de datos
        
        Args:
            db_manager: Instancia de DatabaseManager
            use_all_futbin: Si True, obtiene TODOS los jugadores de FUTBIN
                           Si False, solo actualiza jugadores existentes en DB
            max_pages: Número de páginas de FUTBIN a procesar (si use_all_futbin=True)
            
        Returns:
            Número de precios actualizados
        """
        if use_all_futbin:
            # Obtener y actualizar TODOS los jugadores de FUTBIN
            return self.update_all_players_prices(db_manager, max_pages=max_pages)
        else:
            # Solo actualizar jugadores existentes en DB
            session = db_manager.get_session()
            players = session.query(db_manager.Player).all()
            total = len(players)
            session.close()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Actualizando precios PC para {total} jugadores...")
            logger.info(f"{'='*60}\n")
            
            updated = 0
            for i, player in enumerate(players, 1):
                logger.info(f"[{i}/{total}] Buscando {player.name}...")
                
                player_data = self.search_player(player.name)
                
                if player_data and player_data['price'] > 0:
                    db_manager.add_price_history(
                        player_id=player.id,
                        price=player_data['price']
                    )
                    updated += 1
                    logger.info(f"✅ {player.name}: {player_data['price']:,} coins (PC)")
                else:
                    logger.warning(f"⚠️ No se pudo actualizar: {player.name}")
                
                import time
                time.sleep(2)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ Actualización completa: {updated}/{total} jugadores")
            logger.info(f"{'='*60}\n")
            
            return updated
    
    def _parse_price(self, price_str: str) -> int:
        """Parse price string to integer (e.g., '1.2K' -> 1200, '1.5M' -> 1500000)"""
        try:
            price_str = price_str.strip().upper().replace(',', '')
            
            if 'M' in price_str:
                return int(float(price_str.replace('M', '')) * 1000000)
            elif 'K' in price_str:
                return int(float(price_str.replace('K', '')) * 1000)
            else:
                return int(price_str)
        except:
            return 0
    
    def _get_cached_price(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene precio cacheado de la base de datos como fallback
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            Datos del jugador con último precio conocido
        """
        try:
            from app.database.db_manager import DatabaseManager, Player, PriceHistory
            
            db = DatabaseManager()
            session = db.SessionLocal()
            
            try:
                # Buscar jugador por nombre
                player = session.query(Player).filter(
                    Player.name.ilike(f"%{player_name}%")
                ).first()
                
                if not player:
                    logger.warning(f"No hay precio cacheado para: {player_name}")
                    return None
                
                # Obtener último precio
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.player_id == player.player_id
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                if not latest_price:
                    logger.warning(f"No hay historial de precios para: {player_name}")
                    return None
                
                logger.info(f"Usando precio cacheado: {latest_price.price:,} coins")
                
                return {
                    'player_id': player.player_id,
                    'name': player.name,
                    'rating': player.rating,
                    'position': player.position,
                    'league': player.league,
                    'nation': getattr(player, 'nation', 'Unknown'),
                    'price_pc': latest_price.price,
                    'supply': latest_price.supply if hasattr(latest_price, 'supply') else 0,
                    'demand': latest_price.demand if hasattr(latest_price, 'demand') else 0,
                    'cached': True
                }
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error obteniendo precio cacheado: {e}")
            return None


class FUTBINAPIClient:
    """
    Alternative: Use FUTBIN's internal API (faster but may change)
    """
    
    def __init__(self):
        self.base_url = "https://www.futbin.com/26"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.futbin.com/'
        }
    
    def get_player_prices_batch(self, player_ids: List[str]) -> Dict[str, Any]:
        """
        Get prices for multiple players using FUTBIN API
        
        Args:
            player_ids: List of player IDs
            
        Returns:
            Dictionary with player prices
        """
        try:
            # FUTBIN's API endpoint for player prices
            url = f"{self.base_url}/playerPrices"
            params = {'player': ','.join(player_ids)}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching from FUTBIN API: {e}")
            return {}
    
    def search_players(self, min_rating: int = 83, max_price: int = 10000) -> List[Dict[str, Any]]:
        """
        Search players by criteria
        
        Args:
            min_rating: Minimum player rating
            max_price: Maximum price
            
        Returns:
            List of matching players
        """
        try:
            # FUTBIN search endpoint
            url = f"{self.base_url}/players"
            params = {
                'page': 1,
                'version': 'gold',
                'min_rating': min_rating,
                'max_price': max_price,
                'sort': 'stats',
                'order': 'desc'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                players = []
                
                # Extract player cards
                player_cards = soup.find_all('div', {'class': 'player-card'})
                
                for card in player_cards[:20]:  # Limit to 20 players
                    player_data = self._parse_player_card(card)
                    if player_data:
                        players.append(player_data)
                
                return players
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching players: {e}")
            return []
    
    def _parse_player_card(self, card) -> Optional[Dict[str, Any]]:
        """Parse player card HTML"""
        try:
            player_id = card.get('data-player-id')
            name = card.find('a', {'class': 'player-name'})
            rating = card.find('div', {'class': 'rating'})
            price = card.find('div', {'class': 'price'})
            
            if not all([player_id, name, rating]):
                return None
            
            return {
                'player_id': player_id,
                'name': name.text.strip(),
                'rating': int(rating.text.strip()),
                'price': self._parse_price(price.text.strip()) if price else 0
            }
        except:
            return None
    
    def _parse_price(self, price_text: str) -> int:
        """Parse price text to integer"""
        try:
            price_text = price_text.replace(',', '').replace('.', '')
            if 'K' in price_text:
                return int(float(price_text.replace('K', '')) * 1000)
            elif 'M' in price_text:
                return int(float(price_text.replace('M', '')) * 1000000)
            return int(price_text)
        except:
            return 0


def test_scraper():
    """Test the scraper"""
    print("\n" + "="*60)
    print("  TESTING FUTBIN SCRAPER")
    print("="*60 + "\n")
    
    # Test web scraper
    scraper = FUTBINScraper()
    print("Fetching Memphis Depay (199556)...")
    player = scraper.get_player_price("199556")
    
    if player:
        print(f"✅ {player['name']} - {player['rating']} - {player['price']:,} coins")
    else:
        print("❌ Failed to fetch player")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_scraper()
