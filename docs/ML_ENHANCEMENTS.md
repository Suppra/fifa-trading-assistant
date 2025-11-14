# ML Prediction System - Enhanced Features

## Overview
El sistema de predicciones ha sido mejorado significativamente para incluir detección de eventos, análisis de SBCs, detección de anomalías y múltiples modelos de predicción.

## Nuevas Características

### 1. **Calendario de Eventos de EA FC 26**
Sistema integrado que detecta automáticamente eventos importantes:

- **Weekend League**: Todos los viernes
- **Team of the Week (TOTW)**: Todos los miércoles  
- **TOTY** (Team of the Year): 12-26 de enero
- **TOTS** (Team of the Season): 26 de abril - 7 de junio
- **Futties**: 14 de julio - 18 de agosto
- **Black Friday**: 24-28 de noviembre

**Impacto**: Los precios tienden a subir antes y durante estos eventos.

### 2. **Análisis de Impacto SBC**
Calcula automáticamente el impacto de SBCs activos en la demanda:

```python
# Ejemplo: Un jugador 84 rated es requerido en un SBC
sbc_impact = 0.6  # 60% de impacto en la demanda
precio_ajustado = precio_base * (1 + sbc_impact * 0.15)  # Hasta 15% de aumento
```

**Factores evaluados**:
- Rating del jugador vs requisitos del SBC
- Posición específica requerida
- Liga/nacionalidad del jugador

### 3. **Detección de Anomalías**
Sistema Z-score para detectar movimientos anormales de precios:

```python
# Threshold: 2.5 desviaciones estándar
if z_score > 2.5:
    tipo = 'spike'  # Precio inusualmente alto
elif z_score < -2.5:
    tipo = 'crash'  # Precio inusualmente bajo
```

**Utilidad**: 
- Comprar cuando hay crash (anomalía negativa)
- Vender cuando hay spike (anomalía positiva)

### 4. **Features Avanzados (30+ características)**

#### Características Temporales:
- `day_of_week`: Día de la semana (0-6)
- `hour`: Hora del día (0-23)
- `week_of_year`: Semana del año (1-52)
- `is_weekend`: Si es fin de semana
- `is_weekend_league`: Si es viernes (Weekend League)
- `is_totw`: Si es miércoles (TOTW)

#### Características de Precio:
- `price_ma_7`: Media móvil 7 días
- `price_ma_14`: Media móvil 14 días
- `price_std_7`: Desviación estándar 7 días
- `price_momentum`: Tendencia de precio
- `volatility_7`: Volatilidad 7 días
- `price_range_7`: Rango de precios 7 días

#### Características de Mercado:
- `supply_demand_ratio`: Ratio oferta/demanda
- `market_pressure`: Presión del mercado

#### Características de Eventos:
- `event_count`: Número de eventos activos
- `sbc_impact`: Impacto de SBCs (0-1.0)

### 5. **Método de Predicción Enhanced (Ensemble)**

Combina múltiples enfoques para mayor precisión:

```python
# Métodos combinados:
1. Trend-based (25% peso)      - Análisis de tendencia lineal
2. Moving Average (20% peso)   - Promedio de medias móviles
3. Momentum (15% peso)         - Inercia del precio
4. SBC-adjusted (25% peso)     - Ajuste por demanda de SBCs
5. Event-adjusted (15% peso)   - Ajuste por eventos activos

# Predicción final = Promedio ponderado
```

## Configuración

### config.yaml
```yaml
prediction:
  model_type: enhanced          # 'simple', 'prophet', o 'enhanced'
  enable_sbc_features: true     # Activar análisis de SBCs
  enable_event_features: true   # Activar detección de eventos
  anomaly_threshold: 2.5        # Umbral para detección de anomalías
  training_window_days: 30      # Días de historial para entrenar
  prediction_horizon_days: 7    # Días hacia el futuro
```

### Opciones de model_type:

- **`simple`**: Regresión lineal básica (rápido, menos preciso)
- **`prophet`**: Facebook Prophet (requiere instalación adicional)
- **`enhanced`**: Ensemble con eventos y SBCs (RECOMENDADO)

## Resultados de Predicción

### Estructura de Respuesta:
```json
{
  "player_id": "123456",
  "current_price": 5000,
  "predicted_price": 5500,
  "price_change": 500,
  "price_change_pct": 10.0,
  "confidence": 0.82,
  "trend": "rising",
  "recommendation": "BUY",
  "reason": "Predicción de subida (10.0%) | SBC Impact: 45% | Eventos: Weekend League",
  "sbc_impact": 0.45,
  "active_events": ["Weekend League"],
  "anomaly": {
    "is_anomaly": false,
    "type": null,
    "severity": 0.0,
    "z_score": 1.2
  },
  "method": "enhanced_ensemble"
}
```

### Interpretación:

- **confidence**: 0.0 - 1.0 (mayor = más confiable)
- **trend**: `strongly_rising`, `rising`, `stable`, `falling`, `strongly_falling`
- **recommendation**: `BUY`, `SELL`, o `HOLD`

## Casos de Uso

### Ejemplo 1: Compra Pre-Weekend League
```
Viernes 10:00 AM
- Event: Weekend League activo
- SBC Impact: 0.3 (SBC requiere 84 rated)
- Anomalía: No detectada
- Predicción: +8% en 2 días
→ RECOMENDACIÓN: BUY
```

### Ejemplo 2: Venta en Spike
```
Miércoles 18:00 PM
- Event: TOTW Release
- Anomalía: Spike detectado (z-score: 3.2)
- Predicción: -5% (corrección esperada)
→ RECOMENDACIÓN: SELL (vender en el pico)
```

### Ejemplo 3: Compra en Crash
```
Domingo 22:00 PM
- Event: Fin de Weekend League
- Anomalía: Crash detectado (z-score: -2.8)
- SBC Impact: 0.5 (alta demanda SBC)
- Predicción: +12% recuperación
→ RECOMENDACIÓN: BUY (comprar barato)
```

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Dependencias ML añadidas:
- `scikit-learn>=1.3.0` - Para modelos avanzados
- `xgboost>=2.0.0` - Gradient Boosting (opcional, futuro uso)
- `prophet>=1.1.5` - Facebook Prophet (opcional)
- `tensorflow>=2.15.0` - LSTM (opcional, futuro uso)

**Nota**: Prophet y TensorFlow son opcionales. El método `enhanced` funciona sin ellos.

## Mejoras Futuras Planificadas

### 1. Random Forest Classifier
```python
# Clasificación de tendencias (subida/bajada/estable)
from sklearn.ensemble import RandomForestClassifier
```

### 2. XGBoost Regressor
```python
# Predicción de precios con gradient boosting
from xgboost import XGBRegressor
```

### 3. LSTM (Long Short-Term Memory)
```python
# Redes neuronales para series temporales
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
```

## Limitaciones Actuales

1. **Datos reales limitados**: Las predicciones mejoran con más historial de precios (mínimo 14 días)
2. **Eventos externos**: No detecta noticias o cambios de meta inesperados
3. **Manipulación de mercado**: No puede predecir acciones coordinadas de traders
4. **Actualizaciones de EA**: Cambios en el juego pueden invalidar patrones históricos

## Monitoreo y Ajustes

### Verificar precisión:
```python
# Comparar predicciones con precios reales
SELECT 
    AVG(ABS(predicted_price - actual_price) / actual_price) * 100 as error_pct
FROM predictions
WHERE target_date < NOW()
```

### Ajustar threshold de anomalías:
```yaml
# Más sensible (detecta más anomalías)
anomaly_threshold: 2.0

# Menos sensible (solo anomalías extremas)
anomaly_threshold: 3.0
```

## Soporte

Para problemas o mejoras:
1. Verificar logs en `logs/trading_bot.log`
2. Revisar configuración en `config.yaml`
3. Comprobar que hay suficiente historial de precios (min 14 días)

---

**Última actualización**: Enero 2025
**Versión**: 2.0 Enhanced ML System
