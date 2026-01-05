
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User

def test_reciprocal_relations():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*60)
    print(" [TEST] RELACIONES RECÍPROCAS (GOOGLE STYLE) ".center(60, "="))
    print("="*60)
    
    try:
        # 1. Preparar Datos Maestros (Relación Padre-Hijo)
        print("\n1. Verificando Tipos de Relación...")
        # Asegurarnos de que existe una relación de prueba
        res = db.execute_query("SELECT id FROM user_relation_types WHERE name = 'Padre' OR name = 'Test Relation'")
        if not res:
            service.add_user_relation_type("Test Padre", "Test Hijo")
            rel_type = db.execute_query("SELECT id FROM user_relation_types WHERE name = 'Test Padre'")[0]['id']
        else:
            rel_type = res[0]['id']
        
        # 2. Crear dos usuarios
        print("\n2. Creando Personas para el vínculo...")
        u1_id = service.u_repo.insert(User(first_name="Persona", last_name="A", status_id=1))
        u2_id = service.u_repo.insert(User(first_name="Persona", last_name="B", status_id=1))
        print(f"   ✅ Creados ID {u1_id} y ID {u2_id}")

        # 3. Vincular (Recíproco)
        print("\n3. Creando vínculo: A es 'Padre' de B...")
        service.link_users(u1_id, u2_id, rel_type)
        
        # 4. Validar Búsqueda
        print("\n4. Validando relación en la DB...")
        relations = db.execute_query("SELECT * FROM user_user_relations WHERE from_user_id = %s AND to_user_id = %s", (u1_id, u2_id))
        if relations:
            print(f"   ✅ ÉXITO: Vínculo encontrado.")
        else:
            print("   ❌ ERROR: Vínculo no registrado.")

        # 5. Limpieza
        print("\n5. Limpiando datos de prueba...")
        db.execute_query("DELETE FROM user_user_relations WHERE from_user_id = %s", (u1_id,), commit=True, is_select=False)
        db.execute_query("DELETE FROM users WHERE id IN (%s, %s)", (u1_id, u2_id), commit=True, is_select=False)
        print("   ✅ Limpieza completada.")

    except Exception as e:
        print(f"\n 🔴 ERROR DURANTE EL TEST: {e}")
    finally:
        db.close()
        print("\n" + "="*60)

if __name__ == "__main__":
    test_reciprocal_relations()
