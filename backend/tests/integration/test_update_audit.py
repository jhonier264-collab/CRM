import os
import sys
import logging
import time
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))
from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User, Email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_update_audit():
    db = DatabaseManager()
    service = CRMService(db)
    
    try:
        print("\n--- TEST DE ACTUALIZACIÓN DINÁMICO ---")
        entidad = input("¿Qué desea actualizar? (1: Usuario, 2: Empresa): ")
        
        if entidad == '1':
            users = service.u_repo.list()
            for u in users: print(f"ID: {u.id} | {u.first_name} {u.last_name}")
            uid = input("\nID del usuario a actualizar: ")
            val = input("Nuevo pseudónimo: ")
            
            old_user = service.u_repo.get_by_id(int(uid))
            service.update_user_basic(int(uid), {"seudonimo": val})
            time.sleep(1)
            new_user = service.u_repo.get_by_id(int(uid))
            print(f"\n✅ Auditoría Usuario: updated_at cambió de {old_user.updated_at} a {new_user.updated_at}")
            
        elif entidad == '2':
            comps = service.c_repo.list()
            for c in comps: print(f"ID: {c.id} | {c.legal_name}")
            cid = input("\nID de la empresa a actualizar: ")
            val = input("Nueva descripción: ")
            
            old_comp = service.c_repo.get_by_id(int(cid))
            service.update_company_basic(int(cid), {"description": val})
            time.sleep(1)
            new_comp = service.c_repo.get_by_id(int(cid))
            print(f"\n✅ Auditoría Empresa: updated_at cambió de {old_comp.updated_at} a {new_comp.updated_at}")

    except Exception as e:
        logger.error(f"Error en prueba: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_update_audit()
