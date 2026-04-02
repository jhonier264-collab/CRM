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

from src.core.mysql_repository import MySQLRepository
from src.services.provisioning_service import ProvisioningService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_AUDITOR")

def run_qa_suit_provisioning():
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('MASTER_DB_NAME') or os.getenv('DB_NAME'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    db = MySQLRepository(config)
    prov = ProvisioningService(db)
    
    # 1. Registro de 5 empresas
    companies = [
        {"username": "alpha_corp", "email": "alpha@test.com", "password": "Pass123!", "first_name": "Alpha", "last_name": "Admin", "account_type": "COMPANY", "rut": "900123456-8"},
        {"username": "beta_inc", "email": "beta@test.com", "password": "Pass123!", "first_name": "Beta", "last_name": "Admin", "account_type": "COMPANY", "rut": "800111222-7"},
        {"username": "juan_perez", "email": "juan@test.com", "password": "Pass123!", "first_name": "Juan", "last_name": "Perez", "account_type": "INDIVIDUAL"},
        {"username": "gamma_tech", "email": "gamma@test.com", "password": "Pass123!", "first_name": "Gamma", "last_name": "Admin", "account_type": "COMPANY", "rut": "890987654-0"},
        {"username": "delta_sol", "email": "delta@test.com", "password": "Pass123!", "first_name": "Delta", "last_name": "Admin", "account_type": "COMPANY", "rut": "901234567-9"}
    ]

    tenant_ids = []
    for comp in companies:
        try:
            # Limpieza NUCLEAR previa para facilitar re-ejecución del test
            safe_username = "".join(c for c in comp['username'] if c.isalnum())
            db_name = f"crm_user_{safe_username}"
            
            db.execute_command(f"DROP DATABASE IF EXISTS {db_name}")
            db.execute_command("DELETE FROM global_users WHERE username = %s", (comp['username'],), perform_commit=True, fetch_results=False)
            
            logger.info(f"Registrando {comp['username']}...")
            prov.create_tenant(comp)
            
            # Obtener ID usando la misma lógica de normalización que el servicio
            safe_username = "".join(c for c in comp['username'] if c.isalnum())
            db_name = f"crm_user_{safe_username}"
            
            res = db.execute_command("SELECT id FROM tenants WHERE db_name = %s", (db_name,))
            if res:
                tenant_ids.append(res[0]['id'])
            else:
                logger.error(f"Tenant no encontrado en master tras creación: {db_name}")
        except Exception as e:
            logger.error(f"Error registrando {comp['username']}: {e}")

    if len(tenant_ids) < 3:
        logger.error("No se pudieron registrar suficientes tenants para continuar.")
        return

    # 2. Activar módulo business_pipeline en 3 (Alpha, Beta, Juan)
    for i in range(3):
        t_id = tenant_ids[i]
        logger.info(f"Instalando módulo en tenant ID {t_id}...")
        prov.install_module(t_id, "business_pipeline")

    # 3. Validación de aislamiento
    # Gamma (index 3) no debería tener tablas de deals
    try:
        db.switch_database("crm_user_gammatech")
        db.execute_command("SELECT * FROM deals")
        logger.error("FALLO DE AISLAMIENTO: Gamma puede ver la tabla 'deals'")
    except Exception:
        logger.info("EXITO: Gamma no tiene acceso a 'deals' (Correcto)")
    
    # Alpha (index 0) SI debería verla
    try:
        db.switch_database("crm_user_alphacorp")
        db.execute_command("SELECT * FROM deals")
        logger.info("EXITO: Alpha tiene acceso a 'deals' (Correcto)")
    except Exception as e:
        logger.error(f"FALLO DE ACTIVACIÓN: Alpha no ve sus tablas: {e}")

    db.switch_database(None)

if __name__ == "__main__":
    run_qa_suit_provisioning()
