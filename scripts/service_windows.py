"""
Servicio de Windows para actualizaciones automáticas de FUTBIN
Se ejecuta en segundo plano sin necesidad de tener la app abierta

Para instalar el servicio:
    python service_windows.py install

Para iniciar el servicio:
    python service_windows.py start

Para detener el servicio:
    python service_windows.py stop

Para desinstalar el servicio:
    python service_windows.py remove
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import time
import logging
from pathlib import Path
import schedule

# Configurar paths
SERVICE_DIR = Path(__file__).parent
sys.path.insert(0, str(SERVICE_DIR))

from app.data_collection.futbin_scraper import FUTBINScraper
from app.database.db_manager import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(SERVICE_DIR / 'logs' / 'service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class FC26TradingBotService(win32serviceutil.ServiceFramework):
    """Servicio de Windows para EA FC 26 Trading Bot"""
    
    _svc_name_ = "FC26TradingBot"
    _svc_display_name_ = "EA FC 26 Trading Bot - Auto Updater"
    _svc_description_ = "Actualiza precios de FUTBIN automáticamente a las 9 AM, 1 PM y 10 PM"
    
    def __init__(self, args):
        """Inicializar servicio"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
        
    def SvcStop(self):
        """Detener servicio"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        logger.info("⏹️ Servicio detenido")
        
    def SvcDoRun(self):
        """Ejecutar servicio"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logger.info("🚀 Servicio EA FC 26 Trading Bot iniciado")
        self.main()
        
    def update_prices(self):
        """Actualizar precios de FUTBIN"""
        try:
            logger.info("\n" + "="*70)
            logger.info(" 🔄 ACTUALIZACIÓN AUTOMÁTICA INICIADA ".center(70))
            logger.info("="*70)
            logger.info("\n📊 Procesando 100 páginas (~3000 jugadores)")
            logger.info("⏱️ Tiempo estimado: 2-3 horas\n")
            
            db = DatabaseManager()
            scraper = FUTBINScraper()
            
            # Actualización completa
            updated = scraper.update_database_prices(db, use_all_futbin=True, max_pages=100)
            
            logger.info("\n" + "="*70)
            logger.info(f" ✅ ACTUALIZACIÓN COMPLETADA: {updated} jugadores ".center(70))
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"\n❌ Error en actualización: {e}\n", exc_info=True)
    
    def main(self):
        """Loop principal del servicio"""
        logger.info("⏰ Programando actualizaciones automáticas:")
        logger.info("   • 9:00 AM")
        logger.info("   • 1:00 PM")
        logger.info("   • 10:00 PM")
        
        # Programar actualizaciones
        schedule.every().day.at("09:00").do(self.update_prices)
        schedule.every().day.at("13:00").do(self.update_prices)
        schedule.every().day.at("22:00").do(self.update_prices)
        
        logger.info("\n✅ Servicio listo. Esperando horarios programados...")
        
        # Loop principal
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
            
            # Verificar si se debe detener
            if win32event.WaitForSingleObject(self.stop_event, 0) == win32event.WAIT_OBJECT_0:
                break


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Sin argumentos - mostrar ayuda
        print("\n" + "="*70)
        print(" 🤖 EA FC 26 TRADING BOT - SERVICIO DE WINDOWS ".center(70))
        print("="*70)
        print("\nComandos disponibles:")
        print("  python service_windows.py install    - Instalar servicio")
        print("  python service_windows.py start      - Iniciar servicio")
        print("  python service_windows.py stop       - Detener servicio")
        print("  python service_windows.py remove     - Desinstalar servicio")
        print("  python service_windows.py debug      - Ejecutar en modo debug")
        print("\n" + "="*70 + "\n")
        sys.exit(0)
    else:
        win32serviceutil.HandleCommandLine(FC26TradingBotService)
