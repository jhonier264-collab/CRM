
import os
import sys
import json

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService

def diagnose():
    db = DatabaseManager()
    service = CRMService(db)
    
    print("--- DIAGNOSTICO DE SERVICIO ---")
    
    # 1. Find Jhonier
    try:
        users = service.get_users_summary()
        jhonier_summary = next((u for u in users if 'Jhonier' in u['first_name']), None)
        
        if not jhonier_summary:
            print("ERROR: No se encontró a Jhonier en el resumen inicial.")
            return

        u_id = jhonier_summary['id']
        print(f"Jhonier encontrado con ID: {u_id}")
        
        # 2. Get Detail via Repository
        user = service.u_repo.get_by_id(u_id)
        if not user:
            print("ERROR: El repositorio de usuarios no encuentra el ID.")
            return
            
        print(f"Datos Crudos del Modelo User:")
        print(f"  Prefix: '{user.prefix}'")
        print(f"  First Name: '{user.first_name}'")
        print(f"  Last Name: '{user.last_name}'")
        print(f"  Nickname: '{user.nickname}'")
        print(f"  RUT: '{user.rut_nit}'")
        print(f"  DV: {user.verification_digit}")
        
        # 3. Get Contacts
        phones = service.db.execute_query("SELECT * FROM phones WHERE user_id = %s", (u_id,))
        emails = service.db.execute_query("SELECT * FROM emails WHERE user_id = %s", (u_id,))
        
        print(f"Telefonos encontrados: {len(phones)}")
        for p in phones:
            print(f"  - {p['local_number']}")
            
        print(f"Emails encontrados: {len(emails)}")
        for e in emails:
            print(f"  - {e['email_address']}")

        # 4. Companies
        companies = service.db.execute_query("""
            SELECT c.legal_name, uc.position_id, uc.company_department_id 
            FROM companies c 
            JOIN user_companies uc ON uc.company_id = c.id 
            WHERE uc.user_id = %s
        """, (u_id,))
        print(f"Empresas vinculadas: {len(companies)}")

    except Exception as e:
        print(f"ERROR DURANTE EL DIAGNOSTICO: {e}")

if __name__ == "__main__":
    diagnose()
