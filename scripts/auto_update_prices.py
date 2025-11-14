"""
Auto-actualización de precios desde FUTBIN
Ejecuta actualizaciones automáticas cada hora
"""
import schedule
import time
import logging
from datetime import datetime
from app.data_collection.futbin_scraper import FUTBINScraper
from app.database.db_manager import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def update_prices():
    """Actualiza todos los precios de la base de datos desde FUTBIN"""
    logger.info("\n" + "="*70)
    logger.info(" 🔄 ACTUALIZACIÓN AUTOMÁTICA INICIADA ".center(70))
    logger.info("="*70 + "\n")
    
    try:
        scraper = FUTBINScraper()
        db = DatabaseManager()
        
        # Actualización completa: 100 páginas = ~3000 jugadores
        updated = scraper.update_database_prices(db, use_all_futbin=True, max_pages=100)
        
        logger.info("\n" + "="*70)
        logger.info(f" ✅ ACTUALIZACIÓN COMPLETADA: {updated} jugadores ".center(70))
        logger.info(f" ⏰ Próxima actualización en 1 hora ".center(70))
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Error en actualización: {e}\n")

def main():
    """Ejecuta el auto-actualizador"""
    print("\n" + "="*70)
    print(" 🤖 AUTO-ACTUALIZADOR DE PRECIOS PC - FUTBIN ".center(70))
    print("="*70)
    print(f"\n⏰ Horarios de actualización:")
    print(f"   • 9:00 AM")
    print(f"   • 1:00 PM")
    print(f"   • 10:00 PM")
    print(f"\n🎯 Presiona Ctrl+C para detener\n")
    print("="*70 + "\n")
    
    # Ejecutar actualización inmediata
    logger.info("🚀 Ejecutando primera actualización...")
    update_prices()
    
    # Programar actualizaciones a las 9 AM, 1 PM y 10 PM
    schedule.every().day.at("09:00").do(update_prices)
    schedule.every().day.at("13:00").do(update_prices)
    schedule.every().day.at("22:00").do(update_prices)
    
    logger.info("⏰ Actualizaciones programadas: 9:00 AM, 1:00 PM, 10:00 PM")
    
    # Loop infinito
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print(" ⏹️  AUTO-ACTUALIZADOR DETENIDO ".center(70))
        print("="*70 + "\n")

if __name__ == "__main__":
    main()
