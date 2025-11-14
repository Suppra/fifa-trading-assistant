"""
Interactive Discord Configuration Script
Helps you set up Discord bot easily
"""

import os
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("  🤖 CONFIGURACIÓN INTERACTIVA DE DISCORD BOT")
    print("="*70)
    
    print("\n📋 Tu Application ID: 1438711490541785158")
    print("\n🔗 Links útiles:")
    print("   Bot Token: https://discord.com/developers/applications/1438711490541785158/bot")
    print("   Invitar Bot: https://discord.com/developers/applications/1438711490541785158/oauth2/url-generator")
    
    print("\n" + "-"*70)
    print("PASO 1: Obtener el TOKEN del bot")
    print("-"*70)
    print("1. Abre: https://discord.com/developers/applications/1438711490541785158/bot")
    print("2. Click en 'Reset Token' (o 'Add Bot' si es la primera vez)")
    print("3. Copia el token completo (empieza con MTQz...)")
    print("4. ⚠️  IMPORTANTE: Habilita 'MESSAGE CONTENT INTENT'")
    print("5. Click 'Save Changes'")
    
    token = input("\n👉 Pega tu DISCORD_BOT_TOKEN aquí: ").strip()
    
    if not token or token == "your_discord_bot_token_here":
        print("\n❌ Token inválido. Inténtalo de nuevo.")
        return
    
    print("\n" + "-"*70)
    print("PASO 2: Invitar el bot a tu servidor")
    print("-"*70)
    print("1. Abre: https://discord.com/developers/applications/1438711490541785158/oauth2/url-generator")
    print("2. Selecciona scope: ✅ bot")
    print("3. Selecciona permisos:")
    print("   ✅ View Channels")
    print("   ✅ Send Messages")
    print("   ✅ Embed Links")
    print("   ✅ Read Message History")
    print("4. Copia la URL generada")
    print("5. Pégala en tu navegador")
    print("6. Selecciona tu servidor y autoriza")
    
    input("\n⏸️  Presiona Enter cuando hayas invitado el bot a tu servidor...")
    
    print("\n" + "-"*70)
    print("PASO 3: Obtener ID del canal")
    print("-"*70)
    print("1. En Discord, ve a Settings > Advanced")
    print("2. Activa 'Developer Mode'")
    print("3. Click DERECHO en el canal donde quieres notificaciones")
    print("4. Click en 'Copy ID'")
    
    channel_id = input("\n👉 Pega tu DISCORD_CHANNEL_ID aquí: ").strip()
    
    if not channel_id or not channel_id.isdigit():
        print("\n❌ Channel ID inválido (debe ser solo números). Inténtalo de nuevo.")
        return
    
    # Update .env file
    print("\n" + "-"*70)
    print("💾 Guardando configuración...")
    print("-"*70)
    
    env_path = Path('.env')
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update or add Discord config
        token_found = False
        channel_found = False
        
        for i, line in enumerate(lines):
            if line.startswith('DISCORD_BOT_TOKEN='):
                lines[i] = f'DISCORD_BOT_TOKEN={token}\n'
                token_found = True
            elif line.startswith('DISCORD_CHANNEL_ID='):
                lines[i] = f'DISCORD_CHANNEL_ID={channel_id}\n'
                channel_found = True
        
        if not token_found:
            lines.append(f'\nDISCORD_BOT_TOKEN={token}\n')
        if not channel_found:
            lines.append(f'DISCORD_CHANNEL_ID={channel_id}\n')
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Configuración guardada en .env")
    else:
        print("❌ Archivo .env no encontrado")
        return
    
    print("\n" + "="*70)
    print("  ✅ CONFIGURACIÓN COMPLETADA")
    print("="*70)
    
    print("\n📊 Resumen de configuración:")
    print(f"   Token: {token[:20]}...{token[-10:]}")
    print(f"   Channel ID: {channel_id}")
    
    print("\n🚀 Próximos pasos:")
    print("\n1. INICIAR EL BOT:")
    print("   Opción A (Recomendado):")
    print("      python desktop_app.py")
    print("      → Pestaña Discord > Click 'Conectar Discord'")
    print("\n   Opción B:")
    print("      python discord_bot.py")
    
    print("\n2. PROBAR EN DISCORD:")
    print("   En tu canal, escribe:")
    print("      !fc26 ayuda")
    
    print("\n3. COMANDOS DISPONIBLES:")
    print("   !fc26 status              - Ver estado del bot")
    print("   !fc26 recomendaciones     - Ver mejores compras")
    print("   !fc26 vender              - Ver qué vender")
    print("   !fc26 presupuesto 50000   - Actualizar presupuesto")
    
    print("\n💡 El bot enviará recomendaciones automáticas cada día a las 9:00 AM")
    
    print("\n" + "="*70)
    
    start_now = input("\n¿Quieres iniciar el bot ahora? (s/n): ").strip().lower()
    
    if start_now == 's':
        print("\n🚀 Iniciando Discord bot...")
        print("   Presiona Ctrl+C para detener\n")
        import subprocess
        import sys
        subprocess.run([sys.executable, 'discord_bot.py'])
    else:
        print("\n👋 ¡Configuración completada! Inicia el bot cuando quieras con:")
        print("   python discord_bot.py")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
