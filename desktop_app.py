"""
Launch script for EA FC 26 Trading Bot Desktop Application
Windows native app with Tkinter
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.desktop_app.main_window import TradingBotApp
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    try:
        logger.info("Starting EA FC 26 Trading Bot Desktop Application")
        
        # Create and run app
        app = TradingBotApp()
        app.run()
        
    except Exception as e:
        logger.error(f"Error starting desktop application: {e}")
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
