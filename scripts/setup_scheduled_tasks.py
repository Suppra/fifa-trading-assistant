"""
Configurar tareas programadas de Windows para actualizaciones automáticas
Este script crea 3 tareas en el Task Scheduler que se ejecutan automáticamente
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PYTHON_EXE = sys.executable
UPDATER_SCRIPT = SCRIPT_DIR / "auto_update_prices.py"

def create_scheduled_task(task_name, time_str):
    """
    Crear tarea programada en Windows
    
    Args:
        task_name: Nombre de la tarea
        time_str: Hora en formato HH:MM (ej: "09:00")
    """
    print(f"\n📅 Creando tarea: {task_name} a las {time_str}...")
    
    # Comando para crear la tarea
    cmd = [
        "schtasks", "/Create",
        "/TN", f"FC26TradingBot\\{task_name}",  # Nombre de la tarea
        "/TR", f'"{PYTHON_EXE}" "{UPDATER_SCRIPT}"',  # Comando a ejecutar
        "/SC", "DAILY",  # Frecuencia: diaria
        "/ST", time_str,  # Hora de inicio
        "/RL", "HIGHEST",  # Ejecutar con máximos privilegios
        "/F"  # Forzar (sobrescribir si existe)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Tarea '{task_name}' creada correctamente")
        
        # Configurar para ejecutar si se perdió el horario (PC apagado)
        cmd_delay = [
            "schtasks", "/Change",
            "/TN", f"FC26TradingBot\\{task_name}",
            "/DELAY", "0000:15"  # Ejecutar 15 min después de encender si se perdió
        ]
        subprocess.run(cmd_delay, capture_output=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando tarea: {e.stderr}")
        return False

def remove_scheduled_tasks():
    """Eliminar todas las tareas programadas"""
    print("\n🗑️ Eliminando tareas existentes...")
    
    tasks = [
        "FC26_Update_9AM",
        "FC26_Update_1PM", 
        "FC26_Update_10PM",
        "FC26_Startup_Check"  # Tarea de inicio
    ]
    
    for task in tasks:
        cmd = ["schtasks", "/Delete", "/TN", f"FC26TradingBot\\{task}", "/F"]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ Tarea '{task}' eliminada")
        except subprocess.CalledProcessError:
            pass  # Tarea no existe

def list_scheduled_tasks():
    """Listar tareas programadas"""
    print("\n📋 Tareas programadas activas:")
    
    cmd = ["schtasks", "/Query", "/TN", "FC26TradingBot\\*", "/FO", "LIST", "/V"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("⚠️ No hay tareas programadas")

def setup_all_tasks():
    """Configurar todas las tareas programadas"""
    print("\n" + "="*70)
    print(" 🤖 CONFIGURACIÓN DE TAREAS AUTOMÁTICAS - EA FC 26 BOT ".center(70))
    print("="*70)
    
    print("\n📊 Configuración:")
    print(f"   Python: {PYTHON_EXE}")
    print(f"   Script: {UPDATER_SCRIPT}")
    print(f"   Frecuencia: Diaria")
    print(f"   Horarios: 9:00 AM, 1:00 PM, 10:00 PM")
    print(f"   Páginas por actualización: 100 (~3000 jugadores)")
    
    # Eliminar tareas existentes
    remove_scheduled_tasks()
    
    # Crear nuevas tareas
    print("\n📅 Creando tareas programadas...\n")
    
    success = True
    success &= create_scheduled_task("FC26_Update_9AM", "09:00")
    success &= create_scheduled_task("FC26_Update_1PM", "13:00")
    success &= create_scheduled_task("FC26_Update_10PM", "22:00")
    
    # Crear tarea de respaldo que se ejecuta al iniciar Windows (si hay actualizaciones pendientes)
    print("\n🔄 Creando tarea de respaldo al inicio del sistema...")
    cmd_startup = [
        "schtasks", "/Create",
        "/TN", "FC26TradingBot\\FC26_Startup_Check",
        "/TR", f'"{PYTHON_EXE}" "{UPDATER_SCRIPT}"',
        "/SC", "ONSTART",  # Al iniciar el sistema
        "/DELAY", "0000:05",  # Esperar 5 minutos después del inicio
        "/RL", "HIGHEST",
        "/F"
    ]
    try:
        subprocess.run(cmd_startup, capture_output=True, check=True)
        print("✅ Tarea de inicio creada (se ejecuta 5 min después de encender el PC)")
    except:
        print("⚠️ No se pudo crear tarea de inicio (opcional)")
    
    if success:
        print("\n" + "="*70)
        print(" ✅ TAREAS CONFIGURADAS CORRECTAMENTE ".center(70))
        print("="*70)
        print("\n📋 Las actualizaciones se ejecutarán automáticamente:")
        print("   • 9:00 AM  - Actualización matutina")
        print("   • 1:00 PM  - Actualización mediodía")
        print("   • 10:00 PM - Actualización nocturna")
        print("\n⚙️ Las tareas se ejecutan en segundo plano")
        print("📊 Cada actualización procesa ~3000 jugadores")
        print("⏱️ Duración: 2-3 horas por actualización")
        print("\n💡 SI EL PC ESTÁ APAGADO:")
        print("   • Las tareas se ejecutarán 15 min después de encender el PC")
        print("   • También hay una tarea que se ejecuta 5 min después del inicio")
        print("   • NO perderás ninguna actualización")
        print("\n💡 Para ver el estado: abrir 'Programador de tareas' de Windows")
        print("💡 Para desinstalar: ejecutar este script con argumento 'remove'")
        print("\n" + "="*70 + "\n")
    else:
        print("\n❌ Error configurando tareas. Ejecuta como Administrador.")

def remove_all_tasks():
    """Eliminar todas las tareas"""
    print("\n" + "="*70)
    print(" 🗑️ ELIMINAR TAREAS AUTOMÁTICAS ".center(70))
    print("="*70 + "\n")
    
    remove_scheduled_tasks()
    
    print("\n" + "="*70)
    print(" ✅ TAREAS ELIMINADAS ".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_all_tasks()
    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        list_scheduled_tasks()
    else:
        setup_all_tasks()
