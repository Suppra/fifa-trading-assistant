# 📊 Sistema de Precios FUTBIN - Documentación Completa

## ✅ Sistema Actualizado

El bot ahora usa **FUTBIN** exclusivamente para precios reales de PC.

---

## 🚀 Inicio Rápido

### 1. Actualización Manual (desde UI)
```bash
python desktop_app.py
```
→ Menú: **Acciones → Actualizar Precios FUTBIN (PC)**

### 2. Actualización Manual (consola)
```bash
python update_prices_pc.py
```

### 3. Auto-Actualización (cada hora)
```bash
python auto_update_prices.py
```

---

## 📁 Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `src/data_collection/futbin_scraper.py` | Scraper FUTBIN optimizado para PC |
| `auto_update_prices.py` | Actualización automática cada hora |
| `update_prices_pc.py` | Script de actualización manual |
| `test_futbin.py` | Test del scraper |

---

## ✨ Características

- ✅ **100+ jugadores** populares incluidos
- ✅ Precios reales de **PC únicamente**
- ✅ Rate limiting (2 seg/jugador)
- ✅ Auto-actualización cada hora
- ✅ Sin login requerido
- ✅ Integrado en UI principal

---

## 📊 Jugadores Incluidos

**Top Tier:** Ronaldo, Messi, Mbappé, Haaland, De Bruyne...  
**High Rating:** Rodri, Bruno, Foden, Kane, Son...  
**Budget:** Gnabry, Memphis, Nico Williams, Ferran Torres...  
**Affordable:** Martinelli, Garnacho, Musiala, Wirtz...

---

## ⚙️ Configuración

### Cambiar frecuencia de actualización:
Edita `auto_update_prices.py`:
```python
schedule.every(1).hours.do(update_prices)  # Cambiar '1' por lo que quieras
```

### Agregar más jugadores:
Edita `futbin_scraper.py` → `get_popular_players()`:
```python
player_names = [
    "Tu Jugador Aquí",
    # ...
]
```

---

## 🔧 Troubleshooting

**Error: "No se encontró jugador"**  
→ Verifica ortografía (FUTBIN usa nombres completos)

**Error: "Timeout"**  
→ Verifica internet o espera 5 minutos

**0 jugadores actualizados**  
→ Ejecuta primero: `python setup_database.py`

---

## 📈 Resultados Esperados

### Test Simple:
```bash
python test_futbin.py
```
```
✅ ÉXITO!
  Jugador: Lionel Messi
  Rating: 88
  Precio PC: 830,000 coins
```

### Actualización Completa:
```bash
python update_prices_pc.py
```
```
✅ Actualización completa: 13/19 jugadores
```

---

## 🎯 Próximos Pasos

1. ✅ Ejecutar primera actualización
2. ✅ Iniciar auto-actualizador en background
3. ✅ Usar `desktop_app.py` para trading
4. ✅ Verificar recomendaciones actualizadas

---

**📝 Nota:** Archivos eliminados del proyecto:
- ❌ `ea_webapp_scraper.py` (problemas con Selenium)
- ❌ `modern_ui.py` (errores de sintaxis)
- ❌ Tests temporales de FUTBIN
