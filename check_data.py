
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor(dictionary=True)

print("--- DIAGNOSTICO DE DATOS: JHONIER PUERTA ---")

# 1. User Data
cursor.execute("SELECT * FROM users WHERE first_name LIKE '%Jhonier%'")
users = cursor.fetchall()

if not users:
    print("No se encontro al usuario Jhonier.")
else:
    for u in users:
        print(f"\nID: {u['id']}")
        print(f"Nombre: {u['first_name']} {u['last_name']}")
        print(f"Prefix: {u['prefix']}")
        print(f"Nickname: {u['nickname']}")
        print(f"RUT: {u['rut_nit']} - DV: {u['verification_digit']}")
        
        u_id = u['id']
        
        # 2. Phones
        cursor.execute("SELECT * FROM phones WHERE user_id = %s", (u_id,))
        phones = cursor.fetchall()
        print(f"Telefonos ({len(phones)}): {phones}")
        
        # 3. Emails
        cursor.execute("SELECT * FROM emails WHERE user_id = %s", (u_id,))
        emails = cursor.fetchall()
        print(f"Emails ({len(emails)}): {emails}")
        
        # 4. Companies
        cursor.execute("""
            SELECT c.legal_name, uc.position_id, uc.company_department_id 
            FROM companies c 
            JOIN user_companies uc ON uc.company_id = c.id 
            WHERE uc.user_id = %s
        """, (u_id,))
        comps = cursor.fetchall()
        print(f"Empresas ({len(comps)}): {comps}")

cursor.close()
conn.close()
