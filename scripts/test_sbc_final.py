"""Test final del scraper con parsing correcto"""
import requests
from bs4 import BeautifulSoup

url = "https://www.futbin.com/26/squad-building-challenges"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

print("\n" + "="*70)
print("  TEST SBC SCRAPER - FINAL")
print("="*70 + "\n")

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

wrappers = soup.find_all('div', class_='sbc-card-wrapper')
print(f"✅ Encontrados {len(wrappers)} SBC cards\n")

for idx, wrapper in enumerate(wrappers, 1):
    # Buscar enlace
    link = wrapper.find('a', href=lambda h: h and 'squad-building-challenge/' in h)
    if not link:
        continue
    
    # IMPORTANTE: Buscar SOLO el div.text-ellipsis que está directamente en og-card-wrapper-top
    # Esto evita capturar badges y otros elementos
    top_section = link.find('div', class_='og-card-wrapper-top')
    if not top_section:
        continue
    
    name_container = top_section.find('div', class_='xs-font')
    if not name_container:
        continue
        
    name_div = name_container.find('div', class_='text-ellipsis')
    if not name_div:
        continue
    
    name = name_div.get_text(strip=True)
    
    # Buscar badge (está en el mismo xs-font container pero separado)
    badge = name_container.find('div', class_='sbc-badge')
    badge_text = badge.get_text(strip=True) if badge else ""
    
    print(f"   {idx}. {name:<40} {'[' + badge_text + ']' if badge_text else ''}")

print(f"\n{'='*70}\n")
