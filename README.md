# EA FC 26 Trading Bot ⚽💰

Bot inteligente de trading para EA FC 26 (FIFA) con interfaz moderna, integración Discord y predicciones ML.

## 🚀 Características Principales

- ✨ **Interfaz de Escritorio Moderna** - UI estilo Robinhood con diseño limpio
- 📊 **Análisis de Mercado en Tiempo Real** - Tracking de 12+ SBCs activos de FUTBIN
- 🤖 **Predicciones ML** - Machine Learning para predecir movimientos de precios
- 💬 **Integración Discord** - Notificaciones y comandos en Discord
- 📈 **Auto-Updates** - Actualización automática de SBCs diariamente a las 13:20
- 💾 **Auto-Save** - Guardado automático de configuración y presupuesto
- 🎯 **Estrategias de Trading** - Sniping, Mass Bidding, Fodder Flipping, SBC Trading

## 📁 Estructura del Proyecto (MVC Architecture)

```
fifa-trading-assistant/
├── app/                          # Aplicación principal (MVC)
│   ├── __init__.py
│   ├── models/                   # Modelos de datos (Database)
│   │   ├── __init__.py
│   │   └── database.py           # ORM con SQLAlchemy
│   ├── views/                    # Interfaces de usuario
│   │   ├── __init__.py
│   │   └── desktop_ui.py         # Tkinter Desktop App
│   ├── controllers/              # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── market_controller.py  # Análisis de mercado
│   │   ├── prediction_controller.py # Predicciones ML
│   │   └── trading_controller.py # Motor de trading
│   ├── services/                 # Servicios externos
│   │   ├── __init__.py
│   │   ├── futbin_service.py     # Scraper de FUTBIN
│   │   ├── market_service.py     # Servicio de mercado
│   │   ├── discord_service.py    # Bot de Discord
│   │   ├── dashboard_api.py      # API REST (Flask)
│   │   └── price_generator_service.py # Generador de precios
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── config_loader.py      # Configuración
│       ├── logger.py             # Logging
│       ├── auto_save.py          # Auto-guardado
│       ├── price_alerts.py       # Alertas de precio
│       ├── sbc_tracker.py        # Tracker de SBCs
│       └── query_cache.py        # Cache de queries
├── config/                       # Archivos de configuración
│   ├── .env.example             # Variables de entorno
│   └── budget_config.json       # Configuración de presupuesto
├── docs/                         # Documentación
│   ├── ACTUALIZACIONES_AUTOMATICAS.md
│   ├── DATOS_REALES_README.md
│   ├── DISCORD_SETUP.txt
│   ├── ESTRATEGIAS_11K.md
│   ├── GUIA_USO.md
│   ├── IMPLEMENTACION_FEATURES.md
│   ├── MODERN_UI_README.md
│   ├── NUEVAS_FUNCIONES.md
│   ├── README_v2.md
│   ├── RESUMEN_FINAL.md
│   └── RESUMEN_IMPLEMENTACION.md
├── scripts/                      # Scripts auxiliares
│   ├── setup_database.py        # Inicializar BD
│   ├── setup_discord_service.py # Configurar Discord
│   ├── configure_discord.py     # Wizard de Discord
│   ├── update_prices*.py        # Actualizar precios
│   ├── migrate_*.py             # Migraciones
│   ├── clean_*.py               # Limpieza
│   ├── test_*.py                # Tests
│   └── *.bat                    # Scripts Windows
├── data/                         # Datos de la aplicación
│   └── trading.db               # Base de datos SQLite
├── logs/                         # Logs de la aplicación
├── models/                       # Modelos ML entrenados
├── reports/                      # Reportes generados
├── desktop_app.py               # 🚀 PUNTO DE ENTRADA PRINCIPAL
├── discord_bot.py               # Ejecutar solo Discord bot
├── launcher.py                  # Launcher interactivo
├── requirements.txt             # Dependencias Python
└── .gitignore                   # Archivos ignorados

```

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Suppra/fifa-trading-assistant.git
cd fifa-trading-assistant
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `config/.env.example` a `.env` en la raíz del proyecto:

```bash
copy config\.env.example .env
```

Edita `.env` y añade tus credenciales de Discord:

```env
DISCORD_BOT_TOKEN=tu_token_aqui
DISCORD_CHANNEL_ID=tu_canal_id_aqui
```

### 4. Inicializar base de datos

```bash
python scripts/setup_database.py
```

## 🎮 Uso

### Opción 1: Aplicación de Escritorio (Recomendada)

```bash
python desktop_app.py
```

Esta es la forma principal de usar el bot. Incluye:
- Dashboard con métricas en tiempo real
- Navegación lateral moderna
- Tabs: Comprar, Vender, SBCs, Mercado, Historial, ML Predicciones, Discord, Ajustes
- Auto-actualización de SBCs diariamente a las 13:20
- Integración Discord desde la UI

### Opción 2: Launcher Interactivo

```bash
python launcher.py
```

Menú interactivo con opciones:
1. Iniciar App de Escritorio
2. Iniciar Trading Bot (CLI)
3. Iniciar Bot de Discord
4. Ver Estado del Sistema
5. Configurar Discord
6. Salir

### Opción 3: Solo Discord Bot

```bash
python discord_bot.py
```

Inicia solo el bot de Discord para recibir notificaciones.

## 📱 Comandos de Discord

Una vez configurado, usa estos comandos en tu servidor:

```
!fc26 ayuda              - Ver todos los comandos disponibles
!fc26 status             - Ver estado del bot y conexión
!fc26 recomendaciones    - Mejores oportunidades de compra
!fc26 vender             - Cartas en inventario para vender
!fc26 presupuesto 50000  - Actualizar presupuesto disponible
!fc26 sbc                - Ver SBCs activos
!fc26 prediccion <jugador> - Predicción de precio para jugador
```

El bot enviará automáticamente recomendaciones a las **9:00 AM** cada día.

## 🔧 Configuración

### Configurar Discord

Ejecuta el asistente de configuración:

```bash
python scripts/configure_discord.py
```

O consulta `docs/DISCORD_SETUP.txt` para instrucciones detalladas.

### Ajustar Presupuesto

Desde la app de escritorio:
1. Ve a la pestaña **Ajustes**
2. Modifica el presupuesto total
3. Click en **Guardar Presupuesto**

O edita `config/budget_config.json` manualmente.

## 📊 Características Técnicas

### Arquitectura MVC

- **Models**: SQLAlchemy ORM con modelos Player, Transaction, PriceHistory
- **Views**: Tkinter con diseño moderno tipo Robinhood
- **Controllers**: Lógica de negocio separada (Market, Prediction, Trading)
- **Services**: Servicios externos (FUTBIN, Discord, API)
- **Utils**: Utilidades reutilizables (Config, Logger, Cache)

### Stack Tecnológico

- **Python 3.8+**
- **SQLAlchemy** - ORM para base de datos
- **Tkinter** - Interfaz de escritorio
- **Discord.py** - Bot de Discord
- **BeautifulSoup4** - Web scraping
- **Pandas** - Análisis de datos
- **Flask** - API REST (opcional)
- **Matplotlib** - Gráficos y visualizaciones

### SBC Tracker

- URL: `https://www.futbin.com/26/squad-building-challenges`
- Scraper HTML con selector: `div.sbc-card-wrapper`
- Extracción de 12+ SBCs en tiempo real
- Auto-actualización diaria a las 13:20 (hora de actualización de EA)
- Polling cada 60 segundos para verificar horario
- Parser robusto de requisitos (rating, química, jugadores)

## 📝 Scripts Útiles

### Actualizar Precios de Jugadores

```bash
python scripts/update_prices_pc.py
```

### Limpiar Base de Datos

```bash
python scripts/clean_old_transactions.py
```

### Migrar Base de Datos

```bash
python scripts/migrate_db_add_extinct.py
```

### Tests de Scraping

```bash
python scripts/test_sbc_scraper.py
python scripts/test_futbin.py
```

## 🐛 Troubleshooting

### Error: "No module named 'app'"

Asegúrate de estar ejecutando desde la raíz del proyecto:

```bash
cd fifa-trading-assistant
python desktop_app.py
```

### Discord Bot no conecta

1. Verifica que `.env` esté en la raíz (no en `config/`)
2. Comprueba que `DISCORD_BOT_TOKEN` sea válido
3. Habilita **MESSAGE CONTENT INTENT** en Discord Developer Portal
4. Consulta `docs/DISCORD_SETUP.txt`

### SBCs no se actualizan

- Los SBCs se actualizan automáticamente a las **13:20** (1:20 PM)
- También se cargan al iniciar la aplicación
- Verifica logs en `logs/trading_bot.log`

### Base de datos corrupta

```bash
# Eliminar BD antigua
rm data/trading.db

# Crear nueva
python scripts/setup_database.py
```

## 📚 Documentación Adicional

Consulta la carpeta `docs/` para documentación detallada:

- **GUIA_USO.md** - Guía completa de uso
- **DISCORD_SETUP.txt** - Configuración paso a paso de Discord
- **ESTRATEGIAS_11K.md** - Estrategias de trading con 11K coins
- **MODERN_UI_README.md** - Detalles de la interfaz moderna
- **IMPLEMENTACION_FEATURES.md** - Features implementadas

## 🤝 Contribuir

Pull requests son bienvenidos. Para cambios mayores, abre un issue primero para discutir los cambios propuestos.

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.

## ⚠️ Disclaimer

Este bot es solo para fines educativos. El uso de bots puede violar los términos de servicio de EA Sports. Usa bajo tu propio riesgo.

## 👤 Autor

**Suppra**
- GitHub: [@Suppra](https://github.com/Suppra)
- Email: cristianfwc@gmail.com

---

⭐ Si te gusta este proyecto, dale una estrella en GitHub!
