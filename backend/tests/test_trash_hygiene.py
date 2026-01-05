
import sys
import os
import time
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.services.data_hygiene_service import DataHygieneService
from src.models.models import User

def run_trash_and_hygiene_test():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    hygiene = DataHygieneService(db)
    
    print("\n" + "="*60)
    print(" [TEST] HIGIENE DE DATOS Y PAPELERA (GOOGLE STYLE) ".center(60, "="))
    print("="*60)
    
    try:
        # 1. Crear usuario de prueba
        print("\n1. Creando usuario de prueba...")
        u = User(first_name="Test", last_name="Trashman", rut_nit="TMP-TRASH", status_id=1)
        uid = service.u_repo.insert(u)
        print(f"   ✅ Usuario creado con ID: {uid}")

        # 2. Borrado Lógico (Soft Delete)
        print(f"\n2. Ejecutando Borrado Lógico sobre ID: {uid}...")
        service.u_repo.delete(uid)
        
        # 3. Verificar que NO aparece en la lista activa
        print("\n3. Verificando que el usuario ha desaparecido de la lista activa...")
        active_users = service.u_repo.list()
        if any(user.id == uid for user in active_users):
            print("   ❌ ERROR: El usuario sigue apareciendo en la lista activa.")
        else:
            print("   ✅ ÉXITO: El usuario está oculto de las listas normales.")

        # 4. Verificar presencia en Papelera
        print("\n4. Buscando en la Papelera de Reciclaje...")
        trash = hygiene.list_trash('users')
        if any(t['id'] == uid for t in trash):
            print(f"   ✅ ÉXITO: Usuario encontrado en la papelera.")
        else:
            print("   ❌ ERROR: El usuario no está en la papelera.")

        # 5. Restauración
        print(f"\n5. Restaurando usuario ID: {uid}...")
        hygiene.restore_item('users', uid)
        active_users = service.u_repo.list()
        if any(user.id == uid for user in active_users):
            print("   ✅ ÉXITO: Usuario restaurado correctamente.")
        else:
            print("   ❌ ERROR: Falló la restauración.")

        # 6. Borrado Definitivo (Purga)
        print(f"\n6. Borrando nuevamente y Purgando definitivamente...")
        service.u_repo.delete(uid)
        hygiene.permanent_delete_item('users', uid)
        
        # Verificar que no está ni en activos ni en papelera
        active = service.u_repo.list()
        trash = hygiene.list_trash('users')
        if not any(u.id == uid for u in active) and not any(t['id'] == uid for t in trash):
            print("   ✅ ÉXITO: El usuario ha sido purgado totalmente del sistema.")
        else:
            print("   ❌ ERROR: El registro persiste en alguna tabla.")

    except Exception as e:
        print(f"\n 🔴 ERROR DURANTE EL TEST: {e}")
    finally:
        db.close()
        print("\n" + "="*60)

if __name__ == "__main__":
    run_trash_and_hygiene_test()
