"""
Script de actualización en segundo plano para FUTBIN
Se ejecuta sin necesidad de tener la app abierta
Usar con pythonw.exe para ejecutar sin ventana
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import schedule

# Configurar paths
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Crear directorio de logs si no existe
LOGS_DIR = SCRIPT_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'background_updater.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from app.data_collection.futbin_scraper import FUTBINScraper
from app.database.db_manager import DatabaseManager


def update_prices():
    """Actualizar precios de FUTBIN (100 páginas)"""
    try:
        logger.info("\n" + "="*70)
        logger.info(" 🔄 ACTUALIZACIÓN AUTOMÁTICA INICIADA ".center(70))
        logger.info("="*70)
        logger.info(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("📊 Procesando 100 páginas (~3000 jugadores)")
        logger.info("⏱️ Tiempo estimado: 2-3 horas\n")
        
        db = DatabaseManager()
        scraper = FUTBINScraper()
        
        # Actualización completa
        start_time = time.time()
        updated = scraper.update_database_prices(db, use_all_futbin=True, max_pages=100)
        elapsed = time.time() - start_time
        
        # Calcular tiempo
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info("\n" + "="*70)
        logger.info(f" ✅ ACTUALIZACIÓN COMPLETADA ".center(70))
        logger.info(f" 📊 {updated} jugadores actualizados ".center(70))
        logger.info(f" ⏱️ Tiempo: {hours}h {minutes}m {seconds}s ".center(70))
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Error en actualización: {e}\n", exc_info=True)


def main():
    """Loop principal"""
    logger.info("\n" + "="*70)
    logger.info(" 🤖 ACTUALIZADOR EN SEGUNDO PLANO - EA FC 26 ".center(70))
    logger.info("="*70)
    logger.info("\n⏰ Horarios programados:")
    logger.info("   • 9:00 AM  - Actualización matutina")
    logger.info("   • 1:00 PM  - Actualización mediodía")
    logger.info("   • 10:00 PM - Actualización nocturna")
    logger.info("\n📊 100 páginas (~3000 jugadores) por actualización")
    logger.info("⏱️ Duración: 2-3 horas por actualización")
    logger.info("\n✅ Servicio iniciado. Esperando horarios...\n")
    logger.info("="*70 + "\n")
    
    # Programar actualizaciones
    schedule.every().day.at("09:00").do(update_prices)
    schedule.every().day.at("13:00").do(update_prices)
    schedule.every().day.at("22:00").do(update_prices)
    
    # Loop infinito
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    except KeyboardInterrupt:
        logger.info("\n" + "="*70)
        logger.info(" ⏹️ SERVICIO DETENIDO ".center(70))
        logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()
