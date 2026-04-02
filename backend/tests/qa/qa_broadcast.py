import os
import sys
import logging
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

from src.core.mysql_repository import MySQLRepository
from src.services.provisioning_service import ProvisioningService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_BROADCAST")

def test_broadcast():
    # load_dotenv is now called at the top level
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('MASTER_DB_NAME'),
        'port': int(os.getenv('DB_PORT'))
    }
    db = MySQLRepository(config)
    prov = ProvisioningService(db)
    
    logger.info("Iniciando prueba de Broadcast Maintenance...")
    
    # 1. Crear una tabla de prueba en todos los tenants
    create_table_cmd = "CREATE TABLE IF NOT EXISTS broadcast_test (id INT PRIMARY KEY, val VARCHAR(50))"
    report = prov.maintenance_broadcast(create_table_cmd)
    
    success_count = sum(1 for r in report if r['success'])
    logger.info(f"Resultado Creación Tabla: {success_count}/{len(report)} exitosos.")
    
    # 2. Insertar una marca en todos los tenants
    insert_cmd = "INSERT INTO broadcast_test (id, val) VALUES (1, 'BROADCAST_OK') ON DUPLICATE KEY UPDATE val = 'BROADCAST_OK'"
    report = prov.maintenance_broadcast(insert_cmd)
    
    success_count = sum(1 for r in report if r['success'])
    logger.info(f"Resultado Inserción Datos: {success_count}/{len(report)} exitosos.")
    
    # 3. Verificar en un tenant específico (ej. alpha_corp)
    try:
        db.switch_database("crm_user_alphacorp")
        res = db.execute_command("SELECT val FROM broadcast_test WHERE id = 1")
        if res and res[0]['val'] == 'BROADCAST_OK':
            logger.info("VERIFICACIÓN EXITOSA: Los cambios se propagaron correctamente al tenant.")
        else:
            logger.error("FALLO DE VERIFICACIÓN: Los datos no coinciden.")
    except Exception as e:
        logger.error(f"Error verificando tenant: {e}")
    finally:
        db.switch_database(os.getenv('MASTER_DB_NAME'))

if __name__ == "__main__":
    test_broadcast()
