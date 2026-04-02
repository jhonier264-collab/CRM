import os
import sys
import logging
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

# Patch mysql connection to avoid "Not Connected" if config is empty initially
# Actually TestClient runs the code, so database_manager will initiate.

from api_server import app

client = TestClient(app)

def test_frontend_flow():
    print(">>> 1. Validating RUT (Frontend Logic)")
    # 901.543.210-9 is valid per previous calculation
    rut_payload = {"rut": "901543210-9"}
    response = client.post("/auth/validate-rut", json=rut_payload)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['data']['isValid'] == True
    
    print("\n>>> 2. Registering Company (Provisioning Trigger)")
    # Using a unique username to avoid conflict with previous runs
    import random
    suffix = random.randint(1000,9999)
    username = f"frontend_test_corp_{suffix}"
    
    reg_payload = {
        "username": username,
        "email": f"front_{suffix}@test.com",
        "password": "SecurePass123!",
        "first_name": "Frontend Corp",
        "last_name": "SA",
        "account_type": "COMPANY",
        "rut": "901543210-9"
    }
    
    # We expect this to run provisioning_service.create_tenant
    # This might take a few seconds
    response = client.post("/auth/register", json=reg_payload)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    
    if response.status_code != 200:
        print("Registration failed details:", response.text)
        # If it failed because user exists, it's okay for verifying flow structure, but we want success.
    
    assert response.status_code == 200
    
    print("\n>>> 3. Logging In")
    login_payload = {
        "identifier": username,
        "password": "SecurePass123!"
    }
    response = client.post("/auth/login", json=login_payload)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    assert response.status_code == 200
    
    token = response.json()['data']['token']
    user_db = response.json()['data']['tenant_db']
    print(f"Token obtained. Tenant DB: {user_db}")
    
    print("\n>>> 4. Accessing Protected Route (Users List)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # This request should go to the NEW tenant DB, which is empty except for the admin.
    response = client.get("/users", headers=headers)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    assert response.status_code == 200
    
    users_list = response.json()['data']
    print(f"Users found in tenant: {len(users_list)}")
    # Should be at least 1 (the admin created during provisioning)
    assert len(users_list) >= 1
    # Verify the user matches the created one
    assert users_list[0]['username'] == username
    print("SUCCESS: Frontend Flow verified (RUT -> Register -> Login -> Segregated Access)")

if __name__ == "__main__":
    try:
        test_frontend_flow()
    except Exception:
        import traceback
        traceback.print_exc()
