import os
import sys
import mysql.connector
import dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
dotenv.load_dotenv(os.path.join(backend_dir, '..', '.env'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': 'crm_user_jhonier264'
}

def migrate():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"Connected to {DB_CONFIG['database']}")

        # COMPANY TYPES
        print("Migrating Company Types...")
        try:
            cursor.execute("ALTER TABLE company_relation_types ADD COLUMN inverse_type_id INT DEFAULT NULL")
            cursor.execute("ALTER TABLE company_relation_types ADD KEY fk_inverse_type (inverse_type_id)")
            cursor.execute("ALTER TABLE company_relation_types ADD CONSTRAINT fk_comp_rel_inverse FOREIGN KEY (inverse_type_id) REFERENCES company_relation_types (id) ON DELETE SET NULL")
        except mysql.connector.Error as e:
            print(f"Schema change optional/exists: {e}")

        # Map known IDs (Standard Seed)
        # 1: Matriz (2), 2: Subsidiaria (1), 3: Aliada (3), 4: Asociada (4), 5: Otro (5)
        updates = [
            (2, 1), (1, 2), (3, 3), (4, 4), (5, 5)
        ]
        for inv, pid in updates:
            cursor.execute("UPDATE company_relation_types SET inverse_type_id = %s WHERE id = %s", (inv, pid))
        
        try:
            cursor.execute("ALTER TABLE company_relation_types DROP COLUMN inverse_name")
        except: pass


        # USER TYPES
        print("Migrating User Types...")
        try:
            cursor.execute("ALTER TABLE user_relation_types ADD COLUMN inverse_type_id INT DEFAULT NULL")
            cursor.execute("ALTER TABLE user_relation_types ADD KEY fk_user_rel_inverse (inverse_type_id)")
            cursor.execute("ALTER TABLE user_relation_types ADD CONSTRAINT fk_user_rel_inverse FOREIGN KEY (inverse_type_id) REFERENCES user_relation_types (id) ON DELETE SET NULL")
        except mysql.connector.Error as e:
            print(f"Schema change optional/exists: {e}")

        # Map known IDs
        # 1: Jefe (2), 2: Empleado (1), 3: Familiar (3), 4: Mentor (5), 5: Aprendiz (4), 6: Amigo (6)
        user_updates = [
            (2, 1), (1, 2), (3, 3), (5, 4), (4, 5), (6, 6)
        ]
        for inv, pid in user_updates:
            cursor.execute("UPDATE user_relation_types SET inverse_type_id = %s WHERE id = %s", (inv, pid))

        try:
            cursor.execute("ALTER TABLE user_relation_types DROP COLUMN inverse_name")
        except: pass

        conn.commit()
        print("Migration successful.")
        conn.close()

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
