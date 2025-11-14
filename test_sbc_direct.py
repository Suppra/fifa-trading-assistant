"""Test directo del scraper de SBCs"""
import requests
from bs4 import BeautifulSoup

url = "https://www.futbin.com/26/squad-building-challenges"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

print("\n" + "="*70)
print("  TEST SBC SCRAPER - ESTRATEGIA CORRECTA")
print("="*70 + "\n")

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Buscar sbc-card-wrapper
wrappers = soup.find_all('div', class_='sbc-card-wrapper')
print(f"✅ Encontrados {len(wrappers)} wrappers con clase 'sbc-card-wrapper'\n")

sbcs_found = []

for idx, wrapper in enumerate(wrappers, 1):
    # Buscar enlace
    link = wrapper.find('a', href=lambda h: h and 'squad-building-challenge/' in h)
    if not link:
        print(f"   ✗ SBC #{idx}: No tiene enlace")
        continue
    
    # Buscar nombre
    name_div = link.find('div', class_='text-ellipsis')
    if not name_div:
        print(f"   ✗ SBC #{idx}: No tiene nombre")
        continue
    
    name = name_div.get_text(strip=True)
    
    # Buscar badge
    badge = wrapper.find('div', class_='sbc-badge')
    badge_text = badge.get_text(strip=True) if badge else ""
    
    href = link.get('href', '')
    
    sbcs_found.append({
        'name': name,
        'href': href,
        'badge': badge_text
    })
    
    print(f"   ✓ SBC #{idx}: {name}")
    if badge_text:
        print(f"              Badge: {badge_text}")

print(f"\n{'='*70}")
print(f"  TOTAL: {len(sbcs_found)} SBCs encontrados")
print(f"{'='*70}\n")

# Mostrar lista final
print("📋 LISTA COMPLETA DE SBCs:\n")
for i, sbc in enumerate(sbcs_found, 1):
    print(f"   {i}. {sbc['name']}")
    if sbc['badge']:
        print(f"      [{sbc['badge']}]")
