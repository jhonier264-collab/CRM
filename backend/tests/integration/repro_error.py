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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("REPRO")

def repro():
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
    
    comp = {"username": "alpha_corp", "email": "alpha@test.com", "password": "Pass123!", "first_name": "Alpha", "last_name": "Admin", "account_type": "COMPANY", "rut": "900123456-8"}
    
    # Clean up
    db_name = "crm_user_alphacorp"
    try:
        db.execute_command(f"DROP DATABASE IF EXISTS {db_name}")
        db.execute_command("DELETE FROM global_users WHERE username = %s", (comp['username'],), perform_commit=True, fetch_results=False)
        db.execute_command("DELETE FROM tenants WHERE db_name = %s", (db_name,), perform_commit=True, fetch_results=False)
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")

    logger.info("Starting create_tenant repro...")
    try:
        prov.create_tenant(comp)
        logger.info("SUCCESS!")
    except Exception as e:
        logger.error(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    repro()
