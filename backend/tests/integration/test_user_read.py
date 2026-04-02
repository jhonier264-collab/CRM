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

def test_user_read():
    # load_dotenv is now called at the top level
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*50)
    print(" [TEST] USER READ ")
    print("="*50)
    
    try:
        users = service.u_repo.list()
        print(f" >>> Total users found: {len(users)}")
        for u in users:
            print(f" - ID: {u.id} | Name: {u.first_name} {u.last_name}")
        print("\n >>> Test completed successfully.")
    except Exception as e:
        print(f" >>> Error during user read: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_user_read()
