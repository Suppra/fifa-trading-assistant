# Features Avanzadas - EA FC 26 Trading Bot

**Última actualización**: Noviembre 2025

## 🎯 Resumen de Nuevas Features

Este documento describe las 5 features avanzadas implementadas para análisis profundo de mercado y maximización de ganancias.

---

## 1. 📊 Análisis de Tendencias Históricas

### Descripción
Scraping de gráficos de precios de 7/30/90 días desde FUTBIN para identificar patrones de precio semanales, mensuales y estacionales.

### Servicio
`app/services/historical_trends_service.py`

### Características
- **Obtención de datos históricos**: API de gráficos de FUTBIN
- **Análisis semanal**: Identifica mejor día para comprar/vender
- **Detección de tendencias**: Alcista/Bajista/Lateral
- **Comparación multi-jugador**: Compara rendimiento de varios jugadores
- **Guardado automático**: Historial en `price_history` table

### Métodos Principales

#### `get_price_graph_data(player_id, days=7)`
Obtiene datos del gráfico de precios de FUTBIN.

**Parámetros**:
- `player_id`: ID de FUTBIN del jugador
- `days`: Días de historial (7, 30, 90, 365)

**Returns**:
```python
{
    'player_id': '12345',
    'days': 7,
    'data': [
        {'timestamp': 1699920000000, 'price': 5000},
        {'timestamp': 1700006400000, 'price': 5200},
        ...
    ],
    'fetched_at': '2025-11-14T10:30:00'
}
```

#### `analyze_weekly_pattern(player_id)`
Analiza patrón semanal de precios (Lun-Dom).

**Returns**:
```python
{
    'player_id': '12345',
    'analysis': {
        'Lunes': {'avg_price': 4800, 'min_price': 4500, 'max_price': 5100, ...},
        'Martes': {'avg_price': 4900, ...},
        ...
    },
    'recommendation': {
        'buy_day': 'Lunes',
        'buy_avg': 4800,
        'sell_day': 'Viernes',
        'sell_avg': 5500,
        'avg_profit': 700,
        'profit_pct': 14.58
    }
}
```

#### `detect_price_trends(player_id, days=7)`
Detecta tendencia de precio.

**Returns**:
```python
{
    'trend': 'alcista',  # 'alcista', 'bajista', 'lateral'
    'trend_color': '🟢',
    'change_pct': 12.5,
    'volatility_pct': 8.3,
    ...
}
```

### Ejemplo de Uso

```python
from app.services.historical_trends_service import HistoricalTrendsService

trends = HistoricalTrendsService(db_manager)

# Analizar patrón semanal
pattern = trends.analyze_weekly_pattern('12345')
print(f"Comprar: {pattern['recommendation']['buy_day']}")
print(f"Vender: {pattern['recommendation']['sell_day']}")
print(f"Ganancia: {pattern['recommendation']['profit_pct']}%")

# Detectar tendencia
trend = trends.detect_price_trends('12345', days=30)
print(f"Tendencia: {trend['trend']} ({trend['change_pct']}%)")
```

### Casos de Uso
1. **Weekend League Trading**: Compra Lunes, vende Viernes
2. **Event Trading**: Detecta crashes antes de TOTY/TOTS
3. **Long-term Investment**: Identifica jugadores con tendencia alcista constante

---

## 2. 💼 Dashboard de Portfolio

### Descripción
Sistema completo de tracking de inversiones con cálculo de ROI, profit realizado/no realizado y análisis de distribución.

### Servicio
`app/services/portfolio_service.py`

### Características
- **Resumen completo**: Inversión total, valor actual, profit
- **ROI por carta**: Identifica mejores/peores inversiones
- **Evolución del capital**: Tracking histórico de ganancias
- **Distribución**: Por rating, posición, liga
- **Auto-update**: Se actualiza con cada compra/venta

### Métodos Principales

#### `get_portfolio_summary()`
Resumen completo del portfolio.

**Returns**:
```python
{
    'total_investment': 150000,      # Coins invertidos
    'total_value': 175000,           # Valor actual
    'unrealized_profit': 25000,      # Profit no vendido
    'realized_profit': 10000,        # Profit de ventas
    'total_profit': 35000,           # Total
    'roi_pct': 23.33,                # ROI %
    'cards_owned': 15,
    'cards_sold': 8
}
```

#### `get_top_performers(limit=10)`
Jugadores con mejor ROI.

**Returns**:
```python
[
    {
        'player_name': 'Vinicius Jr',
        'purchase_price': 120000,
        'current_price': 155000,
        'quantity': 2,
        'roi_pct': 29.17,
        'total_profit': 70000
    },
    ...
]
```

#### `get_capital_evolution(days=30)`
Evolución del capital en el tiempo.

**Returns**:
```python
{
    'evolution': [
        {'date': '2025-11-01', 'invested': 50000, 'profit': 2000, 'total': 52000},
        {'date': '2025-11-02', 'invested': 75000, 'profit': 5500, 'total': 80500},
        ...
    ],
    'final_capital': 175000
}
```

### Ejemplo de Uso

```python
from app.services.portfolio_service import PortfolioService

portfolio = PortfolioService(db_manager)

# Resumen
summary = portfolio.get_portfolio_summary()
print(f"ROI Total: {summary['roi_pct']:.2f}%")
print(f"Profit: {summary['total_profit']:,} coins")

# Top 5
top = portfolio.get_top_performers(5)
for inv in top:
    print(f"{inv['player_name']}: {inv['roi_pct']:.1f}% ROI")
```

### Integración UI
- **Sidebar**: Balance y Profit total
- **Tab Historial**: Gráfico de evolución
- **Tab Vender**: ROI por carta individual

---

## 3. ⏰ Análisis de Horas Pico

### Descripción
Monitoreo horario de precios para identificar mejores horas del día para comprar/vender (madrugada vs noche).

### Servicio
`app/services/peak_hours_service.py`

### Características
- **Monitoreo 24h**: Scraping cada hora durante 24h
- **Análisis por hora**: Precio promedio hora 0-23
- **Recomendaciones generales**: Comprar madrugada, vender noche
- **Multi-threading**: Monitoreo en background sin bloquear UI
- **Guardado con hora**: Column `hour_of_day` en `price_history`

### Métodos Principales

#### `start_hourly_monitoring(player_ids, duration_hours=24)`
Inicia monitoreo horario.

**Parámetros**:
- `player_ids`: Lista de IDs a monitorear
- `duration_hours`: Duración del monitoreo

**Ejecución**: Background thread (no bloquea)

#### `analyze_peak_hours(player_id, days=7)`
Analiza horas pico de un jugador.

**Returns**:
```python
{
    'hourly_analysis': {
        0: {'hour': '00:00', 'avg_price': 4500, 'samples': 12},
        1: {'hour': '01:00', 'avg_price': 4480, 'samples': 10},
        ...
        20: {'hour': '20:00', 'avg_price': 5200, 'samples': 25},
    },
    'recommendation': {
        'best_buy_hour': '03:00',
        'best_buy_price': 4400,
        'best_sell_hour': '20:00',
        'best_sell_price': 5200,
        'potential_profit': 800,
        'profit_pct': 18.18
    }
}
```

#### `get_hourly_recommendations()`
Recomendaciones generales por franja horaria.

**Returns**:
```python
{
    'recommendations': [
        {
            'time_range': '00:00 - 06:00',
            'activity': 'Muy Baja',
            'action': '✅ COMPRAR',
            'reason': 'Pocos jugadores activos, precios más bajos'
        },
        {
            'time_range': '18:00 - 23:00',
            'activity': 'Muy Alta',
            'action': '✅ VENDER',
            'reason': 'Peak de jugadores conectados, precios máximos'
        }
    ],
    'best_buy_window': '02:00 - 05:00 (madrugada)',
    'best_sell_window': '19:00 - 22:00 (noche)'
}
```

### Ejemplo de Uso

```python
from app.services.peak_hours_service import PeakHoursService

peak_service = PeakHoursService(db_manager, futbin_service)

# Monitorear jugadores por 24h
player_ids = ['12345', '67890', '11111']
peak_service.start_hourly_monitoring(player_ids, duration_hours=24)

# Después de 24h, analizar
analysis = peak_service.analyze_peak_hours('12345')
print(f"Mejor hora compra: {analysis['recommendation']['best_buy_hour']}")
print(f"Mejor hora venta: {analysis['recommendation']['best_sell_hour']}")

# Recomendaciones generales
recs = peak_service.get_hourly_recommendations()
for rec in recs['recommendations']:
    print(f"{rec['time_range']}: {rec['action']}")
```

### Casos de Uso
1. **Sniping nocturno**: Comprar 2-5 AM, vender 19-22 PM
2. **Flipping diario**: Aprovechar diferencias de +15-20% entre horas
3. **Weekend League timing**: Vender viernes 18-21 PM (máxima demanda)

---

## 4. 🧠 Deep Learning LSTM

### Descripción
Modelo de predicción con LSTM (Long Short-Term Memory) para predecir precios en 1/3/7 días con >70% de precisión.

### Servicio
`app/services/lstm_predictor_service.py`

### Características
- **Arquitectura LSTM**: 3 capas LSTM + Dropout + Dense
- **Entrenamiento automático**: Mínimo 90 días de datos
- **Predicción multi-día**: 1, 3, 7 días adelante
- **Auto-guardado**: Modelos en `models/lstm_{player_id}.h5`
- **Early Stopping**: Previene overfitting
- **Normalización**: MinMaxScaler (0-1)

### Dependencias
```bash
pip install tensorflow>=2.15.0
pip install scikit-learn>=1.3.0
```

### Arquitectura del Modelo

```python
Sequential([
    LSTM(50, return_sequences=True),  # Capa 1
    Dropout(0.2),
    LSTM(50, return_sequences=True),  # Capa 2
    Dropout(0.2),
    LSTM(50),                         # Capa 3
    Dropout(0.2),
    Dense(25),
    Dense(1)                          # Output: precio predicho
])
```

### Métodos Principales

#### `train_model(player_id, epochs=50, batch_size=32)`
Entrena modelo LSTM.

**Parámetros**:
- `player_id`: ID del jugador
- `epochs`: Épocas de entrenamiento
- `batch_size`: Tamaño de batch

**Returns**:
```python
{
    'epochs_trained': 42,         # (early stopping)
    'train_loss': 0.0032,
    'test_loss': 0.0041,
    'train_mae': 0.0234,
    'test_mae': 0.0298,
    'model_path': 'models/lstm_12345.h5'
}
```

#### `predict_price(player_id, days_ahead=1)`
Predice precio futuro.

**Returns**:
```python
{
    'current_price': 120000,
    'days_ahead': 7,
    'predictions': [122000, 125000, 127500, 130000, 131000, 132500, 135000],
    'final_prediction': 135000,
    'change': 15000,
    'change_pct': 12.5,
    'confidence': 78.5,
    'model': 'LSTM'
}
```

#### `batch_train_models(player_ids, epochs=50)`
Entrena modelos para múltiples jugadores.

### Ejemplo de Uso

```python
from app.services.lstm_predictor_service import LSTMPricePredictor

lstm = LSTMPricePredictor(db_manager)

# Entrenar modelo
result = lstm.train_model('12345', epochs=50)
print(f"Test MAE: {result['test_mae']:.4f}")

# Predecir
pred = lstm.predict_price('12345', days_ahead=7)
print(f"Precio actual: {pred['current_price']:,}")
print(f"En 7 días: {pred['final_prediction']:,} ({pred['change_pct']:+.1f}%)")
print(f"Confianza: {pred['confidence']:.1f}%")

# Batch training (top 100 jugadores)
player_ids = ['12345', '67890', ...]
results = lstm.batch_train_models(player_ids[:100])
print(f"Exitosos: {results['successful']}/{results['total']}")
```

### Precisión Esperada
- **1 día**: 75-85% precisión
- **3 días**: 65-75% precisión
- **7 días**: 55-70% precisión

Mejora con:
- Más datos históricos (>180 días ideal)
- Features adicionales (eventos, SBCs, horas)
- Más épocas de entrenamiento (100-200)

---

## 5. ⚡ Real-Time Price Feed

### Descripción
Feed de precios en tiempo real con polling cada 30 segundos y actualización automática sin reiniciar app.

### Servicio
`app/services/realtime_feed_service.py`

### Características
- **Polling automático**: Cada 30 segundos (configurable)
- **Watchlist dinámica**: Añadir/eliminar jugadores en vivo
- **Callbacks**: Notificaciones cuando hay cambios
- **Recent changes**: Últimos 100 cambios en memoria
- **Auto-populate**: Carga watchlist desde inventario
- **Background thread**: No bloquea UI

### Métodos Principales

#### `add_to_watchlist(player_id)`
Añade jugador a monitoreo.

#### `start_polling()`
Inicia polling en background.

#### `register_callback(callback_func)`
Registra función para recibir cambios.

**Callback signature**:
```python
def on_price_change(change: Dict[str, Any]):
    # change = {
    #     'player_id': '12345',
    #     'player_name': 'Vinicius Jr',
    #     'old_price': 120000,
    #     'new_price': 125000,
    #     'change': 5000,
    #     'change_pct': 4.17,
    #     'direction': '📈 SUBIÓ',
    #     'timestamp': '2025-11-14T10:30:00'
    # }
    print(f"{change['player_name']}: {change['change_pct']:+.2f}%")
```

#### `get_recent_changes(limit=20)`
Obtiene últimos cambios.

**Returns**:
```python
[
    {
        'player_name': 'Mbappé',
        'old_price': 500000,
        'new_price': 515000,
        'change_pct': 3.0,
        'timestamp': '2025-11-14T10:30:00'
    },
    ...
]
```

### Ejemplo de Uso

```python
from app.services.realtime_feed_service import RealTimePriceFeed

feed = RealTimePriceFeed(db_manager, futbin_service)

# Auto-populate desde inventario
feed.auto_populate_watchlist_from_inventory()

# Registrar callback
def alert_on_change(change):
    if abs(change['change_pct']) >= 5:
        print(f"🚨 ALERTA: {change['player_name']} {change['change_pct']:+.2f}%")

feed.register_callback(alert_on_change)

# Iniciar feed
feed.start_polling()

# ... app continúa ejecutándose
# Cambios se notifican automáticamente

# Detener feed
feed.stop_polling()
```

### Integración UI

**Tab "⚡ Live Prices"** en desktop app:

1. **Stats Cards**: Estado, watchlist size, cambios detectados
2. **Controls**: Iniciar/Detener, Cargar inventario, Limpiar
3. **Recent Changes Feed**: Cards con cambios en tiempo real
4. **Watchlist Panel**: Jugadores monitoreados

**Screenshot conceptual**:
```
┌─────────────────────────────────────────────────────────┐
│  Estado: 🟢 ACTIVO  │  Monitoreados: 15  │  Cambios: 23 │
├─────────────────────────────────────────────────────────┤
│  [⏸️ DETENER]  [📦 Cargar Inventario]  [🗑️ Limpiar]   │
├─────────────────────────────────────────────────────────┤
│  CAMBIOS EN TIEMPO REAL        │   WATCHLIST            │
│                                 │                        │
│  📈 Vinicius Jr                │   Mbappé (91)          │
│  120,000 → 125,000 (+4.17%)   │   Haaland (91)         │
│  10:30:15                       │   Bellingham (87)      │
│                                 │   ...                  │
│  📉 Rodri                      │                        │
│  65,000 → 62,000 (-4.62%)     │                        │
│  10:30:45                       │                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Comparación de Features

| Feature | Datos Requeridos | Tiempo Ejecución | Precisión | Uso Ideal |
|---------|-----------------|------------------|-----------|-----------|
| **Tendencias Históricas** | 30+ días | 2-5 seg | Alta | Patrón semanal |
| **Portfolio** | Inventario | <1 seg | 100% | Tracking ROI |
| **Horas Pico** | 24h monitoreo | 24 horas | Media | Timing óptimo |
| **LSTM** | 90+ días | 5-15 min entrenar | 70-85% | Predicción futura |
| **Real-Time Feed** | Ninguno | Continuo | 100% | Alertas cambios |

---

## 🚀 Guía de Implementación Completa

### 1. Setup Inicial

```bash
# Instalar dependencias
pip install -r requirements.txt

# TensorFlow (opcional, para LSTM)
pip install tensorflow

# Inicializar BD
python scripts/setup_database.py
```

### 2. Uso en Desktop App

```python
# launcher.py ya inicializa todo automáticamente
python launcher.py

# Navegar a tabs:
# - 📊 Mercado: Ver tendencias
# - 💼 Portfolio: Sidebar (siempre visible)
# - ⏰ Horas Pico: Recomendaciones en Plan de Acción
# - 🧠 LSTM: Predicciones en tab Comprar
# - ⚡ Live Prices: Tab dedicado
```

### 3. Uso Programático

```python
from app.models.database import DatabaseManager
from app.services.historical_trends_service import HistoricalTrendsService
from app.services.portfolio_service import PortfolioService
# ... otros servicios

db = DatabaseManager()

# Tendencias
trends = HistoricalTrendsService(db)
pattern = trends.analyze_weekly_pattern('12345')

# Portfolio
portfolio = PortfolioService(db)
summary = portfolio.get_portfolio_summary()

# etc.
```

---

## 📝 Notas Importantes

### Limitaciones
- **LSTM**: Requiere mínimo 90 días de datos históricos
- **Horas Pico**: Necesita 24h de monitoreo para análisis completo
- **Real-Time Feed**: Rate limiting de FUTBIN (máx 3 jugadores/seg)
- **Tendencias**: Depende de disponibilidad de API de FUTBIN

### Optimizaciones
- Cache de queries frecuentes
- Batch processing para múltiples jugadores
- Background threads para no bloquear UI
- Auto-save de modelos LSTM entrenados

### Futuras Mejoras
- WebSockets para feed en tiempo real (sin polling)
- Integración con FUT Companion App API
- Modelos ensemble (LSTM + Prophet + XGBoost)
- Análisis de sentimiento de redes sociales
- Auto-trading simulado con paper trading

---

## 🤝 Contribuir

Para añadir nuevas features o mejorar existentes:

1. Fork el proyecto
2. Crear rama: `git checkout -b feature/nueva-feature`
3. Implementar en `app/services/`
4. Añadir tests en `scripts/test_*.py`
5. Actualizar documentación
6. Pull Request

---

© 2025 xSuppra - Trading Bot Pro
