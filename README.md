# EA FC 26 Trading Bot Pro ⚽💰

Bot inteligente de trading para EA FC 26 con ML avanzado, datos reales de FUTBIN y sistema de inventario.

**Created by xSuppra** • Última actualización: Noviembre 2025

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FUTBIN](https://img.shields.io/badge/Data-FUTBIN%20Real-orange)](https://www.futbin.com)

## ✨ Características Principales

### 🎯 Sistema de Trading Inteligente
- **Datos 100% Reales** - Scraping directo desde FUTBIN.com
- **Estrategia Weekend League** - Compra Lun/Mar, Vende Jue/Vie
- **Predicciones ML Avanzadas** - Eventos, SBCs, detección de anomalías
- **Sistema de Inventario** - Tracking multi-carta con profit real

### 🤖 Machine Learning Enhanced
- **Calendario de Eventos** - Weekend League, TOTW, TOTY, TOTS, etc.
- **Análisis de SBCs** - Impacto automático en demanda de jugadores
- **Detección de Anomalías** - Identifica crashes y spikes de precio
- **30+ Features Avanzados** - Volatilidad, momentum, tendencias
- **Ensemble Predictions** - Combina 5 métodos para mayor precisión

### 💻 Interfaz Moderna
- **UI Estilo Robinhood** - Diseño limpio y profesional
- **Actualización Automática** - Sistema inteligente de updates desde FUTBIN
- **Descarga Paralela** - 3 hilos concurrentes para velocidad
- **Splash Screen** - Progreso en tiempo real de actualizaciones

### 📊 Gestión Avanzada
- **Inventario Multi-Carta** - Compra 1-100 copias de la misma carta
- **Profit Tracking** - Seguimiento detallado de ganancias por carta
- **Filtros Inteligentes** - Liga, rating, posición (auto-mapping)
- **Auto-Save** - Guardado automático de configuración

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.8 o superior
- Windows 10/11 (optimizado para Windows)
- 4GB RAM mínimo
- Conexión a Internet

### 1. Clonar Repositorio

```bash
git clone https://github.com/Suppra/fifa-trading-assistant.git
cd fifa-trading-assistant
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Inicializar Base de Datos

```bash
python scripts/setup_database.py
```

### 4. Lanzar Aplicación

```bash
python launcher.py
```

La aplicación automáticamente:
1. Descargará ~900 jugadores de FUTBIN (primera vez)
2. Actualizará precios en tiempo real
3. Iniciará la interfaz de escritorio

## 📱 Modo de Uso

### Primera Ejecución (20-30 minutos)
El splash screen descargará datos iniciales de FUTBIN:
- 30 páginas en paralelo (~900 jugadores)
- Precios PC reales
- Identificación de jugadores extintos
- Configuración de base de datos

### Ejecuciones Siguientes (3-5 minutos)
Actualización incremental:
- Solo actualiza jugadores ya existentes
- Mucho más rápido que descarga completa
- Mantiene datos frescos y precisos

### Actualizaciones Manuales
Desde **Ajustes** → **Actualización de Base de Datos**:
- **Completa**: 50 páginas (~1500 jugadores, ~15 min)
- **Rápida**: Solo existentes (~5 min)

## 🎮 Características Detalladas

### 📈 Sistema de Predicciones ML

#### Eventos Detectados Automáticamente
- **Weekend League**: Todos los viernes → Precios suben
- **TOTW**: Todos los miércoles → Volatilidad alta
- **TOTY**: 12-26 Enero → Mercado en caída
- **TOTS**: 26 Abril - 7 Junio → Precios máximos
- **Black Friday**: 24-28 Noviembre → Crash masivo

#### Análisis de SBCs
```python
# Ejemplo: SBC requiere 84 rated
sbc_impact = 0.6  # 60% de demanda extra
precio_ajustado = 5000 * (1 + 0.6 * 0.15)  # +9% = 5,450 coins
```

#### Detección de Anomalías (Z-Score)
- **Crash** (z < -2.5): ¡Comprar barato!
- **Spike** (z > 2.5): ¡Vender caro!
- **Normal** (|z| < 2.5): Precio estable

### 🛒 Sistema de Inventario

#### Comprar Cartas
1. Tab **Comprar** → Buscar carta
2. Seleccionar cantidad (1-100)
3. Click **🛒 COMPRAR**
4. Ve al juego y compra manualmente

#### Vender Cartas
1. Tab **Vender** → Ver inventario
2. Carta muestra:
   - Precio compra vs actual
   - Ganancia por carta
   - Ganancia total (si múltiples)
3. Click **💰 MARCAR COMO VENDIDO**
4. Ve al juego y vende

#### Profit Indicators
- 🟢 **+10%+**: ¡VENDE AHORA!
- 🟡 **+5-10%**: Buen momento
- 🔵 **+0-5%**: Espera más
- 🔴 **Negativo**: En pérdida

### 📊 Filtros Inteligentes

#### Filtro de Liga
```python
# Mapeo automático UI → DB
"La Liga" → "LaLiga"  # Sin espacio en FUTBIN
"Premier League" → "Premier League"  # Exacto
```

#### Filtro de Rating
- 82-84: Fodder bajo
- 84-86: Fodder medio
- 86-88: Alto rating
- 88+: Elite/Icons

### 🔄 Sistema de Actualizaciones

#### Estrategia Inteligente (update_strategy.py)
1. **Primera vez**: 30 páginas paralelas
2. **Diaria**: Incremental (solo existentes)
3. **Semanal**: Completa (50 páginas)

#### Descarga Paralela
```python
# 3 hilos concurrentes
scraper.get_all_players_parallel(
    max_pages=30,
    num_threads=3,
    progress_callback=actualizar_barra
)
```

## 📁 Arquitectura del Proyecto (MVC)

```
fifa-trading-assistant/
├── app/                          # Aplicación principal
│   ├── models/
│   │   └── database.py           # SQLAlchemy: Player, PriceHistory, Inventory, Transaction
│   ├── views/
│   │   ├── desktop_ui.py         # 🖥️ Interfaz principal Tkinter
│   │   └── splash_screen.py      # ⚡ Pantalla de carga con updates
│   ├── controllers/
│   │   ├── market_controller.py  # 📊 Análisis de mercado
│   │   ├── prediction_controller.py # 🤖 ML con eventos y SBCs
│   │   └── trading_controller.py # 💰 Motor de trading
│   ├── services/
│   │   ├── futbin_service.py     # 🌐 Scraper FUTBIN (paralelo)
│   │   ├── market_service.py     # 📈 Servicio de mercado
│   │   ├── discord_service.py    # 💬 Bot de Discord
│   │   └── price_generator_service.py # 🔧 Generador (testing)
│   └── utils/
│       ├── config_loader.py      # ⚙️ Configuración
│       ├── logger.py             # 📝 Logging
│       ├── auto_save.py          # 💾 Auto-guardado
│       ├── price_alerts.py       # 🔔 Alertas de precio
│       ├── sbc_tracker.py        # 🎯 Tracker de SBCs
│       ├── update_strategy.py    # 🔄 Estrategia de updates
│       └── query_cache.py        # 🚀 Cache de queries
├── scripts/
│   ├── setup_database.py        # Inicializar BD
│   ├── update_prices_pc.py      # Actualizar precios PC
│   ├── configure_discord.py     # Wizard Discord
│   ├── test_futbin.py           # Test scraper
│   └── *.bat                    # Scripts Windows
├── data/
│   ├── trading.db               # 💾 Base de datos SQLite
│   └── update_config.json       # 📊 Estado de actualizaciones
├── docs/
│   ├── DATOS_REALES_CONFIRMACION.md # ✅ Verificación datos reales
│   ├── ML_ENHANCEMENTS.md       # 🤖 Guía sistema ML
│   ├── ESTRATEGIAS_11K.md       # 💰 Trading bajo presupuesto
│   └── GUIA_USO.md              # 📖 Guía completa
├── launcher.py                  # 🚀 PUNTO DE ENTRADA
├── desktop_app.py               # 🖥️ App directa (sin splash)
└── requirements.txt             # 📦 Dependencias
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

## 🎮 Uso Rápido

### Lanzar Aplicación (Recomendado)

```bash
python launcher.py
```

Esto iniciará:
1. **Splash Screen** con actualización de datos FUTBIN
2. **Interfaz Principal** cuando termine la carga

### Lanzar Sin Actualización

```bash
python desktop_app.py
```

Inicia directamente (sin splash screen ni update).

## 📊 Tabs de la Aplicación

### 🛒 Tab Comprar
- Recomendaciones ML basadas en datos reales
- Filtros: Liga, Rating (82-84 recomendado)
- Plan de acción según día de la semana
- Indicador de precio (ganancia vs promedio)
- Selector de cantidad (1-100 cartas)

### 💰 Tab Vender
- Inventario de cartas compradas
- Profit por carta y total
- Indicadores de color según ganancia
- Botón "Marcar como Vendido"

### 🎯 Tab SBCs
- SBCs activos scraped de FUTBIN
- Impacto en mercado de jugadores
- Requisitos detallados (rating, química)

### 📈 Tab Mercado
- Estado actual del mercado
- Gráfico de tendencias (7 días)
- Predicciones ML para mañana
- Análisis de actividad por hora

### 📚 Tab Historial
- Todas las transacciones
- Gráfico de profit semanal
- Filtros por tipo y fecha

### ⚙️ Tab Ajustes
- Configurar presupuesto
- Cambiar tema (claro/oscuro)
- **Actualización Manual DB**
  - Completa: 50 páginas
  - Rápida: Solo existentes
- Configurar Discord (futuro)

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

## 🔧 Stack Tecnológico

### Core
- **Python 3.8+** - Lenguaje principal
- **SQLAlchemy 2.0** - ORM para base de datos
- **SQLite** - Base de datos (built-in, no setup)

### UI & Visualización
- **Tkinter** - Interfaz de escritorio nativa
- **Matplotlib** - Gráficos de tendencias
- **ttk** - Widgets modernos

### Web Scraping
- **Requests** - Cliente HTTP
- **BeautifulSoup4** - Parser HTML
- **lxml** - Parser XML rápido

### Machine Learning
- **Pandas** - Análisis de datos
- **NumPy** - Operaciones numéricas
- **scikit-learn** - Modelos ML
- **Prophet** - Series temporales (opcional)

### Opcional
- **Discord.py** - Bot de Discord
- **Flask** - API REST
- **XGBoost** - ML avanzado

## 📊 Base de Datos (SQLite)

### Tablas Principales

#### `players`
```sql
- id (PK)
- player_id (FUTBIN ID único)
- name, rating, position
- league, club, nationality
- is_extinct (bool)
```

#### `price_history`
```sql
- id (PK)
- player_id (FK)
- price (int)
- timestamp (datetime)
- supply, demand
```

#### `inventory` 🆕
```sql
- id (PK)
- player_id (FK)
- player_name
- purchase_price, purchase_date
- quantity (1-100)
- status ('owned', 'listed', 'sold')
- sell_price, sell_date
- profit, notes
```

#### `transactions` (legacy)
```sql
- id (PK)
- player_id (FK)
- transaction_type ('buy', 'sell')
- price, profit
- timestamp, status
```

## 🌐 Integración con FUTBIN

### URLs Utilizadas
```python
# Base
https://www.futbin.com/26

# Listado de jugadores
/players?page=1&minrating=82&maxrating=84

# Jugador específico
/player/{player_id}/{player_name}

# SBCs activos
/squad-building-challenges

# API de precios (no oficial)
/playerPrices?player=ID1,ID2,ID3
```

### Extracción de Precios PC
```python
# Método 1: Regex en texto
match = re.search(r'([\d,]+)\s+on\s+PC', html_text)

# Método 2: Atributo HTML
price_elem.get('data-price-pc')
```

### Rate Limiting
- 1 segundo entre requests (configurado)
- 3 hilos concurrentes en descarga paralela
- Retry automático en error 429 (Too Many Requests)

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

## 🐛 Solución de Problemas

### Error: ModuleNotFoundError

```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar desde raíz del proyecto
cd fifa-trading-assistant
python launcher.py
```

### Base de Datos Vacía

```bash
# Primera vez: Inicializar
python scripts/setup_database.py

# Luego: Lanzar app (descargará datos automáticamente)
python launcher.py
```

### Actualización Muy Lenta

La primera actualización tarda ~20-30 minutos (descarga completa).
Actualizaciones siguientes: 3-5 minutos (incremental).

Para forzar update rápido:
- Ajustes → **Actualización Rápida** (solo existentes)

### Liga Filter Sin Resultados

852 de 871 jugadores tienen `league=NULL` en FUTBIN.
Esto es normal - FUTBIN no siempre captura la liga.

Filtrar por rating funciona correctamente.

### Discord Bot (Opcional)

```bash
# Configurar .env
DISCORD_BOT_TOKEN=tu_token
DISCORD_CHANNEL_ID=tu_canal_id

# Habilitar MESSAGE CONTENT INTENT en Discord Developer Portal
# Consultar docs/DISCORD_SETUP.txt
```

## 📝 Scripts Útiles

### Actualizar Precios Manualmente

```bash
# Actualización completa (lenta)
python scripts/update_prices_pc.py

# Solo jugadores existentes (rápida)
python scripts/update_prices.py
```

### Limpiar Base de Datos

```bash
# Limpiar transacciones antiguas
python scripts/clean_old_transactions.py

# Resetear base de datos completa
rm data/trading.db
python scripts/setup_database.py
```

### Tests de Scraping

```bash
# Test FUTBIN scraper
python scripts/test_futbin.py

# Test SBC scraper
python scripts/test_sbc_scraper.py

# Test sistema de extintos
python scripts/test_extinct_system.py
```

## 📚 Documentación Avanzada

### Guías Completas
- **docs/ML_ENHANCEMENTS.md** - Sistema ML detallado
- **docs/DATOS_REALES_CONFIRMACION.md** - Verificación datos reales
- **docs/ESTRATEGIAS_11K.md** - Trading con bajo presupuesto
- **docs/GUIA_USO.md** - Guía paso a paso

### Configuración
```yaml
# config.yaml (ejemplo)
prediction:
  model_type: enhanced          # 'simple', 'prophet', 'enhanced'
  enable_sbc_features: true
  enable_event_features: true
  anomaly_threshold: 2.5
  training_window_days: 30

market_analysis:
  price_check_interval: 5       # minutos
  min_rating: 82
  top_players_count: 100
```

## 🚀 Roadmap / Mejoras Futuras

### En Desarrollo
- [ ] Alertas de precio en tiempo real
- [ ] Notificaciones push (Windows)
- [ ] Dashboard web (Flask)
- [ ] Exportar reportes PDF/Excel

### Planificado
- [ ] Deep Learning con LSTM
- [ ] Auto-trading (simulado)
- [ ] Análisis de química de equipos
- [ ] Integración con FUT Companion App (API no oficial)

### Ideas
- [ ] Comparación de precios PS/Xbox/PC
- [ ] Tracking de meta players
- [ ] Análisis de popularidad de cartas
- [ ] Sistema de recomendaciones personalizadas

## 🤝 Contribuir

Las contribuciones son bienvenidas! Para cambios importantes:

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Áreas de Mejora
- Optimización de scraping
- Nuevos modelos ML
- Mejor UI/UX
- Tests unitarios
- Documentación

## ⚠️ Disclaimer Legal

**Este proyecto es solo para fines educativos.**

- ❌ NO es un bot automatizado de trading
- ❌ NO interactúa directamente con EA servers
- ✅ Solo proporciona análisis y recomendaciones
- ✅ Requiere intervención manual del usuario

El uso de bots automatizados puede violar los términos de servicio de EA Sports.
**Usa bajo tu propio riesgo.**

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**xSuppra**
- GitHub: [@Suppra](https://github.com/Suppra)
- Email: cristianfwc@gmail.com
- Proyecto: [fifa-trading-assistant](https://github.com/Suppra/fifa-trading-assistant)

## 🙏 Agradecimientos

- **FUTBIN** - Por proporcionar datos públicos de precios
- **EA Sports** - Por crear EA FC 26
- **Comunidad Python** - Por las excelentes librerías

## ⭐ Apoya el Proyecto

Si este proyecto te ha ayudado:

1. ⭐ Dale una estrella en GitHub
2. 🍴 Fork el proyecto
3. 📢 Comparte con otros traders
4. 💡 Sugiere mejoras en Issues

---

**Última actualización**: Noviembre 2025 • **Versión**: 2.0 Enhanced ML

Desarrollado con ❤️ por **xSuppra**
