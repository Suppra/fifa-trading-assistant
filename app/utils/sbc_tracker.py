"""
SBC Tracker - Monitoreo de SBCs activos
Scraping de FUTBIN para detectar requisitos de SBC
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)


class SBCTracker:
    """Rastrea SBCs activos y requisitos"""
    
    def __init__(self):
        self.base_url = "https://www.futbin.com"
        self.sbcs_cache = []
        self.last_update = None
        # No usar intervalo - solo actualizar manualmente o en horario fijo
        self.daily_update_hour = 13  # 1:20 PM (en 24h: 13:20)
        self.daily_update_minute = 20
    
    def get_active_sbcs(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtiene lista de SBCs activos
        
        Args:
            force_refresh: Forzar actualización aunque esté en cache
            
        Returns:
            Lista de SBCs con requisitos
        """
        # Si se fuerza refresh o no hay cache, actualizar
        if force_refresh or not self.sbcs_cache or not self.last_update:
            return self._fetch_sbcs_from_futbin()
        
        # Si hay cache, usarlo
        logger.info(f"✓ Usando cache de SBCs ({len(self.sbcs_cache)} SBCs)")
        return self.sbcs_cache
    
    def _fetch_sbcs_from_futbin(self) -> List[Dict]:
        """Obtiene SBCs directamente de FUTBIN (método interno)"""
        try:
            logger.info("🔍 Obteniendo SBCs activos de FUTBIN...")
            
            # Scrape FUTBIN SBC page - EA FC 26
            url = f"{self.base_url}/26/squad-building-challenges"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.futbin.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            sbcs = []
            
            # Buscar todos los wrappers de SBC cards (estructura real de FUTBIN 2024)
            sbc_wrappers = soup.find_all('div', class_='sbc-card-wrapper')
            
            logger.info(f"📋 Encontrados {len(sbc_wrappers)} SBC cards en FUTBIN")
            
            for idx, wrapper in enumerate(sbc_wrappers, 1):
                try:
                    # El enlace principal está dentro del wrapper
                    link_elem = wrapper.find('a', href=lambda h: h and 'squad-building-challenge/' in h)
                    if not link_elem:
                        logger.debug(f"   ✗ SBC #{idx}: No se encontró enlace")
                        continue
                    
                    # Buscar la sección superior del card
                    top_section = link_elem.find('div', class_='og-card-wrapper-top')
                    if not top_section:
                        logger.debug(f"   ✗ SBC #{idx}: No se encontró top section")
                        continue
                    
                    # Buscar el container del nombre
                    name_container = top_section.find('div', class_='xs-font')
                    if not name_container:
                        logger.debug(f"   ✗ SBC #{idx}: No se encontró name container")
                        continue
                    
                    # El nombre está en div.text-ellipsis (primer div, sin badge)
                    name_elem = name_container.find('div', class_='text-ellipsis')
                    if not name_elem:
                        logger.debug(f"   ✗ SBC #{idx}: No se encontró nombre")
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    if not name or len(name) < 2:
                        logger.debug(f"   ✗ SBC #{idx}: Nombre inválido '{name}'")
                        continue
                    
                    # Construir enlace completo
                    href = link_elem.get('href', '')
                    sbc_url = f"https://www.futbin.com{href}" if not href.startswith('http') else href
                    
                    # Buscar badge (New, Popular, Expiring soon, etc) - está en el mismo container
                    badge_elem = name_container.find('div', class_='sbc-badge')
                    badge = badge_elem.get_text(strip=True) if badge_elem else ""
                    
                    # Buscar fecha de expiración (si existe un elemento específico)
                    expiry_elem = wrapper.find('div', class_=lambda x: x and 'expir' in x.lower() if x else False)
                    expires = expiry_elem.get_text(strip=True) if expiry_elem else ("Temporary" if "expir" in badge.lower() else "Permanent")
                    
                    # Intentar extraer requisitos del HTML
                    requirements = self._parse_requirements(wrapper)
                    
                    # Intentar extraer recompensa
                    reward = self._parse_reward(wrapper)
                    
                    sbc_data = {
                        'name': name,
                        'expiry': expires,
                        'requirements': requirements,
                        'reward': reward,
                        'url': sbc_url
                    }
                    
                    sbcs.append(sbc_data)
                    badge_display = f" ({badge})" if badge else ""
                    logger.debug(f"   ✓ SBC #{idx}: {name}{badge_display}")
                    
                except Exception as e:
                    logger.debug(f"   ✗ Error parseando SBC card #{idx}: {e}")
                    continue
            
            if sbcs:
                self.sbcs_cache = sbcs
                self.last_update = datetime.now()
                logger.info(f"✅ {len(sbcs)} SBCs reales obtenidos de FUTBIN")
                return sbcs
            else:
                # Si no se obtienen datos, NO usar mock data
                logger.warning("⚠️ No se encontraron SBCs activos en FUTBIN")
                self.sbcs_cache = []
                self.last_update = datetime.now()
                return []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo SBCs: {e}")
            
            # NO usar mock data - retornar vacío
            logger.info("ℹ️ Retornando lista vacía - no hay SBCs disponibles")
            return []
    
    def _parse_requirements(self, card_elem) -> Dict:
        """Parsea requisitos de un SBC"""
        try:
            requirements = {
                'min_rating': 'N/A',
                'chemistry': 'N/A',
                'num_players': 11
            }
            
            # Buscar rating mínimo con múltiples estrategias
            text_content = card_elem.get_text()
            
            import re
            
            # Estrategia 1: Buscar "Rating: XX" o "Min Rating: XX"
            rating_match = re.search(r'(?:min\s+)?rating[:\s]+(\d+)', text_content, re.IGNORECASE)
            if rating_match:
                requirements['min_rating'] = int(rating_match.group(1))
            else:
                # Estrategia 2: Buscar solo números en contexto de rating
                rating_elem = card_elem.find(string=re.compile(r'\d{2}', re.IGNORECASE))
                if rating_elem:
                    nums = re.findall(r'\b(\d{2})\b', str(rating_elem))
                    if nums:
                        # Filtrar solo ratings válidos (75-95)
                        valid_ratings = [int(n) for n in nums if 75 <= int(n) <= 95]
                        if valid_ratings:
                            requirements['min_rating'] = valid_ratings[0]
            
            # Buscar química
            chem_match = re.search(r'(?:min\s+)?chem(?:istry)?[:\s]+(\d+)', text_content, re.IGNORECASE)
            if chem_match:
                requirements['chemistry'] = int(chem_match.group(1))
            
            # Buscar número de jugadores
            players_match = re.search(r'(\d+)\s+players?', text_content, re.IGNORECASE)
            if players_match:
                requirements['num_players'] = int(players_match.group(1))
            
            return requirements
            
        except Exception as e:
            logger.debug(f"Error parseando requirements: {e}")
            return {'min_rating': 'N/A', 'chemistry': 'N/A', 'num_players': 11}
    
    def _parse_reward(self, card_elem) -> str:
        """Parsea recompensa de un SBC"""
        try:
            # Estrategia 1: Buscar por clase
            reward_elem = (
                card_elem.find('span', class_=['reward', 'prize', 'pack']) or
                card_elem.find('div', class_=['reward', 'prize', 'pack'])
            )
            
            if reward_elem:
                return reward_elem.text.strip()
            
            # Estrategia 2: Buscar por texto que contenga "pack" o "reward"
            import re
            text_content = card_elem.get_text()
            reward_match = re.search(r'([\w\s]+pack|[\w\s]+reward)', text_content, re.IGNORECASE)
            if reward_match:
                return reward_match.group(1).strip()
            
            return "Reward Pack"
            
        except:
            return "Reward Pack"
    
    def should_update_now(self) -> bool:
        """Verifica si es hora de actualizar SBCs (1:20 PM diario)"""
        now = datetime.now()
        
        # Si no hay última actualización, actualizar
        if not self.last_update:
            return True
        
        # Asegurar que los valores sean int
        daily_hour = int(self.daily_update_hour)
        daily_minute = int(self.daily_update_minute)
        
        # Verificar si es 1:20 PM y no se ha actualizado hoy a esa hora
        if now.hour == daily_hour and now.minute >= daily_minute:
            # Verificar si la última actualización fue antes de hoy a las 1:20 PM
            today_update_time = now.replace(hour=daily_hour, minute=daily_minute, second=0, microsecond=0)
            if self.last_update < today_update_time:
                return True
        
        return False
    
    def get_fodder_impact_analysis(self) -> Dict:
        """
        Analiza impacto de SBCs en precios de Fodder
        
        Returns:
            Análisis de demanda por rating
        """
        sbcs = self.get_active_sbcs()
        
        if not sbcs:
            return {}
        
        rating_demand = {}
        
        for sbc in sbcs:
            req = sbc.get('requirements', {})
            min_rating = req.get('min_rating', 'N/A')
            
            # Skip si no tiene rating válido
            if min_rating == 'N/A' or not isinstance(min_rating, int):
                continue
            
            # Incrementar demanda según rating requerido
            if min_rating >= 85:
                rating_demand[85] = rating_demand.get(85, 0) + 3
                rating_demand[84] = rating_demand.get(84, 0) + 2
                rating_demand[83] = rating_demand.get(83, 0) + 1
            elif min_rating >= 84:
                rating_demand[84] = rating_demand.get(84, 0) + 3
                rating_demand[83] = rating_demand.get(83, 0) + 2
                rating_demand[82] = rating_demand.get(82, 0) + 1
            elif min_rating >= 83:
                rating_demand[83] = rating_demand.get(83, 0) + 3
                rating_demand[82] = rating_demand.get(82, 0) + 2
            elif min_rating >= 82:
                rating_demand[82] = rating_demand.get(82, 0) + 2
        
        if not rating_demand:
            return {}
        
        # Crear análisis por rating
        impact_analysis = {}
        for rating, demand in sorted(rating_demand.items(), reverse=True):
            if demand >= 4:
                impact_level = 'ALTO'
            elif demand >= 2:
                impact_level = 'MEDIO'
            else:
                impact_level = 'BAJO'
            
            impact_analysis[rating] = {
                'demand_score': demand,
                'impact_level': impact_level,
                'sbc_count': len([
                    s for s in sbcs 
                    if isinstance(s.get('requirements', {}).get('min_rating'), int) 
                    and s.get('requirements', {}).get('min_rating') >= rating
                ])
            }
        
        return impact_analysis
