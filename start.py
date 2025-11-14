"""
Quick start script - Setup inicial rápido para el bot
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("🎮 EA FC 26 Trading Assistant - Setup Inicial")
    print("=" * 70)
    print()
    
    # Check if .env exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creando archivo .env desde .env.example...")
        
        # Read example and create .env
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo .env creado")
        print()
    
    # Show current configuration
    print("⚙️  CONFIGURACIÓN ACTUAL:")
    print("-" * 70)
    print("💰 Presupuesto inicial: 11,000 coins")
    print("📊 Max precio compra: 9,000 coins")
    print("💵 Reserva mínima: 2,000 coins")
    print("📦 Max cartas: 3 cartas simultáneas")
    print("📈 Profit mínimo: 10% (1,000+ coins)")
    print("⭐ Rating focus: 82-84 (fodder)")
    print("-" * 70)
    print()
    
    # Check dependencies
    print("🔍 Verificando dependencias...")
    try:
        import requests
        import pandas
        import flask
        print("✅ Todas las dependencias instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return
    print()
    
    # Options
    print("🚀 ¿Qué quieres hacer?")
    print("-" * 70)
    print("1. 🌐 Iniciar Dashboard Web (recomendado)")
    print("2. 💻 Modo Interactivo (consola)")
    print("3. 📖 Ver documentación")
    print("4. ⚙️  Editar configuración")
    print("5. 🚪 Salir")
    print("-" * 70)
    
    choice = input("\nElige una opción (1-5): ").strip()
    
    if choice == "1":
        print("\n🌐 Iniciando Dashboard Web...")
        print("📍 Abre tu navegador en: http://localhost:5000")
        print("⏸️  Presiona Ctrl+C para detener\n")
        os.system(f"{sys.executable} main.py")
        
    elif choice == "2":
        print("\n💻 Iniciando Modo Interactivo...")
        os.system(f"{sys.executable} trading_assistant.py")
        
    elif choice == "3":
        print("\n📖 DOCUMENTACIÓN DISPONIBLE:")
        print("-" * 70)
        print("1. README.md - Introducción y características")
        print("2. GUIA_USO.md - Tutorial paso a paso")
        print("3. ESTRATEGIAS_11K.md - Estrategias para duplicar 11k coins")
        print("-" * 70)
        
        doc = input("\n¿Cuál quieres abrir? (1-3): ").strip()
        docs = {
            "1": "README.md",
            "2": "GUIA_USO.md", 
            "3": "ESTRATEGIAS_11K.md"
        }
        
        if doc in docs:
            filepath = Path(docs[doc])
            if filepath.exists():
                # Try to open with default markdown viewer
                if os.name == 'nt':  # Windows
                    os.system(f'start {filepath}')
                else:
                    os.system(f'open {filepath}')
            else:
                print(f"❌ Archivo {docs[doc]} no encontrado")
        
    elif choice == "4":
        print("\n⚙️  ARCHIVOS DE CONFIGURACIÓN:")
        print("-" * 70)
        print("1. .env - Variables de entorno (presupuesto, límites)")
        print("2. config.yaml - Configuración avanzada (estrategias, ligas)")
        print("-" * 70)
        
        config = input("\n¿Cuál quieres editar? (1-2): ").strip()
        
        if config == "1":
            if os.name == 'nt':
                os.system('notepad .env')
            else:
                os.system('nano .env')
        elif config == "2":
            if os.name == 'nt':
                os.system('notepad config.yaml')
            else:
                os.system('nano config.yaml')
        
        print("\n✅ Configuración actualizada")
        print("💡 Reinicia el bot para aplicar cambios")
        
    elif choice == "5":
        print("\n👋 ¡Hasta luego!")
        return
    
    else:
        print("\n❌ Opción no válida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
