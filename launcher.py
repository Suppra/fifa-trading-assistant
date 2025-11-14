"""
Advanced launcher for EA FC 26 Trading Bot
Includes all features: Desktop App, Discord, Budget Management
MVC Architecture
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime


def print_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🎮 EA FC 26 TRADING BOT 🎮                        ║
║                                                              ║
║     Bot Inteligente de Trading con IA y Discord             ║
║     • Presupuesto Dinámico Adaptable                        ║
║     • App de Escritorio Windows                             ║
║     • Integración con Discord                               ║
║     • Estrategias según Fecha/Hora                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main menu for EA FC 26 Trading Bot"""
    while True:
        print_banner()
        print("\n📋 Selecciona una opción:\n")
        print("  1. 🌐 Iniciar Dashboard Web (puerto 5000)")
        print("  2. 🖥️  Iniciar App de Escritorio (Windows)")
        print("  3. 💬 Iniciar Bot de Discord")
        print("  4. 💻 Iniciar Asistente CLI")
        print("  5. 📚 Ver Documentación")
        print("  6. ⚙️  Configurar Presupuesto")
        print("  7. 🔧 Configurar .env")
        print("  8. 📊 Ver Estado del Sistema")
        print("  9. ❌ Salir")
        print("\n" + "="*60)
        
        choice = input("\n👉 Ingresa el número de tu elección: ").strip()
        
        if choice == '1':
            launch_dashboard()
        elif choice == '2':
            launch_desktop_app()
        elif choice == '3':
            launch_discord_bot()
        elif choice == '4':
            launch_cli()
        elif choice == '5':
            show_documentation()
        elif choice == '6':
            configure_budget()
        elif choice == '7':
            setup_env()
        elif choice == '8':
            show_system_status()
        elif choice == '9':
            print("\n👋 ¡Hasta luego! Buena suerte con el trading.\n")
            break
        else:
            print("\n❌ Opción inválida. Por favor ingresa un número del 1 al 9.")
            time.sleep(2)


def launch_dashboard():
    """Launch web dashboard"""
    print("\n🌐 Iniciando Dashboard Web...")
    print("   El dashboard estará disponible en: http://localhost:5000")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para continuar...")


def launch_desktop_app():
    """Launch Windows desktop application"""
    print("\n🖥️  Iniciando App de Escritorio...")
    print("   Aplicación nativa de Windows con Tkinter")
    print("   Se abrirá en una nueva ventana\n")
    
    try:
        subprocess.run([sys.executable, 'desktop_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n✅ App de escritorio cerrada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para continuar...")


def launch_discord_bot():
    """Launch Discord bot"""
    print("\n💬 Iniciando Bot de Discord...")
    print("   Asegúrate de haber configurado DISCORD_BOT_TOKEN y DISCORD_CHANNEL_ID en .env")
    print("   Presiona Ctrl+C para detener\n")
    
    # Check if Discord is configured
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'your_discord_bot_token_here' in content or 'DISCORD_BOT_TOKEN' not in content:
                print("⚠️  ADVERTENCIA: Discord no está configurado")
                print("\n📝 Para configurar Discord:")
                print("   1. Ve a https://discord.com/developers/applications")
                print("   2. Crea un bot y copia el token")
                print("   3. Edita el archivo .env y agrega:")
                print("      DISCORD_BOT_TOKEN=tu_token_aquí")
                print("      DISCORD_CHANNEL_ID=tu_canal_id_aquí")
                print("\n   O usa la app de escritorio (opción 2) para configurarlo visualmente")
                input("\nPresiona Enter para continuar...")
                return
    
    try:
        subprocess.run([sys.executable, 'discord_bot.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n✅ Bot de Discord detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para continuar...")


def launch_cli():
    """Launch CLI assistant"""
    print("\n💻 Iniciando Asistente CLI...")
    print("   Interfaz de línea de comandos interactiva\n")
    
    try:
        subprocess.run([sys.executable, 'trading_assistant.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n✅ CLI cerrado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para continuar...")


def show_documentation():
    """Show documentation menu"""
    while True:
        print("\n" + "="*60)
        print("  📚 DOCUMENTACIÓN")
        print("="*60)
        print("\n  1. 📖 README - Información general")
        print("  2. 📋 GUIA_USO - Cómo usar el bot")
        print("  3. 💰 ESTRATEGIAS_11K - Trading con bajo presupuesto")
        print("  4. ✨ NUEVAS_FUNCIONES - App de escritorio y Discord")
        print("  5. 🔙 Volver al menú principal")
        print("\n" + "="*60)
        
        choice = input("\n👉 Selecciona un documento: ").strip()
        
        docs = {
            '1': 'README.md',
            '2': 'GUIA_USO.md',
            '3': 'ESTRATEGIAS_11K.md',
            '4': 'NUEVAS_FUNCIONES.md'
        }
        
        if choice == '5':
            break
        elif choice in docs:
            try:
                if sys.platform == 'win32':
                    os.startfile(docs[choice])
                else:
                    subprocess.run(['xdg-open', docs[choice]])
                print(f"\n✅ Abriendo {docs[choice]}...")
                time.sleep(1)
            except Exception as e:
                print(f"\n❌ Error abriendo archivo: {e}")
                input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Opción inválida")
            time.sleep(1)


def configure_budget():
    """Configure budget interactively"""
    print("\n" + "="*60)
    print("  💰 CONFIGURACIÓN DE PRESUPUESTO")
    print("="*60)
    
    # Load current budget
    budget_file = Path('budget_config.json')
    current_budget = 11000
    data = {}
    
    if budget_file.exists():
        try:
            with open(budget_file, 'r') as f:
                data = json.load(f)
                current_budget = data.get('current_budget', 11000)
        except:
            pass
    
    print(f"\n📊 Presupuesto actual: {current_budget:,} monedas")
    print("\n💡 El bot ajustará automáticamente sus estrategias según tu presupuesto:")
    print("   • 0-20k: BAJO - Fodder, cartas rating 82-84")
    print("   • 20-50k: MEDIO - Meta players, rating 84-86")
    print("   • 50-100k: ALTO - Special cards, rating 86-88")
    print("   • 100k+: ELITE - Icons, cartas top rating 88+")
    
    try:
        new_budget = input("\n👉 Ingresa tu nuevo presupuesto (Enter para cancelar): ").strip()
        
        if not new_budget:
            print("\n❌ Cancelado")
            input("\nPresiona Enter para continuar...")
            return
        
        new_budget = int(new_budget)
        
        if new_budget < 0:
            print("\n❌ El presupuesto no puede ser negativo")
            input("\nPresiona Enter para continuar...")
            return
        
        # Determine tier
        if new_budget < 20000:
            tier = "BAJO"
        elif new_budget < 50000:
            tier = "MEDIO"
        elif new_budget < 100000:
            tier = "ALTO"
        else:
            tier = "ELITE"
        
        # Save budget
        budget_data = {
            "current_budget": new_budget,
            "initial_budget": current_budget if not budget_file.exists() else data.get('initial_budget', 11000),
            "total_profit": new_budget - current_budget if new_budget > current_budget else 0,
            "invested": 0,
            "reserve": min(2000, int(new_budget * 0.1)),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(budget_file, 'w') as f:
            json.dump(budget_data, f, indent=4)
        
        print(f"\n✅ Presupuesto actualizado a {new_budget:,} monedas")
        print(f"📊 Nuevo nivel: {tier}")
        print(f"💾 Guardado en budget_config.json")
        
        input("\nPresiona Enter para continuar...")
        
    except ValueError:
        print("\n❌ Por favor ingresa un número válido")
        input("\nPresiona Enter para continuar...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para continuar...")


def setup_env():
    """Setup .env file"""
    env_path = Path('.env')
    env_example = Path('.env.example')
    
    if not env_path.exists() and env_example.exists():
        print("\n📝 Creando .env desde .env.example...")
        
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo .env creado")
        print("\n💡 Edita .env para personalizar la configuración")
    else:
        print("\n📝 Editando .env...")
    
    try:
        if sys.platform == 'win32':
            os.startfile('.env')
        else:
            subprocess.run(['nano', '.env'])
        print("\n✅ Archivo .env abierto")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPresiona Enter para continuar...")


def show_system_status():
    """Show system status and configuration"""
    print("\n" + "="*60)
    print("  📊 ESTADO DEL SISTEMA")
    print("="*60)
    
    # Budget
    budget_file = Path('budget_config.json')
    if budget_file.exists():
        try:
            with open(budget_file, 'r') as f:
                data = json.load(f)
                budget = data.get('current_budget', 0)
                profit = data.get('total_profit', 0)
                invested = data.get('invested', 0)
                
                # Determine tier
                if budget < 20000:
                    tier = "BAJO 🥉"
                elif budget < 50000:
                    tier = "MEDIO 🥈"
                elif budget < 100000:
                    tier = "ALTO 🥇"
                else:
                    tier = "ELITE 💎"
                
                print(f"\n💰 Presupuesto: {budget:,} monedas")
                print(f"📊 Nivel: {tier}")
                print(f"📈 Ganancia Total: {profit:,} monedas")
                print(f"💵 Invertido: {invested:,} monedas")
        except:
            print("\n⚠️  No se pudo cargar información de presupuesto")
    else:
        print("\n⚠️  Archivo de presupuesto no encontrado")
    
    # Dependencies
    print("\n📦 Dependencias:")
    critical_deps = ['discord', 'flask', 'pandas', 'sqlalchemy']
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} (no instalado)")
    
    # Files
    print("\n📁 Archivos:")
    critical_files = ['config.yaml', '.env', 'budget_config.json', 'main.py', 'desktop_app.py', 'discord_bot.py']
    for file in critical_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (no encontrado)")
    
    # Discord config
    print("\n💬 Discord:")
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'DISCORD_BOT_TOKEN' in content and 'your_discord_bot_token_here' not in content:
                print("   ✅ Configurado")
            else:
                print("   ❌ No configurado")
    else:
        print("   ❌ Archivo .env no encontrado")
    
    # Datetime
    print(f"\n⏰ Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    hour = datetime.now().hour
    if hour >= 1 and hour <= 4:
        market_status = "🌙 Madrugada - Sniping"
    elif hour >= 18 and hour <= 21:
        market_status = "🔥 Hora Pico - Vender"
    else:
        market_status = "✅ Normal"
    
    print(f"📊 Estado del Mercado: {market_status}")
    
    input("\n\nPresiona Enter para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego! Buena suerte con el trading.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
