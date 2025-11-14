# 🎮 EA FC 26 Trading Bot - README

## 🚀 Nuevas Funciones Agregadas

### ✨ Novedades v2.0

Este bot ha sido **completamente mejorado** con las siguientes funciones:

#### 1. 💰 Presupuesto Dinámico
- **Adaptación automática** según tu presupuesto actual
- **4 niveles**: BAJO (0-20k), MEDIO (20-50k), ALTO (50-100k), ELITE (100k+)
- Las estrategias se ajustan automáticamente sin reconfiguración manual
- Actualiza tu presupuesto desde la app, Discord o archivo de configuración

#### 2. 🖥️ App de Escritorio para Windows
- Interfaz gráfica nativa con Tkinter
- Dashboard visual con todas las funciones
- Gestión de presupuesto con un click
- Registro de transacciones visual
- Estado del mercado en tiempo real
- Configuración de Discord integrada

#### 3. 💬 Integración con Discord
- Recibe recomendaciones diarias automáticas (9:00 AM)
- Alertas en tiempo real de oportunidades
- Comandos interactivos (!fc26 status, !fc26 recomendaciones, etc.)
- Actualiza presupuesto desde Discord
- Notificaciones en móvil con app de Discord

#### 4. ⏰ Manejo Inteligente de Fecha/Hora
- El bot conoce la hora actual y ajusta estrategias
- **Madrugada (1-4 AM)**: Sniping agresivo
- **Hora Pico (6-9 PM)**: Recomienda VENDER
- **Domingo noche**: Detecta mejores precios de la semana
- **Weekend League**: Alertas viernes-domingo
- Eventos especiales (TOTW, Promos, SBC)

## 🎯 ¿Qué hace este bot?

EA FC 26 Trading Bot es un asistente inteligente que te ayuda a ganar monedas en Ultimate Team mediante:

- 📊 **Análisis de mercado en tiempo real** (precios de FUTBIN)
- 🤖 **Predicciones con IA** (Prophet + TensorFlow)
- 💡 **Recomendaciones personalizadas** según tu presupuesto
- 📈 **Estrategias adaptativas** según día/hora
- 💰 **Seguimiento de ganancias** automático

**IMPORTANTE**: Este NO es un bot de auto-trading. Tú haces las compras/ventas manualmente en el juego, el bot solo te dice QUÉ y CUÁNDO comprar/vender.

## 📦 Instalación

### Requisitos
- Python 3.8 o superior
- Windows (para app de escritorio)
- Conexión a Internet

### Pasos

1. **Clona o descarga el repositorio**
```bash
git clone <tu-repo>
cd Trader
```

2. **Instala dependencias**
```bash
pip install -r requirements.txt
```

3. **Configura el bot**
```bash
# Opción 1: Usar script de configuración
python launcher.py
# Selecciona opción 7 (Configurar .env)

# Opción 2: Manual
copy .env.example .env
# Edita .env con tus preferencias
```

4. **Configura tu presupuesto inicial**
```bash
python launcher.py
# Selecciona opción 6 (Configurar Presupuesto)
```

## 🚀 Uso

### Método 1: Launcher (Recomendado)
```bash
python launcher.py
```

Menú interactivo con todas las opciones:
- 🖥️ App de escritorio (la más fácil de usar)
- 💬 Bot de Discord (notificaciones automáticas)
- 🌐 Dashboard web (localhost:5000)
- 💻 CLI (línea de comandos)

### Método 2: App de Escritorio (Directo)
```bash
python desktop_app.py
```

### Método 3: Discord Bot (Directo)
```bash
# Primero configura DISCORD_BOT_TOKEN y DISCORD_CHANNEL_ID en .env
python discord_bot.py
```

### Método 4: Dashboard Web (Directo)
```bash
python main.py
# Abre http://localhost:5000
```

### Método 5: CLI (Directo)
```bash
python trading_assistant.py
```

## 📚 Documentación

- **README.md** (este archivo) - Información general
- **GUIA_USO.md** - Tutorial detallado paso a paso
- **ESTRATEGIAS_11K.md** - Estrategias para presupuesto bajo
- **NUEVAS_FUNCIONES.md** - Guía completa de las nuevas funciones

## 🎮 Inicio Rápido (3 pasos)

### 1. Instala dependencias
```bash
pip install -r requirements.txt
```

### 2. Configura presupuesto
```bash
python launcher.py
# Opción 6 > Ingresa tu presupuesto actual
```

### 3. Inicia la app de escritorio
```bash
python launcher.py
# Opción 2 (App de Escritorio)
```

¡Listo! Ya puedes empezar a recibir recomendaciones.

## 💬 Comandos de Discord

Una vez configurado el bot de Discord:

```
!fc26 status              - Ver estado y presupuesto
!fc26 recomendaciones     - Mejores compras ahora
!fc26 vender              - Qué vender ahora
!fc26 presupuesto 50000   - Actualizar presupuesto
!fc26 ayuda               - Ver todos los comandos
```

## 🔧 Configuración Avanzada

### Presupuesto Dinámico

Edita `budget_config.json`:
```json
{
    "current_budget": 50000,
    "initial_budget": 11000,
    "total_profit": 39000,
    "invested": 0,
    "reserve": 5000,
    "last_updated": "2025-11-13T12:00:00"
}
```

O usa cualquiera de estos métodos:
- App de escritorio > Archivo > Configurar Presupuesto
- Discord > `!fc26 presupuesto 50000`
- Launcher > Opción 6

### Discord

Edita `.env`:
```env
DISCORD_BOT_TOKEN=tu_token_aquí
DISCORD_CHANNEL_ID=tu_canal_id_aquí
DISCORD_DAILY_REPORT_HOUR=9
```

Ver **NUEVAS_FUNCIONES.md** para guía completa de configuración de Discord.

## 🎯 Estrategias Incluidas

El bot incluye 8 estrategias que se adaptan a tu presupuesto:

### Presupuesto BAJO (0-20k)
1. **Snipe Deals** - Gangas mal preciadas
2. **Mass Bidding** - Pujas en masa
3. **SBC Trading** - Preparación para SBCs
4. **Fodder Flipping** - Compra/vende rating 82-84

### Presupuesto MEDIO (20-50k)
5. **Position Trading** - Cambio de posición
6. **Special Cards** - Cartas especiales accesibles
7. **Meta Players** - Jugadores meta populares
8. **Weekend League** - Trading de fin de semana

### Presupuesto ALTO (50-100k)
- Special Cards premium
- Icons baratos
- Investment a largo plazo
- Promo Cards

### Presupuesto ELITE (100k+)
- Icons top
- High-End Trading
- Market Manipulation
- Investment strategies

## ⏰ Estrategias según Hora

El bot ajusta recomendaciones automáticamente:

- **🌙 Madrugada (1-4 AM)**: Sniping, menos competencia
- **🌅 Mañana (6-9 AM)**: Compras tranquilas
- **☀️ Tarde (12-5 PM)**: Trading general
- **🔥 Hora Pico (6-9 PM)**: VENDER (precios altos)
- **🌃 Noche (9PM-1AM)**: Mixto

**Weekend League:**
- Viernes 6PM+: NO COMPRAR (precios subiendo)
- Sábado: VENDER TODO (picos de precio)
- Domingo 8-11PM: COMPRAR AGRESIVAMENTE (precios bajos)

## 📊 Niveles de Presupuesto

| Nivel | Rango | Focus | Max Inversión | Profit Min |
|-------|-------|-------|---------------|------------|
| 🥉 BAJO | 0-20k | Rating 82-84 | 45% budget | 10% |
| 🥈 MEDIO | 20-50k | Rating 84-86 | 35% budget | 8% |
| 🥇 ALTO | 50-100k | Rating 86-88 | 30% budget | 6% |
| 💎 ELITE | 100k+ | Rating 88+ | 25% budget | 5% |

## 🆘 Solución de Problemas

### "Import Error discord"
```bash
pip install discord.py
```

### "App de escritorio no abre"
```bash
# Verifica Python
python --version

# Reinstala dependencias
pip install -r requirements.txt
```

### "Discord bot no conecta"
1. Verifica TOKEN correcto en .env
2. Habilita MESSAGE CONTENT INTENT en Discord Developer Portal
3. Invita bot a tu servidor con permisos correctos

### "Recomendaciones no se adaptan"
1. Verifica `budget_config.json` existe
2. Actualiza presupuesto manualmente
3. Reinicia la app

Ver **NUEVAS_FUNCIONES.md** sección "Solución de Problemas" para más ayuda.

## 📁 Estructura del Proyecto

```
Trader/
├── main.py                  # Dashboard web
├── desktop_app.py           # App de escritorio Windows
├── discord_bot.py           # Bot de Discord
├── trading_assistant.py     # CLI interactivo
├── launcher.py              # Menú principal (NUEVO)
├── start.py                 # Quick start (legacy)
├── budget_config.json       # Configuración de presupuesto (NUEVO)
├── config.yaml              # Configuración general
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
├── src/
│   ├── data_collection/     # Scraping de FUTBIN
│   ├── market_analysis/     # Análisis de mercado
│   ├── prediction/          # Predicciones con IA
│   ├── trading/             # Motor de trading
│   ├── database/            # Base de datos SQLite
│   ├── api/                 # API Flask (dashboard)
│   ├── discord_bot/         # Bot de Discord (NUEVO)
│   ├── desktop_app/         # App de escritorio (NUEVO)
│   └── utils/               # Utilidades (config, logger)
├── docs/
│   ├── README.md            # Este archivo
│   ├── GUIA_USO.md          # Tutorial completo
│   ├── ESTRATEGIAS_11K.md   # Estrategias bajo presupuesto
│   └── NUEVAS_FUNCIONES.md  # Guía de nuevas funciones (NUEVO)
├── data/                    # Base de datos
├── logs/                    # Logs del sistema
├── models/                  # Modelos de IA entrenados
└── reports/                 # Reportes generados
```

## 🤝 Contribuciones

Este es un proyecto personal, pero puedes:
- Reportar bugs
- Sugerir mejoras
- Compartir estrategias exitosas
- Mejorar documentación

## 📄 Licencia

Proyecto personal de código abierto. Úsalo como quieras, pero recuerda:
- NO es para comercializar
- NO garantiza ganancias
- Úsalo bajo tu propio riesgo

## 🎉 Créditos

- **FUTBIN**: Fuente de datos de precios
- **Prophet**: Predicciones de series temporales
- **Discord.py**: Integración con Discord
- **Flask**: Dashboard web
- **Tkinter**: App de escritorio

## 📞 Soporte

Para ayuda:
1. Lee **NUEVAS_FUNCIONES.md** (guía completa)
2. Lee **GUIA_USO.md** (tutorial paso a paso)
3. Revisa logs en `logs/trading_bot.log`
4. Usa `!fc26 ayuda` en Discord

---

🎮 **¡Buena suerte con el trading!** 💰
