import os
import sys

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


from src.core.mysql_repository import MySQLRepository
from src.core.database_manager import DatabaseManager

print("Checking MySQLRepository...")
try:
    repo = MySQLRepository({})
    print("MySQLRepository OK")
except Exception as e:
    print(f"MySQLRepository Failed: {e}")

print("\nChecking DatabaseManager...")
try:
    mgr = DatabaseManager()
    print("DatabaseManager OK")
except Exception as e:
    print(f"DatabaseManager Failed: {e}")
