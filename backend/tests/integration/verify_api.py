import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

BASE_URL = f"{os.getenv('BASE_URL', 'http://localhost')}:{os.getenv('BACKEND_PORT')}"

def get_token():
    # Attempt to login as admin
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "identifier": "admin",
            "password": "admin"
        }, timeout=5)
        if response.status_code == 200:
            return response.json()['data']['token']
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def verify():
    token = get_token()
    if not token:
        print("Could not get token. Is the server running with default admin/admin?")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Verify /companies summary
    print("Testing GET /companies...")
    try:
        resp = requests.get(f"{BASE_URL}/companies", headers=headers, timeout=5)
        if resp.status_code == 200:
            companies = resp.json()['data']
            if len(companies) > 0:
                print(f"Found {len(companies)} companies.")
                c = companies[0]
                if 'linked_contacts_count' in c:
                    print(f"SUCCESS: linked_contacts_count found: {c['linked_contacts_count']}")
                else:
                    print("FAILURE: linked_contacts_count missing in summary")
            else:
                print("No companies found to test.")
        else:
            print(f"Error GET /companies: {resp.status_code}")
            return
    except Exception as e:
        print(f"Request failed: {e}")
        return

    # 2. Verify /companies/{id} detail
    print("\nTesting GET /companies/{id}...")
    if len(companies) > 0:
        c_id = companies[0]['id']
        try:
            resp = requests.get(f"{BASE_URL}/companies/{c_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                detail = resp.json()['data']
                if 'employees' in detail:
                    print(f"Found {len(detail['employees'])} employees.")
                    if len(detail['employees']) > 0:
                        emp = detail['employees'][0]
                        print(f"Employee data keys: {list(emp.keys())}")
                        if 'email' in emp and 'phone' in emp:
                            print("SUCCESS: email and phone found in employee data")
                        else:
                            print("FAILURE: email or phone missing in employee data")
                    else:
                        print("NOTE: No employees linked to this company yet, but 'employees' key exists.")
                else:
                    print("FAILURE: employees list missing in company detail")
            else:
                print(f"Error GET /companies/{c_id}: {resp.status_code}")
        except Exception as e:
            print(f"Request failed: {e}")

    # 3. Verify DELETE /companies/{id} (Soft Delete)
    print("\nVerifying DELETE /companies/{id} (Soft Delete)...")
    try:
        print("Creating temp company for deletion test...")
        create_resp = requests.post(f"{BASE_URL}/companies", headers=headers, json={
            "legal_name": "TEMP DELETE TEST CORP",
            "status_id": 1
        }, timeout=5)
        if create_resp.status_code == 200:
            temp_id = create_resp.json()['data']['id']
            print(f"Temp company created with ID: {temp_id}")
            
            del_resp = requests.delete(f"{BASE_URL}/companies/{temp_id}", headers=headers, timeout=5)
            if del_resp.status_code == 200:
                print("SUCCESS: DELETE /companies/{id} returned 200")
                
                # Verify soft delete
                list_resp = requests.get(f"{BASE_URL}/companies", headers=headers, timeout=5)
                if any(c['id'] == temp_id for c in list_resp.json()['data']):
                    print("FAILURE: Company still in active list after delete")
                else:
                    print("SUCCESS: Company removed from active list")
                    
                trash_resp = requests.get(f"{BASE_URL}/hygiene/trash/companies", headers=headers, timeout=5)
                if any(c['id'] == temp_id for c in trash_resp.json()['data']):
                    print("SUCCESS: Company found in trash")
                else:
                    print("FAILURE: Company not found in trash")
            else:
                print(f"FAILURE: DELETE /companies/{temp_id} failed with {del_resp.status_code}")
        else:
            print(f"Error creating temp company: {create_resp.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    verify()
