# 🎮 GUÍA DE USO - EA FC 26 Trading Assistant

## 📖 Cómo Usar el Bot (Modo Recomendación)

Este bot **NO compra ni vende automáticamente**. Es tu **asistente personal** que te dice:
- ✅ **Qué cartas comprar** y a qué precio
- ✅ **Cuándo vender** tus cartas para máxima ganancia
- ✅ **Predicciones** de precios para la próxima semana
- ✅ **Análisis del mercado** en tiempo real

### 🚀 Inicio Rápido

1. **Configura el bot:**
   ```powershell
   # Copia el archivo de configuración
   Copy-Item .env.example .env
   
   # Edita .env con tu configuración preferida
   notepad .env
   ```

2. **Inicia el bot:**
   ```powershell
   python main.py
   ```

3. **Abre el dashboard:**
   - Ve a: http://localhost:5000
   - Verás recomendaciones en tiempo real

---

## 💡 Flujo de Trabajo Recomendado

### 1️⃣ Consulta Recomendaciones

**En el Dashboard (http://localhost:5000):**
- Verás las mejores oportunidades de compra
- Rankings de jugadores para invertir
- Cuándo vender tus cartas

**En la Consola:**
```
🛒 BUY RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Kylian Mbappé (Rating: 91)
   💵 Buy at: 450,000 coins
   📊 Potential profit: 12.5%
   🎯 Confidence: 85%
   ⚠️  Risk: low
```

### 2️⃣ Ve al Juego (EA FC 26)

1. Abre EA FC 26 o el Web App
2. Busca el jugador recomendado
3. Verifica el precio actual en el mercado
4. **Compra la carta TÚ MISMO** si el precio es bueno

### 3️⃣ Registra tu Compra

**Opción A - En el Dashboard:**
- Usa el botón "Record Buy" (cuando lo implementes)
- Ingresa: Player ID y Precio

**Opción B - Por Consola (Python):**
```python
from src.trading.trading_engine import TradingEngine
from src.database.db_manager import DatabaseManager
from src.utils.config_loader import ConfigLoader

config = ConfigLoader()
db = DatabaseManager()
engine = TradingEngine(config, db, None, None)

# Registra tu compra
engine.record_buy(
    player_id="231747",  # ID del jugador
    price=450000,         # Precio que pagaste
    strategy="snipe"      # Estrategia usada
)
```

### 4️⃣ Monitorea tus Inversiones

El bot analizará automáticamente tus cartas y te dirá:
- 📈 Cuándo el precio ha subido lo suficiente
- 💰 Cuánta ganancia tendrás (después del 5% tax)
- ⏰ Mejor momento para vender

### 5️⃣ Vende en el Juego

Cuando veas una recomendación de venta:

```
💰 SELL RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Player ID: 231747
   💵 Sell at: 520,000 coins
   📈 Profit: +45,600 coins (+10.1%)
   📅 Held for: 3 days
```

1. Ve al juego
2. Lista la carta en el mercado de transferencias
3. Pon el precio recomendado
4. Registra la venta en el bot

### 6️⃣ Registra tu Venta

```python
# Registra tu venta
engine.record_sell(
    player_id="231747",
    price=520000
)

# Verás:
# ✅ 💰 Sell recorded: 231747 @ 520,000 coins
#    Profit: +45,600 coins (+10.1%)
```

---

## 🎯 Estrategias de Trading

### 📊 Mass Bidding (Pujas Masivas)
```yaml
# Configura en config.yaml
trading:
  strategies:
    - mass_bidding
  
  max_cards_owned: 50
  diversification_limit: 10
```

**Cómo funciona:**
1. Bot encuentra 20 jugadores rating 84 a buen precio
2. Tú pones **pujas** en múltiples cartas
3. Ganas algunas, las vendes cuando suben

**Consejo:** Puja 5-10% menos del precio de mercado

---

### 🎯 Snipe Deals (Cazador de Gangas)
```yaml
trading:
  strategies:
    - snipe_deals
  
  min_profit_percentage: 10
```

**Cómo funciona:**
1. Bot te alerta de cartas listadas MUY baratas
2. Tú las compras rápidamente
3. Revendes inmediatamente con ganancia

**Consejo:** Mantén el Web App abierto para reaccionar rápido

---

### 📈 Position Trading (Inversión a Largo Plazo)
```yaml
trading:
  strategies:
    - position_trading
  
prediction:
  prediction_horizon_days: 7
```

**Cómo funciona:**
1. Bot predice qué jugadores subirán en 7 días
2. Compras y GUARDAS las cartas
3. Vendes cuando el precio suba

**Consejo:** Ideal para Icons y jugadores meta

---

### ⭐ Special Cards (Cartas Especiales)
```yaml
trading:
  strategies:
    - special_cards
```

**Cómo funciona:**
1. Cada miércoles sale Team of the Week (TOTW)
2. Bot analiza qué cartas TOTW subirán
3. Inviertes en ellas antes del Weekend League

**Consejo:** Compra miércoles, vende viernes-domingo

---

## 🔍 Seguimiento de Jugadores Específicos

### Agregar Jugadores para Monitorear

1. **Por ID (desde FUTBIN):**
   ```python
   # Edita src/data_collection/market_scraper.py
   def _get_popular_player_ids(self):
       return [
           "231747",  # Kylian Mbappé
           "239085",  # Erling Haaland
           "192985",  # Kevin De Bruyne
           # ... más jugadores
       ]
   ```

2. **Por Nombre:**
   ```python
   scraper = MarketScraper(config, db)
   scraper.get_player_by_name("Haaland")
   # Te dará el link de FUTBIN para encontrar el ID
   ```

3. **Por Rating:**
   ```yaml
   # En config.yaml
   market_analysis:
     focus_ratings:
       - 83
       - 84
       - 85
   ```

---

## 📊 Usando FUTBIN

### Encontrar IDs de Jugadores

1. Ve a https://www.futbin.com/26/players
2. Busca el jugador
3. En la URL verás: `/26/player/231747/kylian-mbappe`
4. El ID es: **231747**

### Integración Automática

El bot usa la API de FUTBIN para obtener precios:
```python
# El scraper ya está configurado para usar FUTBIN
# Automáticamente obtiene:
# - Precios actuales (PC, PS, Xbox)
# - Rating, posición, liga
# - Oferta en el mercado
```

---

## ⚙️ Configuración Avanzada

### Ajustar Rentabilidad Mínima
```env
# .env
MIN_PROFIT_MARGIN=5    # Cambia a 10 para ser más selectivo
MAX_BUY_PRICE=100000   # Máximo que quieres gastar
```

### Cambiar Intervalo de Análisis
```env
TRADE_INTERVAL_MINUTES=30   # Cada cuánto analiza el mercado
```

### Enfocarse en Ligas Específicas
```yaml
# config.yaml
market_analysis:
  leagues:
    - Premier League
    - La Liga
  min_rating: 83
```

---

## 📈 Dashboard Web

### Características del Dashboard

**Estadísticas Principales:**
- 💰 Ganancias totales
- 📦 Cartas en inventario
- 📊 Estado del mercado

**Recomendaciones:**
- Top 5 compras recomendadas
- Mejores momentos para vender
- Predicciones semanales

**Análisis Individual:**
- Busca cualquier jugador
- Ve su tendencia de precio
- Predicción de precio futuro

### Acceder al Dashboard
```
http://localhost:5000
```

---

## 🧮 Calculadora de Ganancias

El bot calcula automáticamente:
```
Precio de Compra: 100,000 coins
Precio de Venta:  115,000 coins
Tax EA (5%):      -5,750 coins
─────────────────────────────────
Ganancia Neta:    +9,250 coins (9.25%)
```

**Recuerda:** EA siempre cobra 5% de impuesto en ventas

---

## 🎓 Consejos Pro

### 📅 Mejores Días para Comprar/Vender

**Comprar:**
- 🕐 Lunes-Miércoles: Precios más bajos
- 🕐 Durante Rewards (jueves 19:00): Mucha oferta

**Vender:**
- 🕐 Viernes-Domingo: Weekend League
- 🕐 Después de SBC popular: Alta demanda

### 💎 Jugadores Rentables

**Siempre demandados:**
- Rating 83-86 (para SBCs)
- Premier League (liga más popular)
- Posiciones: ST, CAM, CB
- Nacionalidades top: Francia, Brasil, Inglaterra

### ⚠️ Evita Estos Errores

❌ Comprar durante hype (muy caro)
❌ Vender durante market crash
❌ Invertir todo en un solo jugador
❌ Ignorar las predicciones del bot
❌ Vender con menos de 5% ganancia

✅ Diversifica tus inversiones
✅ Sigue las recomendaciones del bot
✅ Ten paciencia
✅ Aprovecha eventos especiales

---

## 🔔 Alertas y Notificaciones

### Por Consola
El bot muestra alertas importantes:
```
🚨 ALERT: Market crash detected (-15%)
💡 TIP: Good time to buy investment cards
```

### Por Dashboard
- Actualización cada 30 segundos
- Notificaciones visuales
- Cambios en recomendaciones

---

## 📊 Reportes

### Ver tu Histórico
```python
# Consulta tus transacciones
total_profit = db.get_total_profit()
print(f"Ganancias totales: {total_profit:,} coins")
```

### Exportar Datos
```python
# Las transacciones están en: data/trading_bot.db
# Usa DB Browser for SQLite para verlas
```

---

## 🆘 Problemas Comunes

### "No buy recommendations"
- **Causa:** Mercado muy caro
- **Solución:** Espera a rewards o market crash

### "Player not found in FUTBIN"
- **Causa:** ID incorrecto o jugador nuevo
- **Solución:** Verifica el ID en FUTBIN

### "Insufficient data for prediction"
- **Causa:** Jugador sin historial de precios
- **Solución:** Espera 24-48 horas para datos

---

## 📞 Soporte

**Logs detallados:**
```
logs/trading_bot_YYYYMMDD.log
```

**Base de datos:**
```
data/trading_bot.db
```

---

## 🎮 ¡A Ganar Coins!

Recuerda:
1. 👀 El bot **RECOMIENDA**
2. 🎮 Tú **EJECUTAS** en el juego
3. 📝 **REGISTRAS** tus transacciones
4. 💰 **GANAS** siguiendo las estrategias

**¡Buena suerte en el mercado de transferencias!** 🚀
