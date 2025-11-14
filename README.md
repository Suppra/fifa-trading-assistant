# EA FC 26 Trading Assistant 🎮⚽

**Un asistente inteligente de trading para EA Sports FC 26 con precios REALES de FUTBIN (PC).**

⚠️ **IMPORTANTE: Este bot NO ejecuta trades automáticamente. Solo te da recomendaciones expertas basadas en datos reales.**

## 🎯 ¿Qué hace el bot?

✅ **Obtiene precios REALES** de FUTBIN (PC) automáticamente
✅ **Analiza el mercado** con datos actualizados cada hora
✅ **Predice precios** futuros con machine learning  
✅ **Te recomienda** qué jugadores comprar y cuándo vender
✅ **Calcula ganancias** automáticamente (incluye el 5% tax de EA)
✅ **Dashboard visual** para ver oportunidades
✅ **100+ jugadores** populares incluidos

❌ **NO compra ni vende por ti** - Tú ejecutas los trades en el juego
❌ **NO necesita credenciales de EA** - Es completamente seguro

### 🌐 Sistema de Precios FUTBIN
- **Scraping automático** de FUTBIN.com
- **Precios reales de PC** únicamente
- **Actualización cada hora** (configurable)
- **100+ jugadores populares** (Top tier, budget beasts, etc.)
- **Rate limiting inteligente** (2 seg/jugador)
- **Sin API key necesaria** - 100% gratuito

### 🔮 Predicciones Inteligentes
- **Predicción de precios semanales** - Usa machine learning
- **Modelos Prophet y LSTM** - Múltiples algoritmos
- **Análisis de confianza** - Cada predicción incluye confianza
- **Identificación de oportunidades** - Encuentra las mejores inversiones

### 📈 Interfaz Gráfica Moderna
- **Desktop App (Tkinter)** - Interfaz nativa de Windows
- **4 tabs principales** - Dashboard, Recomendaciones, Historial, Discord
- **Actualización en vivo** - Precios desde FUTBIN integrados
- **Gestión de presupuesto** - Configura tu budget de trading
- **Discord bot integrado** - Recibe notificaciones

### 💾 Base de Datos SQLite
- **Historial de precios** - Almacena datos históricos
- **Registro de transacciones** - Tracking de compras/ventas
- **Seguimiento de ganancias** - Calcula beneficios automáticamente
- **19 jugadores** pre-configurados

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 2️⃣ Inicializar Base de Datos
```powershell
python setup_database.py
```

### 3️⃣ Actualizar Precios REALES de FUTBIN
```powershell
python update_prices_pc.py
```

### 4️⃣ Ejecutar Interfaz Gráfica
```powershell
python desktop_app.py
```

---

## 🌐 Actualización de Precios FUTBIN

### Opción A - Manual (desde UI):
1. Ejecuta `python desktop_app.py`
2. Menú: **Acciones → Actualizar Precios FUTBIN (PC)**
3. Espera ~40 segundos (actualiza todos los jugadores)

### Opción B - Manual (consola):
```powershell
python update_prices_pc.py
```

### Opción C - Automático (cada hora):
```powershell
python auto_update_prices.py
```
- Actualiza inmediatamente
- Luego cada 60 minutos
- Presiona `Ctrl+C` para detener

### Opción D - Test Rápido:
```powershell
python test_futbin.py
```

---

## 💡 Cómo Funciona

### Flujo de Trabajo

1. **El scraper obtiene** precios reales de FUTBIN (PC)
2. **El bot analiza** y genera recomendaciones  
3. **Tú ves** las recomendaciones en la interfaz
4. **Tú ejecutas** la compra/venta en EA FC 26
5. **Tú registras** la transacción en el bot
6. **El bot monitorea** tus inversiones

### Ejemplo Práctico

```
🛒 RECOMENDACIÓN DEL BOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comprar: Kylian Mbappé
Precio actual: 3,660,200 coins (FUTBIN PC)
Ganancia potencial: +12.5%
Confianza: 85%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

➡️  TÚ vas al juego y compras la carta

✅ TÚ registras en el bot:
   python trading_assistant.py
   > Opción 4: Registrar compra
   > Player ID: 231747
   > Precio: 450000

📊 El bot ahora monitorea esta carta

💰 Cuando suba a 520,000:
   "VENDE AHORA: +45,600 coins de ganancia"

➡️  TÚ vendes en el juego y registras la venta
```

---

## 📊 Fuente de Datos: FUTBIN

El bot usa **FUTBIN** (https://www.futbin.com) para obtener:
- ✅ Precios actuales de jugadores
- ✅ Ratings, posiciones, ligas
- ✅ Oferta en el mercado
- ✅ Tendencias históricas

**No necesitas credenciales de EA ni Web App.**

---

## 🎯 Estrategias Incluidas

## 🎯 Estrategias Incluidas

### 1. 🎯 Snipe Deals (Cazador de Gangas)
Encuentra cartas listadas muy baratas y te alerta para compra rápida.
```yaml
min_profit_percentage: 10
```

### 2. 📊 Mass Bidding (Pujas Masivas)  
Identifica jugadores para poner múltiples pujas y ganar algunas baratas.
```yaml
focus_ratings: [83, 84, 85, 86]  # Para SBCs
```

### 3. 📈 Position Trading (Inversión)
Recomienda cartas para comprar y mantener 5-7 días hasta que suban.
```yaml
prediction_horizon_days: 7
```

### 4. ⭐ Special Cards (TOTW, Icons)
Analiza cartas especiales con alta demanda en Weekend League.

### 5. 🏆 SBC Trading
Predice qué jugadores subirán cuando salgan SBCs populares.

---

## 📱 Interfaces Disponibles

### 🌐 Dashboard Web (Puerto 5000)
```powershell
python main.py
# Abre http://localhost:5000
```

**Características:**
- 📊 Estadísticas en tiempo real
- 🛒 Top 5 compras recomendadas  
- 💰 Cuándo vender tus cartas
- 🔮 Predicciones semanales
- 📈 Gráficos de tendencias

### 💻 Modo Interactivo (Consola)
```powershell
python trading_assistant.py
```

**Menú:**
1. Ver recomendaciones de compra
2. Ver recomendaciones de venta
3. Ver predicciones semanales
4. ✅ Registrar compra manual
5. ✅ Registrar venta manual
6. Ver estado del mercado
7. Ver ganancias totales

---

## 📖 Guía Detallada

**Lee `GUIA_USO.md` para:**
- ✅ Tutorial paso a paso
- ✅ Cómo encontrar IDs de jugadores en FUTBIN
- ✅ Mejores días para comprar/vender
- ✅ Consejos pro para maximizar ganancias
- ✅ Solución de problemas comunes

---

## ⚙️ Configuración Personalizada

### Ajustar Rentabilidad Mínima
```env
# .env
MIN_PROFIT_MARGIN=10     # Solo recomienda si ganancia >= 10%
MAX_BUY_PRICE=200000     # Máximo presupuesto por carta
```

### Cambiar Ligas a Monitorear
```yaml
# config.yaml
market_analysis:
  leagues:
    - Premier League
    - La Liga
    - Serie A
  min_rating: 83
```

### Intervalo de Actualización
```env
TRADE_INTERVAL_MINUTES=15  # Analiza mercado cada 15 min
```

---

## 📚 Documentación Adicional

- **`GUIA_USO.md`**: Tutorial completo paso a paso
- **`ESTRATEGIAS_11K.md`**: 🔥 Estrategias específicas para duplicar 11k coins
- **`config.yaml`**: Configuración personalizada para bajo presupuesto
- **`.env.example`**: Variables de entorno optimizadas

---

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.

---

**¡Buena suerte con tu trading en EA FC 26!** 🎮⚽💰

_Desarrollado con ❤️ para la comunidad de Ultimate Team_
