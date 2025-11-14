"""
Test FUTBIN scraper - Precios PC únicamente
"""
from src.data_collection.futbin_scraper import FUTBINScraper
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

print("\n" + "="*60)
print("🧪 TEST: FUTBIN Scraper - Precios PC")
print("="*60 + "\n")

scraper = FUTBINScraper()

# Test con Messi
print("🔍 Buscando Lionel Messi...\n")
result = scraper.search_player("Messi")

if result and result['price'] > 0:
    print(f"\n{'='*60}")
    print(f"✅ ÉXITO!")
    print(f"{'='*60}")
    print(f"  Jugador: {result['name']}")
    print(f"  Rating:  {result['rating']}")
    print(f"  Precio PC: {result['price']:,} coins")
    print(f"  URL: {result['url']}")
    print(f"{'='*60}\n")
else:
    print(f"\n❌ FALLO: No se pudo obtener precio PC de Messi\n")
    if result:
        print(f"Datos recibidos: {result}\n")
