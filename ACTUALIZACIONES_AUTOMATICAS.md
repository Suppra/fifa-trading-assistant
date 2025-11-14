# 🤖 Actualizaciones Automáticas en Segundo Plano

## 📋 Resumen

El bot ahora puede actualizar precios de FUTBIN **automáticamente** sin necesidad de tener la aplicación abierta.

## ⏰ Horarios de Actualización

Las actualizaciones se ejecutan automáticamente 3 veces al día:

- **9:00 AM** - Actualización matutina
- **1:00 PM** - Actualización mediodía  
- **10:00 PM** - Actualización nocturna

### 💡 ¿Qué pasa si el PC está apagado?

**No te preocupes!** El sistema tiene 2 mecanismos de respaldo:

1. **Ejecución retrasada**: Si el PC estaba apagado a la hora programada, la tarea se ejecutará **15 minutos después** de encender el PC.

2. **Tarea de inicio**: Hay una tarea adicional que se ejecuta **5 minutos después de iniciar Windows** para verificar si hay actualizaciones pendientes.

**Resultado**: NO perderás ninguna actualización, sin importar cuándo enciendas el PC.

## 📊 Detalles Técnicos

- **Páginas procesadas**: 100 páginas por actualización
- **Jugadores**: ~3000 jugadores con precios reales
- **Duración**: 2-3 horas por actualización
- **Jugadores extintos**: Se marcan automáticamente

---

## 🚀 Método 1: Tareas Programadas de Windows (RECOMENDADO)

### Instalación

1. **Abrir PowerShell como Administrador**
2. **Navegar a la carpeta del bot:**
   ```powershell
   cd C:\Users\Crist\Trader
   ```

3. **Ejecutar el configurador:**
   ```powershell
   python setup_scheduled_tasks.py
   ```

4. **¡Listo!** Las tareas están configuradas y se ejecutarán automáticamente.

### Verificar Tareas

Para ver las tareas configuradas:
```powershell
python setup_scheduled_tasks.py list
```

O abrir el **Programador de Tareas de Windows**:
1. Presionar `Win + R`
2. Escribir: `taskschd.msc`
3. Buscar en: `Biblioteca de Programador de Tareas > FC26TradingBot`

### Desinstalar Tareas

Para eliminar las tareas automáticas:
```powershell
python setup_scheduled_tasks.py remove
```

---

## 🎯 Método 2: Ejecutar Manualmente en Segundo Plano

Si prefieres iniciar el servicio manualmente:

### Windows

**Opción A: Usar archivo BAT**
1. Doble clic en: `start_background_updater.bat`
2. El servicio se iniciará en segundo plano

**Opción B: Línea de comandos**
```powershell
pythonw background_updater.py
```

### Verificar Estado

El servicio guarda logs en:
```
logs\background_updater.log
```

### Detener Servicio

1. Abrir **Administrador de Tareas** (`Ctrl + Shift + Esc`)
2. Buscar proceso `pythonw.exe`
3. Click derecho → **Finalizar tarea**

---

## 📱 Uso con la Aplicación de Escritorio

La aplicación de escritorio también puede actualizar precios manualmente:

1. Abrir la app: `python desktop_app.py`
2. Ir a: **Acciones** → **Actualizar Precios FUTBIN (PC)**
3. Aparecerá una barra de progreso con tiempo estimado

**Nota:** Si las tareas automáticas están configuradas, NO es necesario actualizar manualmente.

---

## 🔍 Logs y Monitoreo

### Ver Logs

**Tareas Programadas:**
```
logs\service.log
```

**Actualizador Manual:**
```
logs\background_updater.log
```

**Aplicación de Escritorio:**
Ver directamente en la pestaña "Registro de Actividad"

### Qué se registra

- ✅ Jugadores actualizados exitosamente
- 🔴 Jugadores marcados como extintos
- ⏱️ Tiempo de ejecución
- ❌ Errores encontrados

---

## ⚙️ Configuración Avanzada

### Cambiar Horarios

Editar `auto_update_prices.py` o `background_updater.py`:

```python
# Cambiar horarios (formato 24 horas)
schedule.every().day.at("09:00").do(update_prices)  # 9 AM
schedule.every().day.at("13:00").do(update_prices)  # 1 PM
schedule.every().day.at("22:00").do(update_prices)  # 10 PM
```

### Cambiar Cantidad de Páginas

Editar el número de páginas en:
- `auto_update_prices.py`
- `background_updater.py`
- `src/desktop_app/main_window.py`

```python
# Cambiar de 100 a otro número
scraper.update_database_prices(db, use_all_futbin=True, max_pages=50)
```

---

## 🆘 Solución de Problemas

### Las tareas no se ejecutan

1. Verificar que las tareas existen:
   ```powershell
   python setup_scheduled_tasks.py list
   ```

2. Verificar en Programador de Tareas que estén **Habilitadas**

3. Reinstalar tareas:
   ```powershell
   python setup_scheduled_tasks.py remove
   python setup_scheduled_tasks.py
   ```

### Error de permisos

Ejecutar PowerShell **como Administrador**

### El proceso consume mucha CPU

Es normal durante las actualizaciones (2-3 horas). Después entra en reposo.

### No aparecen jugadores nuevos

1. Verificar que la actualización se completó en los logs
2. Reiniciar la aplicación de escritorio
3. Click en "Actualizar" en la pestaña de Recomendaciones

---

## 📊 Estadísticas

Después de la primera actualización completa tendrás:

- ✅ ~3000 jugadores en la base de datos
- 💰 Precios reales del mercado PC de FUTBIN
- 🔴 Jugadores extintos marcados
- 📈 Historial de precios para análisis
- 🎯 Recomendaciones de trading precisas

---

## 💡 Recomendaciones

1. **Usar Tareas Programadas** (Método 1) para máxima comodidad
2. **Dejar ejecutar** la primera actualización completa (2-3 horas)
3. **Revisar logs** después de la primera ejecución
4. **No ejecutar** actualizaciones manuales si las automáticas están activas

---

## 🔗 Enlaces Útiles

- **Programador de Tareas**: `Win + R` → `taskschd.msc`
- **Administrador de Tareas**: `Ctrl + Shift + Esc`
- **Logs**: Carpeta `logs/` en el directorio del bot

---

**¡Disfruta del trading automatizado!** ⚽💰
