"""
Discord Bot Service - Se ejecuta en segundo plano automáticamente
Independiente de la aplicación de escritorio
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.discord_bot.discord_notifier import DiscordNotifier
from src.utils.config_loader import ConfigLoader

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/discord_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main service loop"""
    # Archivo de estado
    status_file = Path('logs/discord_status.json')
    
    def update_status(status, message=""):
        """Actualiza el archivo de estado"""
        import json
        from datetime import datetime
        status_data = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'pid': os.getpid()
        }
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    try:
        update_status('starting', 'Iniciando servicio...')
        
        # Load config
        config = ConfigLoader()
        
        token = config.get('discord.bot_token')
        channel_id = config.get('discord.channel_id')
        
        if not token or not channel_id:
            logger.warning("⚠️ Discord no configurado - esperando configuración...")
            logger.info("💡 Configura Discord desde la app de escritorio (pestaña Discord)")
            update_status('waiting_config', 'Esperando configuración de Discord')
            
            # Esperar a que se configure (verificar cada 30 segundos)
            while True:
                await asyncio.sleep(30)
                config.reload()
                token = config.get('discord.bot_token')
                channel_id = config.get('discord.channel_id')
                
                if token and channel_id:
                    logger.info("✅ Configuración de Discord detectada!")
                    break
        
        logger.info("🤖 Iniciando Discord Bot Service...")
        logger.info(f"📡 Canal ID: {channel_id}")
        update_status('connecting', 'Conectando al servidor de Discord...')
        
        # Create bot
        bot = DiscordNotifier(token=token, channel_id=int(channel_id))
        
        # Agregar handler para on_ready que actualice el estado
        original_on_ready = bot.bot.event(bot.bot.on_ready)
        
        @bot.bot.event
        async def on_ready():
            logger.info(f"✅ Bot conectado como {bot.bot.user}")
            update_status('connected', f'Conectado como {bot.bot.user}')
            # Llamar al on_ready original si existe
            if original_on_ready:
                await original_on_ready()
        
        # Run bot (this blocks until bot stops)
        await bot.bot.start(token)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servicio detenido por el usuario")
        update_status('stopped', 'Servicio detenido por el usuario')
    except Exception as e:
        logger.error(f"❌ Error en servicio de Discord: {e}")
        update_status('error', str(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  DISCORD BOT SERVICE - EA FC 26 TRADING ASSISTANT")
    print("="*70)
    print("\n🔄 Iniciando servicio en segundo plano...")
    print("📋 Este servicio se ejecuta independientemente de la app")
    print("💡 Presiona Ctrl+C para detener\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Servicio detenido correctamente")
