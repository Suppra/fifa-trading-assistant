"""
Migración de base de datos: Agregar columna is_extinct
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def migrate_database():
    """Agrega la columna is_extinct a la tabla players"""
    
    print("\n" + "="*70)
    print(" MIGRACIÓN DE BASE DE DATOS ".center(70))
    print("="*70)
    print("\n📊 Agregando columna 'is_extinct' a tabla 'players'\n")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('data/trading_bot.db')
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(players)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_extinct' in columns:
            print("✅ La columna 'is_extinct' ya existe")
        else:
            # Agregar la nueva columna
            cursor.execute("""
                ALTER TABLE players 
                ADD COLUMN is_extinct BOOLEAN DEFAULT 0
            """)
            conn.commit()
            print("✅ Columna 'is_extinct' agregada correctamente")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM players")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE is_extinct = 1")
        extinct = cursor.fetchone()[0]
        
        print(f"\n📈 Estadísticas:")
        print(f"   Total jugadores: {total}")
        print(f"   Jugadores extintos: {extinct}")
        print(f"   Jugadores con mercado: {total - extinct}")
        
        conn.close()
        
        print("\n" + "="*70)
        print(" ✅ MIGRACIÓN COMPLETADA ".center(70))
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error en migración: {e}\n")
        raise

if __name__ == "__main__":
    migrate_database()
