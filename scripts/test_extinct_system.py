"""
Prueba rápida del sistema de jugadores extintos
Solo 3 páginas para verificar que funciona
"""
from app.data_collection.futbin_scraper import FUTBINScraper
from app.database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print(" PRUEBA - SISTEMA DE JUGADORES EXTINTOS ".center(70))
print("="*70)
print("\n🧪 Procesando 3 páginas (~90 jugadores)")
print("⏱️ Tiempo estimado: ~3-5 minutos\n")
print("="*70 + "\n")

input("Presiona ENTER para continuar...")

scraper = FUTBINScraper()
db = DatabaseManager()

print("\n🚀 Iniciando prueba...\n")
updated = scraper.update_database_prices(db, use_all_futbin=True, max_pages=3)

# Mostrar estadísticas
import sqlite3
conn = sqlite3.connect('data/trading_bot.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM players WHERE is_extinct = 1")
extinct = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM players WHERE is_extinct = 0")
with_market = cursor.fetchone()[0]

cursor.execute("SELECT name, rating FROM players WHERE is_extinct = 1 ORDER BY rating DESC LIMIT 10")
extinct_players = cursor.fetchall()

conn.close()

print("\n" + "="*70)
print(" 📊 ESTADÍSTICAS DE PRUEBA ".center(70))
print("="*70)
print(f"\n✅ Jugadores actualizados: {updated}")
print(f"🔴 Jugadores extintos: {extinct}")
print(f"💰 Jugadores con mercado: {with_market}")

if extinct_players:
    print(f"\n🔴 Top 10 jugadores EXTINTOS (sin mercado):")
    for name, rating in extinct_players:
        print(f"   • {name} ({rating})")

print("\n" + "="*70 + "\n")
