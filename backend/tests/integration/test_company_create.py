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
from src.models.models import Company, Phone, Email

def test_company_create():
    # load_dotenv is now called at the top level
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*50)
    print(" [TEST] COMPANY CREATE ")
    print("="*50)
    
    try:
        print("\n--- CREACIÓN INTERACTIVA DE EMPRESA ---")
        name = input("Razón Social: ")
        tid = input("NIT: ")
        domain = input("Dominio/Web (Opcional): ")
        
        company = Company(
            legal_name=name,
            rut_nit=tid,
            domain=domain if domain else None,
            status_id=1
        )
        
        company_id = service.create_company_secure(company)
        print(f"\n✅ ÉXITO: Empresa creada con ID: {company_id} y dominio: {company.domain}")
        
    except Exception as e:
        print(f" >>> Error during company creation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_company_create()
