# 🎮 EA FC 26 Trading Bot - Guía de Nuevas Funciones

## 📊 Presupuesto Dinámico

### ¿Qué es?
El bot ahora se adapta automáticamente a tu presupuesto actual. Ya no estás limitado a las configuraciones de 11k coins - el bot ajusta sus estrategias según cuántas monedas tengas.

### Niveles de Presupuesto

#### 🥉 BAJO (0 - 20,000 monedas)
- **Estrategias**: Fodder Flipping, Snipe Deals, Mass Bidding
- **Cartas objetivo**: Rating 82-84
- **Precio máximo**: ~15k por carta
- **Inversión por carta**: Hasta 45% de tu presupuesto
- **Cartas simultáneas**: 3
- **Ganancia mínima**: 10%

#### 🥈 MEDIO (20,000 - 50,000 monedas)
- **Estrategias**: Position Trading, Special Cards, Meta Players
- **Cartas objetivo**: Rating 84-86
- **Precio máximo**: ~35k por carta
- **Inversión por carta**: Hasta 35% de tu presupuesto
- **Cartas simultáneas**: 5
- **Ganancia mínima**: 8%

#### 🥇 ALTO (50,000 - 100,000 monedas)
- **Estrategias**: Special Cards, Icons, Investment
- **Cartas objetivo**: Rating 86-88
- **Precio máximo**: ~70k por carta
- **Inversión por carta**: Hasta 30% de tu presupuesto
- **Cartas simultáneas**: 7
- **Ganancia mínima**: 6%

#### 💎 ELITE (100,000+ monedas)
- **Estrategias**: Icons, High-End Trading, Market Manipulation
- **Cartas objetivo**: Rating 88+
- **Precio máximo**: 50% de tu presupuesto
- **Inversión por carta**: Hasta 25% de tu presupuesto
- **Cartas simultáneas**: 10
- **Ganancia mínima**: 5%

### Cómo Actualizar tu Presupuesto

#### Opción 1: App de Escritorio
1. Abre `desktop_app.py`
2. Click en **Archivo > Configurar Presupuesto**
3. Ingresa tu nuevo presupuesto
4. ¡Listo! Las estrategias se ajustan automáticamente

#### Opción 2: Discord
```
!fc26 presupuesto 50000
```

#### Opción 3: Archivo de Configuración
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

## 🪟 App de Escritorio Windows

### Instalación
```bash
python desktop_app.py
```

### Características

#### 📊 Panel Principal
- **Presupuesto en tiempo real**: Muestra tu presupuesto actual y nivel
- **Estado del bot**: Ver si está activo o detenido
- **Botón de inicio/parada**: Controla el bot con un click

#### 🛒 Pestaña de Recomendaciones
- Lista visual de mejores compras
- Filtrado por estrategia
- Información detallada de cada carta:
  - Precio actual
  - Ganancia potencial
  - Rating y posición
  - Nivel de confianza
  - Tendencia del mercado

#### 💰 Pestaña de Ventas
- Cartas que posees listas para vender
- Cálculo automático de ganancias
- Recomendación de cuándo vender

#### 📈 Estado del Mercado
- **Indicador de hora óptima**: El bot te dice si es buen momento para comprar/vender según la hora
- **Estrategias por día**: Consejos específicos para cada día de la semana
- **Weekend League**: Alertas especiales viernes-domingo

#### 📊 Historial
- Todas tus transacciones
- Ganancia total acumulada
- Estadísticas de trading

#### 💬 Discord
- Configuración completa del bot de Discord
- Instrucciones paso a paso
- Test de conexión

#### 📋 Registro de Actividad
- Log en tiempo real de todas las acciones
- Errores y alertas
- Oportunidades detectadas

### Menús

#### Archivo
- **Configurar Presupuesto**: Actualiza tu presupuesto actual
- **Configurar Discord**: Acceso rápido a configuración de Discord
- **Salir**: Cierra la aplicación

#### Acciones
- **Actualizar Precios**: Obtiene los últimos precios de FUTBIN
- **Ver Recomendaciones**: Genera recomendaciones frescas
- **Registrar Compra**: Registra una compra que hiciste manualmente
- **Registrar Venta**: Registra una venta

#### Ayuda
- **Guía de Uso**: Abre GUIA_USO.md
- **Estrategias 11K**: Abre ESTRATEGIAS_11K.md
- **Acerca de**: Información del bot

## 💬 Integración con Discord

### Configuración Inicial

#### Paso 1: Crear Bot de Discord
1. Ve a https://discord.com/developers/applications
2. Click en **New Application**
3. Dale un nombre (ej: "EA FC 26 Trading Bot")
4. Ve a la sección **Bot**
5. Click en **Add Bot**
6. Copia el **TOKEN** (guárdalo, lo necesitarás)

#### Paso 2: Configurar Permisos
1. En la sección **Bot**, habilita:
   - ✅ **MESSAGE CONTENT INTENT**
   - ✅ **SERVER MEMBERS INTENT**
2. Ve a **OAuth2 > URL Generator**
3. Selecciona scopes:
   - ✅ **bot**
4. Selecciona permisos:
   - ✅ **View Channels**
   - ✅ **Send Messages**
   - ✅ **Embed Links**
   - ✅ **Attach Files**
   - ✅ **Read Message History**

#### Paso 3: Invitar Bot a tu Servidor
1. Copia la URL generada
2. Pégala en tu navegador
3. Selecciona tu servidor
4. Autoriza el bot

#### Paso 4: Obtener ID del Canal
1. En Discord, activa **Modo Desarrollador**:
   - Settings > App Settings > Advanced > Developer Mode
2. Click derecho en el canal donde quieres recibir notificaciones
3. Click en **Copy ID**

#### Paso 5: Configurar el Bot
1. Edita `.env`:
```env
DISCORD_BOT_TOKEN=tu_token_aquí
DISCORD_CHANNEL_ID=tu_canal_id_aquí
DISCORD_DAILY_REPORT_HOUR=9
```

O usa la app de escritorio:
1. Ve a pestaña **Discord**
2. Pega el TOKEN
3. Pega el CHANNEL ID
4. Click en **Guardar Configuración**
5. Click en **Conectar Discord**

### Iniciar Bot de Discord

#### Opción 1: Integrado con App de Escritorio
```bash
python desktop_app.py
```
- Ve a pestaña Discord
- Click en "Conectar Discord"

#### Opción 2: Standalone
```bash
python discord_bot.py
```

### Comandos de Discord

#### !fc26 status
Muestra el estado actual del bot:
- Presupuesto actual
- Nivel (LOW/MEDIUM/HIGH/ELITE)
- Precio máximo de compra
- Estrategias activas

#### !fc26 recomendaciones
Envía las mejores recomendaciones de compra actuales:
- Top 5 cartas para comprar
- Precios y ganancias potenciales
- Nivel de confianza
- Estrategia recomendada
- Tendencia del mercado

#### !fc26 vender
Muestra las cartas que deberías vender:
- Cartas en tu inventario
- Precio de compra vs actual
- Ganancia/pérdida
- Recomendación de acción

#### !fc26 presupuesto [cantidad]
Actualiza tu presupuesto:
```
!fc26 presupuesto 50000
```
El bot automáticamente:
- Actualiza el presupuesto
- Cambia de nivel si corresponde
- Reconfigura estrategias
- Envía nuevas recomendaciones adaptadas

#### !fc26 ayuda
Muestra todos los comandos disponibles.

### Notificaciones Automáticas

#### Reporte Diario (9:00 AM por defecto)
El bot envía automáticamente:
- Estado del mercado
- Mejores oportunidades del día
- Estrategia recomendada según día/hora
- Condiciones especiales (Weekend League, etc.)

#### Alertas en Tiempo Real
El bot te notifica cuando:
- 🔥 **Oportunidad excepcional**: Ganancia potencial >20%
- ⚠️ **Precio cayendo**: Una carta que tienes está perdiendo valor
- 📈 **Buen momento para vender**: Una carta alcanzó precio objetivo
- ⏰ **Cambio de hora pico**: Entrando/saliendo de horas con mucha actividad

## ⏰ Manejo de Fecha y Hora

### Estrategias según Hora del Día

El bot conoce la hora actual y ajusta sus recomendaciones:

#### 🌙 Madrugada (1:00 - 4:00 AM)
```
ESTRATEGIA: Sniping agresivo
RAZÓN: Menos competencia
ACCIÓN: Busca gangas y cartas mal preciadas
RIESGO: Bajo
```

#### 🌅 Mañana (6:00 - 9:00 AM)
```
ESTRATEGIA: Compra tranquila
RAZÓN: Mercado en calma
ACCIÓN: Prepara inversiones para la tarde
RIESGO: Bajo-Medio
```

#### ☀️ Tarde (12:00 - 5:00 PM)
```
ESTRATEGIA: Trading general
RAZÓN: Actividad moderada
ACCIÓN: Monitorea tendencias y ajusta posiciones
RIESGO: Medio
```

#### 🔥 Hora Pico (6:00 - 9:00 PM)
```
ESTRATEGIA: VENDER
RAZÓN: Mucha actividad y demanda
ACCIÓN: Vende tus cartas, evita comprar
RIESGO: Alto (precios inflados)
```

#### 🌃 Noche (9:00 PM - 1:00 AM)
```
ESTRATEGIA: Mixta
RAZÓN: Actividad descendiendo
ACCIÓN: Oportunidades variadas
RIESGO: Medio
```

### Estrategias según Día de la Semana

#### Lunes - Jueves
- Mercado estable
- Mejores días para inversiones a mediano plazo
- Precios normales

#### ⚡ Viernes (especialmente después de 6 PM)
```
🔴 ALERTA WEEKEND LEAGUE
ESTRATEGIA: NO COMPRAR
RAZÓN: Precios subiendo por demanda de WL
ACCIÓN: Vende cartas meta si las tienes
```

#### Sábado
```
📈 PICO DE PRECIOS
ESTRATEGIA: VENDER
RAZÓN: Máximos precios de la semana
ACCIÓN: Vende TODO lo que puedas
```

#### 💎 Domingo (especialmente tarde 8-11 PM)
```
🟢 MEJOR MOMENTO PARA COMPRAR
ESTRATEGIA: COMPRA AGRESIVA
RAZÓN: Jugadores vendiendo después de WL
ACCIÓN: Precios 15-30% más bajos, compra para la semana
```

### Eventos Especiales

El bot detecta automáticamente:
- **Team of the Week (TOTW)**: Miércoles 6 PM
- **Promos nuevas**: Viernes 6 PM
- **Squad Building Challenges (SBC)**: Subidas de fodder
- **Icon SBCs**: Demanda de cartas específicas

## 🚀 Inicio Rápido

### Opción 1: App de Escritorio (Recomendado)
```bash
# Instala dependencias (solo primera vez)
pip install discord.py

# Inicia la app
python desktop_app.py
```

### Opción 2: Discord Bot Solo
```bash
# Configura .env primero (ver arriba)
python discord_bot.py
```

### Opción 3: Todo Integrado
```bash
# Start script actualizado
python start.py
```
Ahora incluye opciones para:
- Dashboard web (puerto 5000)
- App de escritorio
- Discord bot
- CLI tradicional

## 💡 Tips de Uso

### Máxima Eficiencia
1. **Usa la app de escritorio como interfaz principal**
   - Más visual y fácil de usar
   - Todas las funciones en un solo lugar
   
2. **Conecta Discord para notificaciones**
   - No te pierdas oportunidades
   - Recibe alertas en tu móvil (app de Discord)
   
3. **Actualiza tu presupuesto regularmente**
   - Cada vez que hagas profit
   - El bot se adapta automáticamente
   
4. **Presta atención a las horas**
   - El bot te dirá cuándo comprar/vender
   - Sigue las recomendaciones de horario

### Flujo de Trabajo Recomendado

#### Mañana (9:00 AM)
1. Abre la app de escritorio
2. Revisa el reporte diario (Discord o app)
3. Actualiza tu presupuesto si hiciste ventas
4. Revisa recomendaciones adaptadas a tu nuevo presupuesto

#### Tarde (12:00 - 5:00 PM)
1. Monitorea oportunidades
2. Ejecuta compras recomendadas en el juego
3. Registra compras en la app

#### Noche (8:00 - 11:00 PM)
1. Revisa qué vender
2. Lista cartas en el mercado
3. Registra ventas completadas
4. Actualiza presupuesto

#### Domingo Noche
**¡MOMENTO CLAVE!**
1. Presupuesto al máximo
2. Compra agresivamente (precios bajos)
3. Prepara inventario para la semana

## 🆘 Solución de Problemas

### "Discord bot no se conecta"
1. Verifica que el token sea correcto
2. Asegúrate de que MESSAGE CONTENT INTENT esté habilitado
3. Verifica que el bot esté en tu servidor
4. Prueba con `!fc26 ayuda` en Discord

### "App de escritorio no abre"
1. Verifica que Python esté instalado: `python --version`
2. Instala dependencias: `pip install -r requirements.txt`
3. Revisa el log en consola para errores específicos

### "Recomendaciones no se adaptan a mi presupuesto"
1. Verifica `budget_config.json`
2. Actualiza presupuesto manualmente
3. Reinicia la app

### "No recibo alertas de Discord"
1. Verifica que el bot tenga permisos en el canal
2. Revisa DISCORD_CHANNEL_ID en .env
3. El bot debe estar "Conectado" (estado verde)

## 📞 Soporte

Si tienes problemas:
1. Revisa esta guía completa
2. Verifica logs en `logs/trading_bot.log`
3. Revisa la consola de la app de escritorio
4. Usa `!fc26 ayuda` en Discord para ver comandos
