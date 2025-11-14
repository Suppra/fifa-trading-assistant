"""
Test SBC Scraper - Debug para ver qué estructura tiene FUTBIN
"""
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sbc_scraping():
    """Test del scraper de SBCs"""
    print("\n" + "="*70)
    print("  TEST SBC SCRAPER - EA FC 26")
    print("="*70 + "\n")
    
    url = "https://www.futbin.com/26/squad-building-challenges"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.futbin.com/'
    }
    
    print(f"📡 Conectando a: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Respuesta HTTP: {response.status_code}")
        print(f"📊 Tamaño HTML: {len(response.content)} bytes\n")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Guardar HTML para inspección
        with open('sbc_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("💾 HTML guardado en: sbc_page.html\n")
        
        # Estrategia 1: Buscar todos los divs
        print("🔍 Estrategia 1: Buscando divs con clase 'sbc'...")
        divs = soup.find_all('div', class_=lambda x: x and 'sbc' in x.lower() if x else False)
        print(f"   Encontrados: {len(divs)} divs con 'sbc' en clase\n")
        
        # Estrategia 2: Buscar enlaces con 'challenge' o 'sbc'
        print("🔍 Estrategia 2: Buscando enlaces con 'sbc' o 'challenge'...")
        links = soup.find_all('a', href=lambda h: h and ('sbc' in h.lower() or 'challenge' in h.lower()) if h else False)
        print(f"   Encontrados: {len(links)} enlaces\n")
        
        if links:
            print("📋 Primeros 10 enlaces encontrados:")
            for i, link in enumerate(links[:10], 1):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"   {i}. {text[:50]:<50} → {href}")
        
        # Estrategia 3: Buscar por estructura de tabla/grid
        print("\n🔍 Estrategia 3: Buscando tablas/grids...")
        tables = soup.find_all(['table', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['grid', 'list', 'row']) if x else False)
        print(f"   Encontrados: {len(tables)} elementos grid/table\n")
        
        # Estrategia 4: Buscar todos los h2, h3, h4
        print("🔍 Estrategia 4: Buscando títulos (h2, h3, h4)...")
        headers = soup.find_all(['h2', 'h3', 'h4'])
        print(f"   Encontrados: {len(headers)} títulos\n")
        
        if headers:
            print("📋 Primeros 15 títulos:")
            for i, h in enumerate(headers[:15], 1):
                print(f"   {i}. {h.name}: {h.get_text(strip=True)}")
        
        # Estrategia 5: Buscar clases específicas de FUTBIN
        print("\n🔍 Estrategia 5: Clases comunes de FUTBIN...")
        common_classes = ['challenge', 'squad', 'objective', 'card', 'item', 'set']
        
        for cls in common_classes:
            elements = soup.find_all(class_=lambda x: x and cls in x.lower() if x else False)
            if elements:
                print(f"   .{cls}*: {len(elements)} elementos")
        
        # Estrategia 6: Buscar por texto que contenga "SBC"
        print("\n🔍 Estrategia 6: Texto que contiene 'SBC'...")
        sbc_text = soup.find_all(string=lambda t: t and 'sbc' in t.lower() if t else False)
        print(f"   Encontrados: {len(sbc_text)} elementos de texto con 'SBC'\n")
        
        # Mostrar estructura de divs principales
        print("\n📦 Estructura de DIVs principales:")
        main_divs = soup.find_all('div', recursive=False)
        for i, div in enumerate(main_divs[:5], 1):
            classes = div.get('class', [])
            id_attr = div.get('id', '')
            print(f"   {i}. DIV - class={classes}, id={id_attr}")
        
        print("\n" + "="*70)
        print("✅ Test completado - Revisa sbc_page.html para más detalles")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sbc_scraping()
