
import os
import logging
from dotenv import load_dotenv
from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    # Initialize database connection
    # Values are loaded from .env automatically in DatabaseManager
    db = DatabaseManager()
    
    try:
        service = CRMService(db)
        
        # Simple demonstration of querying users from the new English schema
        users = service.u_repo.list()
        
        print("\n--- CRM USER LIST (English Schema) ---")
        if not users:
            print("No users found. Try running the creation tests.")
        else:
            for u in users:
                print(f"ID: {u.id} | Name: {u.first_name} {u.last_name} | Tax ID: {u.tax_id}")
        print("--------------------------------------\n")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()