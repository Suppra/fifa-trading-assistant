"""
Launch script for EA FC 26 Trading Bot Discord Integration
Run this to start the Discord bot separately
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.discord_service import DiscordNotifier
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for Discord bot"""
    try:
        # Load environment variables
        load_dotenv()
        
        token = os.getenv('DISCORD_BOT_TOKEN')
        channel_id = os.getenv('DISCORD_CHANNEL_ID')
        
        if not token or not channel_id:
            logger.error("DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID must be set in .env file")
            print("\n❌ Error: Configuración de Discord incompleta")
            print("\nPor favor configura las siguientes variables en tu archivo .env:")
            print("  - DISCORD_BOT_TOKEN=tu_token_aquí")
            print("  - DISCORD_CHANNEL_ID=tu_canal_id_aquí")
            print("\nVe a la pestaña Discord en la app de escritorio para más instrucciones.")
            sys.exit(1)
        
        logger.info("Starting Discord bot...")
        print("\n🤖 Iniciando bot de Discord...")
        print(f"📡 Canal ID: {channel_id}")
        print("\nEl bot enviará recomendaciones diarias a las 9:00 AM")
        print("Comandos disponibles:")
        print("  !fc26 status - Ver estado del bot")
        print("  !fc26 recomendaciones - Ver compras")
        print("  !fc26 vender - Ver ventas")
        print("  !fc26 presupuesto [cantidad] - Actualizar presupuesto")
        print("  !fc26 ayuda - Ver todos los comandos")
        print("\nPresiona Ctrl+C para detener el bot\n")
        
        # Create and run bot
        bot = DiscordNotifier(token, int(channel_id))
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Discord bot stopped by user")
        print("\n\n✅ Bot detenido correctamente")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
