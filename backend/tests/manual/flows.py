
from ui_utils import interactive_editor, manage_list_flow, print_header, clear_screen
from schemas import (
    USER_FIELDS, COMPANY_FIELDS, PHONE_FIELDS, 
    EMAIL_FIELDS, ADDRESS_FIELDS, PROFESSIONAL_LINK_FIELDS,
    COUNTRY_FIELDS, COMPANY_RELATION_FIELDS, USER_RELATION_FIELDS
)
from src.models.models import User, Company, Phone, Email, Address

class GeographyFlow:
    def __init__(self, service):
        self.service = service

    def main_menu(self):
        while True:
            clear_screen()
            print_header("GEOGRAFÍA Y CONFIGURACIÓN")
            print(" 1. 🌍 Listar Países")
            print(" 2. ➕ Añadir Nuevo País")
            print(" 0. 🔙 Volver")
            
            opt = input("\nSeleccione: ")
            if opt == '1':
                for p in self.service.get_countries():
                    print(f" [{p['id']}] {p['country_name']} (Prefijo: +{p['phone_code']})")
                input("\nEnter...")
            elif opt == '2':
                data = interactive_editor("NUEVO PAÍS", {}, COUNTRY_FIELDS, self.service)
                if data:
                    self.service.add_country(
                        data['country_name'], 
                        data.get('phone_code'), 
                        float(data.get('area_km2', 0) or 0), 
                        int(data.get('population', 0) or 0)
                    )
                    print("✅ País añadido correctamente.")
                    input("Enter...")
            elif opt == '0': break

class RelationshipFlow:
    def __init__(self, service):
        self.service = service

    def main_menu(self):
        while True:
            clear_screen()
            print_header("VÍNCULOS Y ASOCIACIONES")
            print(" 1. 🏢 Relaciones entre Empresas (Holding/Alianza)")
            print(" 2. 👥 Relaciones entre Usuarios (Personal/Familiar)")
            print(" 0. 🔙 Volver")
            
            opt = input("\nSeleccione: ")
            if opt == '1': self.manage_company_relations()
            elif opt == '2': self.manage_user_relations()
            elif opt == '0': break

    def manage_company_relations(self):
        while True:
            clear_screen()
            print_header("RELACIONES ENTRE EMPRESAS")
            print(" 1. ➕ Crear Nuevo Vínculo")
            print(" 2. 🗑️  Eliminar Vínculo")
            print(" 0. 🔙 Volver")
            opt = input("\nSeleccione: ")
            if opt == '1':
                data = interactive_editor("VINCULAR EMPRESAS", {}, COMPANY_RELATION_FIELDS, self.service)
                if data:
                    self.service.link_companies(
                        data['parent_company_id'], 
                        data['child_company_id'], 
                        data['relation_type_id']
                    )
                    print("✅ Vínculo empresarial creado.")
                    input("Enter...")
            elif opt == '2':
                p_id = input("ID Empresa Matriz: ")
                c_id = input("ID Empresa Subsidiaria: ")
                if p_id and c_id:
                    self.service.unlink_companies(int(p_id), int(c_id))
                    print("✅ Vínculo eliminado.")
                    input("Enter...")
            elif opt == '0': break

    def manage_user_relations(self):
        while True:
            clear_screen()
            print_header("RELACIONES ENTRE USUARIOS")
            print(" 1. ➕ Crear Nuevo Vínculo")
            print(" 2. 🗑️  Eliminar Vínculo")
            print(" 0. 🔙 Volver")
            opt = input("\nSeleccione: ")
            if opt == '1':
                data = interactive_editor("VINCULAR USUARIOS", {}, USER_RELATION_FIELDS, self.service)
                if data:
                    self.service.link_users(
                        data['from_user_id'], 
                        data['to_user_id'], 
                        data['relation_type_id'],
                        data.get('custom_label')
                    )
                    print("✅ Vínculo personal creado.")
                    input("Enter...")
            elif opt == '2':
                u1 = input("ID Usuario 1: ")
                u2 = input("ID Usuario 2: ")
                if u1 and u2:
                    self.service.unlink_users(int(u1), int(u2))
                    print("✅ Vínculo eliminado.")
                    input("Enter...")
            elif opt == '0': break

class UserFlow:
    def __init__(self, service, auth_service, tenant_db):
        self.service = service
        self.auth_service = auth_service
        self.tenant_db = tenant_db

    def submenu_dispatcher(self, data, config, service):
        handler = config.get('handler')
        if handler == 'manage_contacts':
            self.manage_contacts(data)
        elif handler == 'manage_professional_links':
            data['user_companies'] = self.manage_professional_links(data.get('user_companies', []))

    def manage_contacts(self, data):
        # Asegurar listas
        for k in ['phones', 'emails', 'addresses']:
            if k not in data: data[k] = []
            
        while True:
            clear_screen()
            print_header("GESTIÓN DE CONTACTOS")
            print(f" 1. 📱 Teléfonos ({len(data['phones'])})")
            print(f" 2. 📧 Correos ({len(data['emails'])})")
            print(f" 3. 🏠 Direcciones ({len(data['addresses'])})")
            print(" 0. 🔙 Volver")
            
            opt = input("\nSeleccione: ")
            if opt == '1':
                data['phones'] = manage_list_flow("TELÉFONOS", data['phones'], PHONE_FIELDS, self.service)
            elif opt == '2':
                data['emails'] = manage_list_flow("CORREOS", data['emails'], EMAIL_FIELDS, self.service)
            elif opt == '3':
                data['addresses'] = manage_list_flow("DIRECCIONES", data['addresses'], ADDRESS_FIELDS, self.service)
            elif opt == '0':
                break

    def manage_professional_links(self, current_links):
        return manage_list_flow("VÍNCULOS PROFESIONALES", current_links, PROFESSIONAL_LINK_FIELDS, self.service)

    def create(self):
        defaults = {
            'role_id': 5, 'status_id': 1, 
            'phones': [], 'emails': [], 'addresses': [], 'user_companies': [],
            'submenu_dispatcher': self.submenu_dispatcher
        }
        data = interactive_editor("CREAR CONTACTO / USUARIO", defaults, USER_FIELDS, self.service)
        if not data: return

        # 1. Validar Contraseñas
        if data.get('password') != data.get('password_confirm'):
            print("\n❌ Error: Las contraseñas no coinciden.")
            input("Presione Enter para volver a intentar...")
            return self.create()

        # 2. Validar Estructura de Correos (Previo)
        for e in data.get('emails', []):
            if not self.service.normalizer.is_valid_email(e['email_address']):
                print(f"\n⚠️  Advertencia: El correo '{e['email_address']}' no parece tener una estructura válida.")
                if input("¿Desea continuar de todos modos? (s/n): ").lower() != 's':
                    return self.create()

        u = User.from_dict(data)
        phones = [Phone.from_dict(p) for p in data.get('phones', [])]
        emails = [Email.from_dict(e) for e in data.get('emails', [])]
        addresses = [Address.from_dict(a) for a in data.get('addresses', [])]
        
        # Guardar todo de forma atómica
        uid = self.service.create_user_complete(u, phones, emails, addresses, password=data.get('password'))
        
        # Registro Global si el rol es Staff (1:Admin, 2:Agente, 3:Especialista)
        if data.get('username') and data.get('password') and str(data.get('role_id')) in ['1', '2', '3']:
            email_val = emails[0].email_address if emails else None
            success, msg = self.auth_service.register_staff_user(
                data['username'], email_val, data['password'], self.tenant_db
            )
            print(f"\n🌍 Registro en Acceso Global: {msg}")
        
        # Guardar vínculos
        # Guardar vínculos
        if 'user_companies' in data:
            self.service.sync_user_companies(uid, data['user_companies'])

        print(f"\n✅ Creado exitosamente ID: {uid}")
        input("\nPresione Enter...")

    def detail_and_edit(self, user_id):
        detail = self.service.get_user_detail_full(user_id)
        if not detail: return
        
        # Inyectar dispatcher para el editor
        detail['submenu_dispatcher'] = self.submenu_dispatcher
        old_username = detail.get('username')
        
        updated = interactive_editor(f"PERFIL: {detail['first_name']}", detail, USER_FIELDS, self.service)
        if updated:
            # 1. Validar Contraseñas si se intenta cambiar
            if updated.get('password') and updated.get('password') != updated.get('password_confirm'):
                print("\n❌ Error: Las contraseñas no coinciden.")
                input("Presione Enter...")
                return self.detail_and_edit(user_id)

            # 2. Actualización local
            self.service.update_user_complete(user_id, updated)
            
            # 3. Sincronización Global si es Staff
            if str(updated.get('role_id')) in ['1', '2', '3']:
                emails_list = updated.get('emails', [])
                success, msg = self.auth_service.update_staff_user(
                    old_username,
                    new_username=updated.get('username'),
                    password=updated.get('password'),
                    email=emails_list[0].get('email_address') if emails_list else None
                )
                print(f"\n🌍 Cambio Global: {msg}")
            # Sincronizar vínculos profesionales (Delete-Or-Update)
            if 'user_companies' in updated:
                self.service.sync_user_companies(user_id, updated['user_companies'])
            print("✅ Actualizado correctamente.")
            input("\nPresione Enter...")

class CompanyFlow:
    def __init__(self, service):
        self.service = service

    def submenu_dispatcher(self, data, config, service):
        if config.get('handler') == 'manage_contacts':
            # Reutilizar lógica (se podría mover a ui_utils si es muy común)
            UserFlow(service, None, None).manage_contacts(data)

    def main_menu(self):
        while True:
            clear_screen()
            print_header("GESTIÓN DE EMPRESAS")
            self.list_all()
            print("\n 1. ➕ Crear Empresa")
            print(" 2. 🔍 Ver Detalle / Editar")
            print(" 3. 🗑️  Eliminar")
            print(" 0. 🔙 Volver")
            
            opt = input("\nSeleccione: ")
            if opt == '1': self.create()
            elif opt == '2':
                cid = input("ID: ")
                if cid: self.detail_and_edit(int(cid))
            elif opt == '3':
                cid = input("ID: ")
                if cid:
                    self.service.delete_company_complete(int(cid))
                    print("✅ Movido a papelera.")
                    input("Enter...")
            elif opt == '0': break

    def detail_and_edit(self, company_id):
        detail = self.service.get_company_detail_full(company_id)
        if not detail: return
        detail['submenu_dispatcher'] = self.submenu_dispatcher
        
        updated = interactive_editor(f"EMPRESA: {detail['legal_name']}", detail, COMPANY_FIELDS, self.service)
        if updated:
            self.service.update_company_complete(company_id, updated)
            print("✅ Actualizado correctamente.")
            input("\nPresione Enter...")

    def list_all(self):
        companies = self.service.get_companies_summary()
        for c in companies:
            print(f" [{c['id']}] {c['legal_name']} - {c['commercial_name']} ({c['rut_nit']})")
        return companies

    def create(self):
        defaults = {
            'status_id': 1, 'phones': [], 'emails': [], 'addresses': [],
            'submenu_dispatcher': self.submenu_dispatcher
        }
        data = interactive_editor("CREAR EMPRESA", defaults, COMPANY_FIELDS, self.service)
        if not data: return
        
        # Validar Estructura de Correos (Previo)
        for e in data.get('emails', []):
            if not self.service.normalizer.is_valid_email(e['email_address']):
                print(f"\n⚠️  Advertencia: El correo '{e['email_address']}' no parece tener una estructura válida.")
                if input("¿Desea continuar de todos modos? (s/n): ").lower() != 's':
                    return self.create()
        
        c = Company.from_dict(data)
        phones = [Phone.from_dict(p) for p in data.get('phones', [])]
        emails = [Email.from_dict(e) for e in data.get('emails', [])]
        addresses = [Address.from_dict(a) for a in data.get('addresses', [])]
        
        cid = self.service.create_company_complete(c, phones, emails, addresses)
        print(f"✅ Empresa creada ID: {cid}")
        input("\nPresione Enter...")
