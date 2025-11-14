"""
Test: Obtener jugadores de FUTBIN (primera página)
"""
from src.data_collection.futbin_scraper import FUTBINScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print(" 🧪 TEST: Obtener jugadores de FUTBIN ".center(70))
print("="*70 + "\n")

scraper = FUTBINScraper()

# Test: obtener jugadores de primera página
print("📄 Obteniendo jugadores de la primera página de FUTBIN...\n")
players = scraper.get_all_players_from_page(page=1, max_players=20)

if players:
    print(f"\n✅ Obtenidos {len(players)} jugadores:\n")
    print("-" * 70)
    for i, player in enumerate(players[:10], 1):
        print(f"{i:2d}. {player['name']:30s} Rating: {player['rating']:2d}")
    
    if len(players) > 10:
        print(f"\n... y {len(players) - 10} jugadores más\n")
    
    print("="*70)
    print(f"\n💡 Total disponible para scraping: {len(players)} jugadores")
    print("🎯 Estos jugadores se pueden obtener con precios REALES de PC\n")
else:
    print("\n❌ No se pudieron obtener jugadores\n")
