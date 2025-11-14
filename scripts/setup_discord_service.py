"""
Instalador de Servicio de Discord para Windows
Configura el bot para ejecutarse automáticamente al iniciar Windows
"""

import os
import sys
import winreg
from pathlib import Path

def install_discord_service():
    """Instala el servicio de Discord en el inicio de Windows"""
    
    print("\n" + "="*70)
    print("  INSTALADOR DE SERVICIO - DISCORD BOT")
    print("="*70 + "\n")
    
    # Obtener rutas
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    script_path = current_dir / "start_discord_service.py"
    
    # Crear script VBS para ejecutar en segundo plano (sin ventana)
    vbs_script = current_dir / "run_discord_silent.vbs"
    
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{python_exe}"" ""{script_path}""", 0, False
Set WshShell = Nothing
'''
    
    with open(vbs_script, 'w') as f:
        f.write(vbs_content)
    
    print(f"✅ Script VBS creado: {vbs_script}\n")
    
    # Registrar en inicio de Windows usando registro
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
        
        # Nombre del servicio
        service_name = "EA_FC26_Discord_Bot"
        
        # Valor: ruta al script VBS
        winreg.SetValueEx(key, service_name, 0, winreg.REG_SZ, str(vbs_script))
        winreg.CloseKey(key)
        
        print("✅ Servicio registrado en inicio de Windows\n")
        print("📋 CONFIGURACIÓN COMPLETADA:")
        print(f"   Nombre: {service_name}")
        print(f"   Script: {vbs_script}")
        print(f"   Python: {python_exe}\n")
        
        print("🔄 El bot de Discord se iniciará automáticamente cuando:")
        print("   1. Inicies sesión en Windows")
        print("   2. Reinicies tu PC\n")
        
        print("💡 SIGUIENTE PASO:")
        print("   Configura Discord desde la app de escritorio (pestaña Discord)")
        print("   O ejecuta ahora: python start_discord_service.py\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al registrar servicio: {e}")
        print("\n💡 SOLUCIÓN ALTERNATIVA:")
        print("   1. Presiona Win + R")
        print("   2. Escribe: shell:startup")
        print("   3. Copia el archivo run_discord_silent.vbs a esa carpeta\n")
        return False


def uninstall_discord_service():
    """Desinstala el servicio de Discord"""
    
    print("\n" + "="*70)
    print("  DESINSTALADOR DE SERVICIO - DISCORD BOT")
    print("="*70 + "\n")
    
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
        
        service_name = "EA_FC26_Discord_Bot"
        
        try:
            winreg.DeleteValue(key, service_name)
            print(f"✅ Servicio '{service_name}' eliminado del inicio\n")
        except FileNotFoundError:
            print(f"⚠️ Servicio '{service_name}' no encontrado en registro\n")
        
        winreg.CloseKey(key)
        
        # Eliminar script VBS
        current_dir = Path(__file__).parent.absolute()
        vbs_script = current_dir / "run_discord_silent.vbs"
        
        if vbs_script.exists():
            vbs_script.unlink()
            print(f"✅ Script VBS eliminado: {vbs_script}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al desinstalar servicio: {e}\n")
        return False


if __name__ == "__main__":
    print("\n¿Qué deseas hacer?\n")
    print("  1. Instalar servicio (inicio automático)")
    print("  2. Desinstalar servicio")
    print("  3. Salir\n")
    
    choice = input("Opción (1/2/3): ").strip()
    
    if choice == '1':
        success = install_discord_service()
        if success:
            start_now = input("\n¿Iniciar servicio ahora? (s/n): ").strip().lower()
            if start_now == 's':
                print("\n🚀 Iniciando servicio...")
                os.system(f'python start_discord_service.py')
    elif choice == '2':
        uninstall_discord_service()
    else:
        print("\n👋 Saliendo...")
    
    input("\nPresiona Enter para cerrar...")
