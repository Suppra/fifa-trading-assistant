# 📢 Guía de Configuración de Alertas Personalizadas

## 🔔 Sistema de Notificaciones Windows

El bot ahora incluye un sistema completo de notificaciones push para Windows que te mantiene informado de eventos importantes sin necesidad de estar mirando la aplicación constantemente.

---

## 📋 Tipos de Alertas Disponibles

### 1. **Alertas de Precio** 💰

#### Caída de Precio (Oportunidad de Compra)
```python
# En app/services/realtime_feed_service.py o price_alerts.py
from app.utils.windows_notifications import get_notifier

notifier = get_notifier()

# Cuando detectes una caída de precio significativa
if price_drop_pct >= 5:
    notifier.notify_price_drop(
        player_name="Kylian Mbappé",
        old_price=250000,
        new_price=235000,
        drop_pct=6.0
    )
```

**Cuándo usar:**
- Caídas de precio ≥ 5% en cartas que sigues
- Precios que bajan del promedio histórico
- Cartas de tu watchlist que alcanzan tu precio objetivo

#### Subida de Precio (Momento de Vender)
```python
# Cuando una carta en tu inventario sube de precio
if price_spike_pct >= 8:
    notifier.notify_price_spike(
        player_name="Erling Haaland",
        old_price=180000,
        new_price=195000,
        spike_pct=8.3
    )
```

**Cuándo usar:**
- Subidas de precio ≥ 8% en tu inventario
- Cartas que superan tu target de venta
- Picos de precio cerca de eventos (Weekends, Rewards)

---

### 2. **Alertas de ROI** 🎯

```python
# En _update_portfolio_stats() en desktop_ui.py
roi = summary.get('roi_pct', 0.0)
profit = summary.get('unrealized_profit', 0)

# Milestones configurables
milestones = [5, 10, 15, 20, 25, 30]

for milestone in milestones:
    if roi >= milestone and not hasattr(self, f'_roi_{milestone}_notified'):
        notifier.notify_roi_milestone(roi, profit)
        setattr(self, f'_roi_{milestone}_notified', True)
```

**Milestones recomendados:**
- ✅ **5% ROI**: Rendimiento sólido (ya implementado)
- ✨ **10% ROI**: Muy bueno (ya implementado)
- 🎉 **15% ROI**: Excelente
- 🚀 **20% ROI**: Extraordinario
- 💎 **25%+ ROI**: Elite trader

---

### 3. **Alertas de Predicción LSTM** 🧠

```python
# Cuando ejecutes predicciones LSTM
prediction = lstm_service.predict_price(player_id, days_ahead=3)

if 'final_prediction' in prediction:
    change_pct = prediction['change_pct']
    
    # Notificar solo cambios significativos
    if abs(change_pct) >= 5:
        notifier.notify_lstm_prediction(
            player_name="Vinicius Jr",
            current_price=220000,
            predicted_price=235000,
            days=3
        )
```

**Configuración recomendada:**
- Umbral mínimo: 5% de cambio predicho
- Días: 1, 3 o 7 días
- Confianza mínima: >70%

---

### 4. **Alertas de Horas Pico** ⏰

```python
# En _update_peak_hours_indicator() en desktop_ui.py
recommendations = peak_hours_service.get_hourly_recommendations()

current_hour = datetime.now().hour
action = recommendations.get('current_hour_action', 'ESPERAR')

# Notificar solo en cambios de ventana
if action != self._last_peak_action:
    if action == 'COMPRAR':
        best_buy = recommendations['best_buy_window']
        notifier.notify_peak_hours(
            action='COMPRAR',
            time_window=f"{best_buy['start_hour']:02d}:00-{best_buy['end_hour']:02d}:00",
            savings_or_profit=best_buy['avg_savings_pct']
        )
    elif action == 'VENDER':
        best_sell = recommendations['best_sell_window']
        notifier.notify_peak_hours(
            action='VENDER',
            time_window=f"{best_sell['start_hour']:02d}:00-{best_sell['end_hour']:02d}:00",
            savings_or_profit=best_sell['avg_profit_pct']
        )
    
    self._last_peak_action = action
```

**Ventanas óptimas típicas:**
- 🌙 **Compra**: 02:00-05:00 (madrugada, precios bajos)
- 🔥 **Venta**: 19:00-22:00 (prime time, precios altos)

---

### 5. **Alertas de SBC** ⚽

```python
# Cuando detectes un nuevo SBC
new_sbcs = sbc_tracker.get_active_sbcs(force_refresh=True)

for sbc in new_sbcs:
    if sbc['is_new']:  # Flag que indica SBC nuevo
        # Analizar requirements
        max_rating = max(squad['min_rating'] for squad in sbc['squads'])
        total_players = sum(squad['num_players'] for squad in sbc['squads'])
        
        notifier.notify_sbc_requirement(
            sbc_name=sbc['name'],
            required_rating=max_rating,
            required_cards=total_players
        )
```

**Impacto en mercado:**
- 📈 SBCs con rating 83+: Precios suben 10-20%
- ⚡ SBCs temporales: Oportunidad de venta rápida
- 💎 SBCs premium: Cartas específicas pueden x2 o x3

---

### 6. **Alertas de Inventario** 📦

```python
# Monitorear capacidad de inventario
inventory_count = session.query(Inventory).filter_by(status='active').count()
total_value = sum(item.buy_price for item in inventory_items)

# Alertar cuando el inventario esté casi lleno
if inventory_count >= 80:  # Límite típico es 100
    notifier.notify_inventory_full(
        total_items=inventory_count,
        total_value=total_value
    )
```

**Umbrales recomendados:**
- ⚠️ **80 items**: Advertencia
- 🚨 **90 items**: Urgente - vender pronto
- 🔴 **95+ items**: Crítico - no comprar más

---

### 7. **Alertas de Target de Ganancia** 🎯

```python
# En _create_sell_card() cuando se alcance target
profit_pct = ((current_price - buy_price) / buy_price) * 100

# Targets personalizables
if profit_pct >= 15:  # Target de 15% alcanzado
    notifier.notify_profit_target(
        player_name=card['player_name'],
        buy_price=card['buy_price'],
        sell_price=card['current_price'],
        profit=card['total_profit']
    )
```

**Targets por estrategia:**
- 🏃 **Flipping rápido**: 5-10% profit
- 📊 **Trading normal**: 10-15% profit
- 💎 **Inversión largo plazo**: 20%+ profit

---

### 8. **Alertas de Tendencia de Mercado** 📈

```python
# Analizar tendencia general del mercado
trend_data = trends_service.detect_price_trends(player_id, days=7)

if trend_data:
    trend_type = trend_data.get('trend', 'LATERAL')
    avg_change = trend_data.get('avg_daily_change_pct', 0)
    
    # Notificar cambios significativos de tendencia
    if abs(avg_change) >= 3:
        notifier.notify_market_trend(
            trend_type=trend_type,
            avg_change_pct=avg_change
        )
```

**Interpretación:**
- 📈 **ALCISTA** (+3%+): Momento de vender
- 📉 **BAJISTA** (-3%-): Momento de comprar
- ➡️ **LATERAL**: Mercado estable, esperar

---

## 🎛️ Personalización Avanzada

### Configurar Frecuencia de Notificaciones

```python
# En app/utils/windows_notifications.py

class WindowsNotifier:
    def __init__(self):
        # ... código existente ...
        
        # Configuración de cooldowns (evitar spam)
        self._last_notifications = {}  # {tipo: timestamp}
        self._cooldowns = {
            'price_drop': 300,      # 5 minutos
            'price_spike': 300,     # 5 minutos
            'roi_milestone': 3600,  # 1 hora
            'lstm_prediction': 600, # 10 minutos
            'peak_hours': 1800,     # 30 minutos
            'sbc': 7200,           # 2 horas
            'inventory': 3600,     # 1 hora
            'profit_target': 600,  # 10 minutos
            'market_trend': 1800   # 30 minutos
        }
    
    def _should_notify(self, notification_type: str) -> bool:
        """Check if enough time has passed since last notification"""
        from datetime import datetime, timedelta
        
        if notification_type not in self._last_notifications:
            return True
        
        last_time = self._last_notifications[notification_type]
        cooldown = self._cooldowns.get(notification_type, 300)
        
        if (datetime.now() - last_time).total_seconds() >= cooldown:
            return True
        
        return False
    
    def show_notification(self, title, message, duration=5, notification_type=None):
        """Show notification with cooldown check"""
        if notification_type and not self._should_notify(notification_type):
            logger.debug(f"Notification skipped (cooldown): {notification_type}")
            return False
        
        # ... código existente para mostrar notificación ...
        
        if notification_type:
            self._last_notifications[notification_type] = datetime.now()
        
        return True
```

### Filtros por Horario

```python
# Solo notificaciones en horario activo
def _is_active_hours(self) -> bool:
    """Check if current time is within active trading hours"""
    from datetime import datetime
    
    current_hour = datetime.now().hour
    
    # Configuración personalizable
    active_start = 8   # 8 AM
    active_end = 23    # 11 PM
    
    return active_start <= current_hour <= active_end

# Usar en show_notification()
if not self._is_active_hours() and not force:
    return False
```

### Prioridades de Notificaciones

```python
# Sistema de prioridades
NOTIFICATION_PRIORITY = {
    'CRITICAL': ['sbc', 'inventory', 'profit_target'],
    'HIGH': ['price_drop', 'price_spike', 'roi_milestone'],
    'MEDIUM': ['lstm_prediction', 'peak_hours'],
    'LOW': ['market_trend']
}

# Configurar por prioridad
def set_notification_level(self, level: str):
    """Set minimum priority level for notifications"""
    self._min_priority = level  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
```

---

## 🧪 Testing de Notificaciones

### Test Manual
```python
# En desktop_ui.py o scripts/test_notifications.py
from app.utils.windows_notifications import get_notifier

notifier = get_notifier()

# Test básico
notifier.test_notification()

# Test de cada tipo
notifier.notify_price_drop("Test Player", 100000, 95000, 5.0)
notifier.notify_roi_milestone(10.5, 50000)
notifier.notify_lstm_prediction("Test", 100000, 110000, 3)
```

### Test Automático
```bash
# Crear script de test
python -c "from app.utils.windows_notifications import get_notifier; get_notifier().test_notification()"
```

---

## 📊 Ejemplo de Configuración Completa

```python
# En desktop_ui.py, agregar al __init__:

# Configurar notificaciones personalizadas
if self.notifier and self.notifier.is_enabled():
    logger.info("📢 Configurando notificaciones personalizadas...")
    
    # Test inicial
    self.notifier.test_notification()
    
    # Configurar watchlist de precios
    self._setup_price_alerts()
    
    # Configurar alertas de ROI
    self._roi_milestones = [5, 10, 15, 20, 25]
    
    # Tracking de última acción de peak hours
    self._last_peak_action = None

def _setup_price_alerts(self):
    """Setup price monitoring for notifications"""
    # Monitorear cartas de alta demanda
    high_demand_players = [
        "Kylian Mbappé", "Erling Haaland", "Vinicius Jr",
        "Jude Bellingham", "Rodri", "Harry Kane"
    ]
    
    # Configurar thresholds
    self._price_alert_thresholds = {
        'drop': 5.0,   # Notificar caídas ≥ 5%
        'spike': 8.0   # Notificar subidas ≥ 8%
    }
```

---

## 🎯 Mejores Prácticas

### 1. **Evitar Spam de Notificaciones**
- ✅ Usar cooldowns entre notificaciones del mismo tipo
- ✅ Agrupar notificaciones similares
- ✅ Notificar solo cambios significativos (>5%)

### 2. **Priorizar Información Crítica**
- 🔴 **URGENTE**: SBCs nuevos, inventario lleno, targets alcanzados
- 🟡 **IMPORTANTE**: Cambios de precio >10%, ROI milestones
- 🟢 **INFORMATIVO**: Predicciones, tendencias, peak hours

### 3. **Horarios Inteligentes**
- 🌅 **Mañana (8-12)**: Resumen nocturno, nuevas oportunidades
- ☀️ **Tarde (12-18)**: Alertas de precio, SBCs
- 🌙 **Noche (18-23)**: Peak hours, targets alcanzados
- 😴 **Madrugada (0-8)**: Solo notificaciones CRÍTICAS

### 4. **Personalización por Usuario**
- Traders agresivos: Más alertas, umbrales bajos (3%+)
- Traders conservadores: Menos alertas, umbrales altos (10%+)
- Inversores: Solo milestones y tendencias a largo plazo

---

## 🚀 Próximas Mejoras Sugeridas

1. **Sonidos personalizados** por tipo de notificación
2. **Grupos de notificaciones** (ej: "Trading Activo", "Monitoring", "Alertas")
3. **Historial de notificaciones** con registro en base de datos
4. **Dashboard de notificaciones** en la UI
5. **Integración con Discord** para alertas móviles
6. **Machine Learning** para predecir momentos óptimos de notificación
7. **Acciones rápidas** en notificaciones (ej: "Comprar Ahora", "Ver Detalles")

---

## 📞 Soporte

Si tienes problemas con las notificaciones:

1. Verificar que `win10toast` está instalado: `pip install win10toast`
2. Revisar permisos de Windows para notificaciones
3. Comprobar logs: `logs/trading_bot.log`
4. Test manual: `notifier.test_notification()`

**¡Happy Trading con alertas inteligentes! 🎯📢**
