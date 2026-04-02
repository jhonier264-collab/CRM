import os
import sys
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.services.data_hygiene_service import DataHygieneService

def test_user_delete():
    # load_dotenv is now called at the top level
    db = DatabaseManager()
    service = CRMService(db)
    hygiene = DataHygieneService(db)
    
    print("\n" + "="*50)
    print(" [TEST] USER DELETE (GOOGLE STYLE) ")
    print("="*50)
    
    try:
        # List users (active only)
        users = service.u_repo.list()
        print("\n--- Usuarios Activos ---")
        for u in users:
            print(f"ID: {u.id} | {u.first_name} {u.last_name}")
        
        target_id_str = input("\n>>> Ingrese ID a enviar a la PAPELERA (Enter cancelar): ")
        if not target_id_str: return

        target_id = int(target_id_str)
        
        # 1. SOFT DELETE
        print(f"\n1. Enviando ID {target_id} a la papelera...")
        service.delete_user_complete(target_id)
        print("✅ Movido a la papelera.")

        # 2. SUB-MENU TEST
        while True:
            print(f"\n--- ESTADO DEL USUARIO {target_id} ---")
            print(" 1. Verificar en Papelera")
            print(" 2. Restaurar Usuario")
            print(" 3. Eliminar DEFINITIVAMENTE (Purgar)")
            print(" 0. Salir del Test")
            
            opt = input("\nSeleccione acción: ")
            if opt == '1':
                trash = hygiene.list_trash('users')
                if any(t['id'] == target_id for t in trash):
                    print(f"✅ CONFIRMADO: El usuario {target_id} está en la papelera.")
                else:
                    print(f"❌ ERROR: El usuario no se encuentra en la papelera.")
            
            elif opt == '2':
                hygiene.restore_item('users', target_id)
                print(f"✅ RESTAURADO: El usuario vuelve a estar activo.")
                break
            
            elif opt == '3':
                confirm = input("¿Está TOTALMENTE seguro? No hay vuelta atrás. (s/n): ")
                if confirm.lower() == 's':
                    hygiene.permanent_delete_item('users', target_id)
                    print(f"🔥 PURGADO: El registro ha sido eliminado del disco.")
                break
            elif opt == '0': break

    except Exception as e:
        print(f" >>> Error during user deletion/trash test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_user_delete()
