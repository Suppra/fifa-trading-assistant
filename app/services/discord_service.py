"""
Discord notification system for EA FC 26 Trading Bot
Sends daily recommendations and real-time alerts to Discord channels
"""

import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime, time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """
    Discord bot for sending trading recommendations and alerts
    """
    
    def __init__(self, token: str, channel_id: int):
        """
        Initialize Discord notifier
        
        Args:
            token: Discord bot token
            channel_id: Discord channel ID for notifications
        """
        self.token = token
        self.channel_id = channel_id
        
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Create bot instance
        self.bot = commands.Bot(command_prefix='!fc26 ', intents=intents)
        self.channel: Optional[discord.TextChannel] = None
        
        # Setup event handlers
        self._setup_events()
        self._setup_commands()
    
    def _setup_events(self):
        """Setup Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            """Called when bot is ready"""
            logger.info(f'Discord bot logged in as {self.bot.user}')
            
            # Get notification channel
            self.channel = self.bot.get_channel(self.channel_id)
            if self.channel:
                logger.info(f'Connected to channel: {self.channel.name}')
                await self.channel.send('🤖 **EA FC 26 Trading Bot conectado!**')
            else:
                logger.error(f'Channel {self.channel_id} not found')
            
            # Start scheduled tasks
            if not self.daily_recommendations.is_running():
                self.daily_recommendations.start()
    
    def _setup_commands(self):
        """Setup Discord bot commands"""
        
        @self.bot.command(name='status')
        async def status(ctx):
            """Check bot status and budget"""
            from app.utils.config_loader import ConfigLoader
            
            config = ConfigLoader()
            budget_info = config.get_budget_info()
            
            embed = discord.Embed(
                title='📊 Estado del Bot',
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name='💰 Presupuesto Actual',
                value=f"{budget_info['current_budget']:,} monedas",
                inline=True
            )
            embed.add_field(
                name='📈 Nivel',
                value=budget_info['tier'].upper(),
                inline=True
            )
            embed.add_field(
                name='🎯 Precio Máximo',
                value=f"{budget_info['max_buy_price']:,} monedas",
                inline=True
            )
            embed.add_field(
                name='📋 Estrategias Activas',
                value=', '.join(budget_info['strategies'][:3]),
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='recomendaciones')
        async def recommendations(ctx):
            """Get current buy recommendations"""
            await self.send_buy_recommendations()
        
        @self.bot.command(name='vender')
        async def sell_alerts(ctx):
            """Get current sell recommendations"""
            await self.send_sell_recommendations()
        
        @self.bot.command(name='presupuesto')
        async def update_budget(ctx, amount: int):
            """Update current budget"""
            from app.utils.config_loader import ConfigLoader
            
            config = ConfigLoader()
            old_tier = config.get_budget_info()['tier']
            
            config.update_budget(amount)
            
            new_info = config.get_budget_info()
            new_tier = new_info['tier']
            
            embed = discord.Embed(
                title='💰 Presupuesto Actualizado',
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name='Nuevo Presupuesto',
                value=f"{amount:,} monedas",
                inline=True
            )
            embed.add_field(
                name='Nivel',
                value=f"{old_tier.upper()} → {new_tier.upper()}",
                inline=True
            )
            embed.add_field(
                name='Estrategias Ajustadas',
                value=new_info['tier_description'],
                inline=False
            )
            
            await ctx.send(embed=embed)
            
            # Send new recommendations based on updated budget
            await asyncio.sleep(2)
            await self.send_buy_recommendations()
        
        @self.bot.command(name='ayuda')
        async def help_command(ctx):
            """Show available commands"""
            embed = discord.Embed(
                title='🤖 Comandos del Bot',
                description='Lista de comandos disponibles para EA FC 26 Trading Bot',
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            commands_list = [
                ('!fc26 status', 'Ver estado del bot y presupuesto actual'),
                ('!fc26 recomendaciones', 'Obtener recomendaciones de compra'),
                ('!fc26 vender', 'Ver recomendaciones de venta'),
                ('!fc26 presupuesto [cantidad]', 'Actualizar presupuesto (ej: !fc26 presupuesto 50000)'),
                ('!fc26 ayuda', 'Mostrar esta ayuda'),
            ]
            
            for cmd, desc in commands_list:
                embed.add_field(name=cmd, value=desc, inline=False)
            
            await ctx.send(embed=embed)
    
    @tasks.loop(time=time(hour=9, minute=0))  # 9:00 AM daily
    async def daily_recommendations(self):
        """Send daily recommendations automatically"""
        if self.channel:
            await self.channel.send('📅 **Recomendaciones Diarias**')
            await self.send_buy_recommendations()
    
    async def send_buy_recommendations(self):
        """Send buy recommendations to Discord channel"""
        if not self.channel:
            logger.warning('Discord channel not available')
            return
        
        try:
            from app.controllers.trading_engine import TradingEngine
            from app.services.market_service import MarketScraper
            from app.controllers.analyzer import MarketAnalyzer
            from app.models.db_manager import DatabaseManager
            from app.utils.config_loader import ConfigLoader
            
            # Initialize components
            config = ConfigLoader()
            db = DatabaseManager()
            scraper = MarketScraper(db, config)
            analyzer = MarketAnalyzer(db, config)
            engine = TradingEngine(db, analyzer, config)
            
            # Get current budget info
            budget_info = config.get_budget_info()
            current_time = datetime.now()
            
            # Create header embed
            header_embed = discord.Embed(
                title='🛒 Recomendaciones de Compra',
                description=f"**Presupuesto:** {budget_info['current_budget']:,} monedas | **Nivel:** {budget_info['tier'].upper()}",
                color=discord.Color.green(),
                timestamp=current_time
            )
            
            # Add time-based strategy note
            hour = current_time.hour
            day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
            
            if day_of_week == 4 and hour >= 18:  # Friday after 6 PM
                strategy_note = '⚡ **Weekend League**: Precios subiendo, considera vender en vez de comprar'
            elif day_of_week == 6:  # Sunday
                strategy_note = '📉 **Domingo**: Mejores precios de la semana, excelente momento para comprar'
            elif hour >= 1 and hour <= 4:  # 1-4 AM
                strategy_note = '🌙 **Madrugada**: Menos competencia, busca sniping'
            elif hour >= 18 and hour <= 21:  # 6-9 PM
                strategy_note = '🔥 **Hora pico**: Mucha actividad, cuidado con precios inflados'
            else:
                strategy_note = '✅ **Momento normal**: Condiciones estándar de mercado'
            
            header_embed.add_field(
                name='📊 Condiciones de Mercado',
                value=strategy_note,
                inline=False
            )
            
            await self.channel.send(embed=header_embed)
            
            # Get recommendations
            recommendations = engine._generate_buy_recommendations()
            
            if not recommendations:
                await self.channel.send('❌ No hay recomendaciones disponibles en este momento.')
                return
            
            # Send top 5 recommendations
            for i, rec in enumerate(recommendations[:5], 1):
                embed = discord.Embed(
                    title=f"{i}. {rec['player_name']}",
                    color=self._get_rating_color(rec['rating'])
                )
                
                # Price info
                embed.add_field(
                    name='💵 Precio Actual',
                    value=f"{rec['current_price']:,} monedas",
                    inline=True
                )
                
                # Profit potential
                profit_emoji = '🔥' if rec['profit_potential'] > 2000 else '💰'
                embed.add_field(
                    name=f'{profit_emoji} Ganancia Potencial',
                    value=f"+{rec['profit_potential']:,} ({rec['profit_percentage']:.1f}%)",
                    inline=True
                )
                
                # Rating and position
                embed.add_field(
                    name='⭐ Info',
                    value=f"Rating: {rec['rating']} | {rec.get('position', 'N/A')}",
                    inline=True
                )
                
                # Strategy and confidence
                embed.add_field(
                    name='📈 Estrategia',
                    value=rec.get('strategy', 'General'),
                    inline=True
                )
                
                confidence_emoji = '🟢' if rec['confidence'] > 0.7 else '🟡' if rec['confidence'] > 0.5 else '🟠'
                embed.add_field(
                    name=f'{confidence_emoji} Confianza',
                    value=f"{rec['confidence']*100:.0f}%",
                    inline=True
                )
                
                # Trend
                trend = rec.get('trend', 'stable')
                trend_emoji = '📈' if trend == 'rising' else '📉' if trend == 'falling' else '➡️'
                embed.add_field(
                    name=f'{trend_emoji} Tendencia',
                    value=trend.capitalize(),
                    inline=True
                )
                
                # Reason
                if 'reason' in rec:
                    embed.add_field(
                        name='💡 Razón',
                        value=rec['reason'],
                        inline=False
                    )
                
                await self.channel.send(embed=embed)
                await asyncio.sleep(1)  # Rate limiting
            
            # Footer with tips
            footer_embed = discord.Embed(
                description='💡 **Tip**: Usa `!fc26 presupuesto [cantidad]` para actualizar tu presupuesto y recibir recomendaciones personalizadas',
                color=discord.Color.blue()
            )
            await self.channel.send(embed=footer_embed)
            
        except Exception as e:
            logger.error(f'Error sending buy recommendations: {e}')
            await self.channel.send(f'❌ Error al obtener recomendaciones: {str(e)}')
    
    async def send_sell_recommendations(self):
        """Send sell recommendations to Discord channel"""
        if not self.channel:
            logger.warning('Discord channel not available')
            return
        
        try:
            from app.controllers.trading_engine import TradingEngine
            from app.services.market_service import MarketScraper
            from app.controllers.analyzer import MarketAnalyzer
            from app.models.db_manager import DatabaseManager
            from app.utils.config_loader import ConfigLoader
            
            # Initialize components
            config = ConfigLoader()
            db = DatabaseManager()
            scraper = MarketScraper(db, config)
            analyzer = MarketAnalyzer(db, config)
            engine = TradingEngine(db, analyzer, config)
            
            # Get sell recommendations
            recommendations = engine._generate_sell_recommendations()
            
            if not recommendations:
                await self.channel.send('✅ No tienes cartas para vender en este momento.')
                return
            
            # Header
            embed = discord.Embed(
                title='💰 Recomendaciones de Venta',
                description='Cartas que deberías considerar vender ahora',
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            await self.channel.send(embed=embed)
            
            # Send each recommendation
            for i, rec in enumerate(recommendations, 1):
                embed = discord.Embed(
                    title=f"{i}. {rec['player_name']}",
                    color=discord.Color.green() if rec['profit'] > 0 else discord.Color.red()
                )
                
                # Buy and sell prices
                embed.add_field(
                    name='💵 Precio Compra',
                    value=f"{rec['buy_price']:,} monedas",
                    inline=True
                )
                embed.add_field(
                    name='💰 Precio Venta',
                    value=f"{rec['current_price']:,} monedas",
                    inline=True
                )
                
                # Profit
                profit_emoji = '✅' if rec['profit'] > 0 else '❌'
                embed.add_field(
                    name=f'{profit_emoji} Ganancia',
                    value=f"{rec['profit']:+,} ({rec['profit_percentage']:+.1f}%)",
                    inline=True
                )
                
                # Recommendation
                embed.add_field(
                    name='🎯 Acción',
                    value=rec['recommendation'],
                    inline=False
                )
                
                if 'reason' in rec:
                    embed.add_field(
                        name='💡 Razón',
                        value=rec['reason'],
                        inline=False
                    )
                
                await self.channel.send(embed=embed)
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f'Error sending sell recommendations: {e}')
            await self.channel.send(f'❌ Error al obtener recomendaciones de venta: {str(e)}')
    
    async def send_alert(self, alert_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Send real-time alert to Discord channel
        
        Args:
            alert_type: Type of alert (opportunity, warning, info)
            message: Alert message
            data: Additional data for the alert
        """
        if not self.channel:
            return
        
        color_map = {
            'opportunity': discord.Color.green(),
            'warning': discord.Color.orange(),
            'info': discord.Color.blue(),
            'error': discord.Color.red()
        }
        
        emoji_map = {
            'opportunity': '🔥',
            'warning': '⚠️',
            'info': 'ℹ️',
            'error': '❌'
        }
        
        embed = discord.Embed(
            title=f"{emoji_map.get(alert_type, '📢')} {alert_type.upper()}",
            description=message,
            color=color_map.get(alert_type, discord.Color.blue()),
            timestamp=datetime.now()
        )
        
        if data:
            for key, value in data.items():
                embed.add_field(name=key, value=str(value), inline=True)
        
        await self.channel.send(embed=embed)
    
    def _get_rating_color(self, rating: int) -> discord.Color:
        """Get color based on player rating"""
        if rating >= 88:
            return discord.Color.from_rgb(255, 215, 0)  # Gold
        elif rating >= 85:
            return discord.Color.from_rgb(192, 192, 192)  # Silver
        elif rating >= 82:
            return discord.Color.from_rgb(205, 127, 50)  # Bronze
        else:
            return discord.Color.from_rgb(139, 69, 19)  # Common
    
    def run(self):
        """Run the Discord bot"""
        try:
            self.bot.run(self.token)
        except Exception as e:
            logger.error(f'Error running Discord bot: {e}')
            raise
    
    async def start_async(self):
        """Start bot asynchronously (for integration with other async code)"""
        try:
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f'Error starting Discord bot: {e}')
            raise
    
    async def stop(self):
        """Stop the Discord bot gracefully"""
        await self.bot.close()
