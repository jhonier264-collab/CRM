
import sys
import os
from datetime import datetime

# Añadir el path del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User, Company, Phone, Email, Address

def test_full_contact_sync():
    print("🚀 Iniciando prueba de sincronización completa de contactos...")
    db = DatabaseManager()
    service = CRMService(db)
    
    # 1. Crear Usuario con contactos
    u = User(
        first_name="Test",
        last_name="Contacts",
        username="test_contacts_" + str(int(datetime.now().timestamp())),
        is_natural_person=True
    )
    
    phones = [
        Phone(local_number="3001112233", label_id=1), # Personal
        Phone(local_number="6014445566", label_id=2)  # Trabajo
    ]
    
    emails = [
        Email(email_address="test@example.com", label_id=1)
    ]
    
    addresses = [
        Address(address_line1="Calle Falsa 123", country_id=1, state_id=1, city_id=1)
    ]
    
    u_id = service.create_user_complete(u, phones, emails, addresses)
    print(f"✅ Usuario creado con ID: {u_id}")
    
    # 2. Verificar datos
    detail = service.get_user_detail_full(u_id)
    assert len(detail['phones']) == 2
    assert len(detail['emails']) == 1
    assert len(detail['addresses']) == 1
    print("✅ Verificación inicial exitosa.")
    
    # 3. Actualizar (Sincronizar)
    # Cambiamos un teléfono, eliminamos el otro, añadimos un email y cambiamos la dirección
    updated_phones = [
        {'id': detail['phones'][0]['id'], 'local_number': '3009998877', 'label_id': 1}, # Modificado
        {'local_number': '3110000000', 'label_id': 2} # Nuevo
    ]
    
    updated_emails = [
        {'id': detail['emails'][0]['id'], 'email_address': 'test_updated@example.com', 'label_id': 1},
        {'email_address': 'another@example.com', 'label_id': 2}
    ]
    
    updated_addresses = [
        {'id': detail['addresses'][0]['id'], 'address_line1': 'Nueva Avenida 456', 'country_id': 1}
    ]
    
    data = {
        'first_name': 'Test Updated',
        'phones': updated_phones,
        'emails': updated_emails,
        'addresses': updated_addresses
    }
    
    res = service.update_user_complete(u_id, data)
    assert res is True
    print("✅ Sincronización de actualización enviada.")
    
    # 4. Verificar post-actualización
    final_detail = service.get_user_detail_full(u_id)
    assert final_detail['first_name'] == 'Test Updated'
    assert len(final_detail['phones']) == 2
    assert final_detail['phones'][0]['local_number'] == '3009998877'
    assert len(final_detail['emails']) == 2
    assert final_detail['addresses'][0]['address_line1'] == 'Nueva Avenida 456'
    
    print("✅ PRUEBA TOTAL EXITOSA.")

if __name__ == "__main__":
    try:
        test_full_contact_sync()
    except Exception as e:
        print(f"❌ ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
