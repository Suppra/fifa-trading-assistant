"""
Splash Screen con actualización de datos de FUTBIN
Garantiza que la aplicación siempre trabaje con datos reales
"""

import tkinter as tk
from tkinter import ttk
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SplashScreen:
    """Pantalla de carga con actualización de precios desde FUTBIN"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EA FC 26 Trading Bot")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Colors
        self.bg_color = "#1a1a1a"
        self.accent_color = "#00d4ff"
        self.text_color = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
        
        # Create UI
        self._create_ui()
        
        # Status variables
        self.current_step = ""
        self.progress_value = 0
        self.total_players = 0
        self.processed_players = 0
        self.start_time = None
        
    def _create_ui(self):
        """Create splash screen UI"""
        # Main container with border
        main_frame = tk.Frame(self.root, bg=self.accent_color, padx=2, pady=2)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Logo/Title
        title_frame = tk.Frame(content, bg=self.bg_color)
        title_frame.pack(pady=(40, 20))
        
        tk.Label(title_frame, text="🎮", font=("Segoe UI Emoji", 48),
                bg=self.bg_color).pack()
        
        tk.Label(title_frame, text="EA FC 26 TRADING BOT", 
                font=("Segoe UI", 24, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(pady=(10, 5))
        
        tk.Label(title_frame, text="Powered by FUTBIN Real Data", 
                font=("Segoe UI", 10),
                bg=self.bg_color, fg=self.accent_color).pack()
        
        tk.Label(title_frame, text="Created by xSuppra", 
                font=("Segoe UI", 8, "italic"),
                bg=self.bg_color, fg="#666666").pack(pady=(5, 0))
        
        # Status section
        status_frame = tk.Frame(content, bg=self.bg_color)
        status_frame.pack(pady=(30, 10), padx=40, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, 
                                     text="Inicializando...", 
                                     font=("Segoe UI", 11),
                                     bg=self.bg_color, fg=self.text_color)
        self.status_label.pack(anchor='w')
        
        # Progress bar
        progress_frame = tk.Frame(content, bg=self.bg_color)
        progress_frame.pack(pady=(10, 5), padx=40, fill=tk.X)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor=self.bg_color,
                       bordercolor=self.accent_color,
                       background=self.accent_color,
                       lightcolor=self.accent_color,
                       darkcolor=self.accent_color)
        
        self.progress = ttk.Progressbar(progress_frame, 
                                       mode='determinate',
                                       style="Custom.Horizontal.TProgressbar",
                                       length=520)
        self.progress.pack(fill=tk.X)
        
        # Progress details
        details_frame = tk.Frame(content, bg=self.bg_color)
        details_frame.pack(pady=(5, 10), padx=40, fill=tk.X)
        
        self.progress_label = tk.Label(details_frame, 
                                       text="0%", 
                                       font=("Segoe UI", 9),
                                       bg=self.bg_color, fg="#888888")
        self.progress_label.pack(side=tk.LEFT)
        
        self.time_label = tk.Label(details_frame, 
                                   text="", 
                                   font=("Segoe UI", 9),
                                   bg=self.bg_color, fg="#888888")
        self.time_label.pack(side=tk.RIGHT)
        
        # Info section
        info_frame = tk.Frame(content, bg=self.bg_color)
        info_frame.pack(pady=(20, 20), padx=40)
        
        tk.Label(info_frame, 
                text="⚡ Actualizando precios reales desde FUTBIN", 
                font=("Segoe UI", 9),
                bg=self.bg_color, fg="#666666").pack()
        
        tk.Label(info_frame, 
                text="Esto garantiza datos precisos para tus decisiones de trading", 
                font=("Segoe UI", 9),
                bg=self.bg_color, fg="#666666").pack()
        
        # Footer
        footer = tk.Label(content, 
                         text=f"© 2025 xSuppra • EA FC 26 Trading Bot • {datetime.now().strftime('%d/%m/%Y')}", 
                         font=("Segoe UI", 8),
                         bg=self.bg_color, fg="#444444")
        footer.pack(side=tk.BOTTOM, pady=10)
        
    def update_status(self, message: str):
        """Update status message"""
        self.current_step = message
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def update_progress(self, current: int, total: int):
        """Update progress bar"""
        self.processed_players = current
        self.total_players = total
        
        if total > 0:
            percentage = (current / total) * 100
            self.progress['value'] = percentage
            self.progress_label.config(text=f"{percentage:.1f}% • {current}/{total} jugadores")
            
            # Calculate ETA
            if self.start_time and current > 0:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = current / elapsed if elapsed > 0 else 0
                remaining = (total - current) / rate if rate > 0 else 0
                
                if remaining > 60:
                    eta_str = f"~{int(remaining/60)}min {int(remaining%60)}s restantes"
                else:
                    eta_str = f"~{int(remaining)}s restantes"
                
                self.time_label.config(text=eta_str)
        
        self.root.update_idletasks()
        
    def start_update(self, callback):
        """Start price update process with intelligent mode detection"""
        self.start_time = datetime.now()
        
        def run_update():
            try:
                from app.models.database import DatabaseManager
                from app.services.futbin_service import FUTBINScraper
                from app.utils.update_strategy import UpdateStrategy
                
                db = DatabaseManager()
                scraper = FUTBINScraper()
                strategy = UpdateStrategy()
                
                # Determine update mode
                update_mode = strategy.get_update_mode(force_full=False)
                
                logger.info(f"🎯 Modo de actualización: {update_mode}")
                
                # Progress callback
                def progress_callback(current, total, player_name=""):
                    msg = f"📊 Actualizando: {player_name}" if player_name else "📊 Actualizando..."
                    self.root.after(0, lambda: self.update_status(msg))
                    self.root.after(0, lambda: self.update_progress(current, total))
                
                if update_mode == 'initial':
                    # FIRST RUN: 50 pages parallel (~20 min)
                    self.update_status(f"🚀 Primera ejecución: Descarga paralela de 50 páginas...")
                    
                    pages = strategy.get_initial_pages()
                    all_players = scraper.get_all_players_parallel(
                        max_pages=pages,
                        num_threads=3,  # Reducido para evitar rate limiting
                        progress_callback=lambda p, t, name: progress_callback(p, t, name)
                    )
                    
                    self.update_status(f"💰 Obteniendo precios de {len(all_players)} jugadores...")
                    updated = self._update_players_batch(scraper, db, all_players, progress_callback)
                    
                    strategy.mark_first_run_complete(updated)
                    self.update_status(f"✅ Base inicial: {updated} jugadores")
                    
                elif update_mode == 'incremental':
                    # DAILY: Update existing only (~5 min)
                    self.update_status(f"🔄 Actualización diaria: Solo jugadores existentes...")
                    
                    updated = scraper.update_existing_players_incremental(
                        db_manager=db,
                        progress_callback=progress_callback
                    )
                    
                    strategy.mark_incremental_update(updated)
                    self.update_status(f"✅ Actualización diaria: {updated} jugadores")
                    
                elif update_mode == 'full':
                    # WEEKLY: Full update 100 pages (~30 min)
                    self.update_status(f"🔄 Actualización semanal: 100 páginas paralelas...")
                    
                    pages = strategy.get_full_pages()
                    all_players = scraper.get_all_players_parallel(
                        max_pages=pages,
                        num_threads=3,  # Reducido para evitar rate limiting
                        progress_callback=lambda p, t, name: progress_callback(p, t, name)
                    )
                    
                    self.update_status(f"💰 Obteniendo precios de {len(all_players)} jugadores...")
                    updated = self._update_players_batch(scraper, db, all_players, progress_callback)
                    
                    strategy.mark_full_update(updated)
                    self.update_status(f"✅ Actualización completa: {updated} jugadores")
                
                self.update_progress(100, 100)
                self.root.after(1000, lambda: callback(True))
                
            except Exception as e:
                logger.error(f"Error updating prices: {e}", exc_info=True)
                self.update_status(f"⚠️ Error: {str(e)}")
                self.root.after(2000, lambda: callback(False))
        
        # Start update thread
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
        
    def _update_players_batch(self, scraper, db_manager, players_list, progress_callback):
        """
        Update prices for a batch of players
        
        Args:
            scraper: FUTBINScraper instance
            db_manager: DatabaseManager instance
            players_list: List of player dictionaries with URLs
            progress_callback: Progress callback function
            
        Returns:
            Number of players updated
        """
        from app.models.database import Player
        from bs4 import BeautifulSoup
        import re
        import time
        
        updated = 0
        total = len(players_list)
        
        for i, player in enumerate(players_list, 1):
            try:
                # Get price from player page
                response = scraper.session.get(player['url'], timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    price_text = soup.get_text()
                    match = re.search(r'([\d,]+)\s+on\s+PC', price_text, re.IGNORECASE)
                    
                    session = db_manager.get_session()
                    
                    if match:
                        price_str = match.group(1).replace(',', '')
                        pc_price = int(price_str)
                        
                        # Get or create player
                        existing_player = session.query(Player).filter_by(
                            player_id=player['player_id']
                        ).first()
                        
                        if not existing_player:
                            new_player = Player(
                                player_id=player['player_id'],
                                name=player['name'],
                                rating=player['rating'],
                                position='Unknown',
                                is_extinct=False
                            )
                            session.add(new_player)
                            session.commit()
                            player_db_id = new_player.id
                        else:
                            if existing_player.is_extinct:
                                existing_player.is_extinct = False
                                session.commit()
                            player_db_id = existing_player.id
                        
                        session.close()
                        
                        # Add price
                        db_manager.add_price_history(player_db_id, pc_price)
                        updated += 1
                    else:
                        # Player extinct
                        existing_player = session.query(Player).filter_by(
                            player_id=player['player_id']
                        ).first()
                        
                        if not existing_player:
                            new_player = Player(
                                player_id=player['player_id'],
                                name=player['name'],
                                rating=player['rating'],
                                position='Unknown',
                                is_extinct=True
                            )
                            session.add(new_player)
                            session.commit()
                        else:
                            existing_player.is_extinct = True
                            session.commit()
                        
                        session.close()
                    
                    progress_callback(i, total, player['name'])
                    time.sleep(1)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Error updating {player.get('name', 'unknown')}: {e}")
                progress_callback(i, total)
                continue
        
        return updated
    
    def show(self):
        """Show splash screen"""
        self.root.mainloop()
        
    def close(self):
        """Close splash screen"""
        self.root.destroy()
