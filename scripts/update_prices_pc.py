"""
Actualizar precios de PC desde FUTBIN - TODOS los jugadores disponibles
"""
from app.data_collection.futbin_scraper import FUTBINScraper
from app.database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print(" ACTUALIZACIÓN MASIVA - TODOS LOS JUGADORES FUTBIN (PC) ".center(70))
print("="*70)
print("\n⚠️  ATENCIÓN:")
print("   Este proceso obtendrá TODOS los jugadores disponibles en FUTBIN")
print("   Páginas a procesar: 100 (aprox. 3000 jugadores)")
print("   Tiempo estimado: ~2-3 HORAS (con rate limiting)")
print("\n" + "="*70 + "\n")

input("Presiona ENTER para continuar o Ctrl+C para cancelar...")

scraper = FUTBINScraper()
db = DatabaseManager()

# Usar el nuevo método que obtiene TODOS los jugadores de FUTBIN
print("\n🚀 Iniciando actualización masiva...\n")
updated = scraper.update_database_prices(db, use_all_futbin=True, max_pages=100)

print("\n" + "="*70)
print(f" ✅ COMPLETADO: {updated} jugadores con precios REALES ".center(70))
print("="*70 + "\n")
