import sys
import os

# Ajustar path para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from lib.shared_auth.security import validar_rut_colombia

def test_rut_validation():
    print("--- Testing RUT Colombia (Module 11) ---")
    
    # Casos válidos conocidos
    valid_cases = [
        "900123456-1",
        "860001234-1",
        "13825489-0",
        "800197268-4"
    ]
    
    # Casos inválidos
    invalid_cases = [
        "900123456-0",  # DV incorrecto
        "12345-6",      # Muy corto
        "ABCDEFG-1",    # No es dígito
        "900123456",    # Sin guion
    ]
    
    for rut in valid_cases:
        result = validar_rut_colombia(rut)
        status = "PASS" if result else "FAIL"
        print(f"Validating {rut:15} | Result: {result} | Status: {status}")

    for rut in invalid_cases:
        result = validar_rut_colombia(rut)
        status = "PASS" if not result else "FAIL"
        print(f"Validating {rut:15} | Result: {result} | Status: {status}")

if __name__ == "__main__":
    test_rut_validation()
