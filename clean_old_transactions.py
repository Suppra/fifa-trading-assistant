"""
Limpia TODAS las transacciones de prueba de la base de datos
"""
from datetime import datetime, timedelta
from src.database.db_manager import DatabaseManager, Transaction

def clean_old_transactions():
    """Elimina TODAS las transacciones (reset completo)"""
    db = DatabaseManager()
    session = db.SessionLocal()
    
    try:
        # Contar todas las transacciones
        total_count = session.query(Transaction).count()
        
        if total_count == 0:
            print("✅ No hay transacciones que eliminar - Base de datos ya limpia")
            return
        
        print(f"🔍 Encontradas {total_count} transacciones en la base de datos")
        print("⚠️  Se eliminarán TODAS las transacciones para empezar desde cero")
        
        # Eliminar TODAS las transacciones
        session.query(Transaction).delete()
        
        session.commit()
        print(f"✅ Eliminadas {total_count} transacciones")
        print("✅ Base de datos completamente limpia - Listo para empezar!")
        print("\n💡 Ahora cuando compres una carta, aparecerá en el tab 'Vender'")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LIMPIEZA DE TRANSACCIONES ANTIGUAS")
    print("="*60 + "\n")
    clean_old_transactions()
    print()
