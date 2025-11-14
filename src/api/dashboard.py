"""
Dashboard API for EA FC 26 Trading Bot
Provides REST API and web interface for monitoring and control
"""

import logging
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from typing import Dict, Any

class DashboardAPI:
    """
    Flask-based API for trading bot dashboard
    """
    
    def __init__(self, config, db_manager, market_analyzer, price_predictor, trading_engine):
        """Initialize dashboard API"""
        self.config = config
        self.db_manager = db_manager
        self.market_analyzer = market_analyzer
        self.price_predictor = price_predictor
        self.trading_engine = trading_engine
        self.logger = logging.getLogger("TradingBot.Dashboard")
        
        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.route('/')
        def index():
            """Dashboard home page"""
            return render_template_string(self._get_dashboard_html())
        
        @self.app.route('/api/status')
        def status():
            """Get bot status"""
            total_profit = self.db_manager.get_total_profit()
            
            return jsonify({
                'status': 'running',
                'owned_cards': len(self.trading_engine.owned_cards),
                'total_profit': total_profit,
                'auto_trading': self.trading_engine.auto_trading_enabled
            })
        
        @self.app.route('/api/recommendations')
        def recommendations():
            """Get trading recommendations"""
            recs = self.trading_engine.get_recommendations()
            return jsonify(recs)
        
        @self.app.route('/api/market-state')
        def market_state():
            """Get market state"""
            state = self.market_analyzer.get_market_state()
            return jsonify(state)
        
        @self.app.route('/api/predictions')
        def predictions():
            """Get price predictions"""
            preds = self.price_predictor.predict_weekly_trends()
            return jsonify(preds[:20])
        
        @self.app.route('/api/player/<player_id>')
        def player_info(player_id):
            """Get player information"""
            analysis = self.market_analyzer.analyze_player_trend(player_id)
            prediction = self.price_predictor.predict_price(player_id)
            
            return jsonify({
                'analysis': analysis,
                'prediction': prediction
            })
        
        @self.app.route('/api/execute-buy', methods=['POST'])
        def execute_buy():
            """Execute buy transaction"""
            data = request.json
            player_id = data.get('player_id')
            price = data.get('price')
            
            if not player_id or not price:
                return jsonify({'error': 'Missing player_id or price'}), 400
            
            success = self.trading_engine.execute_buy(player_id, price, strategy='manual')
            
            return jsonify({
                'success': success,
                'message': 'Buy executed successfully' if success else 'Buy failed'
            })
        
        @self.app.route('/api/execute-sell', methods=['POST'])
        def execute_sell():
            """Execute sell transaction"""
            data = request.json
            player_id = data.get('player_id')
            price = data.get('price')
            
            if not player_id or not price:
                return jsonify({'error': 'Missing player_id or price'}), 400
            
            success = self.trading_engine.execute_sell(player_id, price)
            
            return jsonify({
                'success': success,
                'message': 'Sell executed successfully' if success else 'Sell failed'
            })
    
    def _get_dashboard_html(self) -> str:
        """Get dashboard HTML template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>EA FC 26 Trading Assistant 🎮</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: #eee;
                    padding-bottom: 50px;
                }
                .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
                
                /* Header */
                .header {
                    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    border: 2px solid #00d4ff;
                    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
                }
                h1 { 
                    color: #00d4ff;
                    margin-bottom: 10px;
                    font-size: 2.5em;
                    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                }
                .subtitle {
                    color: #aaa;
                    font-size: 1.1em;
                    margin-top: 10px;
                }
                .budget-info {
                    background: rgba(255, 215, 0, 0.1);
                    border: 2px solid #ffd700;
                    border-radius: 10px;
                    padding: 15px;
                    margin-top: 15px;
                    display: inline-block;
                }
                .budget-info strong {
                    color: #ffd700;
                    font-size: 1.3em;
                }
                
                /* Stats Cards */
                .stats { 
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .stat-card { 
                    background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
                    padding: 25px;
                    border-radius: 15px;
                    border: 2px solid #0f3460;
                    transition: all 0.3s ease;
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                }
                .stat-card:hover {
                    transform: translateY(-5px);
                    border-color: #00d4ff;
                    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
                }
                .stat-value { 
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #00d4ff;
                    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
                }
                .stat-label { 
                    color: #aaa;
                    margin-top: 10px;
                    font-size: 1.1em;
                }
                .stat-trend {
                    margin-top: 10px;
                    font-size: 0.9em;
                    padding: 5px 10px;
                    border-radius: 5px;
                    display: inline-block;
                }
                .trend-up { background: rgba(0, 255, 0, 0.2); color: #0f0; }
                .trend-down { background: rgba(255, 0, 0, 0.2); color: #f00; }
                
                /* Sections */
                .section { 
                    background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
                    padding: 25px;
                    border-radius: 15px;
                    margin-bottom: 25px;
                    border: 2px solid #0f3460;
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                }
                h2 { 
                    color: #00d4ff;
                    margin-bottom: 20px;
                    font-size: 1.8em;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                /* Tables */
                table { 
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }
                th, td { 
                    padding: 15px;
                    text-align: left;
                    border-bottom: 1px solid #0f3460;
                }
                th { 
                    color: #00d4ff;
                    font-weight: 600;
                    background: rgba(0, 212, 255, 0.1);
                    position: sticky;
                    top: 0;
                }
                tr:hover {
                    background: rgba(0, 212, 255, 0.05);
                }
                .positive { color: #00ff00; font-weight: bold; }
                .negative { color: #ff0000; font-weight: bold; }
                .neutral { color: #ffa500; }
                
                /* Badges */
                .badge {
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.85em;
                    font-weight: bold;
                    display: inline-block;
                    margin-left: 5px;
                }
                .badge-high { background: #00ff00; color: #000; }
                .badge-medium { background: #ffa500; color: #000; }
                .badge-low { background: #ff4444; color: #fff; }
                .badge-info { background: #00d4ff; color: #000; }
                
                /* Buttons */
                .btn { 
                    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
                    color: #1a1a2e;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 1em;
                    transition: all 0.3s ease;
                    box-shadow: 0 3px 10px rgba(0, 212, 255, 0.3);
                }
                .btn:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(0, 212, 255, 0.5);
                }
                
                /* Alerts */
                .alert {
                    padding: 15px 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    border-left: 5px solid;
                    animation: slideIn 0.5s ease;
                }
                .alert-success { background: rgba(0, 255, 0, 0.1); border-color: #0f0; }
                .alert-warning { background: rgba(255, 165, 0, 0.1); border-color: #ffa500; }
                .alert-danger { background: rgba(255, 0, 0, 0.1); border-color: #f00; }
                
                @keyframes slideIn {
                    from { opacity: 0; transform: translateX(-20px); }
                    to { opacity: 1; transform: translateX(0); }
                }
                
                /* Loading */
                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #00d4ff;
                }
                .spinner {
                    border: 4px solid rgba(0, 212, 255, 0.1);
                    border-top: 4px solid #00d4ff;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                /* Responsive */
                @media (max-width: 768px) {
                    .stats { grid-template-columns: 1fr; }
                    h1 { font-size: 1.8em; }
                    table { font-size: 0.9em; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎮 EA FC 26 Trading Assistant</h1>
                    <div class="subtitle">
                        🤖 Tu asistente personal de trading - Modo Recomendación
                    </div>
                    <div class="budget-info">
                        💰 <strong>Presupuesto inicial: 11,000 coins</strong> | 
                        🎯 Objetivo: Duplicar en 2 semanas
                    </div>
                </div>
                
                <!-- Alerts Section -->
                <div id="alerts-container"></div>
                
                <!-- Stats Cards -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="total-profit">0</div>
                        <div class="stat-label">💰 Ganancia Total</div>
                        <div class="stat-trend" id="profit-trend"></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="owned-cards">0</div>
                        <div class="stat-label">📦 Cartas en Inventario</div>
                        <div class="stat-trend" id="cards-trend">Máx: 3 cartas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="available-budget">11,000</div>
                        <div class="stat-label">💵 Presupuesto Disponible</div>
                        <div class="stat-trend" id="budget-trend">Reserva: 2,000</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="bot-status">✅ Activo</div>
                        <div class="stat-label">🔧 Estado del Bot</div>
                        <div class="stat-trend" id="last-update">Actualizando...</div>
                    </div>
                </div>
                
                <!-- Buy Recommendations -->
                <div class="section">
                    <h2>🟢 Oportunidades de Compra (Rating 82-84)</h2>
                    <p style="color: #aaa; margin-bottom: 15px;">
                        💡 <strong>Filtradas para tu presupuesto de 11k coins</strong> - 
                        Solo cartas de 1.5k a 9k con mínimo 10% profit
                    </p>
                    <table id="buy-recommendations">
                        <thead>
                            <tr>
                                <th>🎮 Jugador</th>
                                <th>⭐ Rating</th>
                                <th>💵 Precio</th>
                                <th>📊 Profit</th>
                                <th>🎯 Confianza</th>
                                <th>⚠️ Riesgo</th>
                                <th>📅 Acción</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="7" class="loading"><div class="spinner"></div>Cargando datos...</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Sell Recommendations -->
                <div class="section">
                    <h2>🔴 Recomendaciones de Venta</h2>
                    <p style="color: #aaa; margin-bottom: 15px;">
                        💰 Vende cuando alcances mínimo 10% profit (1,000+ coins por carta)
                    </p>
                    <table id="sell-recommendations">
                        <thead>
                            <tr>
                                <th>🎮 Jugador</th>
                                <th>💵 Precio Venta</th>
                                <th>📈 Ganancia</th>
                                <th>📅 Días</th>
                                <th>💡 Razón</th>
                                <th>🎯 Confianza</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="loading">No tienes cartas aún - ¡Empieza comprando!</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Weekly Predictions -->
                <div class="section">
                    <h2>🔮 Predicciones de la Semana</h2>
                    <p style="color: #aaa; margin-bottom: 15px;">
                        📈 Jugadores que <strong>SUBIRÁN</strong> en los próximos 7 días (según IA)
                    </p>
                    <table id="predictions">
                        <thead>
                            <tr>
                                <th>🎮 Jugador</th>
                                <th>💵 Precio Actual</th>
                                <th>🔮 Predicción</th>
                                <th>📈 Cambio</th>
                                <th>🎯 Confianza</th>
                                <th>⏰ Estrategia</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="loading"><div class="spinner"></div>Analizando tendencias...</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Tips Section -->
                <div class="section">
                    <h2>💡 Consejos para Trading con 11k Coins</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-top: 15px;">
                        <div style="background: rgba(0,212,255,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #00d4ff;">
                            <strong>⭐ Compra Rating 82-84</strong><br>
                            <span style="color: #aaa; font-size: 0.9em;">
                                Son los más accesibles y rentables. Suben con cada SBC.
                            </span>
                        </div>
                        <div style="background: rgba(0,255,0,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #0f0;">
                            <strong>📈 Vende en Weekend League</strong><br>
                            <span style="color: #aaa; font-size: 0.9em;">
                                Viernes-Domingo los precios suben por alta demanda.
                            </span>
                        </div>
                        <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #ffd700;">
                            <strong>🛡️ Diversifica</strong><br>
                            <span style="color: #aaa; font-size: 0.9em;">
                                Máximo 3 cartas. Nunca gastes los últimos 2k coins.
                            </span>
                        </div>
                        <div style="background: rgba(255,0,0,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #f00;">
                            <strong>⚠️ Evita Panic Sell</strong><br>
                            <span style="color: #aaa; font-size: 0.9em;">
                                Si bajan precios, espera. El mercado siempre se recupera.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Calcular presupuesto disponible
                function calculateBudget(totalProfit, ownedCards) {
                    const initialBudget = 11000;
                    const reserveCoins = 2000;
                    const invested = ownedCards * 5000; // Estimado
                    return Math.max(0, initialBudget + totalProfit - invested);
                }
                
                // Mostrar alertas
                function showAlert(message, type = 'info') {
                    const alertsContainer = document.getElementById('alerts-container');
                    const alertClass = type === 'success' ? 'alert-success' : 
                                      type === 'warning' ? 'alert-warning' : 
                                      type === 'danger' ? 'alert-danger' : 'alert-info';
                    
                    const alertHTML = `
                        <div class="alert ${alertClass}">
                            ${message}
                        </div>
                    `;
                    
                    alertsContainer.innerHTML = alertHTML;
                    setTimeout(() => { alertsContainer.innerHTML = ''; }, 10000);
                }
                
                // Actualizar dashboard
                function updateDashboard() {
                    const now = new Date();
                    document.getElementById('last-update').textContent = 
                        `Actualizado: ${now.toLocaleTimeString()}`;
                    
                    // Status
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {
                            const profit = data.total_profit || 0;
                            const cards = data.owned_cards || 0;
                            
                            document.getElementById('total-profit').textContent = 
                                profit >= 0 ? `+${profit.toLocaleString()}` : profit.toLocaleString();
                            document.getElementById('owned-cards').textContent = `${cards}/3`;
                            
                            // Budget
                            const budget = calculateBudget(profit, cards);
                            document.getElementById('available-budget').textContent = 
                                budget.toLocaleString();
                            
                            // Trends
                            const profitTrend = document.getElementById('profit-trend');
                            if (profit > 0) {
                                profitTrend.textContent = `↗ Ganando`;
                                profitTrend.className = 'stat-trend trend-up';
                            } else if (profit < 0) {
                                profitTrend.textContent = `↘ Pérdida temporal`;
                                profitTrend.className = 'stat-trend trend-down';
                            }
                            
                            // Budget warning
                            if (budget < 2000) {
                                showAlert('⚠️ ALERTA: Presupuesto bajo. No compres más hasta vender.', 'warning');
                            }
                        })
                        .catch(err => console.error('Error fetching status:', err));
                    
                    // Recommendations
                    fetch('/api/recommendations')
                        .then(r => r.json())
                        .then(data => {
                            // Buy recommendations
                            const buyTable = document.querySelector('#buy-recommendations tbody');
                            const buyRecs = data.buy_recommendations || [];
                            
                            if (buyRecs.length === 0) {
                                buyTable.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#aaa;">📊 No hay oportunidades en este momento. Espera a que bajen los precios.</td></tr>';
                            } else {
                                buyTable.innerHTML = buyRecs.slice(0, 5).map((item, idx) => {
                                    const profit = item.potential_profit_pct || item.profit_analysis?.profit_percentage || 0;
                                    const conf = (item.confidence || item.prediction?.confidence || 0) * 100;
                                    const risk = item.profit_analysis?.risk_level || 'medium';
                                    const price = item.current_price || 0;
                                    
                                    // Alert if great opportunity
                                    if (idx === 0 && profit >= 15 && conf >= 75) {
                                        showAlert(`🔥 ¡OPORTUNIDAD! ${item.name}: ${profit.toFixed(1)}% profit potencial`, 'success');
                                    }
                                    
                                    const riskBadge = risk === 'low' ? 'badge-high' : 
                                                     risk === 'medium' ? 'badge-medium' : 'badge-low';
                                    const confBadge = conf >= 75 ? 'badge-high' : 
                                                     conf >= 50 ? 'badge-medium' : 'badge-low';
                                    
                                    return `
                                        <tr>
                                            <td><strong>${item.name || item.player_id}</strong></td>
                                            <td><span class="badge badge-info">${item.rating || 'N/A'}</span></td>
                                            <td><strong>${price.toLocaleString()}</strong> coins</td>
                                            <td class="positive">+${profit.toFixed(1)}%</td>
                                            <td><span class="badge ${confBadge}">${conf.toFixed(0)}%</span></td>
                                            <td><span class="badge ${riskBadge}">${risk}</span></td>
                                            <td>
                                                ${price <= 9000 ? '✅ Comprable' : '❌ Muy caro'}
                                            </td>
                                        </tr>
                                    `;
                                }).join('');
                            }
                            
                            // Sell recommendations
                            const sellTable = document.querySelector('#sell-recommendations tbody');
                            const sellRecs = data.sell_recommendations || [];
                            
                            if (sellRecs.length === 0) {
                                sellTable.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#aaa;">📦 No tienes cartas para vender. ¡Empieza comprando!</td></tr>';
                            } else {
                                sellTable.innerHTML = sellRecs.map((item, idx) => {
                                    const profit = item.profit_after_tax || 0;
                                    const profitPct = item.profit_percentage || 0;
                                    const conf = (item.confidence || 0) * 100;
                                    
                                    // Alert for urgent sell
                                    if (profitPct >= 15) {
                                        showAlert(`💰 ¡VENDE YA! ${item.player_id}: +${profit.toLocaleString()} coins`, 'success');
                                    }
                                    
                                    return `
                                        <tr>
                                            <td><strong>${item.player_id}</strong></td>
                                            <td><strong>${(item.current_price || 0).toLocaleString()}</strong> coins</td>
                                            <td class="${profit >= 0 ? 'positive' : 'negative'}">
                                                ${profit >= 0 ? '+' : ''}${profit.toLocaleString()} 
                                                (${profitPct >= 0 ? '+' : ''}${profitPct.toFixed(1)}%)
                                            </td>
                                            <td>${item.owned_card?.days || 0} días</td>
                                            <td>${item.reason || 'Precio alto'}</td>
                                            <td><span class="badge badge-high">${conf.toFixed(0)}%</span></td>
                                        </tr>
                                    `;
                                }).join('');
                            }
                        })
                        .catch(err => console.error('Error fetching recommendations:', err));
                    
                    // Predictions
                    fetch('/api/predictions')
                        .then(r => r.json())
                        .then(data => {
                            const predTable = document.querySelector('#predictions tbody');
                            const predictions = (data || []).filter(p => p.predicted_price > p.current_price);
                            
                            if (predictions.length === 0) {
                                predTable.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#aaa;">🔮 Recopilando datos para predicciones...</td></tr>';
                            } else {
                                predTable.innerHTML = predictions.slice(0, 10).map(item => {
                                    const change = (item.predicted_price || 0) - (item.current_price || 0);
                                    const changePct = (change / item.current_price * 100) || 0;
                                    const conf = (item.confidence || 0) * 100;
                                    
                                    const strategy = changePct >= 15 ? '🚀 Comprar ahora' :
                                                   changePct >= 10 ? '📈 Buena inversión' :
                                                   changePct >= 5 ? '⏰ Monitorear' : '⏸️ Esperar';
                                    
                                    return `
                                        <tr>
                                            <td><strong>${item.player_id}</strong></td>
                                            <td>${(item.current_price || 0).toLocaleString()} coins</td>
                                            <td class="positive">${(item.predicted_price || 0).toLocaleString()} coins</td>
                                            <td class="positive">+${change.toLocaleString()} (+${changePct.toFixed(1)}%)</td>
                                            <td><span class="badge ${conf >= 70 ? 'badge-high' : 'badge-medium'}">${conf.toFixed(0)}%</span></td>
                                            <td>${strategy}</td>
                                        </tr>
                                    `;
                                }).join('');
                            }
                        })
                        .catch(err => console.error('Error fetching predictions:', err));
                }
                
                // Initial update
                updateDashboard();
                
                // Auto-update every 15 seconds
                setInterval(updateDashboard, 15000);
                
                // Show welcome message
                setTimeout(() => {
                    showAlert('👋 Bienvenido al Trading Assistant. Presupuesto: 11k coins. ¡Vamos a duplicarlo!', 'success');
                }, 1000);
            </script>
        </body>
        </html>
        """
    
    def run(self):
        """Run the dashboard API server"""
        host = self.config.get('api.host', 'localhost')
        port = self.config.get('api.port', 5000)
        
        self.logger.info(f"Starting dashboard at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=False)
