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

def migrate_tenant():
    load_dotenv()
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT')),
            database='crm_user_jhonier264'
        )
        cursor = conn.cursor()
        
        print("Migrating tenant database 'crm_user_jhonier264'...")
        
        # Add employee_count
        try:
            cursor.execute("ALTER TABLE companies ADD COLUMN employee_count int DEFAULT 0 AFTER revenue")
            print("Added 'employee_count' to 'companies'.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print("'employee_count' already exists.")
            else:
                raise err

        # Add company_department_id
        try:
            cursor.execute("ALTER TABLE companies ADD COLUMN company_department_id int DEFAULT NULL AFTER employee_count")
            cursor.execute("ALTER TABLE companies ADD CONSTRAINT fk_company_dept FOREIGN KEY (company_department_id) REFERENCES company_departments(id)")
            print("Added 'company_department_id' and foreign key to 'companies'.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print("'company_department_id' already exists.")
            elif err.errno == 1061: # Duplicate key name
                print("Constraint 'fk_company_dept' already exists.")
            else:
                raise err

        conn.commit()
        conn.close()
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_tenant()
