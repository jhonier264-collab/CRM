
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.services.data_hygiene_service import DataHygieneService

def test_company_delete():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    hygiene = DataHygieneService(db)
    
    print("\n" + "="*50)
    print(" [TEST] COMPANY DELETE (GOOGLE STYLE) ")
    print("="*50)
    
    try:
        # List companies (active only)
        companies = service.c_repo.list()
        print("\n--- Empresas Activas ---")
        for c in companies:
            print(f"ID: {c.id} | {c.legal_name}")
        
        target_id_str = input("\n>>> Ingrese ID a enviar a la PAPELERA (Enter cancelar): ")
        if not target_id_str: return

        target_id = int(target_id_str)
        
        # 1. SOFT DELETE
        print(f"\n1. Enviando Empresa ID {target_id} a la papelera...")
        service.delete_company_complete(target_id)
        print("✅ Movido a la papelera.")

        # 2. SUB-MENU TEST
        while True:
            print(f"\n--- ESTADO DE EMPRESA {target_id} ---")
            print(" 1. Verificar en Papelera")
            print(" 2. Restaurar Empresa")
            print(" 3. Eliminar DEFINITIVAMENTE (Purgar)")
            print(" 0. Salir del Test")
            
            opt = input("\nSeleccione acción: ")
            if opt == '1':
                trash = hygiene.list_trash('companies')
                if any(t['id'] == target_id for t in trash):
                    print(f"✅ CONFIRMADO: La empresa {target_id} está en la papelera.")
                else:
                    print(f"❌ ERROR: La empresa no se encuentra en la papelera.")
            
            elif opt == '2':
                hygiene.restore_item('companies', target_id)
                print(f"✅ RESTAURADO: La empresa vuelve a estar activa.")
                break
            
            elif opt == '3':
                confirm = input("¿Está TOTALMENTE seguro? No hay vuelta atrás. (s/n): ")
                if confirm.lower() == 's':
                    hygiene.permanent_delete_item('companies', target_id)
                    print(f"🔥 PURGADO: El registro corporativo ha sido eliminado.")
                break
            elif opt == '0': break

    except Exception as e:
        print(f" >>> Error during company deletion test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_company_delete()
