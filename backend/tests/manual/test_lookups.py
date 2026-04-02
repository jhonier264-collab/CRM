
import sys
import os

# Añadir el path del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService

def test_lookups():
    print("🚀 Verificando lookups de base de datos...")
    db = DatabaseManager()
    service = CRMService(db)
    
    lookups = {
        'Genders': service.get_genders,
        'Roles': service.get_roles,
        'Statuses': service.get_statuses,
        'Labels': service.get_labels,
        'Positions': service.get_positions,
        'Departments': service.get_departments,
        'Countries': service.get_countries
    }
    
    for name, func in lookups.items():
        try:
            items = func()
            print(f"✅ {name}: {len(items)} ítems encontrados.")
            if items:
                # Verificar campos básicos
                item = items[0]
                assert 'id' in item, f"{name} no tiene 'id'"
                # Países tienen 'country_name', los demás usan el alias 'name'
                if name == 'Countries':
                    assert 'country_name' in item, f"{name} no tiene 'country_name'"
                else:
                    assert 'name' in item, f"{name} no tiene 'name'"
                
        except Exception as e:
            print(f"❌ ERROR EN {name}: {e}")
            raise

    print("\n✨ TODOS LOS LOOKUPS FUNCIONAN CORRECTAMENTE.")

if __name__ == "__main__":
    try:
        test_lookups()
    except Exception as e:
        sys.exit(1)
