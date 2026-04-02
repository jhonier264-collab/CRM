
import sys
import os
import logging

# Ajustar path para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Importar utilidades, repositorios y servicios
from ui_utils import clear_screen, print_header, get_masked_input, safe_execute
from flows import UserFlow, CompanyFlow, GeographyFlow, RelationshipFlow

# Importar la infraestructura agnóstica
from src.core.mysql_repository import MySQLRepository
from src.services.services import CRMService
from src.services.auth_service import AuthService
from src.services.data_hygiene_service import DataHygieneService

class CRMConsole:
    def __init__(self):
        """
        Inicializa la consola configurando la infraestructura de persistencia.
        Por qué: Centraliza la configuración de la DB y la inyecta en los servicios.
        """
        # Configuración desde .env (sin valores por defecto hardcodeados)
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('MASTER_DB_NAME'),
            'port': int(os.getenv('DB_PORT'))
        }
        
        # Instanciamos el repositorio concreto
        self.persistence = MySQLRepository(self.db_config)
        
        # Inyectamos la persistencia en el servicio de autenticación
        self.auth_service = AuthService(self.persistence)
        
        self.current_user = None
        self.tenant_db = None
        self.service = None
        self.hygiene = None
        self.user_flow = None
        self.company_flow = None
        self.geo_flow = None
        self.rel_flow = None

    def splash_screen(self):
        while True:
            clear_screen()
            print_header("CRM INDUSTRIAL - ACCESO GLOBAL")
            print(" 1. 🔑 Iniciar Sesión (Identificador/Pass)")
            print(" 2. 🚀 Registrar Nuevo Cliente (Persona/Empresa)")
            print(" 3. 🛡️  Recuperar Contraseña")
            print(" 0. ❌ Salir")
            
            choice = input("\nOpciones: ")
            if choice == '1':
                if self.login_flow(): self.main_menu()
            elif choice == '2': self.registration_flow()
            elif choice == '3': self.password_recovery_flow()
            elif choice == '0': break

    def login_flow(self):
        print_header("Inicio de Sesión")
        # Identificador puede ser username o email
        id_input = input("Usuario o Email: ")
        p = get_masked_input("Contraseña: ")
        
        res = self.auth_service.login(id_input, p)
        if res['authenticated']:
            self.current_user = res['username']
            self.login_success(res)
            return True
        else:
            print(f"\n❌ Error: {res.get('error', 'Fallo')}")
            input("Continuar...")
            return False

    def password_recovery_flow(self):
        print_header("Recuperación de Contraseña")
        identifier = input("Ingrese su Usuario o Email: ")
        
        success, msg = self.auth_service.request_recovery(identifier)
        print(f"\n{msg}")
        
        if success:
            token = input("\nIngrese el código de 6 dígitos: ")
            new_pass = get_masked_input("Nueva Contraseña: ")
            confirm_pass = get_masked_input("Confirmar Nueva Contraseña: ")
            
            if new_pass != confirm_pass:
                print("\n❌ Las contraseñas no coinciden.")
            else:
                ok, res_msg = self.auth_service.reset_password(identifier, token, new_pass)
                print(f"\n{'✅' if ok else '❌'} {res_msg}")
        
        input("\nContinuar...")

    def registration_flow(self):
        print_header("Registro de Nuevo Cliente (SaaS-Ready)")
        
        print("Tipo de Cuenta:")
        print(" 1. Persona Natural")
        print(" 2. Empresa / Persona Jurídica")
        type_choice = input("\nSeleccione (1/2): ")
        
        account_type = 'COMPANY' if type_choice == '2' else 'INDIVIDUAL'
        
        data = {
            'account_type': account_type,
            'first_name': input("Nombre: "),
            'last_name': input("Apellido: "),
            'email': input("Email: "),
            'username': input("Username: "),
            'password': get_masked_input("Contraseña: "),
            'password_confirm': get_masked_input("Confirmar: ")
        }
        
        if account_type == 'COMPANY':
            print("\n[Validación DIAN] Registro de Empresa")
            data['rut'] = input("Ingrese NIT/RUT (Ej: 900123456-1): ")

        res = self.auth_service.register_root_user(data)
        print(f"\n{'✅' if res['success'] else '❌'} {res['message']}")
        input("Continuar...")

    def login_success(self, auth_result):
        """
        Configura el contexto de trabajo tras un login exitoso.
        Por qué: Asegura que todos los servicios apunten a la base de datos del cliente (Tenant).
        """
        self.tenant_db = auth_result['tenant_db']
        
        # Creamos una persistencia específica para el tenant
        tenant_persistence = MySQLRepository(self.db_config)
        tenant_persistence.connect(database_name=self.tenant_db)
        
        # Inyectamos la persistencia del tenant en los servicios de negocio
        self.service = CRMService(tenant_persistence)
        self.hygiene = DataHygieneService(tenant_persistence)
        
        # Los flujos de UI también reciben los servicios ya inyectados
        self.user_flow = UserFlow(self.service, self.auth_service, self.tenant_db)
        self.company_flow = CompanyFlow(self.service)
        self.geo_flow = GeographyFlow(self.service)
        self.rel_flow = RelationshipFlow(self.service)
        
        print(f"\n✅ Conectado exitosamente.")
        print(f"🔗 Tenant: {self.tenant_db}")
        input("Presione Enter para continuar...")

    def main_menu(self):
        while True:
            clear_screen()
            print_header(f"MENÚ: {self.tenant_db} ({self.current_user})")
            print(" 1. 👥 Gestión de Usuarios y Contactos")
            print(" 2. 🏢 Gestión de Empresas")
            print(" 3. � Vínculos (B2B / Holding)")
            print(" 4. ⚙️  Configuración y Geo")
            print(" 5. 🗑️  Papelera")
            print(" 0. � Cerrar Sesión")
            
            choice = input("\nOpciones: ")
            if choice == '1': self.user_flow.main_menu()
            elif choice == '2': self.company_flow.main_menu()
            elif choice == '3': self.rel_flow.main_menu()
            elif choice == '4': self.geo_flow.main_menu()
            elif choice == '5': self.trash_menu() # Assuming a trash_menu method exists or will be added
            elif choice == '0': break

    def trash_menu(self):
        while True:
            clear_screen()
            print_header("PAPELERA Y RECUPERACIÓN")
            print(" 1. 👥 Usuarios Eliminados")
            print(" 2. 🏢 Empresas Eliminadas")
            print(" 0. 🔙 Volver")
            
            opt = input("\nSeleccione: ")
            if opt == '0': break
            print("\n🚧 Funcionalidad de restauración en desarrollo (DB ready).")
            input("Presione Enter...")

if __name__ == "__main__":
    app = CRMConsole()
    app.splash_screen()
