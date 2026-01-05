
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User, Company

def test_b2b_b2c():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*50)
    print(" [ID: 7.1] [TEST] B2B / B2C IDENTITY & LINKS ")
    print("="*50)
    
    try:
        # 1. List current setup
        print("\n--- Estado Actual ---")
        users = service.u_repo.list()
        comps = service.c_repo.list()
        print(f"Usuarios: {len(users)} | Empresas: {len(comps)}")

        # 2. Interactive Choice
        print("\n1. Crear Persona Natural (B2C)")
        print("2. Vincular Usuario a Empresa (B2B)")
        print("3. Listar solo Personas Naturales")
        choice = input("\nSeleccione una prueba: ")

        if choice == '1':
            print("\n--- NUEVA PERSONA NATURAL ---")
            fn = input("Nombre: ")
            ln = input("Apellido: ")
            tid = input("RUT/NIT (Obligatorio para Persona Natural): ")
            
            u = User(first_name=fn, last_name=ln, rut_nit=tid, is_natural_person=True)
            try:
                uid = service.create_user_complete(u)
                print(f"✅ ÉXITO: Usuario creado con ID: {uid} como Persona Natural.")
            except Exception as e:
                print(f"❌ ERROR: {e}")

        elif choice == '2':
            print("\n--- VINCULAR USUARIO A EMPRESA ---")
            for u in users: print(f"  [User {u.id}] {u.first_name} {u.last_name}")
            uid = int(input("ID del Usuario: "))
            
            for c in comps: print(f"  [Comp {c.id}] {c.legal_name}")
            cid = int(input("ID de la Empresa: "))
            
            print("\n--- Lista de Departamentos ---")
            depts = service.get_departments()
            for d in depts: print(f"  [{d['id']}] {d['nombre_departamento']}")
            did = int(input("Seleccione el ID del Departamento: "))

            print("\n--- Lista de Cargos ---")
            cargos = service.get_cargos()
            for cg in cargos: print(f"  [{cg['id']}] {cg['nombre_cargo']}")
            cgid = int(input("Seleccione el ID del Cargo: "))
            
            service.link_user_to_company(uid, cid, position_id=cgid, department_id=did)
            print(f"✅ ÉXITO: Usuario {uid} vinculado a Empresa {cid} en Dept {did} con Cargo {cgid}.")

        elif choice == '3':
            naturals = service.list_natural_persons()
            print("\n--- PERSONAS NATURALES REGISTRADAS ---")
            for n in naturals:
                print(f"ID: {n.id} | {n.first_name} {n.last_name} | RUT/NIT: {n.rut_nit}")

    except Exception as e:
        print(f" >>> Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_b2b_b2c()
