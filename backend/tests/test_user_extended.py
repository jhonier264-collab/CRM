
import sys
import os
from datetime import date
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User

def test_extended_fields():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*60)
    print(" [TEST] CAMPOS EXTENDIDOS (GOOGLE CONTACTS) ".center(60, "="))
    print("="*60)
    
    try:
        # 1. Crear usuario con todos los campos nuevos
        print("\n1. Creando usuario con campos fonéticos y fecha de nacimiento...")
        u = User(
            first_name="Juan",
            last_name="Pérez",
            phonetic_first_name="Huan",
            phonetic_last_name="Peres",
            birthday=date(1990, 5, 15),
            notes="Usuario de prueba para campos Google",
            gender_id=1, # Masculino (asumido en migrations)
            status_id=1,
            is_natural_person=True
        )
        
        uid = service.u_repo.insert(u)
        print(f"   ✅ Usuario insertado con ID: {uid}")

        # 2. Recuperar y Validar
        print("\n2. Recuperando usuario desde DB...")
        u_db = service.u_repo.get_by_id(uid)
        
        if u_db:
            print(f"   - Nombre Fonético: {u_db.phonetic_first_name}")
            print(f"   - Fecha Nacimiento: {u_db.birthday}")
            print(f"   - Notas: {u_db.notes}")
            
            if u_db.phonetic_first_name == "Huan" and u_db.birthday == date(1990, 5, 15):
                print("\n   ✅ ÉXITO: Los campos se guardaron y recuperaron correctamente.")
            else:
                print("\n   ❌ ERROR: Discrepancia en los datos recuperados.")
        else:
            print("   ❌ ERROR: No se pudo recuperar el usuario.")

        # 3. Limpieza
        service.u_repo.delete(uid)
        print("\n3. Usuario movido a papelera (test finalizado).")

    except Exception as e:
        print(f"\n 🔴 ERROR DURANTE EL TEST: {e}")
    finally:
        db.close()
        print("\n" + "="*60)

if __name__ == "__main__":
    test_extended_fields()
