import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

def init_master_db():
    try:
        # Connect without DB first to create it if not exists
        db_user = os.getenv('DB_USER')
        if not db_user:
            raise ValueError("DB_USER environment variable not set.")
            
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=db_user,
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT'))
        )
        cursor = conn.cursor()

        # Read SQL file
        with open('../../database/master_db.sql', 'r') as f:
            sql_script = f.read()

        # Execute statements
        for statement in sql_script.split(';'):
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Error executing statement: {statement[:50]}... -> {e}")

        conn.commit()
        print("Master Database initialized successfully.")
        
    except Exception as e:
        print(f"Failed to initialize Master DB: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    init_master_db()
