import sys
import os
from unittest.mock import MagicMock, patch

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.models import User
from src.services.services import CRMService

def test_natural_person_automation():
    mock_db = MagicMock()
    service = CRMService(mock_db)
    
    # CASE 1: With RUT
    u1 = User(first_name="Test", last_name="User", rut_nit="12345678-9")
    service.create_user_complete(u1)
    # Check the SQL params (second call to execute usually audit, first one is insert)
    # Actually u1 should have is_natural_person=True after normalization
    print(f"User with RUT - is_natural_person: {u1.is_natural_person}")
    assert u1.is_natural_person is True
    
    # CASE 2: No RUT
    u2 = User(first_name="Test", last_name="User", rut_nit=None)
    service.create_user_complete(u2)
    print(f"User without RUT - is_natural_person: {u2.is_natural_person}")
    assert u2.is_natural_person is False

def test_password_hashing_on_update():
    mock_db = MagicMock()
    service = CRMService(mock_db)
    
    # Update with password
    data = {'first_name': 'NewName', 'password': 'newpassword123'}
    
    with patch.object(service, 'hash_password', return_value='HASHED_PW') as mock_hash:
        service.update_user_complete(1, data)
        # Check if hash_password was called
        mock_hash.assert_called_once_with('newpassword123')
        print("Password hashing on update verified.")

if __name__ == "__main__":
    test_natural_person_automation()
    test_password_hashing_on_update()
    print("\n✅ Service logic verification passed!")
