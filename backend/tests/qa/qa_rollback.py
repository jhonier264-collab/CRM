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
logger = logging.getLogger("QA_ROLLBACK")

def test_rollback():
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
    
    tenant_db = "crm_user_alphacorp"
    tenant_id = 1 # Según el registro previo
    
    logger.info("Iniciando prueba de Rollback...")
    
    # 1. Intentar instalar el módulo roto
    try:
        prov.install_module(tenant_id, "broken_module")
        logger.error("FALLO: La instalación no falló como se esperaba.")
    except Exception as e:
        logger.info(f"Éxito: La instalación falló (esperado): {e}")
        
    # 2. Verificar que 'rollback_success' NO existe en el tenant
    try:
        db.switch_database(tenant_db)
        res = db.execute_command("SHOW TABLES LIKE 'rollback_success'")
        if not res:
            logger.info("VERIFICACIÓN EXITOSA: La base de datos se mantuvo limpia tras el fallo.")
        else:
            logger.error("FALLO: La tabla 'rollback_success' persistió a pesar del rollback.")
    except Exception as e:
        logger.error(f"Error verificando tenant: {e}")
    finally:
        db.switch_database(os.getenv('MASTER_DB_NAME'))

if __name__ == "__main__":
    test_rollback()
