"""
Quick launcher for Modern UI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.desktop_app.modern_ui import ModernTradingApp

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ⚽ EA FC 26 TRADING BOT - ULTRA MODERN INTERFACE")
    print("="*60)
    print("\n  Características:")
    print("    ✨ Diseño Glassmorphism profesional")
    print("    📊 Dashboard interactivo en tiempo real")
    print("    🎯 20 jugadores con datos históricos")
    print("    💰 Sistema de presupuesto optimizado para 11k")
    print("    🎨 Inspirado en: Spotify, Discord, Notion, GitHub")
    print("\n" + "="*60 + "\n")
    
    app = ModernTradingApp()
    app.run()
