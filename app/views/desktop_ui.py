"""
Windows Desktop Application for EA FC 26 Trading Bot
Built with Tkinter for native Windows experience
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

logger = logging.getLogger(__name__)


class TradingBotApp:
    """
    Main desktop application window for EA FC 26 Trading Bot
    """
    
    def __init__(self):
        """Initialize desktop application"""
        self.root = tk.Tk()
        self.root.title("⚽ EA FC 26 Trading Bot Pro • by xSuppra")
        self.root.geometry("1920x1080")
        # Maximizar ventana para 1080p
        try:
            self.root.state('zoomed')
        except:
            pass
        
        # Modern Financial App Theme (Robinhood/Trading212 inspired)
        self.colors = {
            'bg_dark': '#0D0D0D',           # Pure dark background
            'bg_medium': '#1A1A1A',         # Card background
            'bg_light': '#262626',          # Lighter elements
            'bg_input': '#2A2A2A',          # Input fields
            'accent_green': '#00C805',      # Success/Profit green
            'accent_red': '#FF3B30',        # Loss/Danger red
            'accent_blue': '#0A84FF',       # Info blue
            'accent_cyan': '#00D4FF',       # Cyan blue
            'accent_gold': '#FFD60A',       # Premium gold
            'accent_purple': '#BF5AF2',     # Highlight purple
            'text_white': '#FFFFFF',        # Primary text
            'text_gray': '#8E8E93',         # Secondary text
            'text_light': '#C7C7CC',        # Tertiary text
            'border': '#2C2C2E',            # Subtle borders
            'chart_green': '#30D158',       # Chart positive
            'chart_red': '#FF453A'          # Chart negative
        }
        
        # Light theme colors
        self.colors_light = {
            'bg_dark': '#FFFFFF',
            'bg_medium': '#F5F5F7',
            'bg_light': '#E5E5EA',
            'bg_input': '#FFFFFF',
            'accent_green': '#00C805',
            'accent_red': '#FF3B30',
            'accent_blue': '#0A84FF',
            'accent_cyan': '#00D4FF',
            'accent_gold': '#FFD60A',
            'accent_purple': '#BF5AF2',
            'text_white': '#000000',
            'text_gray': '#6E6E73',
            'text_light': '#48484A',
            'border': '#D1D1D6',
            'chart_green': '#30D158',
            'chart_red': '#FF453A'
        }
        
        # Load theme from config
        self.current_theme = self._load_theme_preference()
        
        # Apply theme colors
        if self.current_theme == 'light':
            self.colors_dark = self.colors.copy()  # Save dark colors
            self.colors = self.colors_light.copy()
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Financial app fonts (clean and professional)
        self.fonts = {
            'title': ('SF Pro Display', 28, 'bold'),
            'header': ('SF Pro Display', 18, 'bold'),
            'subheader': ('SF Pro Display', 14, 'bold'),
            'body': ('SF Pro Text', 11),
            'small': ('SF Pro Text', 9),
            'mono': ('SF Mono', 10)
        }
        
        # Fallback to Segoe UI if SF Pro not available
        try:
            tk.Label(self.root, font=self.fonts['title']).destroy()
        except:
            self.fonts = {
                'title': ('Segoe UI', 28, 'bold'),
                'header': ('Segoe UI', 18, 'bold'),
                'subheader': ('Segoe UI', 14, 'bold'),
                'body': ('Segoe UI', 11),
                'small': ('Segoe UI', 9),
                'mono': ('Consolas', 10)
            }
        
        # Set icon (if available)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Initialize variables
        self.is_running = False
        self.discord_bot = None
        self.market_data_cache = None  # Cache for market data
        self.activity_log_lines = []  # Track log lines
        self.max_log_lines = 50  # Limit log to 50 lines
        
        # Initialize advanced features
        try:
            from app.utils.price_alerts import PriceAlertManager
            from app.utils.auto_save import AutoSaveManager
            from app.utils.query_cache import db_cache
            from app.utils.sbc_tracker import SBCTracker
            from app.utils.windows_notifications import get_notifier
            
            self.alert_manager = PriceAlertManager()
            self.auto_save = AutoSaveManager(save_interval=300)  # 5 min
            self.db_cache = db_cache
            self.sbc_tracker = SBCTracker()
            self.notifier = get_notifier()
            
            # Test notification on startup
            if self.notifier.is_enabled():
                self.notifier.test_notification()
            
            # Actualizar SBCs al iniciar (datos frescos)
            logger.info("🔄 Actualizando SBCs al iniciar aplicación...")
            try:
                sbcs = self.sbc_tracker.get_active_sbcs(force_refresh=True)
                logger.info(f"✅ SBCs iniciales cargados: {len(sbcs)} SBCs activos")
            except Exception as e:
                logger.warning(f"⚠️ No se pudieron cargar SBCs iniciales: {e}")
            
            logger.info("✅ Características avanzadas inicializadas")
        except Exception as e:
            logger.error(f"Error iniciando características avanzadas: {e}")
            self.alert_manager = None
            self.auto_save = None
            self.db_cache = None
            self.sbc_tracker = None
            self.notifier = None
        
        # Initialize Database Manager
        try:
            from app.models.database import DatabaseManager
            
            self.db_manager = DatabaseManager()
            
            # Initialize alert manager with DB
            if self.alert_manager:
                self.alert_manager.db = self.db_manager
            
            # Initialize advanced services
            try:
                from app.services.historical_trends_service import HistoricalTrendsService
                from app.services.portfolio_service import PortfolioService
                from app.services.peak_hours_service import PeakHoursService
                from app.services.futbin_service import FUTBINScraper
                
                self.futbin_scraper = FUTBINScraper()
                self.trends_service = HistoricalTrendsService(self.db_manager)
                self.portfolio_service = PortfolioService(self.db_manager)
                self.peak_hours_service = PeakHoursService(self.db_manager, self.futbin_scraper)
                
                logger.info("✅ Servicios avanzados inicializados (tendencias, portfolio, peak hours)")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando servicios avanzados: {e}")
                self.trends_service = None
                self.portfolio_service = None
                self.peak_hours_service = None
            
            logger.info("✅ Database Manager iniciado")
        except Exception as e:
            logger.error(f"Error iniciando DB Manager: {e}")
            self.db_manager = None
        
        # Fodder Assistant y Price Updater (opcional - no implementado aún)
        self.fodder_assistant = None
        self.price_updater = None
        
        # Filters state
        self.filters = {
            'league': 'Todas',
            'position': 'Todas',
            'rating_min': 82,
            'rating_max': 84
        }
        
        # Create UI - NO MENU BAR (removido menú anticuado)
        self._create_widgets()
        
        # Load initial data
        self._load_budget()
        
        # Start auto-save
        if self.auto_save:
            self.auto_save.register_callback(self._auto_save_callback)
            self.auto_save.start()
        
        # Start real-time clock update
        self._update_realtime_clock()
        
        # Start price alert checker (every 5 minutes)
        self._check_price_alerts()
        
        # Start SBC daily update checker (every minute)
        self._check_sbc_updates()
        
        # Auto-refresh
        self._schedule_refresh()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Configurar Presupuesto", command=self._show_budget_config)
        file_menu.add_command(label="Configurar Discord", command=self._show_discord_config)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Actions menu
        actions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Acciones", menu=actions_menu)
        # Actualización manual removida - ahora es automática
        actions_menu.add_command(label="Ver Recomendaciones", command=self._show_recommendations)
        actions_menu.add_separator()
        actions_menu.add_command(label="Ver Recomendaciones", command=self._show_recommendations)
        actions_menu.add_command(label="Registrar Compra", command=self._show_buy_dialog)
        actions_menu.add_command(label="Registrar Venta", command=self._show_sell_dialog)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Guía de Uso", command=self._show_help)
        help_menu.add_command(label="Estrategias 11K", command=self._show_strategies)
        help_menu.add_command(label="Acerca de", command=self._show_about)
    
    def _create_widgets(self):
        """Create main UI widgets with modern financial app design"""
        # Main container with proper layout
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create 2-column layout: Left sidebar + Right content
        # Left sidebar (20%)
        sidebar = tk.Frame(main_container, bg=self.colors['bg_medium'], width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        sidebar.pack_propagate(False)
        
        # Right content area (80%)
        content_area = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === SIDEBAR CONTENT ===
        # Logo/Title section con mejor visibilidad
        logo_frame = tk.Frame(sidebar, bg=self.colors['bg_medium'], height=100)
        logo_frame.pack(fill=tk.X, pady=(0, 20))
        logo_frame.pack_propagate(False)
        
        # Emoji más grande y visible
        tk.Label(logo_frame, text="⚽", font=('Segoe UI Emoji', 42),
                bg=self.colors['bg_medium']).pack(pady=(20, 5))
        tk.Label(logo_frame, text="FC 26 TRADING", font=('Segoe UI', 13, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack()
        tk.Label(logo_frame, text="BOT PRO", font=('Segoe UI', 10),
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack()
        
        # Budget section
        budget_section = tk.Frame(sidebar, bg=self.colors['bg_light'], relief=tk.FLAT)
        budget_section.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(budget_section, text="Balance", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(15, 0))
        
        budget_amount_frame = tk.Frame(budget_section, bg=self.colors['bg_light'])
        budget_amount_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        self.budget_label = tk.Label(budget_amount_frame, text="11,000", font=('Segoe UI', 24, 'bold'),
                                     bg=self.colors['bg_light'], fg=self.colors['text_white'])
        self.budget_label.pack(side=tk.LEFT)
        tk.Label(budget_amount_frame, text=" coins", font=self.fonts['body'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(side=tk.LEFT, pady=(8, 0))
        
        # Profit section
        profit_section = tk.Frame(sidebar, bg=self.colors['bg_light'], relief=tk.FLAT)
        profit_section.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(profit_section, text="Ganancias Totales", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(15, 0))
        
        profit_amount_frame = tk.Frame(profit_section, bg=self.colors['bg_light'])
        profit_amount_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        self.profit_label = tk.Label(profit_amount_frame, text="+0", font=('Segoe UI', 20, 'bold'),
                                     bg=self.colors['bg_light'], fg=self.colors['accent_green'])
        self.profit_label.pack(side=tk.LEFT)
        tk.Label(profit_amount_frame, text=" coins", font=self.fonts['body'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(side=tk.LEFT, pady=(6, 0))
        
        # Tier section
        tier_section = tk.Frame(sidebar, bg=self.colors['bg_light'], relief=tk.FLAT)
        tier_section.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(tier_section, text="Nivel de Trading", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        self.tier_label = tk.Label(tier_section, text="BAJO (0-20K)", font=self.fonts['body'],
                                   bg=self.colors['bg_light'], fg=self.colors['accent_blue'])
        self.tier_label.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        # Auto-update status
        auto_section = tk.Frame(sidebar, bg=self.colors['bg_light'], relief=tk.FLAT)
        auto_section.pack(fill=tk.X, padx=15, pady=(0, 20))
        
        tk.Label(auto_section, text="⚡ Actualizaciones Automáticas", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        tk.Label(auto_section, text="✓ 9:00 AM", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['accent_green']).pack(anchor=tk.W, padx=15, pady=(0, 2))
        tk.Label(auto_section, text="✓ 1:00 PM", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['accent_green']).pack(anchor=tk.W, padx=15, pady=(0, 2))
        tk.Label(auto_section, text="✓ 10:00 PM", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['accent_green']).pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        # Status and action button - REMOVIDO (no es necesario)
        # El bot funciona automáticamente con las actualizaciones programadas
        
        # Spacer at bottom
        tk.Frame(sidebar, bg=self.colors['bg_medium'], height=20).pack(side=tk.BOTTOM)
        
        # === CONTENT AREA ===
        # Header with title and real-time clock
        header = tk.Frame(content_area, bg=self.colors['bg_dark'], height=60)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        # Left side: Page title
        self.page_title = tk.Label(header, text="🛒 Recomendaciones de Compra", 
                                   font=self.fonts['title'],
                                   bg=self.colors['bg_dark'], fg=self.colors['text_white'])
        self.page_title.pack(side=tk.LEFT, pady=15)
        
        # Right side: Real-time clock and date
        clock_frame = tk.Frame(header, bg=self.colors['bg_dark'])
        clock_frame.pack(side=tk.RIGHT, pady=15)
        
        self.current_time_label = tk.Label(clock_frame, text="00:00:00", 
                                           font=('Segoe UI', 20, 'bold'),
                                           bg=self.colors['bg_dark'], fg=self.colors['accent_blue'])
        self.current_time_label.pack(anchor='e')
        
        self.current_date_label = tk.Label(clock_frame, text="Cargando...", 
                                           font=self.fonts['small'],
                                           bg=self.colors['bg_dark'], fg=self.colors['text_gray'])
        self.current_date_label.pack(anchor='e')
        
        # Modern navigation menu (side buttons instead of tabs)
        nav_frame = tk.Frame(sidebar, bg=self.colors['bg_medium'])
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.nav_buttons = {}
        self.current_page = 'recommendations'
        
        # Navigation items
        nav_items = [
            ('recommendations', '🛒 Comprar', self._show_recommendations_page),
            ('sell', '💰 Vender', self._show_sell_page),
            ('bidding', '🎯 Pujas Masivas', self._show_bidding_page),
            ('sbcs', '⚽ SBCs', self._show_sbcs_page),
            ('market', '📈 Mercado', self._show_market_page),
            ('live_prices', '⚡ Live Prices', self._show_live_prices_page),
            ('history', '📊 Historial', self._show_history_page),
            ('discord', '💬 Discord', self._show_discord_page),
            ('settings', '⚙️ Ajustes', self._show_settings_page)
        ]
        
        for page_id, label, command in nav_items:
            btn = tk.Button(nav_frame, text=label,
                          command=lambda p=page_id, c=command: self._switch_page(p, c),
                          bg=self.colors['bg_light'] if page_id == 'recommendations' else self.colors['bg_medium'],
                          fg=self.colors['text_white'],
                          activebackground=self.colors['bg_light'],
                          activeforeground=self.colors['text_white'],
                          font=self.fonts['body'],
                          relief=tk.FLAT, borderwidth=0,
                          cursor='hand2',
                          anchor=tk.W,
                          padx=20, pady=12)
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.nav_buttons[page_id] = btn
        
        # Content container (replaces notebook)
        self.content_container = tk.Frame(content_area, bg=self.colors['bg_dark'])
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Create all page frames
        self.pages = {}
        
        # Recommendations page
        rec_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['recommendations'] = rec_frame
        self._create_recommendations_tab(rec_frame)
        rec_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sell page
        sell_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['sell'] = sell_frame
        self._create_sell_tab(sell_frame)
        
        # Mass Bidding page
        bidding_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['bidding'] = bidding_frame
        self._create_bidding_tab(bidding_frame)
        
        # SBCs page
        sbcs_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['sbcs'] = sbcs_frame
        self._create_sbcs_tab(sbcs_frame)
        
        # Market page
        market_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['market'] = market_frame
        self._create_market_tab(market_frame)
        
        # Live Prices page
        live_prices_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['live_prices'] = live_prices_frame
        self._create_live_prices_tab(live_prices_frame)
        
        # History page
        history_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['history'] = history_frame
        self._create_history_tab(history_frame)
        
        # Discord page
        discord_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['discord'] = discord_frame
        self._create_discord_tab(discord_frame)
        
        # Settings page
        settings_frame = tk.Frame(self.content_container, bg=self.colors['bg_dark'])
        self.pages['settings'] = settings_frame
        self._create_settings_tab(settings_frame)
        
        # Activity log at bottom (compact and visible)
        log_section = tk.Frame(content_area, bg=self.colors['bg_medium'], height=150)
        log_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        log_section.pack_propagate(False)
        
        log_header = tk.Frame(log_section, bg=self.colors['bg_medium'])
        log_header.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(log_header, text="📋 Actividad Reciente", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        tk.Button(log_header, text="Limpiar",
                 command=lambda: self.log_text.delete('1.0', tk.END),
                 bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=12, pady=4).pack(side=tk.RIGHT)
        
        self.log_text = scrolledtext.ScrolledText(log_section, height=5,
                                                  bg=self.colors['bg_input'],
                                                  fg=self.colors['text_light'],
                                                  font=self.fonts['mono'],
                                                  relief=tk.FLAT,
                                                  insertbackground=self.colors['accent_green'],
                                                  selectbackground=self.colors['accent_blue'],
                                                  borderwidth=0,
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Initial log
        self._log("✓ Sistema iniciado correctamente")
        self._log(f"✓ Actualizaciones automáticas configuradas: 9 AM | 1 PM | 10 PM")
        self._log(f"✓ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _switch_page(self, page_id: str, command):
        """Switch between pages in modern navigation"""
        # Update button styles
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.config(bg=self.colors['bg_light'], fg=self.colors['text_white'])
            else:
                btn.config(bg=self.colors['bg_medium'], fg=self.colors['text_gray'])
        
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        self.pages[page_id].pack(fill=tk.BOTH, expand=True)
        
        # Update page title
        titles = {
            'recommendations': '🛒 Recomendaciones de Compra',
            'sell': '💰 Cartas para Vender',
            'market': '📈 Estado del Mercado',
            'history': '📊 Historial de Transacciones',
            'discord': '💬 Configuración de Discord',
            'settings': '⚙️ Ajustes del Bot'
        }
        self.page_title.config(text=titles.get(page_id, 'Panel de Control'))
        
        # Execute page-specific command if needed
        if command:
            try:
                command()
            except:
                pass
        
        self.current_page = page_id
        self._log(f"✓ Vista cambiada a: {titles.get(page_id)}")
    
    def _show_recommendations_page(self):
        """Show recommendations page"""
        self._refresh_recommendations()
    
    def _show_sell_page(self):
        """Show sell page"""
        self._refresh_sell_recommendations()
    
    def _show_bidding_page(self):
        """Show mass bidding page"""
        self._refresh_bidding_recommendations()
    
    def _show_sbcs_page(self):
        """Show SBCs page"""
        self._refresh_sbcs()
    
    def _show_market_page(self):
        """Show market page"""
        pass  # Already loaded
    
    def _show_live_prices_page(self):
        """Show live prices page"""
        self._refresh_live_prices()
    
    def _show_history_page(self):
        """Show history page"""
        self._refresh_history()
    
    def _show_discord_page(self):
        """Show Discord page"""
        pass  # Already loaded
    
    def _show_settings_page(self):
        """Show settings page"""
        pass  # Already loaded
    
    def _create_recommendations_tab(self, parent):
        """Create Fodder Flipping recommendations tab with action plan and filters"""
        # Toolbar with filters
        toolbar = tk.Frame(parent, bg=self.colors['bg_dark'], height=60)
        toolbar.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Filters section
        filter_frame = tk.Frame(toolbar, bg=self.colors['bg_medium'])
        filter_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        tk.Label(filter_frame, text="🔍 Filtros:", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT, padx=(15, 10))
        
        # League filter
        tk.Label(filter_frame, text="Liga:", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.league_filter = ttk.Combobox(filter_frame, 
                                         values=["Todas", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"],
                                         state="readonly",
                                         width=15,
                                         font=self.fonts['small'])
        self.league_filter.set("Todas")
        self.league_filter.pack(side=tk.LEFT, padx=(0, 15))
        self.league_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Position filter (DISABLED - positions not scraped correctly yet)
        # tk.Label(filter_frame, text="Posición:", font=self.fonts['small'],
        #         bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT, padx=(0, 5))
        
        # self.position_filter = ttk.Combobox(filter_frame,
        #                                    values=["Todas", "GK", "DEF", "MID", "ATT"],
        #                                    state="readonly",
        #                                    width=10,
        #                                    font=self.fonts['small'])
        # self.position_filter.set("Todas")
        # self.position_filter.pack(side=tk.LEFT, padx=(0, 15))
        # self.position_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Temporary: Set position to Todas always
        class MockFilter:
            def get(self): return 'Todas'
            def set(self, val): pass
        self.position_filter = MockFilter()
        
        # Rating range
        tk.Label(filter_frame, text="Rating:", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.rating_min_filter = ttk.Combobox(filter_frame,
                                             values=["82", "83", "84", "85"],
                                             state="readonly",
                                             width=5,
                                             font=self.fonts['small'])
        self.rating_min_filter.set("82")
        self.rating_min_filter.pack(side=tk.LEFT, padx=(0, 5))
        self.rating_min_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        tk.Label(filter_frame, text="-", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.rating_max_filter = ttk.Combobox(filter_frame,
                                             values=["82", "83", "84", "85"],
                                             state="readonly",
                                             width=5,
                                             font=self.fonts['small'])
        self.rating_max_filter.set("84")
        self.rating_max_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.rating_max_filter.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Clear filters button
        tk.Button(filter_frame, text="✖ Limpiar",
                 command=self._clear_filters,
                 bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=(5, 15))
        
        # Refresh button
        tk.Button(toolbar, text="🔄 Actualizar Plan",
                 command=self._refresh_fodder_plan,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.RIGHT)
        
        # Action Plan Card (top section)
        action_plan_card = tk.Frame(parent, bg=self.colors['bg_medium'], relief=tk.FLAT)
        action_plan_card.pack(fill=tk.X, padx=20, pady=(10, 10))
        
        # Header
        plan_header = tk.Frame(action_plan_card, bg=self.colors['bg_medium'])
        plan_header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(plan_header, text="🎯 PLAN DE ACCIÓN - FODDER FLIPPING", 
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        # Peak Hours Indicator (right side of header)
        self.peak_hours_indicator = tk.Label(plan_header, text="⏰ Analizando...", 
                                            font=self.fonts['body'],
                                            bg=self.colors['bg_medium'], 
                                            fg=self.colors['text_muted'])
        self.peak_hours_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Peak Hours Info Card (below header)
        self.peak_hours_card = tk.Frame(action_plan_card, bg=self.colors['bg_light'])
        self.peak_hours_card.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        peak_info_frame = tk.Frame(self.peak_hours_card, bg=self.colors['bg_light'])
        peak_info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Buy Window
        buy_frame = tk.Frame(peak_info_frame, bg=self.colors['bg_light'])
        buy_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        tk.Label(buy_frame, text="🌙 MEJOR COMPRA", 
                font=self.fonts['small_bold'],
                bg=self.colors['bg_light'], 
                fg=self.colors['info']).pack(anchor='w')
        
        self.best_buy_time_label = tk.Label(buy_frame, text="--:-- - --:--", 
                                           font=self.fonts['body'],
                                           bg=self.colors['bg_light'], 
                                           fg=self.colors['text_white'])
        self.best_buy_time_label.pack(anchor='w')
        
        # Sell Window
        sell_frame = tk.Frame(peak_info_frame, bg=self.colors['bg_light'])
        sell_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        tk.Label(sell_frame, text="🔥 MEJOR VENTA", 
                font=self.fonts['small_bold'],
                bg=self.colors['bg_light'], 
                fg=self.colors['success']).pack(anchor='w')
        
        self.best_sell_time_label = tk.Label(sell_frame, text="--:-- - --:--", 
                                            font=self.fonts['body'],
                                            bg=self.colors['bg_light'], 
                                            fg=self.colors['text_white'])
        self.best_sell_time_label.pack(anchor='w')
        
        # Current Action
        action_frame = tk.Frame(peak_info_frame, bg=self.colors['bg_light'])
        action_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        tk.Label(action_frame, text="💡 AHORA", 
                font=self.fonts['small_bold'],
                bg=self.colors['bg_light'], 
                fg=self.colors['warning']).pack(anchor='w')
        
        self.current_action_label = tk.Label(action_frame, text="Calculando...", 
                                            font=self.fonts['body'],
                                            bg=self.colors['bg_light'], 
                                            fg=self.colors['text_white'])
        self.current_action_label.pack(anchor='w')
        
        # Market Moment Section
        self.market_moment_frame = tk.Frame(action_plan_card, bg=self.colors['bg_light'])
        self.market_moment_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Instructions Section
        instructions_label = tk.Label(action_plan_card, text="📋 INSTRUCCIONES PASO A PASO:", 
                                     font=self.fonts['subheader'],
                                     bg=self.colors['bg_medium'], fg=self.colors['text_white'])
        instructions_label.pack(anchor='w', padx=20, pady=(10, 10))
        
        self.instructions_text = scrolledtext.ScrolledText(action_plan_card, 
                                                          height=8,
                                                          bg=self.colors['bg_light'],
                                                          fg=self.colors['text_white'],
                                                          font=self.fonts['body'],
                                                          relief=tk.FLAT,
                                                          wrap=tk.WORD)
        self.instructions_text.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Separator
        tk.Frame(parent, bg=self.colors['border'], height=1).pack(fill=tk.X, padx=20, pady=10)
        
        # Recommendations list with cards
        rec_header = tk.Frame(parent, bg=self.colors['bg_dark'])
        rec_header.pack(fill=tk.X, padx=20, pady=(10, 10))
        
        tk.Label(rec_header, text="🛒 CARTAS RECOMENDADAS (Rating 82-84)", 
                font=self.fonts['subheader'],
                bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        list_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, bg=self.colors['bg_medium'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.rec_canvas = tk.Canvas(list_frame, bg=self.colors['bg_dark'],
                                   yscrollcommand=scrollbar.set,
                                   highlightthickness=0)
        self.rec_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.rec_canvas.yview)
        
        # Container frame
        self.rec_container = tk.Frame(self.rec_canvas, bg=self.colors['bg_dark'])
        self.rec_canvas.create_window((0, 0), window=self.rec_container, anchor=tk.NW)
        
        self.rec_container.bind('<Configure>',
                               lambda e: self.rec_canvas.configure(
                                   scrollregion=self.rec_canvas.bbox('all')))
        
        # Load initial data
        self._refresh_fodder_plan()
    
    def _create_sell_tab(self, parent):
        """Create sell recommendations tab with modern design and portfolio stats"""
        # Portfolio Stats Section (NEW)
        stats_section = tk.Frame(parent, bg=self.colors['bg_dark'])
        stats_section.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        tk.Label(stats_section, text="💼 Estadísticas del Portfolio", font=self.fonts['subheader'],
                bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(anchor='w', pady=(0, 10))
        
        # Stats cards row
        stats_row = tk.Frame(stats_section, bg=self.colors['bg_dark'])
        stats_row.pack(fill=tk.X)
        
        # Investment card
        inv_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        inv_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(inv_card, text="Inversión Total", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(12, 3))
        self.portfolio_investment_label = tk.Label(inv_card, text="0", font=self.fonts['header'],
                                                   bg=self.colors['bg_medium'], fg=self.colors['text_white'])
        self.portfolio_investment_label.pack(padx=15, pady=(0, 12))
        
        # Value card
        val_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        val_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(val_card, text="Valor Actual", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(12, 3))
        self.portfolio_value_label = tk.Label(val_card, text="0", font=self.fonts['header'],
                                              bg=self.colors['bg_medium'], fg=self.colors['accent_cyan'])
        self.portfolio_value_label.pack(padx=15, pady=(0, 12))
        
        # Profit card
        profit_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        profit_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(profit_card, text="Profit No Realizado", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(12, 3))
        self.portfolio_profit_label = tk.Label(profit_card, text="+0", font=self.fonts['header'],
                                               bg=self.colors['bg_medium'], fg=self.colors['accent_green'])
        self.portfolio_profit_label.pack(padx=15, pady=(0, 12))
        
        # ROI card
        roi_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        roi_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(roi_card, text="ROI Global", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(12, 3))
        self.portfolio_roi_label = tk.Label(roi_card, text="0.0%", font=self.fonts['header'],
                                            bg=self.colors['bg_medium'], fg=self.colors['accent_gold'])
        self.portfolio_roi_label.pack(padx=15, pady=(0, 12))
        
        # Toolbar
        toolbar = tk.Frame(parent, bg=self.colors['bg_dark'], height=50)
        toolbar.pack(fill=tk.X, padx=0, pady=(10, 10))
        
        tk.Button(toolbar, text="🔄  Actualizar Ventas",
                 command=self._refresh_sell_recommendations,
                 bg=self.colors['accent_green'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT)
        
        list_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, bg=self.colors['bg_medium'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sell_canvas = tk.Canvas(list_frame, bg=self.colors['bg_dark'],
                                    yscrollcommand=scrollbar.set,
                                    highlightthickness=0)
        self.sell_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.sell_canvas.yview)
        
        self.sell_container = tk.Frame(self.sell_canvas, bg=self.colors['bg_dark'])
        self.sell_canvas.create_window((0, 0), window=self.sell_container, anchor=tk.NW)
        
        self.sell_container.bind('<Configure>',
                                lambda e: self.sell_canvas.configure(
                                    scrollregion=self.sell_canvas.bbox('all')))
    
    def _create_bidding_tab(self, parent):
        """Create Mass Bidding Assistant tab"""
        # Header
        header = tk.Frame(parent, bg=self.colors['bg_medium'], height=100)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="🎯 ASISTENTE DE PUJAS MASIVAS",
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(pady=(20, 5))
        
        tk.Label(header, 
                text="Calcula rangos óptimos de pujas para Fodder según el mercado actual",
                font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(0, 15))
        
        # Info card
        info_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        info_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(info_card, text="ℹ️ Cómo funciona", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        info_text = """El sistema calcula rangos de puja óptimos basados en:
• Precio promedio del mercado en las últimas 24 horas
• Margen de seguridad (85-90% del precio actual)
• Disponibilidad de cartas en el mercado
• Potencial de ganancia (venta al precio de mercado)

Estrategia recomendada:
1. Puja en el rango inferior para maximizar ganancias
2. Aumenta gradualmente si no consigues cartas
3. Evita pujar cerca del precio de mercado (bajo margen)"""
        
        info_frame = tk.Frame(info_card, bg=self.colors['bg_input'])
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Label(info_frame, text=info_text, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
        
        # Scrollable container for bidding recommendations
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        self.bidding_canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_dark'],
                                        highlightthickness=0)
        bidding_scrollbar = tk.Scrollbar(canvas_frame, orient='vertical',
                                         command=self.bidding_canvas.yview)
        
        self.bidding_container = tk.Frame(self.bidding_canvas, bg=self.colors['bg_dark'])
        
        self.bidding_canvas.create_window((0, 0), window=self.bidding_container, anchor='nw')
        self.bidding_canvas.configure(yscrollcommand=bidding_scrollbar.set)
        
        self.bidding_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bidding_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.bidding_container.bind('<Configure>',
                                   lambda e: self.bidding_canvas.configure(
                                       scrollregion=self.bidding_canvas.bbox('all')))
    
    def _create_sbcs_tab(self, parent):
        """Create SBCs tab with active SBCs and fodder impact analysis"""
        # Header
        header = tk.Frame(parent, bg=self.colors['bg_medium'], height=100)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="⚽ SBCs ACTIVOS",
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(pady=(20, 5))
        
        tk.Label(header, 
                text="Monitorea SBCs activos y su impacto en el mercado de Fodder",
                font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(0, 15))
        
        # Top section: SBC Impact Summary
        summary_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        summary_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(summary_card, text="📊 Impacto en el Mercado", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        self.sbc_impact_frame = tk.Frame(summary_card, bg=self.colors['bg_input'])
        self.sbc_impact_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Scrollable container for SBC cards
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        self.sbcs_canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_dark'],
                                     highlightthickness=0)
        sbcs_scrollbar = tk.Scrollbar(canvas_frame, orient='vertical',
                                      command=self.sbcs_canvas.yview)
        
        self.sbcs_container = tk.Frame(self.sbcs_canvas, bg=self.colors['bg_dark'])
        
        self.sbcs_canvas.create_window((0, 0), window=self.sbcs_container, anchor='nw')
        self.sbcs_canvas.configure(yscrollcommand=sbcs_scrollbar.set)
        
        self.sbcs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sbcs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sbcs_container.bind('<Configure>',
                                lambda e: self.sbcs_canvas.configure(
                                    scrollregion=self.sbcs_canvas.bbox('all')))
    
    def _create_market_tab(self, parent):
        """Create market status tab with trends graph and predictions"""
        # Main container
        main_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section: Market status cards
        status_section = tk.Frame(main_container, bg=self.colors['bg_dark'])
        status_section.pack(fill=tk.X, pady=(0, 20))
        
        # Current market status
        self._create_market_status_card(status_section)
        
        # Middle section: Graph
        graph_card = tk.Frame(main_container, bg=self.colors['bg_medium'], relief=tk.FLAT)
        graph_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Graph header
        graph_header = tk.Frame(graph_card, bg=self.colors['bg_medium'])
        graph_header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(graph_header, text="📊 Tendencias Históricas del Mercado", 
                font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor='w')
        
        # Selector de días
        selector_frame = tk.Frame(graph_header, bg=self.colors['bg_medium'])
        selector_frame.pack(anchor='w', pady=(5, 0))
        
        tk.Label(selector_frame, text="Período:", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT, padx=(0, 10))
        
        # Days selector variable
        self.trend_days_var = tk.StringVar(value="7")
        
        for days in ['7', '30', '90']:
            rb = tk.Radiobutton(selector_frame, text=f"{days} días",
                               variable=self.trend_days_var, value=days,
                               command=self._refresh_market_graph,
                               bg=self.colors['bg_medium'], fg=self.colors['text_white'],
                               selectcolor=self.colors['bg_light'],
                               activebackground=self.colors['bg_medium'],
                               activeforeground=self.colors['accent_blue'],
                               font=self.fonts['small'])
            rb.pack(side=tk.LEFT, padx=5)
        
        # Create matplotlib graph
        self._create_market_graph(graph_card)
        
        # Bottom section: Predictions
        prediction_section = tk.Frame(main_container, bg=self.colors['bg_dark'])
        prediction_section.pack(fill=tk.X)
        
        self._create_market_predictions(prediction_section)
    
    def _create_market_status_card(self, parent):
        """Create current market status card"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 10))
        
        content = tk.Frame(card, bg=self.colors['bg_medium'])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Current time and day
        current_time = datetime.now()
        hour = current_time.hour
        day_of_week = current_time.strftime('%A')
        
        # Translate day to Spanish
        days_es = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        day_of_week_es = days_es.get(day_of_week, day_of_week)
        
        # Header
        header_frame = tk.Frame(content, bg=self.colors['bg_medium'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="⏰ Estado Actual del Mercado", 
                font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        # Real-time updating time label
        time_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        time_frame.pack(side=tk.RIGHT)
        
        tk.Label(time_frame, text=f"{day_of_week_es} • ", font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT)
        
        self.market_status_time_label = tk.Label(time_frame, text=current_time.strftime('%H:%M'), 
                font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray'])
        self.market_status_time_label.pack(side=tk.LEFT)
        
        # Status boxes
        boxes_frame = tk.Frame(content, bg=self.colors['bg_medium'])
        boxes_frame.pack(fill=tk.X)
        
        # Determine market status
        status_text, status_color, activity_level, recommendation = self._get_market_status(hour, day_of_week)
        
        # Status box
        status_box = tk.Frame(boxes_frame, bg=self.colors['bg_light'], relief=tk.FLAT)
        status_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(status_box, text="Estado", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.market_status_label = tk.Label(status_box, text=status_text, font=self.fonts['subheader'],
                bg=self.colors['bg_light'], fg=status_color)
        self.market_status_label.pack(pady=(0, 10))
        
        # Activity box
        activity_box = tk.Frame(boxes_frame, bg=self.colors['bg_light'], relief=tk.FLAT)
        activity_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(activity_box, text="Actividad", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.market_activity_label = tk.Label(activity_box, text=activity_level, font=self.fonts['subheader'],
                bg=self.colors['bg_light'], fg=self.colors['text_white'])
        self.market_activity_label.pack(pady=(0, 10))
        
        # Recommendation box
        rec_box = tk.Frame(boxes_frame, bg=self.colors['bg_light'], relief=tk.FLAT)
        rec_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(rec_box, text="Recomendación", font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.market_recommendation_label = tk.Label(rec_box, text=recommendation, font=self.fonts['subheader'],
                bg=self.colors['bg_light'], fg=self.colors['accent_blue'])
        self.market_recommendation_label.pack(pady=(0, 10))
    
    def _get_market_status(self, hour, day_of_week):
        """Get current market status based on time"""
        if hour >= 1 and hour <= 4:
            return "🌙 MADRUGADA", self.colors['accent_blue'], "MUY BAJA", "SNIPING"
        elif hour >= 6 and hour <= 9:
            return "🌅 MAÑANA", self.colors['accent_green'], "BAJA", "COMPRAR"
        elif hour >= 12 and hour <= 17:
            return "☀️ TARDE", "#FFD60A", "MEDIA", "TRADING"
        elif hour >= 18 and hour <= 21:
            return "🔥 HORA PICO", self.colors['accent_red'], "MUY ALTA", "VENDER"
        else:
            return "🌃 NOCHE", self.colors['accent_blue'], "MEDIA", "MIXTO"
    
    def _create_market_graph(self, parent):
        """Create market trend graph using matplotlib with historical trends"""
        # Create figure
        fig = Figure(figsize=(12, 4), dpi=100, facecolor=self.colors['bg_medium'])
        ax = fig.add_subplot(111)
        
        # Get selected period
        days = int(self.trend_days_var.get()) if hasattr(self, 'trend_days_var') else 7
        
        # Try to get real data from trends service
        real_dates, real_prices, trend_info = self._get_historical_trends_data(days)
        
        if real_dates and real_prices and len(real_prices) > 1:
            # Use real data from historical trends
            dates = real_dates
            prices = real_prices
            logger.info(f"Using historical trends data: {len(prices)} days")
        else:
            # Fallback to database data
            real_dates, real_prices = self._get_market_data_from_db()
            
            if real_dates and real_prices and len(real_prices) > 1:
                dates = real_dates
                prices = real_prices
                logger.info(f"Using database market data: {len(prices)} days")
            else:
                # Fallback to sample data if no real data available
                dates = [datetime.now() - timedelta(days=i) for i in range(days-1, -1, -1)]
                base_price = 50000
                prices = []
                
                for i, date in enumerate(dates):
                    variation = base_price * (0.1 * (i % 3 - 1))
                    weekend_boost = 5000 if date.strftime('%A') in ['Saturday', 'Sunday'] else 0
                    price = base_price + variation + weekend_boost
                    prices.append(price)
                
                logger.warning("No real market data found, using sample data")
                trend_info = None
        
        # Predict tomorrow's price (simple linear extrapolation)
        if len(prices) >= 2:
            trend = prices[-1] - prices[-2]
        else:
            trend = 0
            
        tomorrow = dates[-1] + timedelta(days=1)
        tomorrow_price = prices[-1] + trend
        
        # Plot historical data
        ax.plot(dates, prices, color=self.colors['accent_blue'], linewidth=2.5, 
               marker='o', markersize=6, label='Precio Promedio Real')
        
        # Plot prediction
        ax.plot([dates[-1], tomorrow], [prices[-1], tomorrow_price], 
               color=self.colors['accent_green'] if trend > 0 else self.colors['accent_red'], 
               linewidth=2.5, linestyle='--', marker='o', markersize=6, 
               label='Predicción para Mañana')
        
        # Styling
        ax.set_facecolor(self.colors['bg_light'])
        ax.set_xlabel('Fecha', color=self.colors['text_gray'], fontsize=10)
        ax.set_ylabel('Precio Promedio (Coins)', color=self.colors['text_gray'], fontsize=10)
        ax.tick_params(colors=self.colors['text_gray'], labelsize=9)
        ax.grid(True, alpha=0.1, color=self.colors['text_gray'])
        ax.legend(facecolor=self.colors['bg_light'], edgecolor=self.colors['text_gray'], 
                 labelcolor=self.colors['text_white'], fontsize=9)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate(rotation=0, ha='center')
        
        # Spine colors
        for spine in ax.spines.values():
            spine.set_edgecolor(self.colors['bg_light'])
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Store canvas and data for later updates
        self.market_graph_canvas = canvas
        self.market_graph_ax = ax
        self.market_graph_fig = fig
        self.market_graph_data = {
            'dates': dates,
            'prices': prices,
            'tomorrow': tomorrow,
            'tomorrow_price': tomorrow_price,
            'trend': trend
        }
        
        # Schedule graph refresh every 5 minutes
        self.root.after(300000, self._refresh_market_graph)
    
    def _create_market_predictions(self, parent):
        """Create ML-powered market predictions"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'], relief=tk.FLAT)
        card.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=self.colors['bg_medium'])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Header
        header_frame = tk.Frame(content, bg=self.colors['bg_medium'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="🔮 Predicciones ML para Mañana", 
                font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        # Refresh button
        def refresh_predictions():
            self._log("🔄 Actualizando predicciones ML...")
            self._refresh_ml_predictions()
            self._log("✅ Predicciones actualizadas")
        
        tk.Button(header_frame, text="🔄 Actualizar",
                 command=refresh_predictions,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=15, pady=5).pack(side=tk.RIGHT)
        
        # Scrollable predictions container
        pred_canvas_frame = tk.Frame(content, bg=self.colors['bg_medium'], height=300)
        pred_canvas_frame.pack(fill=tk.BOTH, expand=True)
        pred_canvas_frame.pack_propagate(False)
        
        pred_canvas = tk.Canvas(pred_canvas_frame, bg=self.colors['bg_medium'],
                               highlightthickness=0, height=300)
        pred_scrollbar = tk.Scrollbar(pred_canvas_frame, orient='horizontal',
                                     command=pred_canvas.xview)
        
        self.ml_predictions_container = tk.Frame(pred_canvas, bg=self.colors['bg_medium'])
        
        pred_canvas.create_window((0, 0), window=self.ml_predictions_container, anchor='nw')
        pred_canvas.configure(xscrollcommand=pred_scrollbar.set)
        
        pred_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        pred_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.ml_predictions_container.bind('<Configure>',
                                          lambda e: pred_canvas.configure(
                                              scrollregion=pred_canvas.bbox('all')))
        
        # Initial load of predictions
        self._refresh_ml_predictions()
    
    def _refresh_ml_predictions(self):
        """Refresh ML predictions for top players"""
        # Clear existing
        for widget in self.ml_predictions_container.winfo_children():
            widget.destroy()
        
        try:
            from app.models.database import DatabaseManager, Player, PriceHistory
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            db = DatabaseManager()
            session = db.SessionLocal()
            
            try:
                # Get top 10 most traded players (those with most price history entries)
                top_players = session.query(
                    Player.player_id,
                    Player.name,
                    Player.rating,
                    Player.position,
                    func.count(PriceHistory.price).label('trade_count')
                ).join(
                    PriceHistory,
                    Player.player_id == PriceHistory.player_id
                ).group_by(
                    Player.player_id,
                    Player.name,
                    Player.rating,
                    Player.position
                ).order_by(
                    func.count(PriceHistory.price).desc()
                ).limit(10).all()
                
                if not top_players:
                    # No data - show helpful message
                    empty_frame = tk.Frame(self.ml_predictions_container, bg=self.colors['bg_medium'])
                    empty_frame.pack(expand=True, fill=tk.BOTH, pady=40)
                    
                    tk.Label(empty_frame, text="🤖",
                            font=('Segoe UI Emoji', 48),
                            bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=10)
                    tk.Label(empty_frame,
                            text="Predicciones ML no disponibles",
                            font=('Segoe UI', 14, 'bold'),
                            bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(pady=5)
                    tk.Label(empty_frame,
                            text="Necesitas actualizar precios primero para generar predicciones",
                            font=self.fonts['body'],
                            bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=5)
                    tk.Label(empty_frame,
                            text="💡 Ejecuta: python update_prices_pc.py",
                            font=self.fonts['small'],
                            bg=self.colors['bg_medium'], fg=self.colors['accent_blue']).pack(pady=5)
                    return
                
                # Generate predictions for each player
                for player_id, name, rating, position, trade_count in top_players:
                    # Get current price
                    latest_price = session.query(PriceHistory).filter(
                        PriceHistory.player_id == player_id
                    ).order_by(PriceHistory.timestamp.desc()).first()
                    
                    if not latest_price:
                        continue
                    
                    current_price = latest_price.price
                    
                    # Get price history for prediction
                    history = session.query(PriceHistory).filter(
                        PriceHistory.player_id == player_id
                    ).order_by(PriceHistory.timestamp.asc()).all()
                    
                    if len(history) < 7:  # Need at least 7 days
                        predicted_price = current_price  # Use current as fallback
                        confidence = 0.5
                    else:
                        # Simple linear regression prediction
                        prices = [h.price for h in history[-14:]]  # Last 14 days
                        avg_change = (prices[-1] - prices[0]) / len(prices)
                        predicted_price = int(current_price + avg_change)
                        
                        # Calculate confidence based on price volatility
                        import statistics
                        volatility = statistics.stdev(prices) if len(prices) > 1 else 0
                        confidence = max(0.5, min(0.95, 1 - (volatility / current_price)))
                    
                    # Create prediction card
                    self._create_ml_prediction_card(
                        self.ml_predictions_container,
                        name, rating, position,
                        current_price, predicted_price, confidence
                    )
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error refreshing ML predictions: {e}")
            tk.Label(self.ml_predictions_container,
                    text=f"⚠️ Error al generar predicciones: {str(e)}",
                    font=self.fonts['body'],
                    bg=self.colors['bg_medium'], fg=self.colors['accent_red']).pack(pady=20)
    
    def _create_ml_prediction_card(self, parent, name, rating, position, current_price, predicted_price, confidence):
        """Create ML prediction card for a player"""
        card = tk.Frame(parent, bg=self.colors['bg_light'], width=250)
        card.pack(side=tk.LEFT, padx=(0, 15), fill=tk.Y)
        card.pack_propagate(False)
        
        # Player header
        header = tk.Frame(card, bg=self.colors['bg_input'])
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"{rating}",
                font=('Segoe UI', 16, 'bold'),
                bg=self.colors['accent_gold'], fg='white',
                width=3).pack(side=tk.LEFT, padx=(10, 10), pady=10)
        
        player_info = tk.Frame(header, bg=self.colors['bg_input'])
        player_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(player_info, text=name,
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_input'], fg=self.colors['text_white'],
                anchor=tk.W).pack(anchor=tk.W, fill=tk.X)
        
        tk.Label(player_info, text=position,
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_gray'],
                anchor=tk.W).pack(anchor=tk.W)
        
        # Current price
        current_frame = tk.Frame(card, bg=self.colors['bg_light'])
        current_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(current_frame, text="Precio Actual",
                font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W)
        
        tk.Label(current_frame, text=f"{current_price:,}",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['text_white']).pack(anchor=tk.W)
        
        # Predicted price
        pred_frame = tk.Frame(card, bg=self.colors['bg_light'])
        pred_frame.pack(fill=tk.X, padx=15, pady=(5, 5))
        
        tk.Label(pred_frame, text="Predicción Mañana",
                font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W)
        
        # Calculate change
        price_change = predicted_price - current_price
        change_percent = (price_change / current_price * 100) if current_price > 0 else 0
        
        if price_change > 0:
            emoji = "📈"
            color = self.colors['accent_green']
        elif price_change < 0:
            emoji = "📉"
            color = self.colors['accent_red']
        else:
            emoji = "➡️"
            color = self.colors['text_gray']
        
        pred_text = f"{emoji} {predicted_price:,} ({change_percent:+.1f}%)"
        tk.Label(pred_frame, text=pred_text,
                font=('Segoe UI', 13, 'bold'),
                bg=self.colors['bg_light'], fg=color).pack(anchor=tk.W)
        
        # Confidence
        conf_frame = tk.Frame(card, bg=self.colors['bg_light'])
        conf_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        tk.Label(conf_frame, text=f"Confianza: {confidence*100:.0f}%",
                font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor=tk.W)
        
        # Action recommendation
        action_frame = tk.Frame(card, bg=self.colors['bg_light'])
        action_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        if price_change > current_price * 0.05 and confidence > 0.7:
            action_text = "✅ COMPRAR"
            action_bg = self.colors['accent_green']
        elif price_change < -current_price * 0.05 and confidence > 0.7:
            action_text = "💰 VENDER"
            action_bg = self.colors['accent_blue']
        else:
            action_text = "⏳ ESPERAR"
            action_bg = self.colors['text_gray']
        
        action_label = tk.Label(action_frame, text=action_text,
                               font=self.fonts['small'],
                               bg=action_bg, fg='white',
                               padx=10, pady=5)
        action_label.pack(fill=tk.X)
    
    def _create_history_tab(self, parent):
        """Create transaction history tab with modern design and statistics"""
        # Stats cards at top
        stats_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        stats_container.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        # Total profit card
        profit_card = tk.Frame(stats_container, bg=self.colors['bg_medium'])
        profit_card.pack(side=tk.LEFT, padx=10, ipadx=30, ipady=15)
        
        tk.Label(profit_card, text="💰 Ganancia Total", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.total_profit_label = tk.Label(profit_card, text="0 coins",
                                          font=self.fonts['header'],
                                          bg=self.colors['bg_medium'], 
                                          fg=self.colors['accent_green'])
        self.total_profit_label.pack(pady=(0, 10))
        
        # Total transactions card
        trans_card = tk.Frame(stats_container, bg=self.colors['bg_medium'])
        trans_card.pack(side=tk.LEFT, padx=10, ipadx=30, ipady=15)
        
        tk.Label(trans_card, text="📊 Transacciones", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.total_trans_label = tk.Label(trans_card, text="0",
                                         font=self.fonts['header'],
                                         bg=self.colors['bg_medium'], 
                                         fg=self.colors['accent_blue'])
        self.total_trans_label.pack(pady=(0, 10))
        
        # Average profit card
        avg_card = tk.Frame(stats_container, bg=self.colors['bg_medium'])
        avg_card.pack(side=tk.LEFT, padx=10, ipadx=30, ipady=15)
        
        tk.Label(avg_card, text="📈 Ganancia Promedio", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.avg_profit_label = tk.Label(avg_card, text="0 coins",
                                        font=self.fonts['header'],
                                        bg=self.colors['bg_medium'], 
                                        fg=self.colors['text_white'])
        self.avg_profit_label.pack(pady=(0, 10))
        
        # Win rate card
        winrate_card = tk.Frame(stats_container, bg=self.colors['bg_medium'])
        winrate_card.pack(side=tk.LEFT, padx=10, ipadx=30, ipady=15)
        
        tk.Label(winrate_card, text="✅ Tasa de Éxito", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(10, 5))
        self.winrate_label = tk.Label(winrate_card, text="0%",
                                      font=self.fonts['header'],
                                      bg=self.colors['bg_medium'], 
                                      fg=self.colors['accent_green'])
        self.winrate_label.pack(pady=(0, 10))
        
        # Refresh button
        tk.Button(stats_container, text="🔄  Actualizar",
                 command=self._refresh_history,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.RIGHT, padx=10)
        
        # Profit/Loss Chart
        chart_frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        chart_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        chart_header = tk.Frame(chart_frame, bg=self.colors['bg_medium'])
        chart_header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(chart_header, text="📈 Evolución de Ganancias",
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(side=tk.LEFT)
        
        # Toggle buttons for time range
        toggle_frame = tk.Frame(chart_header, bg=self.colors['bg_medium'])
        toggle_frame.pack(side=tk.RIGHT)
        
        self.profit_chart_range = 'daily'  # daily, weekly, monthly
        
        tk.Button(toggle_frame, text="Diario",
                 command=lambda: self._update_profit_chart('daily'),
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toggle_frame, text="Semanal",
                 command=lambda: self._update_profit_chart('weekly'),
                 bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toggle_frame, text="Mensual",
                 command=lambda: self._update_profit_chart('monthly'),
                 bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                 font=self.fonts['small'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Canvas for profit chart
        self.profit_chart_canvas_frame = tk.Frame(chart_frame, bg=self.colors['bg_medium'])
        self.profit_chart_canvas_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # History table with modern styling
        table_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Modern Treeview styling with dark background
        style = ttk.Style()
        style.configure("History.Treeview",
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_light'],
                       fieldbackground=self.colors['bg_dark'],
                       borderwidth=0,
                       font=self.fonts['body'])
        style.configure("History.Treeview.Heading",
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_white'],
                       borderwidth=0,
                       font=self.fonts['subheader'])
        style.map("History.Treeview",
                 background=[('selected', self.colors['accent_blue'])],
                 foreground=[('selected', 'white')])
        
        columns = ('Fecha', 'Jugador', 'Tipo', 'Precio', 'Ganancia', 'ROI')
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                        height=15, style="History.Treeview")
        
        # Column widths
        self.history_tree.heading('Fecha', text='Fecha')
        self.history_tree.column('Fecha', width=150)
        
        self.history_tree.heading('Jugador', text='Jugador')
        self.history_tree.column('Jugador', width=200)
        
        self.history_tree.heading('Tipo', text='Tipo')
        self.history_tree.column('Tipo', width=80)
        
        self.history_tree.heading('Precio', text='Precio')
        self.history_tree.column('Precio', width=120)
        
        self.history_tree.heading('Ganancia', text='Ganancia')
        self.history_tree.column('Ganancia', width=120)
        
        self.history_tree.heading('ROI', text='ROI %')
        self.history_tree.column('ROI', width=100)
        
        scrollbar = tk.Scrollbar(table_frame, command=self.history_tree.yview,
                                bg=self.colors['bg_dark'])
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_discord_tab(self, parent):
        """Create Discord configuration tab with modern design"""
        # Header
        header = tk.Frame(parent, bg=self.colors['bg_medium'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="💬 Configuración de Discord",
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(pady=(20, 5))
        
        tk.Label(header, 
                text="Recibe recomendaciones automáticas y alertas en tiempo real",
                font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(0, 15))
        
        # Configuration form in card
        form_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        form_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Bot Token
        tk.Label(form_card, text="Bot Token", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        self.discord_token_entry = tk.Entry(form_card, show='*',
                                           bg=self.colors['bg_input'], fg=self.colors['text_white'],
                                           font=self.fonts['body'],
                                           relief=tk.FLAT,
                                           insertbackground=self.colors['accent_green'],
                                           borderwidth=1)
        self.discord_token_entry.pack(fill=tk.X, padx=20, pady=(0, 15), ipady=8)
        
        # Channel ID
        tk.Label(form_card, text="ID del Canal", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        self.discord_channel_entry = tk.Entry(form_card,
                                             bg=self.colors['bg_input'], fg=self.colors['text_white'],
                                             font=self.fonts['body'],
                                             relief=tk.FLAT,
                                             insertbackground=self.colors['accent_green'],
                                             borderwidth=1)
        self.discord_channel_entry.pack(fill=tk.X, padx=20, pady=(0, 15), ipady=8)
        
        # Status
        status_frame = tk.Frame(form_card, bg=self.colors['bg_medium'])
        status_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        tk.Label(status_frame, text="Estado:", font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(side=tk.LEFT)
        
        self.discord_status_label = tk.Label(status_frame, text="● Desconectado",
                                            font=self.fonts['body'],
                                            bg=self.colors['bg_medium'], fg=self.colors['accent_red'])
        self.discord_status_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = tk.Frame(form_card, bg=self.colors['bg_medium'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(button_frame, text="💾 Guardar",
                 command=self._save_discord_config,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="▶ Conectar",
                 command=self._connect_discord,
                 bg=self.colors['accent_green'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="🧪 Probar",
                 command=self._test_discord,
                 bg=self.colors['accent_gold'], fg=self.colors['bg_dark'],
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT)
        
        # Instructions card
        inst_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        inst_card.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        tk.Label(inst_card, text="📋 Guía de Configuración", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        instructions = """1. Ve a Discord Developer Portal: https://discord.com/developers/applications
2. Crea una nueva aplicación
3. Ve a "Bot" y copia el TOKEN
4. Habilita "MESSAGE CONTENT INTENT"
5. Invita el bot con permisos: Ver canales, Enviar mensajes
6. Copia el ID del canal (click derecho > Copiar ID)
7. Pega TOKEN y CHANNEL ID arriba
8. Click en "Guardar" y luego "Conectar"

Comandos disponibles:
• !fc26 status - Ver estado del bot
• !fc26 recomendaciones - Ver mejores compras
• !fc26 vender - Ver cartas para vender
• !fc26 presupuesto [cantidad] - Actualizar presupuesto
• !fc26 ayuda - Ver todos los comandos

El bot enviará recomendaciones automáticas a las 9:00 AM"""
        
        inst_text = scrolledtext.ScrolledText(inst_card, height=15,
                                             bg=self.colors['bg_input'], fg=self.colors['text_light'],
                                             font=self.fonts['mono'],
                                             relief=tk.FLAT,
                                             wrap=tk.WORD,
                                             borderwidth=0)
        inst_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        inst_text.insert('1.0', instructions)
        inst_text.config(state='disabled')
        
        # Load saved config
        self._load_discord_config()
    
    def _create_settings_tab(self, parent):
        """Create settings tab with modern design"""
        # Header
        header = tk.Frame(parent, bg=self.colors['bg_medium'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Configuración del Bot",
                font=self.fonts['header'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(pady=(20, 5))
        
        tk.Label(header, 
                text="Personaliza el comportamiento del bot según tus necesidades",
                font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(pady=(0, 15))
        
        # Budget configuration card
        budget_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        budget_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(budget_card, text="💰 Presupuesto de Trading", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        budget_input_frame = tk.Frame(budget_card, bg=self.colors['bg_medium'])
        budget_input_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(budget_input_frame, text="Monedas disponibles:", font=self.fonts['body'],
                bg=self.colors['bg_medium'], fg=self.colors['text_light']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.budget_entry = tk.Entry(budget_input_frame,
                                     bg=self.colors['bg_input'], fg=self.colors['text_white'],
                                     font=self.fonts['body'],
                                     relief=tk.FLAT,
                                     insertbackground=self.colors['accent_green'],
                                     width=15)
        self.budget_entry.pack(side=tk.LEFT, ipady=6)
        self.budget_entry.insert(0, "11000")
        
        tk.Button(budget_input_frame, text="💾 Guardar",
                 command=self._save_budget_from_settings,
                 bg=self.colors['accent_green'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=8).pack(side=tk.LEFT, padx=10)
        
        # Info about tiers
        tier_info = tk.Frame(budget_card, bg=self.colors['bg_input'])
        tier_info.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tier_text = """Niveles de Trading:
• BAJO (0-20K): Bronze/Silver flipping, Mass bidding
• MEDIO (20K-100K): Fodder trading, League SBCs
• ALTO (100K+): High-end cards, Icon SBCs
• ELITE (1M+): Icons, TOTY, Market manipulation"""
        
        tk.Label(tier_info, text=tier_text, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
        
        # Update schedule card
        schedule_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        schedule_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(schedule_card, text="⏰ Horarios de Actualización", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        schedule_info = tk.Frame(schedule_card, bg=self.colors['bg_input'])
        schedule_info.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        schedule_text = """Actualizaciones automáticas configuradas:
✓ 9:00 AM - Actualización matutina
✓ 1:00 PM - Actualización mediodía
✓ 10:00 PM - Actualización nocturna

Si el PC está apagado, las actualizaciones se ejecutarán:
• 15 minutos después de encender el PC
• Durante el arranque de Windows (5 min después)

Esto garantiza que NUNCA pierdas una actualización de precios."""
        
        tk.Label(schedule_info, text=schedule_text, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
        
        # Theme toggle card
        theme_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        theme_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(theme_card, text="🎨 Apariencia", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        theme_btn_frame = tk.Frame(theme_card, bg=self.colors['bg_medium'])
        theme_btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        theme_icon = "🌙" if self.current_theme == 'dark' else "☀️"
        theme_text = "Cambiar a Tema Claro" if self.current_theme == 'dark' else "Cambiar a Tema Oscuro"
        
        tk.Button(theme_btn_frame, text=f"{theme_icon} {theme_text}",
                 command=self._toggle_theme,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT)
        
        theme_info = tk.Frame(theme_card, bg=self.colors['bg_input'])
        theme_info.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        theme_desc = "Cambia entre tema oscuro y claro. La aplicación se reiniciará para aplicar los cambios."
        tk.Label(theme_info, text=theme_desc, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
        
        # Database update card (NUEVO)
        update_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        update_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(update_card, text="🔄 Actualización de Base de Datos", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        update_btn_frame = tk.Frame(update_card, bg=self.colors['bg_medium'])
        update_btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Button(update_btn_frame, text="🔄 Actualización Completa (100 páginas)",
                 command=self._run_full_database_update,
                 bg=self.colors['accent_cyan'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(update_btn_frame, text="⚡ Actualización Rápida (Solo existentes)",
                 command=self._run_quick_database_update,
                 bg=self.colors['accent_green'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, borderwidth=0,
                 cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT)
        
        update_info = tk.Frame(update_card, bg=self.colors['bg_input'])
        update_info.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        update_desc = """Actualización Manual de Datos:
• Completa: Descarga ~1500 jugadores desde FUTBIN (50 páginas) - 15 min
• Rápida: Solo actualiza jugadores ya existentes en tu base de datos - 3-5 min

Recomendado: Actualización Completa 1 vez por semana
Uso diario: La app actualiza automáticamente al iniciar"""
        
        tk.Label(update_info, text=update_desc, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
        
        # About section
        about_card = tk.Frame(parent, bg=self.colors['bg_medium'])
        about_card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        tk.Label(about_card, text="ℹ️ Acerca del Bot", font=self.fonts['subheader'],
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        about_info = tk.Frame(about_card, bg=self.colors['bg_input'])
        about_info.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        about_text = """EA FC 26 Trading Bot Pro v2.0
Desarrollado para trading inteligente en EA FC 26
Created by xSuppra

Características:
✓ Precios reales de FUTBIN (~900-1500 jugadores)
✓ Estrategias adaptadas a tu presupuesto
✓ Actualizaciones automáticas al inicio
✓ Predicciones ML con eventos y SBCs
✓ Análisis de mercado por horarios
✓ Detección de jugadores extintos
✓ Sistema de recomendaciones inteligente
✓ Descarga paralela optimizada (sin rate limiting)

© 2025 xSuppra - Todos los derechos reservados"""
        
        tk.Label(about_info, text=about_text, font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_light'],
                justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)
    
    def _create_live_prices_tab(self, parent):
        """Create live prices tab with real-time feed"""
        # Tab container
        tab_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        tab_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header = tk.Frame(tab_container, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Stats cards row
        stats_row = tk.Frame(header, bg=self.colors['bg_dark'])
        stats_row.pack(fill=tk.X)
        
        # Polling status card
        status_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        status_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(status_card, text="Estado del Feed", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(15, 5))
        
        self.feed_status_label = tk.Label(status_card, text="⚪ DETENIDO", font=self.fonts['header'],
                                          bg=self.colors['bg_medium'], fg=self.colors['text_gray'])
        self.feed_status_label.pack(padx=15, pady=(0, 15))
        
        # Watchlist size card
        watchlist_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        watchlist_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(watchlist_card, text="Jugadores Monitoreados", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(15, 5))
        
        self.watchlist_size_label = tk.Label(watchlist_card, text="0", font=self.fonts['header'],
                                             bg=self.colors['bg_medium'], fg=self.colors['accent_blue'])
        self.watchlist_size_label.pack(padx=15, pady=(0, 15))
        
        # Updates detected card
        updates_card = tk.Frame(stats_row, bg=self.colors['bg_medium'], relief=tk.FLAT)
        updates_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(updates_card, text="Cambios Detectados", font=self.fonts['small'],
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack(padx=15, pady=(15, 5))
        
        self.updates_count_label = tk.Label(updates_card, text="0", font=self.fonts['header'],
                                            bg=self.colors['bg_medium'], fg=self.colors['accent_green'])
        self.updates_count_label.pack(padx=15, pady=(0, 15))
        
        # Control buttons
        controls_frame = tk.Frame(tab_container, bg=self.colors['bg_dark'])
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Start/Stop button
        self.feed_toggle_btn = tk.Button(controls_frame, text="▶️ INICIAR FEED",
                                         command=self._toggle_price_feed,
                                         bg=self.colors['accent_green'], fg='white',
                                         font=self.fonts['subheader'],
                                         relief=tk.FLAT, cursor='hand2',
                                         padx=25, pady=12)
        self.feed_toggle_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-populate from inventory button
        tk.Button(controls_frame, text="📦 Cargar desde Inventario",
                 command=self._load_watchlist_from_inventory,
                 bg=self.colors['accent_blue'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear watchlist button
        tk.Button(controls_frame, text="🗑️ Limpiar Watchlist",
                 command=self._clear_watchlist,
                 bg=self.colors['accent_red'], fg='white',
                 font=self.fonts['body'],
                 relief=tk.FLAT, cursor='hand2',
                 padx=20, pady=10).pack(side=tk.LEFT)
        
        # Content area: 2 columns
        content = tk.Frame(tab_container, bg=self.colors['bg_dark'])
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left column: Recent changes (60%)
        left_col = tk.Frame(content, bg=self.colors['bg_dark'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_col, text="⚡ Cambios en Tiempo Real", font=self.fonts['subheader'],
                bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=(0, 10))
        
        # Scrollable frame for changes
        changes_canvas = tk.Canvas(left_col, bg=self.colors['bg_medium'], highlightthickness=0)
        changes_scroll = tk.Scrollbar(left_col, orient=tk.VERTICAL, command=changes_canvas.yview)
        self.changes_frame = tk.Frame(changes_canvas, bg=self.colors['bg_medium'])
        
        self.changes_frame.bind('<Configure>', 
                               lambda e: changes_canvas.configure(scrollregion=changes_canvas.bbox('all')))
        
        changes_canvas.create_window((0, 0), window=self.changes_frame, anchor='nw')
        changes_canvas.configure(yscrollcommand=changes_scroll.set)
        
        changes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        changes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right column: Watchlist (40%)
        right_col = tk.Frame(content, bg=self.colors['bg_dark'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_col, text="👁️ Watchlist", font=self.fonts['subheader'],
                bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=(0, 10))
        
        # Scrollable frame for watchlist
        watchlist_canvas = tk.Canvas(right_col, bg=self.colors['bg_medium'], highlightthickness=0)
        watchlist_scroll = tk.Scrollbar(right_col, orient=tk.VERTICAL, command=watchlist_canvas.yview)
        self.watchlist_frame = tk.Frame(watchlist_canvas, bg=self.colors['bg_medium'])
        
        self.watchlist_frame.bind('<Configure>',
                                 lambda e: watchlist_canvas.configure(scrollregion=watchlist_canvas.bbox('all')))
        
        watchlist_canvas.create_window((0, 0), window=self.watchlist_frame, anchor='nw')
        watchlist_canvas.configure(yscrollcommand=watchlist_scroll.set)
        
        watchlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        watchlist_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize real-time feed service
        self.price_feed = None
        self._initialize_price_feed()
    
    def _initialize_price_feed(self):
        """Initialize real-time price feed service"""
        try:
            from app.services.realtime_feed_service import RealTimePriceFeed
            from app.services.futbin_service import FUTBINScraper
            
            if not hasattr(self, 'futbin_scraper'):
                self.futbin_scraper = FUTBINScraper()
            
            self.price_feed = RealTimePriceFeed(self.db_manager, self.futbin_scraper)
            
            # Register callback for price changes
            self.price_feed.register_callback(self._on_price_change)
            
            logger.info("✅ Real-Time Price Feed inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando price feed: {e}")
            self.price_feed = None
    
    def _toggle_price_feed(self):
        """Toggle price feed on/off"""
        if not self.price_feed:
            messagebox.showwarning("Error", "Price feed no disponible")
            return
        
        if self.price_feed.is_running:
            # Stop feed
            self.price_feed.stop_polling()
            self.feed_toggle_btn.config(text="▶️ INICIAR FEED", bg=self.colors['accent_green'])
            self.feed_status_label.config(text="⚪ DETENIDO", fg=self.colors['text_gray'])
            self._add_activity_log("⏸️ Feed de precios detenido")
        else:
            # Start feed
            if len(self.price_feed.watchlist) == 0:
                messagebox.showwarning("Watchlist Vacía", 
                                      "Añade jugadores a la watchlist primero.\n\nUsa 'Cargar desde Inventario' o añade manualmente.")
                return
            
            self.price_feed.start_polling()
            self.feed_toggle_btn.config(text="⏸️ DETENER FEED", bg=self.colors['accent_red'])
            self.feed_status_label.config(text="🟢 ACTIVO", fg=self.colors['accent_green'])
            self._add_activity_log(f"▶️ Feed iniciado ({len(self.price_feed.watchlist)} jugadores)")
    
    def _load_watchlist_from_inventory(self):
        """Load watchlist from inventory"""
        if not self.price_feed:
            return
        
        self.price_feed.auto_populate_watchlist_from_inventory()
        self._refresh_live_prices()
        
        count = len(self.price_feed.watchlist)
        self._add_activity_log(f"📦 Watchlist cargada desde inventario: {count} jugadores")
        messagebox.showinfo("Éxito", f"Watchlist cargada con {count} jugadores del inventario")
    
    def _clear_watchlist(self):
        """Clear watchlist"""
        if not self.price_feed:
            return
        
        if messagebox.askyesno("Confirmar", "¿Limpiar toda la watchlist?"):
            self.price_feed.clear_watchlist()
            self._refresh_live_prices()
            self._add_activity_log("🗑️ Watchlist limpiada")
    
    def _on_price_change(self, change: Dict[str, Any]):
        """Callback cuando hay cambio de precio"""
        # Add to changes feed
        self._add_price_change_card(change)
        
        # Update stats
        if self.price_feed:
            stats = self.price_feed.get_stats()
            self.updates_count_label.config(text=str(stats['updates']))
        
        # Add to activity log
        direction_emoji = "📈" if change['change'] > 0 else "📉"
        self._add_activity_log(
            f"{direction_emoji} {change['player_name']}: "
            f"{change['old_price']:,} → {change['new_price']:,} ({change['change_pct']:+.1f}%)"
        )
    
    def _add_price_change_card(self, change: Dict[str, Any]):
        """Add price change card to feed"""
        try:
            # Create card
            card = tk.Frame(self.changes_frame, bg=self.colors['bg_light'], relief=tk.FLAT)
            card.pack(fill=tk.X, pady=5, padx=10)
            
            # Header row: Name and timestamp
            header = tk.Frame(card, bg=self.colors['bg_light'])
            header.pack(fill=tk.X, padx=15, pady=(12, 5))
            
            tk.Label(header, text=change['player_name'], font=self.fonts['subheader'],
                    bg=self.colors['bg_light'], fg=self.colors['text_white']).pack(side=tk.LEFT)
            
            timestamp = datetime.fromisoformat(change['timestamp'])
            time_str = timestamp.strftime('%H:%M:%S')
            tk.Label(header, text=time_str, font=self.fonts['small'],
                    bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(side=tk.RIGHT)
            
            # Price row
            price_row = tk.Frame(card, bg=self.colors['bg_light'])
            price_row.pack(fill=tk.X, padx=15, pady=(0, 12))
            
            # Old price
            tk.Label(price_row, text=f"{change['old_price']:,}", font=self.fonts['body'],
                    bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(side=tk.LEFT)
            
            # Arrow
            arrow = "→" if change['change'] >= 0 else "→"
            tk.Label(price_row, text=f" {arrow} ", font=self.fonts['body'],
                    bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(side=tk.LEFT)
            
            # New price
            price_color = self.colors['accent_green'] if change['change'] > 0 else self.colors['accent_red']
            tk.Label(price_row, text=f"{change['new_price']:,}", font=self.fonts['subheader'],
                    bg=self.colors['bg_light'], fg=price_color).pack(side=tk.LEFT)
            
            # Change percentage
            change_text = f"{change['change_pct']:+.2f}%"
            tk.Label(price_row, text=change_text, font=self.fonts['body'],
                    bg=self.colors['bg_light'], fg=price_color).pack(side=tk.LEFT, padx=(10, 0))
            
            # Keep only last 20 changes
            children = self.changes_frame.winfo_children()
            if len(children) > 20:
                children[0].destroy()
            
        except Exception as e:
            logger.error(f"Error añadiendo card de cambio: {e}")
    
    def _refresh_live_prices(self):
        """Refresh live prices display"""
        if not self.price_feed:
            return
        
        try:
            # Update stats
            stats = self.price_feed.get_stats()
            self.watchlist_size_label.config(text=str(stats['watchlist_size']))
            self.updates_count_label.config(text=str(stats['updates']))
            
            # Update status
            if stats['is_running']:
                self.feed_status_label.config(text="🟢 ACTIVO", fg=self.colors['accent_green'])
                self.feed_toggle_btn.config(text="⏸️ DETENER FEED", bg=self.colors['accent_red'])
            else:
                self.feed_status_label.config(text="⚪ DETENIDO", fg=self.colors['text_gray'])
                self.feed_toggle_btn.config(text="▶️ INICIAR FEED", bg=self.colors['accent_green'])
            
            # Refresh watchlist display
            for widget in self.watchlist_frame.winfo_children():
                widget.destroy()
            
            if len(self.price_feed.watchlist) == 0:
                tk.Label(self.watchlist_frame, text="Watchlist vacía\n\nUsa 'Cargar desde Inventario'",
                        font=self.fonts['body'], bg=self.colors['bg_medium'],
                        fg=self.colors['text_gray']).pack(pady=50)
            else:
                session = self.db_manager.get_session()
                
                for player_id in self.price_feed.watchlist:
                    player = session.query(self.db_manager.Player).filter_by(
                        player_id=player_id
                    ).first()
                    
                    if player:
                        # Create watchlist item
                        item = tk.Frame(self.watchlist_frame, bg=self.colors['bg_light'], relief=tk.FLAT)
                        item.pack(fill=tk.X, pady=3, padx=10)
                        
                        # Player name and rating
                        info_frame = tk.Frame(item, bg=self.colors['bg_light'])
                        info_frame.pack(fill=tk.X, padx=15, pady=10)
                        
                        tk.Label(info_frame, text=player.name, font=self.fonts['body'],
                                bg=self.colors['bg_light'], fg=self.colors['text_white']).pack(side=tk.LEFT)
                        
                        rating_badge = tk.Label(info_frame, text=str(player.rating),
                                               bg=self.colors['accent_gold'], fg='black',
                                               font=self.fonts['small'], padx=8, py=3)
                        rating_badge.pack(side=tk.RIGHT)
                
                session.close()
        
        except Exception as e:
            logger.error(f"Error refreshing live prices: {e}")
    
    def _load_theme_preference(self):
        """Load theme preference from config file"""
        try:
            import yaml
            import os
            
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    
                if 'ui' in config_data and 'theme' in config_data['ui']:
                    theme = config_data['ui']['theme']
                    logger.info(f"✓ Tema cargado desde config: {theme}")
                    return theme
        except Exception as e:
            logger.error(f"Error cargando preferencia de tema: {e}")
        
        # Default to dark theme
        return 'dark'
    
    def _load_budget(self):
        """Load and display current budget"""
        try:
            from app.utils.config_loader import ConfigLoader
            
            config = ConfigLoader()
            budget_info = config.get_budget_info()
            
            self.budget_label.config(text=f"{budget_info['current_budget']:,}")
            
            tier = budget_info['tier'].upper()
            tier_map = {
                'LOW': 'BAJO (0-20K)',
                'MEDIUM': 'MEDIO (20K-100K)',
                'HIGH': 'ALTO (100K+)',
                'ELITE': 'ELITE (1M+)'
            }
            tier_colors = {
                'LOW': self.colors['accent_blue'],
                'MEDIUM': self.colors['accent_gold'],
                'HIGH': self.colors['accent_purple'],
                'ELITE': self.colors['accent_green']
            }
            tier_text = tier_map.get(tier, tier)
            self.tier_label.config(text=tier_text, fg=tier_colors.get(tier, self.colors['accent_blue']))
            
            self._log(f"✓ Presupuesto: {budget_info['current_budget']:,} coins ({tier})")
            
        except Exception as e:
            logger.error(f"Error loading budget: {e}")
            self._log(f"✗ Error al cargar presupuesto: {e}")
    
    def _show_budget_config(self):
        """Show budget configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurar Presupuesto")
        dialog.geometry("400x250")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Content
        tk.Label(dialog, text="💰 Configurar Presupuesto",
                font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#00d9ff').pack(pady=20)
        
        tk.Label(dialog, text="Ingresa tu presupuesto actual en monedas:",
                font=('Arial', 10),
                bg='#1a1a2e', fg='#ffffff').pack(pady=5)
        
        budget_entry = tk.Entry(dialog, width=30,
                               bg='#16213e', fg='#ffffff',
                               font=('Arial', 12),
                               justify=tk.CENTER,
                               relief=tk.FLAT,
                               insertbackground='#00ff88')
        budget_entry.pack(pady=10)
        budget_entry.insert(0, str(self.budget_label.cget('text').replace(' monedas', '').replace(',', '')))
        
        def save_budget():
            try:
                new_budget = int(budget_entry.get())
                
                from app.utils.config_loader import ConfigLoader
                config = ConfigLoader()
                config.update_budget(new_budget)
                
                self._load_budget()
                self._log(f"Presupuesto actualizado a {new_budget:,} monedas")
                messagebox.showinfo("Éxito", f"Presupuesto actualizado a {new_budget:,} monedas")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un número válido")
        
        tk.Button(dialog, text="💾 Guardar",
                 command=save_budget,
                 bg='#00ff88', fg='#1a1a2e',
                 font=('Arial', 10, 'bold'),
                 relief=tk.RAISED, borderwidth=2,
                 padx=30, pady=8).pack(pady=20)
    
    def _save_budget_from_settings(self):
        """Save budget from settings page"""
        try:
            new_budget = int(self.budget_entry.get())
            
            from app.utils.config_loader import ConfigLoader
            config = ConfigLoader()
            config.update_budget(new_budget)
            
            self._load_budget()
            self._log(f"✓ Presupuesto actualizado a {new_budget:,} monedas")
            messagebox.showinfo("Éxito", f"Presupuesto actualizado a {new_budget:,} monedas")
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un número válido")
    
    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        try:
            # Save current dark colors if not already saved
            if not hasattr(self, 'colors_dark'):
                self.colors_dark = self.colors.copy()
            
            # Toggle theme
            if self.current_theme == 'dark':
                new_theme = 'light'
                self._log("🌙 → ☀️ Cambiando a tema claro...")
            else:
                new_theme = 'dark'
                self._log("☀️ → 🌙 Cambiando a tema oscuro...")
            
            # Save theme preference to config
            from app.utils.config_loader import ConfigLoader
            config = ConfigLoader()
            
            # Load config file
            import yaml
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            else:
                config_data = {}
            
            # Update theme
            if 'ui' not in config_data:
                config_data['ui'] = {}
            config_data['ui']['theme'] = new_theme
            
            # Save config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            # Show restart message
            result = messagebox.askquestion(
                "Reiniciar Aplicación",
                f"Tema cambiado a {'Claro' if new_theme == 'light' else 'Oscuro'}.\n\n"
                "¿Deseas reiniciar la aplicación ahora para aplicar los cambios?",
                icon='question'
            )
            
            if result == 'yes':
                # Close and restart
                import sys
                self.root.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)
            
        except Exception as e:
            self._log(f"❌ Error al cambiar tema: {e}")
            messagebox.showerror("Error", f"No se pudo cambiar el tema: {e}")
    
    def _run_full_database_update(self):
        """Ejecuta actualización completa de base de datos (100 páginas)"""
        from tkinter import messagebox
        import threading
        
        result = messagebox.askyesno(
            "Actualización Completa",
            "Esto descargará ~1500 jugadores desde FUTBIN (50 páginas).\n"
            "Tiempo estimado: 15 minutos\n\n"
            "¿Deseas continuar?",
            icon='question'
        )
        
        if not result:
            return
        
        self._log("🔄 Iniciando actualización completa de base de datos...")
        
        def run_update():
            try:
                from app.services.futbin_service import FUTBINScraper
                from app.models.database import DatabaseManager
                from app.utils.update_strategy import UpdateStrategy
                
                scraper = FUTBINScraper()
                db = DatabaseManager()
                strategy = UpdateStrategy()
                
                self._log("📥 Descargando 50 páginas en paralelo (3 hilos)...")
                
                # Descarga paralela
                all_players = scraper.get_all_players_parallel(
                    max_pages=50,
                    num_threads=3,
                    progress_callback=None
                )
                
                self._log(f"💰 Obteniendo precios de {len(all_players)} jugadores...")
                
                # Actualizar precios
                updated = 0
                for player in all_players:
                    try:
                        response = scraper.session.get(player['url'], timeout=15)
                        if response.status_code == 200:
                            from bs4 import BeautifulSoup
                            import re
                            soup = BeautifulSoup(response.text, 'html.parser')
                            price_text = soup.get_text()
                            match = re.search(r'([\d,]+)\s+on\s+PC', price_text, re.IGNORECASE)
                            
                            if match:
                                price_str = match.group(1).replace(',', '')
                                pc_price = int(price_str)
                                
                                # Crear o actualizar jugador
                                session = db.get_session()
                                from app.models.database import Player
                                
                                existing = session.query(Player).filter_by(
                                    player_id=player['player_id']
                                ).first()
                                
                                if not existing:
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
                                    if existing.is_extinct:
                                        existing.is_extinct = False
                                        session.commit()
                                    player_db_id = existing.id
                                
                                session.close()
                                db.add_price_history(player_db_id, pc_price)
                                updated += 1
                                
                                if updated % 100 == 0:
                                    self._log(f"✓ {updated} jugadores actualizados...")
                                
                    except Exception as e:
                        continue
                
                # Marcar actualización
                strategy.mark_full_update(updated)
                
                self._log(f"✅ Actualización completa: {updated} jugadores actualizados")
                messagebox.showinfo("Éxito", f"Base de datos actualizada con {updated} jugadores")
                
            except Exception as e:
                self._log(f"❌ Error en actualización: {e}")
                messagebox.showerror("Error", f"Error durante actualización: {e}")
        
        # Ejecutar en thread
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
    
    def _run_quick_database_update(self):
        """Ejecuta actualización rápida solo de jugadores existentes"""
        from tkinter import messagebox
        import threading
        
        result = messagebox.askyesno(
            "Actualización Rápida",
            "Esto actualizará solo los jugadores que ya están en tu base de datos.\n"
            "Tiempo estimado: 3-5 minutos\n\n"
            "¿Deseas continuar?",
            icon='question'
        )
        
        if not result:
            return
        
        self._log("⚡ Iniciando actualización rápida...")
        
        def run_update():
            try:
                from app.services.futbin_service import FUTBINScraper
                from app.models.database import DatabaseManager
                from app.utils.update_strategy import UpdateStrategy
                
                scraper = FUTBINScraper()
                db = DatabaseManager()
                strategy = UpdateStrategy()
                
                self._log("🔄 Actualizando jugadores existentes...")
                
                updated = scraper.update_existing_players_incremental(
                    db_manager=db,
                    progress_callback=None
                )
                
                strategy.mark_incremental_update(updated)
                
                self._log(f"✅ Actualización rápida: {updated} jugadores actualizados")
                messagebox.showinfo("Éxito", f"{updated} jugadores actualizados correctamente")
                
            except Exception as e:
                self._log(f"❌ Error en actualización: {e}")
                messagebox.showerror("Error", f"Error durante actualización: {e}")
        
        # Ejecutar en thread
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
    
    def _show_discord_config(self):
        """Show Discord configuration (switch to Discord tab)"""
        # This will be implemented to switch tabs
        self._log("Abriendo configuración de Discord...")
    
    def _get_demo_recommendations(self):
        """Get demo recommendations for display"""
        return [
            {
                'player_name': 'Casemiro',
                'rating': 83,
                'current_price': 3500,
                'profit_potential': 800,
                'profit_percentage': 22.8,
                'confidence': 0.85,
                'strategy': 'Fodder Flipping',
                'trend': 'rising'
            },
            {
                'player_name': 'Bruno Fernandes',
                'rating': 86,
                'current_price': 7200,
                'profit_potential': 1500,
                'profit_percentage': 20.8,
                'confidence': 0.78,
                'strategy': 'Weekend League',
                'trend': 'stable'
            },
            {
                'player_name': 'Nico Williams',
                'rating': 82,
                'current_price': 2800,
                'profit_potential': 600,
                'profit_percentage': 21.4,
                'confidence': 0.72,
                'strategy': 'Snipe Deals',
                'trend': 'falling'
            }
        ]
    
    def _add_to_inventory(self, player_id: str, player_name: str, price: int, quantity: int):
        """Add purchase to inventory"""
        try:
            from app.models.database import Inventory
            from datetime import datetime
            
            if not self.db_manager:
                self._log("⚠️ Database no disponible")
                return
            
            session = self.db_manager.get_session()
            
            # Create inventory entry
            inventory_item = Inventory(
                player_id=player_id,
                player_name=player_name,
                purchase_price=price,
                quantity=quantity,
                status='owned',
                notes=f"Compra desde recomendaciones - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            session.add(inventory_item)
            session.commit()
            
            total_cost = price * quantity
            self._log(f"✅ COMPRA REGISTRADA: {quantity}x {player_name} @ {price:,} coins = {total_cost:,} coins total")
            self._log(f"💡 Ve a EA FC 26 y compra {quantity} carta(s) de {player_name} al precio aproximado de {price:,} coins")
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error adding to inventory: {e}", exc_info=True)
            self._log(f"❌ Error al registrar compra: {str(e)}")
    
    def _log(self, message: str):
        """Add message to activity log with optimized management"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Add to tracking list
        self.activity_log_lines.append(formatted_message)
        
        # Limit to max lines
        if len(self.activity_log_lines) > self.max_log_lines:
            self.activity_log_lines = self.activity_log_lines[-self.max_log_lines:]
            
            # Rebuild log text
            self.log_text.delete('1.0', tk.END)
            for line in self.activity_log_lines:
                self.log_text.insert(tk.END, line)
        else:
            # Just append
            self.log_text.insert(tk.END, formatted_message)
        
        # Auto-scroll to end
        self.log_text.see(tk.END)
    
    def _toggle_bot(self):
        """Toggle bot on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_label.config(text="● ACTIVO", fg=self.colors['accent_green'])
            self.start_button.config(text="Detener Bot", bg=self.colors['accent_red'])
            self._log("✓ Bot iniciado")
        else:
            self.status_label.config(text="● INACTIVO", fg=self.colors['accent_red'])
            self.start_button.config(text="Iniciar Bot", bg=self.colors['accent_green'])
            self._log("✓ Bot detenido")
    
    def _update_prices(self):
        """Actualizar TODOS los precios desde FUTBIN (PC)"""
        self._log("🌐 Actualizando TODOS los jugadores desde FUTBIN (PC)...")
        self._log("⚠️ Esto puede tomar 3-5 minutos...")
        
        def run_futbin_scraper():
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                
                from app.services.futbin_service import FUTBINScraper
                from app.models.database import DatabaseManager
                
                db = DatabaseManager()
                scraper = FUTBINScraper()
                
                # Crear ventana de progreso
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Actualización Optimizada")
                progress_window.geometry("500x250")
                progress_window.configure(bg=self.colors['bg_dark'])
                progress_window.resizable(False, False)
                
                # Centrar ventana
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                tk.Label(progress_window, text="🎯 Actualización Optimizada", 
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['accent_green']).pack(pady=20)
                
                # Info box
                info_frame = tk.Frame(progress_window, bg=self.colors['bg_medium'])
                info_frame.pack(fill=tk.X, padx=20, pady=10)
                
                info_text = """Solo actualiza jugadores relevantes:
• Fodder 82-85 (todas las ligas)
• Especiales 86-88 (ligas top)
• High rated <50k (oportunidades)

⚡ 10x más rápido que actualización completa"""
                
                tk.Label(info_frame, text=info_text, 
                        font=('Segoe UI', 9),
                        bg=self.colors['bg_medium'], fg=self.colors['text_light'],
                        justify=tk.LEFT).pack(padx=10, pady=10)
                
                # Barra de progreso
                progress_bar = ttk.Progressbar(progress_window, length=400, mode='indeterminate')
                progress_bar.pack(pady=10)
                progress_bar.start(10)
                
                # Labels de estado
                status_label = tk.Label(progress_window, text="Iniciando actualización optimizada...", 
                                       font=('Segoe UI', 10),
                                       bg=self.colors['bg_dark'], fg=self.colors['text_light'])
                status_label.pack(pady=5)
                
                time_label = tk.Label(progress_window, text="⏱️ Tiempo estimado: 2-3 minutos", 
                                     font=('Segoe UI', 9),
                                     bg=self.colors['bg_dark'], fg=self.colors['text_gray'])
                time_label.pack(pady=5)
                
                progress_window.update()
                
                self._log(f"🎯 Iniciando actualización optimizada...")
                self._log(f"📋 Solo jugadores relevantes (Fodder 82-85 + Especiales)")
                self._log(f"⚡ 10x más rápido que actualización completa\n")
                
                # Actualización optimizada
                import time
                start_time = time.time()
                
                status_label.config(text="Scraping FUTBIN (solo ratings relevantes)...")
                progress_window.update()
                
                # Ejecutar actualización optimizada
                updated = scraper.update_database(db)
                
                elapsed = time.time() - start_time
                mins, secs = divmod(int(elapsed), 60)
                
                progress_bar.stop()
                progress_window.destroy()
                
                self._log(f"\n✅ Actualización optimizada completada en {mins}m {secs}s")
                self._log(f"📊 {updated} jugadores actualizados")
                self._refresh_recommendations()
                
                messagebox.showinfo("Éxito", 
                    f"✅ Actualización Optimizada Completada\n\n"
                    f"📊 {updated} jugadores actualizados\n"
                    f"⏱️ Tiempo: {mins}m {secs}s\n\n"
                    f"💡 Solo se actualizan jugadores relevantes para trading")
                
            except Exception as e:
                if 'progress_window' in locals():
                    progress_bar.stop()
                    progress_window.destroy()
                self._log(f"❌ Error en actualización optimizada: {e}")
                import traceback
                self._log(traceback.format_exc())
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        # Ejecutar en background
        import threading
        threading.Thread(target=run_futbin_scraper, daemon=True).start()
    
    def _show_recommendations(self):
        """Show buy recommendations"""
        self._log("Obteniendo recomendaciones de compra...")
        self._refresh_recommendations()
    
    def _show_buy_dialog(self):
        """Show dialog to record a buy"""
        # Implementation here
        pass
    
    def _show_sell_dialog(self):
        """Show dialog to record a sell"""
        # Implementation here
        pass
    
    def _refresh_fodder_plan(self):
        """Refresh buy recommendations based on real market data"""
        try:
            logger.info("🔄 Actualizando recomendaciones de compra...")
            
            # Clear market moment frame
            if hasattr(self, 'market_moment_frame'):
                for widget in self.market_moment_frame.winfo_children():
                    widget.destroy()
                
                # Get current market moment based on day/time
                from datetime import datetime
                now = datetime.now()
                hour = now.hour
                day = now.weekday()  # 0=Monday, 4=Friday
                
                # Determine market moment - Weekend League Strategy
                if day in [0, 1]:  # Monday/Tuesday - BUY phase
                    emoji = "🛒"
                    action = "COMPRAR AHORA"
                    reason = "Lunes/Martes - Precios bajos, poca demanda"
                    urgency = "ALTA"
                    confidence = 90
                elif day == 2:  # Wednesday - HOLD/Monitor
                    emoji = "📊"
                    action = "MANTENER Y MONITOREAR"
                    reason = "Miércoles - Espera la subida del fin de semana"
                    urgency = "BAJA"
                    confidence = 70
                elif day in [3, 4]:  # Thursday/Friday - SELL phase
                    emoji = "💰"
                    action = "VENDER AHORA"
                    reason = "Jueves/Viernes - Weekend League, alta demanda"
                    urgency = "ALTA"
                    confidence = 85
                elif day in [5, 6]:  # Saturday/Sunday - Weekend
                    emoji = "🎮"
                    action = "NO COMPRAR"
                    reason = "Fin de semana - Precios máximos por WL activo"
                    urgency = "BAJA"
                    confidence = 80
                elif hour < 10:
                    emoji = "🌅"
                    action = "COMPRAR - PRECIOS BAJOS"
                    reason = "Madrugada - Menos competencia"
                    urgency = "MEDIA"
                    confidence = 70
                elif hour > 20:
                    emoji = "🌙"
                    action = "ESPERAR"
                    reason = "Noche - Precios elevados"
                    urgency = "BAJA"
                    confidence = 60
                else:
                    emoji = "📊"
                    action = "MONITOREAR MERCADO"
                    reason = "Horario normal - Buscar oportunidades"
                    urgency = "MEDIA"
                    confidence = 65
                
                # Display market moment
                moment_content = tk.Frame(self.market_moment_frame, bg=self.colors['bg_light'])
                moment_content.pack(fill=tk.X, padx=20, pady=15)
                
                # Emoji and action
                tk.Label(moment_content, text=emoji, font=('Segoe UI Emoji', 32),
                        bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=(0, 15))
                
                action_frame = tk.Frame(moment_content, bg=self.colors['bg_light'])
                action_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                action_color = self.colors['accent_green'] if 'COMPRAR' in action else \
                              self.colors['accent_gold'] if 'VENDER' in action else \
                              self.colors['accent_red'] if 'NO COMPRAR' in action else \
                              self.colors['text_white']
                
                tk.Label(action_frame, text=action, font=('Segoe UI', 18, 'bold'),
                        bg=self.colors['bg_light'], fg=action_color).pack(anchor='w')
                
                tk.Label(action_frame, text=reason, font=self.fonts['body'],
                        bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor='w', pady=(5, 0))
                
                # Urgency and confidence
                stats_frame = tk.Frame(moment_content, bg=self.colors['bg_light'])
                stats_frame.pack(side=tk.RIGHT)
                
                tk.Label(stats_frame, text=f"⚡ Urgencia: {urgency}", font=self.fonts['body'],
                        bg=self.colors['bg_light'], fg=self.colors['accent_gold']).pack(anchor='e')
                tk.Label(stats_frame, text=f"📊 Confianza: {confidence}%", font=self.fonts['small'],
                        bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor='e', pady=(5, 0))
            
            # Update instructions
            if hasattr(self, 'instructions_text'):
                self.instructions_text.config(state='normal')
                self.instructions_text.delete('1.0', tk.END)
                
                instructions = [
                    "ESTRATEGIA WEEKEND LEAGUE (Lun-Mar: Comprar | Jue-Vie: Vender)",
                    "",
                    "1. 🔍 Revisa las cartas recomendadas abajo (rating 82-84)",
                    "2. 💰 Compara precios actuales vs históricos",
                    "3. 📈 Busca cartas con tendencia de subida",
                    "4. 🎯 Prioriza jugadores con demanda de SBCs activos",
                    "5. ⏰ IMPORTANTE: Compra Lun/Mar, Vende Jue/Vie",
                    "6. 🛒 Compra cuando veas -5% o más vs precio promedio",
                    "7. 💸 Vende cuando veas +10% o más de ganancia"
                ]
                
                for instruction in instructions:
                    self.instructions_text.insert(tk.END, instruction + '\n\n')
                
                self.instructions_text.config(state='disabled')
            
            # Get buy recommendations from database
            self._refresh_buy_recommendations()
            
        except Exception as e:
            logger.error(f"Error refreshing buy recommendations: {e}", exc_info=True)
            
    def _refresh_buy_recommendations(self):
        """Get buy recommendations from database with ML predictions"""
        try:
            if not self.db_manager:
                logger.warning("Database manager no disponible")
                return
            
            # Clear recommendations container
            if hasattr(self, 'rec_container'):
                for widget in self.rec_container.winfo_children():
                    widget.destroy()
            
            # Get players from database with price history
            from app.models.database import Player, PriceHistory
            session = self.db_manager.get_session()
            
            # Build query with filters
            query = session.query(Player).filter(
                Player.rating >= self.filters['rating_min'],
                Player.rating <= self.filters['rating_max'],
                Player.is_extinct == False
            )
            
            # Apply league filter in query
            if self.filters['league'] != 'Todas':
                # Map UI names to database values
                league_map = {
                    'Premier League': 'Premier League',
                    'La Liga': 'LaLiga',  # DB uses LaLiga (sin espacio)
                    'Serie A': 'Serie A',
                    'Bundesliga': 'Bundesliga',
                    'Ligue 1': 'Ligue 1'
                }
                db_league = league_map.get(self.filters['league'], self.filters['league'])
                query = query.filter(Player.league == db_league)
            
            # Apply position filter in query (DISABLED - positions are Unknown)
            # TODO: Fix scraper to capture positions correctly
            # if self.filters['position'] != 'Todas':
            #     if self.filters['position'] == 'DEF':
            #         query = query.filter(Player.position.in_(['CB', 'LB', 'RB', 'RWB', 'LWB']))
            #     elif self.filters['position'] == 'MID':
            #         query = query.filter(Player.position.in_(['CM', 'CDM', 'CAM', 'RM', 'LM']))
            #     elif self.filters['position'] == 'ATT':
            #         query = query.filter(Player.position.in_(['ST', 'CF', 'LW', 'RW']))
            #     elif self.filters['position'] == 'GK':
            #         query = query.filter(Player.position == 'GK')
            
            # Execute query
            players = query.limit(200).all()
            
            logger.info(f"🔍 Jugadores encontrados con filtros (rating={self.filters['rating_min']}-{self.filters['rating_max']}, liga={self.filters['league']}, pos={self.filters['position']}): {len(players)}")
            
            recommendations = []
            
            for player in players:
                # Get recent price history
                recent_prices = session.query(PriceHistory).filter(
                    PriceHistory.player_id == player.id
                ).order_by(PriceHistory.timestamp.desc()).limit(14).all()
                
                # Require at least 1 price entry (changed from 3)
                if len(recent_prices) < 1:
                    continue
                
                current_price = recent_prices[0].price
                
                # Calculate average (use current if only 1 entry)
                if len(recent_prices) >= 3:
                    avg_price = sum(p.price for p in recent_prices) / len(recent_prices)
                else:
                    avg_price = current_price  # No historical data yet
                
                # Calculate price change %
                price_change_pct = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
                
                recommendations.append({
                    'player_id': player.id,
                    'player_name': player.name,
                    'rating': player.rating,
                    'position': player.position or 'Unknown',
                    'league': player.league or 'Unknown',
                    'current_price': int(current_price),
                    'avg_price': int(avg_price),
                    'price_change_pct': price_change_pct,
                    'buy_score': -price_change_pct,  # Negative change = good buy
                    'has_enough_history': len(recent_prices) >= 3
                })
            
            session.close()
            
            # Sort by buy score (best deals first)
            recommendations.sort(key=lambda x: x['buy_score'], reverse=True)
            
            logger.info(f"📊 Recomendaciones con historial suficiente: {len(recommendations)}")
            
            # Display recommendations
            if not recommendations:
                tk.Label(self.rec_container, 
                        text="🔍 No hay cartas que cumplan los filtros actuales\n\nIntenta ajustar los filtros de rating, liga o posición",
                        font=self.fonts['body'],
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray'],
                        justify=tk.CENTER).pack(pady=50)
            else:
                for i, rec in enumerate(recommendations[:20]):  # Top 20
                    self._create_buy_card(self.rec_container, rec, i)
            
            # Force canvas update
            self.rec_container.update_idletasks()
            self.rec_canvas.configure(scrollregion=self.rec_canvas.bbox('all'))
            
            # Update peak hours indicator
            self._update_peak_hours_indicator()
            
            logger.info(f"✅ {len(recommendations)} recomendaciones de compra mostradas")
            
        except Exception as e:
            logger.error(f"Error loading buy recommendations: {e}", exc_info=True)
    
    def _create_buy_card(self, parent, rec: Dict[str, Any], index: int):
        """Create a buy recommendation card"""
        card = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, borderwidth=1)
        card.pack(fill=tk.X, padx=10, pady=6)
        
        content = tk.Frame(card, bg=self.colors['bg_light'])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Left: Rank with rating badge
        left_frame = tk.Frame(content, bg=self.colors['bg_light'])
        left_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(left_frame, text=f"#{index+1}", font=('Segoe UI', 24, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['accent_gold']).pack()
        
        # Rating badge
        rating_badge = tk.Label(left_frame, text=f"⭐ {rec['rating']}", 
                               font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['accent_gold'], fg='black',
                               padx=8, pady=2)
        rating_badge.pack(pady=(5, 0))
        
        # Center: Player details
        center_frame = tk.Frame(content, bg=self.colors['bg_light'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Player name
        tk.Label(center_frame, text=rec['player_name'], font=('Segoe UI', 16, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['text_white']).pack(anchor='w')
        
        # Position and league
        info_text = f"📍 {rec['position']}  •  🏆 {rec['league']}"
        tk.Label(center_frame, text=info_text, 
                font=('Segoe UI', 11),
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor='w', pady=(4, 0))
        
        # Price change indicator
        change_pct = rec['price_change_pct']
        if abs(change_pct) > 0.1:  # Only show if there's actual change
            color = self.colors['accent_green'] if change_pct < 0 else self.colors['accent_red']
            emoji = "📉 GANANCIA" if change_pct < 0 else "📈 CARO"
            status_bg = self.colors['accent_green'] if change_pct < -3 else self.colors['bg_medium']
            
            status_label = tk.Label(center_frame, 
                    text=f"{emoji} {abs(change_pct):.1f}% vs promedio",
                    font=('Segoe UI', 11, 'bold'),
                    bg=status_bg, fg='white' if change_pct < -3 else color,
                    padx=10, pady=4)
            status_label.pack(anchor='w', pady=(8, 0))
        elif not rec.get('has_enough_history', True):
            tk.Label(center_frame, text="ℹ️ Historial limitado - precio reciente",
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_light'], fg=self.colors['accent_cyan']).pack(anchor='w', pady=(8, 0))
        
        # Right: Price info
        right_frame = tk.Frame(content, bg=self.colors['bg_light'])
        right_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Current price - bigger and more visible
        price_container = tk.Frame(right_frame, bg=self.colors['bg_medium'], padx=15, pady=10)
        price_container.pack()
        
        tk.Label(price_container, text="💰 PRECIO", font=('Segoe UI', 9),
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).pack()
        tk.Label(price_container, text=f"{rec['current_price']:,}", font=('Segoe UI', 22, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['accent_cyan']).pack()
        
        # Average price
        if abs(change_pct) > 0.1:
            tk.Label(right_frame, text=f"Promedio: {rec['avg_price']:,}", 
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(pady=(5, 0))
        
        # Quantity selector and buy button
        action_frame = tk.Frame(right_frame, bg=self.colors['bg_light'])
        action_frame.pack(pady=(10, 0))
        
        # Quantity label and spinbox
        tk.Label(action_frame, text="Cantidad:", font=('Segoe UI', 9),
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack()
        
        quantity_var = tk.IntVar(value=1)
        quantity_spinbox = tk.Spinbox(action_frame, from_=1, to=100, width=5,
                                      textvariable=quantity_var,
                                      font=('Segoe UI', 11),
                                      bg=self.colors['bg_medium'],
                                      fg=self.colors['text_white'],
                                      buttonbackground=self.colors['accent_blue'],
                                      relief=tk.FLAT)
        quantity_spinbox.pack(pady=(2, 8))
        
        # Buy button with quantity
        buy_btn = tk.Button(action_frame, text="🛒 COMPRAR",
                           command=lambda: self._add_to_inventory(
                               player_id=rec['player_id'],
                               player_name=rec['player_name'],
                               price=rec['current_price'],
                               quantity=quantity_var.get()
                           ),
                           bg=self.colors['accent_blue'], fg='white',
                           font=('Segoe UI', 11, 'bold'),
                           relief=tk.FLAT, cursor='hand2',
                           padx=15, pady=8)
        buy_btn.pack(pady=(10, 0))
    
    def _record_purchase(self, rec: Dict[str, Any]):
        """Record a purchase transaction with budget validation"""
        try:
            from app.models.database import DatabaseManager
            from app.utils.config_loader import ConfigLoader
            
            db = DatabaseManager()
            config = ConfigLoader()
            
            # VALIDATE BUDGET FIRST
            budget_info = config.get_budget_info()
            current_budget = budget_info['current_budget']
            purchase_price = rec['current_price']
            
            if purchase_price > current_budget:
                messagebox.showerror(
                    "Presupuesto Insuficiente",
                    f"❌ No tienes suficientes coins\n\n"
                    f"Necesitas: {purchase_price:,} coins\n"
                    f"Tienes: {current_budget:,} coins\n"
                    f"Faltan: {(purchase_price - current_budget):,} coins"
                )
                self._log(f"❌ Compra cancelada: presupuesto insuficiente ({current_budget:,} < {purchase_price:,})")
                return
            
            session = db.SessionLocal()
            
            try:
                from app.models.database import Transaction, Player
                
                # Find or create player
                player = session.query(Player).filter(
                    Player.name == rec['player_name']
                ).first()
                
                if not player:
                    # Create new player entry
                    player = Player(
                        player_id=f"fodder_{rec['player_name'].lower().replace(' ', '_')}",
                        name=rec['player_name'],
                        rating=rec['rating'],
                        position=rec.get('position', 'Unknown'),
                        league=rec.get('league', 'Unknown'),
                        is_extinct=False
                    )
                    session.add(player)
                    session.flush()
                
                # Create transaction
                transaction = Transaction(
                    player_id=player.player_id,
                    transaction_type='buy',
                    price=rec['current_price'],
                    timestamp=datetime.now(),
                    status='completed'
                )
                session.add(transaction)
                
                # Update budget
                new_budget = current_budget - purchase_price
                config.update_budget(new_budget)
                
                session.commit()
                
                # Update UI
                self._load_budget()
                self._log(f"✅ Compra registrada: {rec['player_name']} por {rec['current_price']:,} coins")
                
                # Show confirmation
                messagebox.showinfo(
                    "Compra Registrada",
                    f"✅ {rec['player_name']}\n\n"
                    f"Precio: {rec['current_price']:,} coins\n"
                    f"Nuevo presupuesto: {new_budget:,} coins\n\n"
                    f"Ve al tab 'Vender' para ver tu inventario"
                )
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error recording purchase: {e}")
            messagebox.showerror("Error", f"Error al registrar compra: {str(e)}")
    
    def _get_demo_recommendations(self) -> List[Dict[str, Any]]:
        """Get demo recommendations when database is empty"""
        return [
            {
                'player_name': 'Erling Haaland',
                'rating': 91,
                'current_price': 15000,
                'strategy': 'Snipe Deal',
                'confidence': 0.85,
                'predicted_price': 18000,
                'profit_potential': 2850,
                'profit_percentage': 19.0
            },
            {
                'player_name': 'Vinicius Jr',
                'rating': 89,
                'current_price': 12500,
                'strategy': 'Mass Bidding',
                'confidence': 0.78,
                'predicted_price': 14500,
                'profit_potential': 1900,
                'profit_percentage': 15.2
            },
            {
                'player_name': 'Jude Bellingham',
                'rating': 87,
                'current_price': 8500,
                'strategy': 'SBC Trading',
                'confidence': 0.92,
                'predicted_price': 10200,
                'profit_potential': 1615,
                'profit_percentage': 19.0
            }
        ]
    
    def _refresh_sell_recommendations(self):
        """Refresh sell recommendations - show user's real inventory"""
        # Clear existing
        for widget in self.sell_container.winfo_children():
            widget.destroy()
        
        try:
            from app.models.database import DatabaseManager, Inventory, Player, PriceHistory
            from datetime import datetime
            
            if not self.db_manager:
                self._log("⚠️ Database no disponible")
                return
            
            session = self.db_manager.get_session()
            
            # Get inventory items that are still owned
            inventory_items = session.query(Inventory).filter(
                Inventory.status == 'owned'
            ).all()
            
            if not inventory_items:
                # Empty state
                empty_frame = tk.Frame(self.sell_container, bg=self.colors['bg_dark'])
                empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
                
                tk.Label(empty_frame, text="📦",
                        font=('Segoe UI Emoji', 48),
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=10)
                tk.Label(empty_frame, 
                        text="Tu inventario está vacío",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=5)
                tk.Label(empty_frame, 
                        text="Compra cartas en el tab 'Comprar' y aparecerán aquí",
                        font=('Segoe UI', 10),
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=5)
                
                session.close()
                return
            
            # Get current prices for each card
            sell_cards = []
            
            for item in inventory_items:
                # Get latest price
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.player_id == item.player_id
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                current_price = latest_price.price if latest_price else item.purchase_price
                
                # Calculate profit PER CARD
                tax_per_card = int(current_price * 0.05)
                profit_per_card = current_price - item.purchase_price - tax_per_card
                profit_percent = (profit_per_card / item.purchase_price) * 100 if item.purchase_price > 0 else 0
                
                # Total profit for all cards
                total_profit = profit_per_card * item.quantity
                
                days_held = (datetime.now() - item.purchase_date).days
                
                sell_cards.append({
                    'inventory_id': item.id,
                    'player_id': item.player_id,
                    'player_name': item.player_name,
                    'quantity': item.quantity,
                    'buy_price': item.purchase_price,
                    'current_price': current_price,
                    'profit_per_card': profit_per_card,
                    'total_profit': total_profit,
                    'profit_percent': profit_percent,
                    'days_held': days_held,
                    'buy_date': item.purchase_date,
                    'should_sell': profit_percent >= 10  # Sell if 10%+ profit
                })
            
            # Sort by profit percent (best opportunities first)
            sell_cards.sort(key=lambda x: x['profit_percent'], reverse=True)
            
            # Create cards
            for i, card in enumerate(sell_cards):
                self._create_sell_card(self.sell_container, card, i)
            
            # Force canvas update
            self.sell_container.update_idletasks()
            self.sell_canvas.configure(scrollregion=self.sell_canvas.bbox('all'))
            
            total_cards = sum(card['quantity'] for card in sell_cards)
            self._log(f"✓ {len(sell_cards)} tipos de cartas en inventario ({total_cards} cartas totales)")
            
            session.close()
            
            # Update portfolio stats (NEW)
            self._update_portfolio_stats()
                
        except Exception as e:
            logger.error(f"Error refreshing sell recommendations: {e}", exc_info=True)
            self._log(f"❌ Error: {e}")
    
    def _create_sell_card(self, parent, card: Dict[str, Any], index: int):
        """Create a sell recommendation card for inventory"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, borderwidth=1)
        card_frame.pack(fill=tk.X, padx=10, pady=6)
        
        content = tk.Frame(card_frame, bg=self.colors['bg_light'])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Left: Rank + Player info
        left_frame = tk.Frame(content, bg=self.colors['bg_light'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Player name with quantity
        name_text = f"{card['player_name']} (x{card['quantity']})" if card.get('quantity', 1) > 1 else card['player_name']
        tk.Label(left_frame, text=name_text, font=('Segoe UI', 16, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['text_white']).pack(anchor='w')
        
        tk.Label(left_frame, text=f"📅 Comprado hace {card['days_held']} días", 
                font=('Segoe UI', 11),
                bg=self.colors['bg_light'], fg=self.colors['text_gray']).pack(anchor='w', pady=(5, 0))
        
        # Profit indicator
        profit_pct = card.get('profit_percent', 0)
        if profit_pct >= 10:
            status_text = f"📈 +{profit_pct:.1f}% - ¡VENDE AHORA!"
            status_color = self.colors['accent_green']
        elif profit_pct >= 5:
            status_text = f"📊 +{profit_pct:.1f}% - Buen momento"
            status_color = self.colors['accent_gold']
        elif profit_pct >= 0:
            status_text = f"⏱️ +{profit_pct:.1f}% - Espera más"
            status_color = self.colors['accent_cyan']
        else:
            status_text = f"📉 {profit_pct:.1f}% - En pérdida"
            status_color = self.colors['accent_red']
        
        tk.Label(left_frame, text=status_text, 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg_light'], fg=status_color).pack(anchor='w', pady=(8, 0))
        
        # Sell button
        sell_btn = tk.Button(left_frame, text="💰 MARCAR COMO VENDIDO",
                            command=lambda: self._record_sale(card),
                            bg=self.colors['accent_green'], fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief=tk.FLAT, cursor='hand2',
                            padx=20, pady=8)
        sell_btn.pack(anchor='w', pady=(12, 0))
        
        # Right: Prices
        right_frame = tk.Frame(content, bg=self.colors['bg_light'])
        right_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Price table
        price_table = tk.Frame(right_frame, bg=self.colors['bg_medium'], padx=15, pady=10)
        price_table.pack()
        
        # Buy price
        tk.Label(price_table, text="💳 Compra (c/u)", font=('Segoe UI', 9),
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).grid(row=0, column=0, sticky='w', pady=2)
        tk.Label(price_table, text=f"{card['buy_price']:,}", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['text_white']).grid(row=0, column=1, sticky='e', padx=(10,0), pady=2)
        
        # Current price
        tk.Label(price_table, text="💰 Actual (c/u)", font=('Segoe UI', 9),
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).grid(row=1, column=0, sticky='w', pady=2)
        tk.Label(price_table, text=f"{card['current_price']:,}", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['accent_cyan']).grid(row=1, column=1, sticky='e', padx=(10,0), pady=2)
        
        # Profit per card
        profit_color = self.colors['accent_green'] if card.get('profit_per_card', 0) >= 0 else self.colors['accent_red']
        profit_symbol = "+" if card.get('profit_per_card', 0) >= 0 else ""
        tk.Label(price_table, text="📊 Ganancia (c/u)", font=('Segoe UI', 9),
                bg=self.colors['bg_medium'], fg=self.colors['text_gray']).grid(row=2, column=0, sticky='w', pady=2)
        tk.Label(price_table, text=f"{profit_symbol}{card.get('profit_per_card', 0):,}", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_medium'], fg=profit_color).grid(row=2, column=1, sticky='e', padx=(10,0), pady=2)
        
        # Total profit (if multiple cards)
        if card.get('quantity', 1) > 1:
            tk.Label(price_table, text=f"💎 Total ({card['quantity']}x)", font=('Segoe UI', 9, 'bold'),
                    bg=self.colors['bg_medium'], fg=self.colors['accent_gold']).grid(row=3, column=0, sticky='w', pady=(8,2))
            tk.Label(price_table, text=f"{profit_symbol}{card.get('total_profit', 0):,}", font=('Segoe UI', 13, 'bold'),
                    bg=self.colors['bg_medium'], fg=self.colors['accent_gold']).grid(row=3, column=1, sticky='e', padx=(10,0), pady=(8,2))
    
    def _record_sale(self, card: Dict[str, Any]):
        """Record a sale transaction - mark inventory as sold"""
        try:
            from app.models.database import Inventory
            from datetime import datetime
            from tkinter import messagebox
            
            if not self.db_manager:
                self._log("⚠️ Database no disponible")
                return
            
            session = self.db_manager.get_session()
            
            # Get inventory item
            inventory_item = session.query(Inventory).filter(
                Inventory.id == card['inventory_id']
            ).first()
            
            if not inventory_item:
                self._log("❌ Carta no encontrada en inventario")
                session.close()
                return
            
            # Update inventory item as sold
            inventory_item.status = 'sold'
            inventory_item.sell_price = card['current_price']
            inventory_item.sell_date = datetime.now()
            inventory_item.profit = card.get('total_profit', 0)
            
            session.commit()
            
            # Update UI
            self._refresh_sell_recommendations()
            
            total_sale = card['current_price'] * card.get('quantity', 1)
            total_profit = card.get('total_profit', 0)
            
            self._log(f"✅ VENTA REGISTRADA: {card.get('quantity', 1)}x {card['player_name']} @ {card['current_price']:,} = {total_sale:,} coins (+{total_profit:,} ganancia)")
            self._log(f"💡 Ve a EA FC 26 y vende {card.get('quantity', 1)} carta(s) de {card['player_name']}")
            
            # Show confirmation
            messagebox.showinfo(
                "Venta Registrada",
                f"💰 {card['player_name']} (x{card.get('quantity', 1)})\n\n"
                f"Precio venta (c/u): {card['current_price']:,} coins\n"
                f"Total: {total_sale:,} coins\n"
                f"Ganancia total: +{total_profit:,} coins\n\n"
                f"¡Buen trabajo! 🎉"
            )
            
            session.close()
                
        except Exception as e:
            logger.error(f"Error recording sale: {e}", exc_info=True)
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al registrar venta: {str(e)}")
    
    def _update_portfolio_stats(self):
        """Update portfolio statistics display from portfolio service"""
        try:
            if not hasattr(self, 'portfolio_service') or not self.portfolio_service:
                # Set default values if service not available
                self.portfolio_investment_label.config(text="0")
                self.portfolio_value_label.config(text="0")
                self.portfolio_profit_label.config(text="0")
                self.portfolio_roi_label.config(text="0.0%")
                return
            
            # Get portfolio summary
            summary = self.portfolio_service.get_portfolio_summary()
            
            # Update investment
            investment = summary.get('total_investment', 0)
            self.portfolio_investment_label.config(text=f"{investment:,}")
            
            # Update current value
            current_value = summary.get('total_value', 0)
            self.portfolio_value_label.config(text=f"{current_value:,}")
            
            # Update unrealized profit
            profit = summary.get('unrealized_profit', 0)
            profit_symbol = "+" if profit >= 0 else ""
            profit_color = self.colors['success'] if profit >= 0 else self.colors['danger']
            self.portfolio_profit_label.config(
                text=f"{profit_symbol}{profit:,}",
                foreground=profit_color
            )
            
            # Update ROI percentage
            roi = summary.get('roi_pct', 0.0)
            roi_color = self.colors['success'] if roi >= 0 else self.colors['danger']
            self.portfolio_roi_label.config(
                text=f"{roi:+.1f}%",
                foreground=roi_color
            )
            
            # Check for ROI milestones and notify
            if self.notifier and self.notifier.is_enabled():
                # Only notify on significant milestones
                if roi >= 10 and not hasattr(self, '_roi_10_notified'):
                    self.notifier.notify_roi_milestone(roi, profit)
                    self._roi_10_notified = True
                elif roi >= 5 and not hasattr(self, '_roi_5_notified'):
                    self.notifier.notify_roi_milestone(roi, profit)
                    self._roi_5_notified = True
            
            self._log(f"📊 Portfolio actualizado: {investment:,} → {current_value:,} ({roi:+.1f}%)")
            
        except Exception as e:
            logger.error(f"Error updating portfolio stats: {e}", exc_info=True)
            # Set error state
            self.portfolio_investment_label.config(text="Error")
            self.portfolio_value_label.config(text="Error")
            self.portfolio_profit_label.config(text="Error")
            self.portfolio_roi_label.config(text="Error")
    
    def _update_peak_hours_indicator(self):
        """Update peak hours indicator with optimal buy/sell windows"""
        try:
            if not hasattr(self, 'peak_hours_service') or not self.peak_hours_service:
                self.peak_hours_indicator.config(text="⏰ No disponible", fg=self.colors['text_muted'])
                self.best_buy_time_label.config(text="--:-- - --:--")
                self.best_sell_time_label.config(text="--:-- - --:--")
                self.current_action_label.config(text="Sin datos")
                return
            
            # Get hourly recommendations
            recommendations = self.peak_hours_service.get_hourly_recommendations()
            
            if not recommendations:
                self.peak_hours_indicator.config(text="⏰ Sin datos suficientes", fg=self.colors['text_muted'])
                return
            
            from datetime import datetime
            current_hour = datetime.now().hour
            
            # Extract best windows
            best_buy = recommendations.get('best_buy_window', {})
            best_sell = recommendations.get('best_sell_window', {})
            current = recommendations.get('current_hour_action', 'ESPERAR')
            
            # Update indicator in header
            if current == 'COMPRAR':
                indicator_text = f"⏰ 🛒 COMPRAR (Hora óptima: {current_hour}:00)"
                indicator_color = self.colors['info']
            elif current == 'VENDER':
                indicator_text = f"⏰ 💰 VENDER (Hora óptima: {current_hour}:00)"
                indicator_color = self.colors['success']
            else:
                indicator_text = f"⏰ ⏸️ ESPERAR (Hora actual: {current_hour}:00)"
                indicator_color = self.colors['warning']
            
            self.peak_hours_indicator.config(text=indicator_text, fg=indicator_color)
            
            # Update best buy window
            if best_buy:
                buy_start = best_buy.get('start_hour', 0)
                buy_end = best_buy.get('end_hour', 0)
                buy_savings = best_buy.get('avg_savings_pct', 0)
                self.best_buy_time_label.config(
                    text=f"{buy_start:02d}:00 - {buy_end:02d}:00 (-{buy_savings:.1f}%)"
                )
            
            # Update best sell window
            if best_sell:
                sell_start = best_sell.get('start_hour', 0)
                sell_end = best_sell.get('end_hour', 0)
                sell_profit = best_sell.get('avg_profit_pct', 0)
                self.best_sell_time_label.config(
                    text=f"{sell_start:02d}:00 - {sell_end:02d}:00 (+{sell_profit:.1f}%)"
                )
            
            # Update current action
            action_text = current
            if current == 'COMPRAR':
                action_color = self.colors['info']
            elif current == 'VENDER':
                action_color = self.colors['success']
            else:
                action_color = self.colors['text_muted']
            
            self.current_action_label.config(text=action_text, foreground=action_color)
            
            self._log(f"⏰ Hora óptima actualizada: {current} (Hora actual: {current_hour}:00)")
            
        except Exception as e:
            logger.error(f"Error updating peak hours indicator: {e}", exc_info=True)
            self.peak_hours_indicator.config(text="⏰ Error", fg=self.colors['danger'])
    
    def _refresh_bidding_recommendations(self):
        """Refresh mass bidding recommendations with optimal bid ranges"""
        # Clear existing
        for widget in self.bidding_container.winfo_children():
            widget.destroy()
        
        try:
            from app.models.database import DatabaseManager
            from app.models.database import Player, PriceHistory
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            db = DatabaseManager()
            session = db.SessionLocal()
            
            try:
                # Get ratings to analyze (82-85 Fodder range)
                ratings = [82, 83, 84, 85]
                
                bidding_data = []
                
                for rating in ratings:
                    # Count available cards in DB
                    card_count = session.query(func.count(Player.player_id)).filter(
                        Player.rating == rating
                    ).scalar()
                    
                    # Get average price from last 24 hours
                    yesterday = datetime.now() - timedelta(days=1)
                    
                    avg_price_result = session.query(
                        func.avg(PriceHistory.price)
                    ).join(
                        Player,
                        PriceHistory.player_id == Player.player_id
                    ).filter(
                        Player.rating == rating,
                        PriceHistory.timestamp >= yesterday
                    ).scalar()
                    
                    if avg_price_result and card_count > 0:
                        avg_price = int(avg_price_result)
                        
                        # Calculate bid range (85-90% of market price)
                        bid_min = int(avg_price * 0.85)
                        bid_max = int(avg_price * 0.90)
                        
                        # Calculate potential profit (sell at market price - 5% tax)
                        tax = int(avg_price * 0.05)
                        profit_min = avg_price - bid_max - tax
                        profit_max = avg_price - bid_min - tax
                        profit_percent_min = (profit_min / bid_max) * 100
                        profit_percent_max = (profit_max / bid_min) * 100
                        
                        bidding_data.append({
                            'rating': rating,
                            'avg_price': avg_price,
                            'bid_min': bid_min,
                            'bid_max': bid_max,
                            'profit_min': profit_min,
                            'profit_max': profit_max,
                            'profit_percent_min': profit_percent_min,
                            'profit_percent_max': profit_percent_max,
                            'card_count': card_count
                        })
                
                if not bidding_data:
                    # No data available
                    empty_frame = tk.Frame(self.bidding_container, bg=self.colors['bg_dark'])
                    empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
                    
                    tk.Label(empty_frame, text="📊",
                            font=('Segoe UI Emoji', 48),
                            bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=10)
                    tk.Label(empty_frame, 
                            text="No hay datos de mercado disponibles",
                            font=('Segoe UI', 14, 'bold'),
                            bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=5)
                    tk.Label(empty_frame, 
                            text="Actualiza precios en el tab 'Mercado' para ver recomendaciones de pujas",
                            font=('Segoe UI', 10),
                            bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=5)
                    return
                
                # Display bidding cards
                for data in bidding_data:
                    self._create_bidding_card(self.bidding_container, data)
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error refreshing bidding recommendations: {e}")
            tk.Label(self.bidding_container,
                    text=f"⚠️ Error al cargar recomendaciones: {str(e)}",
                    font=self.fonts['body'],
                    bg=self.colors['bg_dark'], fg=self.colors['accent_red']).pack(pady=50)
    
    def _create_bidding_card(self, parent, data):
        """Create bidding recommendation card for a rating"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'])
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Header with rating
        header = tk.Frame(card, bg=self.colors['bg_light'])
        header.pack(fill=tk.X)
        
        rating_badge = tk.Frame(header, bg=self.colors['accent_gold'])
        rating_badge.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(rating_badge, text=str(data['rating']),
                font=('Segoe UI', 24, 'bold'),
                bg=self.colors['accent_gold'], fg='white',
                padx=15, pady=5).pack()
        
        header_text = tk.Frame(header, bg=self.colors['bg_light'])
        header_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=15)
        
        tk.Label(header_text, text=f"Rating {data['rating']} - Fodder",
                font=self.fonts['subheader'],
                bg=self.colors['bg_light'], fg=self.colors['text_white'],
                anchor=tk.W).pack(anchor=tk.W)
        
        tk.Label(header_text, 
                text=f"{data['card_count']} cartas disponibles • Precio promedio: {data['avg_price']:,} coins",
                font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                anchor=tk.W).pack(anchor=tk.W, pady=(3, 0))
        
        # Body with bid ranges
        body = tk.Frame(card, bg=self.colors['bg_medium'])
        body.pack(fill=tk.X, padx=20, pady=15)
        
        # Grid layout
        grid = tk.Frame(body, bg=self.colors['bg_medium'])
        grid.pack(fill=tk.X)
        
        # Bid range
        bid_frame = tk.Frame(grid, bg=self.colors['bg_input'], relief=tk.FLAT)
        bid_frame.grid(row=0, column=0, padx=(0, 10), sticky='ew', pady=(0, 10))
        
        tk.Label(bid_frame, text="🎯 Rango de Puja",
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(10, 3))
        
        tk.Label(bid_frame, text=f"{data['bid_min']:,} - {data['bid_max']:,} coins",
                font=('Segoe UI', 16, 'bold'),
                bg=self.colors['bg_input'], fg=self.colors['accent_blue']).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Profit range
        profit_frame = tk.Frame(grid, bg=self.colors['bg_input'], relief=tk.FLAT)
        profit_frame.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        tk.Label(profit_frame, text="💰 Ganancia Potencial",
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(10, 3))
        
        profit_color = self.colors['accent_green'] if data['profit_min'] > 0 else self.colors['accent_red']
        
        tk.Label(profit_frame, text=f"{data['profit_min']:,} - {data['profit_max']:,} coins",
                font=('Segoe UI', 16, 'bold'),
                bg=self.colors['bg_input'], fg=profit_color).pack(anchor=tk.W, padx=15)
        
        tk.Label(profit_frame, text=f"({data['profit_percent_min']:.1f}% - {data['profit_percent_max']:.1f}%)",
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=profit_color).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        
        # Recommendation
        rec_text = "✅ EXCELENTE" if data['profit_percent_min'] > 10 else "⚠️ MODERADO" if data['profit_percent_min'] > 5 else "❌ BAJO MARGEN"
        rec_color = self.colors['accent_green'] if data['profit_percent_min'] > 10 else self.colors['accent_gold'] if data['profit_percent_min'] > 5 else self.colors['accent_red']
        
        rec_frame = tk.Frame(body, bg=rec_color)
        rec_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(rec_frame, text=rec_text,
                font=self.fonts['body'],
                bg=rec_color, fg='white',
                padx=15, pady=8).pack(anchor=tk.W)
    
    def _refresh_sbcs(self):
        """Refresh SBCs tab with active SBCs and impact analysis"""
        # Clear existing
        for widget in self.sbcs_container.winfo_children():
            widget.destroy()
        
        for widget in self.sbc_impact_frame.winfo_children():
            widget.destroy()
        
        try:
            if not self.sbc_tracker:
                # SBC Tracker not initialized
                empty_frame = tk.Frame(self.sbcs_container, bg=self.colors['bg_dark'])
                empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
                
                tk.Label(empty_frame, text="⚠️",
                        font=('Segoe UI Emoji', 48),
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=10)
                tk.Label(empty_frame, 
                        text="SBC Tracker no disponible",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=5)
                return
            
            # Get active SBCs from tracker
            active_sbcs = self.sbc_tracker.get_active_sbcs()
            
            if not active_sbcs:
                # No active SBCs
                empty_frame = tk.Frame(self.sbcs_container, bg=self.colors['bg_dark'])
                empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
                
                tk.Label(empty_frame, text="⚽",
                        font=('Segoe UI Emoji', 48),
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=10)
                tk.Label(empty_frame, 
                        text="No hay SBCs activos",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['text_white']).pack(pady=5)
                tk.Label(empty_frame, 
                        text="Los SBCs activos aparecerán aquí cuando estén disponibles",
                        font=('Segoe UI', 10),
                        bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(pady=5)
                
                # Show impact analysis anyway
                impact_data = self.sbc_tracker.get_fodder_impact_analysis()
                if impact_data:
                    self._show_impact_summary(impact_data)
                
                return
            
            # Show impact analysis only if there's real data
            impact_data = self.sbc_tracker.get_fodder_impact_analysis()
            if impact_data and isinstance(impact_data, dict) and len(impact_data) > 0:
                self._show_impact_summary(impact_data)
            
            # Display SBC cards
            for sbc in active_sbcs:
                if isinstance(sbc, dict):  # Only show valid SBCs
                    self._create_sbc_card(self.sbcs_container, sbc)
                
        except Exception as e:
            logger.error(f"Error refreshing SBCs: {e}")
            tk.Label(self.sbcs_container,
                    text=f"⚠️ Error al cargar SBCs: {str(e)}",
                    font=self.fonts['body'],
                    bg=self.colors['bg_dark'], fg=self.colors['accent_red']).pack(pady=50)
    
    def _show_impact_summary(self, impact_data):
        """Show fodder impact analysis summary"""
        # Validar que impact_data sea un dict
        if not isinstance(impact_data, dict):
            logger.warning(f"Impact data no es dict: {type(impact_data)}")
            tk.Label(self.sbc_impact_frame, 
                    text="⚠️ Formato de datos incorrecto",
                    font=self.fonts['small'],
                    bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(padx=15, pady=10)
            return
        
        # Sort by demand score
        sorted_ratings = sorted(impact_data.items(), 
                               key=lambda x: x[1].get('demand_score', 0) if isinstance(x[1], dict) else 0, 
                               reverse=True)
        
        if not sorted_ratings:
            tk.Label(self.sbc_impact_frame, 
                    text="No hay datos de impacto disponibles",
                    font=self.fonts['small'],
                    bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(padx=15, pady=10)
            return
        
        # Create grid of impact cards
        grid = tk.Frame(self.sbc_impact_frame, bg=self.colors['bg_input'])
        grid.pack(fill=tk.X, padx=15, pady=10)
        
        for idx, (rating, data) in enumerate(sorted_ratings[:4]):  # Top 4 ratings
            # Validar que data sea dict
            if not isinstance(data, dict):
                continue
            
            impact_level = data.get('impact_level', 'BAJO')
            demand_score = data.get('demand_score', 0)
            sbc_count = data.get('sbc_count', 0)
            
            # Determine color based on impact
            if impact_level == 'ALTO':
                bg_color = self.colors['accent_green']
            elif impact_level == 'MEDIO':
                bg_color = self.colors['accent_gold']
            else:
                bg_color = self.colors['accent_blue']
            
            card = tk.Frame(grid, bg=bg_color)
            card.grid(row=0, column=idx, padx=5, sticky='ew')
            
            tk.Label(card, text=f"Rating {rating}",
                    font=self.fonts['small'],
                    bg=bg_color, fg='white').pack(padx=10, pady=(8, 2))
            
            tk.Label(card, text=impact_level,
                    font=('Segoe UI', 14, 'bold'),
                    bg=bg_color, fg='white').pack(padx=10, pady=(0, 2))
            
            tk.Label(card, text=f"{sbc_count} SBCs",
                    font=self.fonts['small'],
                    bg=bg_color, fg='white').pack(padx=10, pady=(0, 8))
            
            grid.columnconfigure(idx, weight=1)
    
    def _create_sbc_card(self, parent, sbc):
        """Create SBC card"""
        # Validar que sbc sea dict
        if not isinstance(sbc, dict):
            logger.warning(f"SBC no es dict: {type(sbc)} - {sbc}")
            return
        
        card = tk.Frame(parent, bg=self.colors['bg_medium'])
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Header
        header = tk.Frame(card, bg=self.colors['bg_light'])
        header.pack(fill=tk.X)
        
        header_left = tk.Frame(header, bg=self.colors['bg_light'])
        header_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(header_left, text=sbc.get('name', 'SBC Desconocido'),
                font=self.fonts['subheader'],
                bg=self.colors['bg_light'], fg=self.colors['text_white'],
                anchor=tk.W).pack(anchor=tk.W)
        
        # Expiry info
        expiry = sbc.get('expiry', 'Sin fecha')
        tk.Label(header_left, 
                text=f"⏰ Expira: {expiry}",
                font=self.fonts['small'],
                bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                anchor=tk.W).pack(anchor=tk.W, pady=(3, 0))
        
        # Body with requirements and reward
        body = tk.Frame(card, bg=self.colors['bg_medium'])
        body.pack(fill=tk.X, padx=20, pady=15)
        
        # Requirements
        req_frame = tk.Frame(body, bg=self.colors['bg_input'])
        req_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(req_frame, text="📋 Requisitos",
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        requirements = sbc.get('requirements', {})
        if not isinstance(requirements, dict):
            requirements = {}
        
        req_text = f"• Min Rating: {requirements.get('min_rating', 'N/A')}\n"
        req_text += f"• Química: {requirements.get('chemistry', 'N/A')}\n"
        req_text += f"• Jugadores: {requirements.get('num_players', 'N/A')}"
        
        tk.Label(req_frame, text=req_text,
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_white'],
                justify=tk.LEFT).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Reward
        reward_frame = tk.Frame(body, bg=self.colors['bg_input'])
        reward_frame.pack(fill=tk.X)
        
        tk.Label(reward_frame, text="🎁 Recompensa",
                font=self.fonts['small'],
                bg=self.colors['bg_input'], fg=self.colors['text_gray']).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        reward = sbc.get('reward', 'Recompensa desconocida')
        tk.Label(reward_frame, text=reward,
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg_input'], fg=self.colors['accent_green']).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def _refresh_history(self):
        """Refresh transaction history with statistics"""
        # Clear existing
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            from app.models.database import DatabaseManager
            db = DatabaseManager()
            session = db.SessionLocal()
            
            try:
                from app.models.database import Transaction, Player
                
                # Get all transactions with player info
                transactions = session.query(
                    Transaction,
                    Player
                ).join(
                    Player,
                    Transaction.player_id == Player.player_id
                ).order_by(Transaction.timestamp.desc()).all()
                
                if not transactions:
                    self._log("No hay transacciones aún")
                    self.total_profit_label.config(text="0 coins")
                    self.total_trans_label.config(text="0")
                    self.avg_profit_label.config(text="0 coins")
                    self.winrate_label.config(text="0%")
                    return
                
                # Calculate statistics
                total_profit = 0
                profitable_trades = 0
                total_sells = 0
                buy_prices = {}  # player_id -> buy_price
                
                for transaction, player in transactions:
                    if transaction.transaction_type == 'buy':
                        buy_prices[player.player_id] = transaction.price
                    elif transaction.transaction_type == 'sell':
                        total_sells += 1
                        if transaction.profit and transaction.profit > 0:
                            profitable_trades += 1
                            total_profit += transaction.profit
                        elif transaction.profit:
                            total_profit += transaction.profit
                
                # Update statistics labels
                self.total_profit_label.config(
                    text=f"{total_profit:,} coins" if total_profit >= 0 else f"{total_profit:,} coins",
                    fg=self.colors['accent_green'] if total_profit >= 0 else self.colors['accent_red']
                )
                
                self.total_trans_label.config(text=str(len(transactions)))
                
                avg_profit = total_profit / total_sells if total_sells > 0 else 0
                self.avg_profit_label.config(
                    text=f"{int(avg_profit):,} coins",
                    fg=self.colors['accent_green'] if avg_profit >= 0 else self.colors['accent_red']
                )
                
                win_rate = (profitable_trades / total_sells * 100) if total_sells > 0 else 0
                self.winrate_label.config(
                    text=f"{win_rate:.1f}%",
                    fg=self.colors['accent_green'] if win_rate >= 50 else self.colors['accent_red']
                )
                
                # Populate table
                for transaction, player in transactions:
                    date_str = transaction.timestamp.strftime('%d/%m/%Y %H:%M')
                    tipo = "🔴 COMPRA" if transaction.transaction_type == 'buy' else "🟢 VENTA"
                    precio = f"{transaction.price:,} coins"
                    
                    # Calculate profit and ROI for sells
                    if transaction.transaction_type == 'sell':
                        ganancia = f"{transaction.profit:,}" if transaction.profit else "0"
                        buy_price = buy_prices.get(player.player_id, transaction.price)
                        roi = (transaction.profit / buy_price * 100) if buy_price > 0 and transaction.profit else 0
                        roi_str = f"{roi:+.1f}%"
                    else:
                        ganancia = "-"
                        roi_str = "-"
                    
                    # Insert with color tags
                    tags = ()
                    if transaction.transaction_type == 'sell':
                        if transaction.profit and transaction.profit > 0:
                            tags = ('profit',)
                        elif transaction.profit and transaction.profit < 0:
                            tags = ('loss',)
                    
                    self.history_tree.insert('', 'end',
                                            values=(date_str, player.name, tipo, precio, ganancia, roi_str),
                                            tags=tags)
                
                # Configure tags for colored rows
                self.history_tree.tag_configure('profit', foreground=self.colors['accent_green'])
                self.history_tree.tag_configure('loss', foreground=self.colors['accent_red'])
                
                # Update profit chart
                self._update_profit_chart(self.profit_chart_range)
                
                self._log(f"✓ Historial cargado: {len(transactions)} transacciones, ganancia total: {total_profit:,} coins")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error refreshing history: {e}")
            self._log(f"Error: {e}")
    
    def _save_discord_config(self):
        """Save Discord configuration"""
        token = self.discord_token_entry.get().strip()
        channel_id = self.discord_channel_entry.get().strip()
        
        if not token or not channel_id:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        
        try:
            # Save to .env
            env_path = Path('.env')
            config_lines = []
            
            if env_path.exists():
                with open(env_path, 'r') as f:
                    config_lines = f.readlines()
            
            # Update or add Discord config
            token_found = False
            channel_found = False
            
            for i, line in enumerate(config_lines):
                if line.startswith('DISCORD_BOT_TOKEN='):
                    config_lines[i] = f'DISCORD_BOT_TOKEN={token}\n'
                    token_found = True
                elif line.startswith('DISCORD_CHANNEL_ID='):
                    config_lines[i] = f'DISCORD_CHANNEL_ID={channel_id}\n'
                    channel_found = True
            
            if not token_found:
                config_lines.append(f'\n# Discord Bot Configuration\nDISCORD_BOT_TOKEN={token}\n')
            if not channel_found:
                config_lines.append(f'DISCORD_CHANNEL_ID={channel_id}\n')
            
            with open(env_path, 'w') as f:
                f.writelines(config_lines)
            
            self._log("Configuración de Discord guardada")
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            
        except Exception as e:
            logger.error(f"Error saving Discord config: {e}")
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def _load_discord_config(self):
        """Load saved Discord configuration"""
        try:
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            token = os.getenv('DISCORD_BOT_TOKEN', '')
            channel_id = os.getenv('DISCORD_CHANNEL_ID', '')
            
            if token:
                self.discord_token_entry.insert(0, token)
            if channel_id:
                self.discord_channel_entry.insert(0, channel_id)
            
        except Exception as e:
            logger.error(f"Error loading Discord config: {e}")
    
    def _connect_discord(self):
        """Connect Discord bot"""
        token = self.discord_token_entry.get().strip()
        channel_id = self.discord_channel_entry.get().strip()
        
        if not token or not channel_id:
            messagebox.showerror("Error", "Por favor configura el token y canal primero")
            return
        
        try:
            from app.services.discord_service import DiscordNotifier
            
            self.discord_bot = DiscordNotifier(token, int(channel_id))
            
            # Run in separate thread
            discord_thread = threading.Thread(target=self.discord_bot.run, daemon=True)
            discord_thread.start()
            
            self.discord_status_label.config(text="✅ Conectado", fg='#00ff88')
            self._log("Bot de Discord conectado")
            messagebox.showinfo("Éxito", "Bot de Discord conectado correctamente")
            
        except Exception as e:
            logger.error(f"Error connecting Discord: {e}")
            self._log(f"Error conectando Discord: {e}")
            messagebox.showerror("Error", f"No se pudo conectar: {e}")
    
    def _test_discord(self):
        """Send test message to Discord"""
        if not self.discord_bot:
            messagebox.showerror("Error", "Primero conecta el bot de Discord")
            return
        
        try:
            import asyncio
            
            async def send_test():
                await self.discord_bot.send_alert(
                    'info',
                    'Mensaje de prueba desde EA FC 26 Trading Bot',
                    {'Status': 'Conectado correctamente', 'Hora': datetime.now().strftime('%H:%M:%S')}
                )
            
            asyncio.run(send_test())
            self._log("Mensaje de prueba enviado a Discord")
            messagebox.showinfo("Éxito", "Mensaje de prueba enviado")
            
        except Exception as e:
            logger.error(f"Error sending test: {e}")
            messagebox.showerror("Error", f"No se pudo enviar: {e}")
    
    def _show_help(self):
        """Show help dialog"""
        import webbrowser
        webbrowser.open('GUIA_USO.md')
    
    def _show_strategies(self):
        """Show strategies guide"""
        import webbrowser
        webbrowser.open('ESTRATEGIAS_11K.md')
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("Acerca de", 
                          "EA FC 26 Trading Bot\n\n"
                          "Versión 1.0\n\n"
                          "Bot de trading inteligente para EA FC 26\n"
                          "con análisis de mercado, predicciones y\n"
                          "recomendaciones personalizadas.\n\n"
                          "© 2025")
    
    def _schedule_refresh(self):
        """Schedule automatic refresh"""
        self._load_budget()
        # Refresh every 5 minutes
        self.root.after(300000, self._schedule_refresh)
    
    def _refresh_market_graph(self):
        """Refresh market graph with updated data"""
        try:
            if not hasattr(self, 'market_graph_canvas'):
                return
            
            # Get fresh data from database
            real_dates, real_prices = self._get_market_data_from_db()
            
            if real_dates and real_prices and len(real_prices) > 1:
                dates = real_dates
                prices = real_prices
            else:
                # Keep existing data if no new data
                if hasattr(self, 'market_graph_data'):
                    return
                dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
                prices = [50000] * 7
            
            # Calculate trend and prediction
            if len(prices) >= 2:
                trend = prices[-1] - prices[-2]
            else:
                trend = 0
            
            tomorrow = dates[-1] + timedelta(days=1)
            tomorrow_price = prices[-1] + trend
            
            # Clear and redraw
            self.market_graph_ax.clear()
            
            # Plot updated data
            self.market_graph_ax.plot(dates, prices, color=self.colors['accent_blue'], 
                                     linewidth=2.5, marker='o', markersize=6, 
                                     label='Precio Promedio Real')
            
            self.market_graph_ax.plot([dates[-1], tomorrow], [prices[-1], tomorrow_price], 
                                     color=self.colors['accent_green'] if trend > 0 else self.colors['accent_red'], 
                                     linewidth=2.5, linestyle='--', marker='o', markersize=6, 
                                     label='Predicción para Mañana')
            
            # Reapply styling
            self.market_graph_ax.set_facecolor(self.colors['bg_light'])
            self.market_graph_ax.set_xlabel('Fecha', color=self.colors['text_gray'], fontsize=10)
            self.market_graph_ax.set_ylabel('Precio Promedio (Coins)', color=self.colors['text_gray'], fontsize=10)
            self.market_graph_ax.tick_params(colors=self.colors['text_gray'], labelsize=9)
            self.market_graph_ax.grid(True, alpha=0.1, color=self.colors['text_gray'])
            self.market_graph_ax.legend(facecolor=self.colors['bg_light'], 
                                       edgecolor=self.colors['text_gray'], 
                                       labelcolor=self.colors['text_white'], fontsize=9)
            
            self.market_graph_ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            self.market_graph_fig.autofmt_xdate(rotation=0, ha='center')
            
            for spine in self.market_graph_ax.spines.values():
                spine.set_edgecolor(self.colors['bg_light'])
            
            self.market_graph_canvas.draw()
            
            # Update stored data
            self.market_graph_data = {
                'dates': dates,
                'prices': prices,
                'tomorrow': tomorrow,
                'tomorrow_price': tomorrow_price,
                'trend': trend
            }
            
            logger.info("Market graph refreshed with latest data")
            
        except Exception as e:
            logger.error(f"Error refreshing market graph: {e}")
        
        # Schedule next refresh in 5 minutes
        self.root.after(300000, self._refresh_market_graph)
    
    
    def _update_realtime_clock(self):
        """Update clock and date in real-time"""
        try:
            if hasattr(self, 'current_time_label'):
                now = datetime.now()
                time_str = now.strftime('%H:%M:%S')
                date_str = now.strftime('%A, %d de %B %Y')
                
                # Translate to Spanish
                days_es = {
                    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                }
                months_es = {
                    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
                }
                
                for eng, esp in days_es.items():
                    date_str = date_str.replace(eng, esp)
                for eng, esp in months_es.items():
                    date_str = date_str.replace(eng, esp)
                
                self.current_time_label.config(text=time_str)
                self.current_date_label.config(text=date_str)
            
            # Update market status if visible
            if hasattr(self, 'market_status_time_label'):
                now = datetime.now()
                self.market_status_time_label.config(text=now.strftime('%H:%M'))
                
                # Update market status
                hour = now.hour
                day_of_week = now.strftime('%A')
                status_text, status_color, activity_level, recommendation = self._get_market_status(hour, day_of_week)
                
                if hasattr(self, 'market_status_label'):
                    self.market_status_label.config(text=status_text, fg=status_color)
                if hasattr(self, 'market_activity_label'):
                    self.market_activity_label.config(text=activity_level)
                if hasattr(self, 'market_recommendation_label'):
                    self.market_recommendation_label.config(text=recommendation)
        except Exception as e:
            logger.error(f"Error updating real-time clock: {e}")
        
        # Update every second
        self.root.after(1000, self._update_realtime_clock)
    
    def _get_historical_trends_data(self, days=7):
        """Get historical trends data from trends service"""
        try:
            if not hasattr(self, 'trends_service') or not self.trends_service:
                return None, None, None
            
            # Get a top-rated player to analyze
            session = self.db_manager.get_session()
            
            player = session.query(self.db_manager.Player).filter(
                self.db_manager.Player.rating >= 85
            ).first()
            
            if not player:
                session.close()
                return None, None, None
            
            player_id = player.player_id
            session.close()
            
            # Get price graph data
            graph_data = self.trends_service.get_price_graph_data(player_id, days=days)
            
            if not graph_data or 'data' not in graph_data or not graph_data['data']:
                return None, None, None
            
            # Extract dates and prices
            dates = []
            prices = []
            
            for point in graph_data['data']:
                timestamp_ms = point['timestamp']
                price = point['price']
                
                # Convert timestamp from milliseconds to datetime
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                dates.append(dt)
                prices.append(price)
            
            # Get trend info
            trend_data = self.trends_service.detect_price_trends(player_id, days=days)
            
            logger.info(f"Historical trends loaded: {len(dates)} days for {player.name}")
            
            return dates, prices, trend_data
            
        except Exception as e:
            logger.error(f"Error getting historical trends data: {e}")
            return None, None, None
    
    def _get_market_data_from_db(self):
        """Get real market data from database (last 7 days)"""
        try:
            from app.utils.config_loader import ConfigLoader
            from app.models.database import DatabaseManager
            from sqlalchemy import func
            
            config = ConfigLoader()
            db = DatabaseManager()
            
            # Create session
            session = db.SessionLocal()
            
            try:
                # Get top 100 most traded players
                from app.models.database import Player, PriceHistory
                
                # Query for last 7 days of price data
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                # Get average price per day for top players
                daily_averages = session.query(
                    func.date(PriceHistory.timestamp).label('date'),
                    func.avg(PriceHistory.price).label('avg_price')
                ).filter(
                    PriceHistory.timestamp >= seven_days_ago,
                    PriceHistory.price > 0
                ).group_by(
                    func.date(PriceHistory.timestamp)
                ).order_by('date').all()
                
                if daily_averages and len(daily_averages) > 0:
                    dates = []
                    prices = []
                    
                    for row in daily_averages:
                        # Convert date string to datetime
                        date_obj = datetime.strptime(str(row.date), '%Y-%m-%d')
                        dates.append(date_obj)
                        prices.append(float(row.avg_price))
                    
                    # Fill missing days with interpolation
                    all_dates = []
                    all_prices = []
                    
                    for i in range(7):
                        target_date = datetime.now() - timedelta(days=6-i)
                        target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                        all_dates.append(target_date)
                        
                        # Find matching price or interpolate
                        found = False
                        for j, date in enumerate(dates):
                            if date.date() == target_date.date():
                                all_prices.append(prices[j])
                                found = True
                                break
                        
                        if not found:
                            # Use last known price or base price
                            if len(all_prices) > 0:
                                all_prices.append(all_prices[-1])
                            else:
                                all_prices.append(50000)  # Default base price
                    
                    return all_dates, all_prices
                else:
                    # No data in DB, return None
                    return None, None
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error getting market data from DB: {e}")
            return None, None
    
    def _get_price_comparison(self, player_id: str, current_price: int) -> Optional[Dict]:
        """Get price comparison vs yesterday and last week"""
        if not player_id or not self.db_manager:
            return None
        
        try:
            from app.models.database import PriceHistory
            from datetime import datetime, timedelta
            
            session = self.db_manager.SessionLocal()
            
            try:
                now = datetime.now()
                
                # Price from 1 day ago
                yesterday = now - timedelta(days=1)
                price_1d = session.query(PriceHistory).filter(
                    PriceHistory.player_id == player_id,
                    PriceHistory.timestamp >= yesterday - timedelta(hours=12),
                    PriceHistory.timestamp <= yesterday + timedelta(hours=12)
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                # Price from 7 days ago
                last_week = now - timedelta(days=7)
                price_7d = session.query(PriceHistory).filter(
                    PriceHistory.player_id == player_id,
                    PriceHistory.timestamp >= last_week - timedelta(hours=12),
                    PriceHistory.timestamp <= last_week + timedelta(hours=12)
                ).order_by(PriceHistory.timestamp.desc()).first()
                
                result = {
                    'yesterday': None,
                    'last_week': None
                }
                
                if price_1d:
                    change_1d = current_price - price_1d.price
                    pct_1d = (change_1d / price_1d.price * 100) if price_1d.price > 0 else 0
                    result['yesterday'] = {
                        'old_price': price_1d.price,
                        'change': change_1d,
                        'change_percent': pct_1d
                    }
                
                if price_7d:
                    change_7d = current_price - price_7d.price
                    pct_7d = (change_7d / price_7d.price * 100) if price_7d.price > 0 else 0
                    result['last_week'] = {
                        'old_price': price_7d.price,
                        'change': change_7d,
                        'change_percent': pct_7d
                    }
                
                return result
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error getting price comparison: {e}")
            return None
    
    def _apply_filters(self):
        """Apply filters to recommendations"""
        # Update filters dict
        self.filters['league'] = self.league_filter.get()
        self.filters['position'] = self.position_filter.get()
        self.filters['rating_min'] = int(self.rating_min_filter.get())
        self.filters['rating_max'] = int(self.rating_max_filter.get())
        
        # Refresh with filters
        self._refresh_fodder_plan()
        self._log(f"🔍 Filtros aplicados: Liga={self.filters['league']}, Pos={self.filters['position']}, Rating={self.filters['rating_min']}-{self.filters['rating_max']}")
    
    def _clear_filters(self):
        """Clear all filters"""
        self.league_filter.set("Todas")
        # Position filter disabled
        self.rating_min_filter.set("82")
        self.rating_max_filter.set("84")
        
        self.filters = {
            'league': 'Todas',
            'position': 'Todas',
            'rating_min': 82,
            'rating_max': 84
        }
        
        self._refresh_fodder_plan()
        self._log("✖ Filtros limpiados")
    
    def _update_profit_chart(self, range_type: str = 'daily'):
        """Update profit/loss historical chart"""
        self.profit_chart_range = range_type
        
        try:
            from app.models.database import DatabaseManager, Transaction
            from datetime import datetime, timedelta
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.dates as mdates
            
            db = DatabaseManager()
            session = db.SessionLocal()
            
            try:
                # Query sell transactions with profit
                transactions = session.query(Transaction).filter(
                    Transaction.transaction_type == 'sell',
                    Transaction.profit.isnot(None)
                ).order_by(Transaction.timestamp).all()
                
                if not transactions:
                    # Show empty chart message
                    for widget in self.profit_chart_canvas_frame.winfo_children():
                        widget.destroy()
                    
                    tk.Label(self.profit_chart_canvas_frame,
                            text="📊 No hay datos de ventas aún\n\nRealiza algunas ventas para ver la evolución",
                            font=self.fonts['body'],
                            bg=self.colors['bg_medium'], fg=self.colors['text_gray'],
                            justify=tk.CENTER).pack(pady=40)
                    return
                
                # Group by date range
                profit_by_date = {}
                
                for trans in transactions:
                    if range_type == 'daily':
                        date_key = trans.timestamp.date()
                    elif range_type == 'weekly':
                        date_key = trans.timestamp.date() - timedelta(days=trans.timestamp.weekday())
                    else:  # monthly
                        date_key = trans.timestamp.replace(day=1).date()
                    
                    if date_key not in profit_by_date:
                        profit_by_date[date_key] = 0
                    profit_by_date[date_key] += trans.profit if trans.profit else 0
                
                # Sort by date
                dates = sorted(profit_by_date.keys())
                profits = [profit_by_date[d] for d in dates]
                
                # Calculate cumulative profit
                cumulative_profit = []
                total = 0
                for p in profits:
                    total += p
                    cumulative_profit.append(total)
                
                # Clear previous chart
                for widget in self.profit_chart_canvas_frame.winfo_children():
                    widget.destroy()
                
                # Create matplotlib figure
                fig = Figure(figsize=(12, 4), facecolor=self.colors['bg_medium'])
                ax = fig.add_subplot(111, facecolor=self.colors['bg_light'])
                
                # Plot cumulative profit
                ax.plot(dates, cumulative_profit, color=self.colors['accent_green'],
                       linewidth=2, marker='o', markersize=4)
                
                # Fill area under curve
                ax.fill_between(dates, cumulative_profit, 0,
                               alpha=0.2, color=self.colors['accent_green'])
                
                # Add zero line
                ax.axhline(y=0, color=self.colors['text_gray'], linestyle='--', linewidth=1, alpha=0.5)
                
                # Styling
                ax.set_title(f'Ganancia Acumulada ({range_type.capitalize()})',
                           color=self.colors['text_white'], fontsize=12, pad=15)
                ax.set_xlabel('Fecha', color=self.colors['text_gray'], fontsize=10)
                ax.set_ylabel('Coins', color=self.colors['text_gray'], fontsize=10)
                
                # Format axes
                ax.tick_params(colors=self.colors['text_gray'], labelsize=9)
                ax.spines['bottom'].set_color(self.colors['border'])
                ax.spines['left'].set_color(self.colors['border'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Format dates
                if range_type == 'daily':
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                elif range_type == 'weekly':
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                else:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                
                fig.autofmt_xdate()
                fig.tight_layout()
                
                # Embed in Tkinter
                canvas = FigureCanvasTkAgg(fig, master=self.profit_chart_canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                logger.info(f"✓ Gráfica de profit actualizada ({range_type})")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error updating profit chart: {e}")
    
    def _auto_save_callback(self):
        """Callback ejecutado cada 5 minutos por AutoSaveManager"""
        try:
            # Save any pending data
            logger.info("💾 Auto-guardado ejecutándose...")
            
            # Force save budget if modified
            # (budget ya se guarda automáticamente en cada transacción)
            
            # Could add more save operations here
            # Example: self._save_filters(), self._save_ui_state(), etc.
            
        except Exception as e:
            logger.error(f"Error en auto-save callback: {e}")
    
    def _check_price_alerts(self):
        """Check price alerts periodically (every 5 minutes)"""
        if self.alert_manager and self.db_manager:
            try:
                alerts = self.alert_manager.check_price_changes()
                
                if alerts:
                    for alert in alerts:
                        self._log(f"🚨 ALERTA: {alert['player_name']} {alert['change_percent']:+.1f}%")
                
            except Exception as e:
                logger.error(f"Error checking price alerts: {e}")
        
        # Schedule next check in 5 minutes
        self.root.after(300000, self._check_price_alerts)
    
    def _check_sbc_updates(self):
        """Verificar cada minuto si es hora de actualizar SBCs (1:20 PM)"""
        if self.sbc_tracker:
            try:
                if self.sbc_tracker.should_update_now():
                    logger.info("⏰ Hora de actualización de SBCs (1:20 PM) - Actualizando...")
                    self._log("⏰ Actualizando SBCs diarios (1:20 PM)...")
                    
                    # Actualizar SBCs
                    sbcs = self.sbc_tracker.get_active_sbcs(force_refresh=True)
                    logger.info(f"✅ SBCs actualizados: {len(sbcs)} activos")
                    self._log(f"✅ SBCs actualizados: {len(sbcs)} activos")
                    
                    # Refrescar vista de SBCs si está visible
                    if hasattr(self, 'current_page') and self.current_page == 'sbcs':
                        self._refresh_sbcs()
            except Exception as e:
                logger.error(f"Error verificando actualización de SBCs: {e}")
        
        # Verificar nuevamente en 1 minuto (60000 ms)
        self.root.after(60000, self._check_sbc_updates)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point for desktop app"""
    app = TradingBotApp()
    app.run()


if __name__ == '__main__':
    main()
