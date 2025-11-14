"""
Launcher for EA FC 26 Trading Bot - Desktop Application
Windows native app with Tkinter
MVC Architecture

GARANTIZA DATOS REALES: Actualiza precios desde FUTBIN antes de iniciar
"""

import sys
import logging

def main():
    """Launch EA FC 26 Trading Bot Desktop Application"""
    
    # Setup logging first
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("  🎮 EA FC 26 TRADING BOT - Aplicación de Escritorio")
    print("="*60)
    print("\n  🔄 Actualizando datos reales desde FUTBIN...")
    print("  ⚡ Esto garantiza información precisa y actualizada")
    print("\n" + "="*60 + "\n")
    
    try:
        # Import splash screen
        from app.views.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        
        # Flag to track if update completed
        update_completed = [False]
        
        def on_update_complete(success):
            """Callback when update finishes"""
            update_completed[0] = True
            splash.close()
            
            if success:
                logger.info("✅ Datos actualizados correctamente desde FUTBIN")
            else:
                logger.warning("⚠️ Actualización completada con advertencias")
            
            # Now launch main application
            launch_main_app()
        
        # Start update process
        splash.start_update(on_update_complete)
        
        # Show splash screen (blocks until closed)
        splash.show()
        
    except KeyboardInterrupt:
        print("\n\n✅ Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


def launch_main_app():
    """Launch main trading bot application"""
    try:
        from app.views.desktop_ui import TradingBotApp
        
        print("\n" + "="*60)
        print("  ✅ Iniciando aplicación principal...")
        print("="*60 + "\n")
        
        # Create and run app
        app = TradingBotApp()
        app.run()
        
    except Exception as e:
        print(f"\n❌ Error en aplicación principal: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


if __name__ == '__main__':
    main()
