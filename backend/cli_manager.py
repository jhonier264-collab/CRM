
import sys
import os

# Ajustar path para importar desde src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.services.schema_manager import SchemaManager
from src.services.data_hygiene_service import DataHygieneService
from src.services.contact_normalization_service import ContactNormalizationService
from src.models.models import User, Company, Address, Phone, Email
import logging

# Desactivar logs ruidosos para la CLI
logging.getLogger('src.core.database_manager').setLevel(logging.ERROR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50, " "))
    print("="*50)

def safe_execute(func):
    """Decorator to catch exceptions and prevent CLI from crashing."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            msg = str(e)
            if "Duplicate entry" in msg:
                print("\n⚠️  ERROR: Ya existe un registro con esos datos únicos (Ej: Nombre/Apellido o RUT repetido).")
            elif "foreign key constraint" in msg:
                print("\n⚠️  ERROR: No se puede realizar la acción porque el registro está siendo usado en otro lugar.")
            else:
                print(f"\n⚠️  ERROR DEL SISTEMA: {msg}")
            input("\nPresione Enter para continuar...")
            return None
    return wrapper

class CRMConsole:
    def __init__(self):
        self.db = DatabaseManager()
        self.service = CRMService(self.db)
        self.schema_manager = SchemaManager(self.db)
        self.hygiene = DataHygieneService(self.db)
        self.normalizer = ContactNormalizationService(self.db)

    def run(self):
        while True:
            clear_screen()
            print_header("CRM INDELPA - Consola de Gestión")
            print(" 1. 👥 Gestión de Usuarios")
            print(" 2. 🏢 Gestión de Empresas")
            print(" 3. 📞 Vínculos Usuarios-Empresa (B2B)")
            print(" 4. 🏢 Jerarquía de Empresas (Holding)")
            print(" 5. 👥 Vínculos entre Usuarios (Google Style)")
            print(" 6. 🌍 Expansión Geográfica (Países/Deptos/Mun)")
            print(" 7. ⚙️ Configuración de Sistema (Esquema/Tags)")
            print(" 8. 🗑️ Papelera de Reciclaje")
            print(" 0. ❌ Salir")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1': self.menu_users()
            elif choice == '2': self.menu_companies()
            elif choice == '3': self.menu_relations()
            elif choice == '4': self.menu_hierarchy()
            elif choice == '5': self.menu_user_user_relations()
            elif choice == '6': self.menu_geography()
            elif choice == '7': self.menu_config()
            elif choice == '8': self.menu_trash()
            elif choice == '0': break
            
        self.db.close()

    @safe_execute
    def menu_users(self):
        while True:
            clear_screen()
            print_header("Gestión de Usuarios")
            print(" 1. Listar Usuarios")
            print(" 2. Crear Usuario")
            print(" 3. Actualizar Usuario")
            print(" 4. Eliminar Usuario (Papelera)")
            print(" 5. ✨ Combinar y Corregir (Duplicados)")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                users = self.service.u_repo.list()
                print_header("Lista de Usuarios")
                for u in users:
                    print(f"ID: {u.id} | {u.first_name} {u.last_name} | RUT/NIT: {u.rut_nit} {'(Natural)' if u.is_natural_person else ''}")
                input("\nPresione Enter para continuar...")
                
            elif choice == '2':
                print_header("Nuevo Usuario")
                fn = input("Primer Nombre: ")
                ln = input("Primer Apellido: ")
                is_nat = input("¿Es Persona Natural? (s/n): ").lower() == 's'
                tid = input("RUT/NIT: ")
                
                print("\nSeleccione Género:")
                genders = self.service.get_genders()
                for g in genders: print(f"  [{g['id']}] {g['name']}")
                gid = input("ID Género: ")
                
                u = User(first_name=fn, last_name=ln, rut_nit=tid, is_natural_person=is_nat, gender_id=int(gid) if gid else None, status_id=1)
                try:
                    uid = self.service.create_user_complete(u)
                    print(f"\n✅ Usuario creado con ID: {uid}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                input("\nPresione Enter...")
                
            elif choice == '3':
                uid = input("\nID del usuario a actualizar: ")
                print("Deje en blanco para no cambiar.")
                fn = input("Nuevo Nombre: ")
                ln = input("Nuevo Apellido: ")
                data = {}
                if fn: data['first_name'] = fn
                if ln: data['last_name'] = ln
                
                if data:
                    self.service.update_user_basic(int(uid), data)
                    print("\n✅ Usuario actualizado.")
                input("\nPresione Enter...")

            elif choice == '4':
                uid = input("\nID del usuario a ELIMINAR (Papelera): ")
                confirm = input(f"¿Está seguro de enviar al usuario {uid} a la papelera? (s/n): ")
                if confirm.lower() == 's':
                    self.service.u_repo.delete(int(uid))
                    print("\n✅ Usuario movido a la papelera.")
                input("\nPresione Enter...")

            elif choice == '5':
                self.menu_merge_users()
                
            elif choice == '0': break

    @safe_execute
    def menu_companies(self):
        while True:
            clear_screen()
            print_header("Gestión de Empresas")
            print(" 1. Listar Empresas")
            print(" 2. Crear Empresa")
            print(" 3. Actualizar Empresa")
            print(" 4. Eliminar Empresa (Papelera)")
            print(" 5. ✨ Combinar y Corregir (Duplicados)")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                comps = self.service.c_repo.list()
                print_header("Lista de Empresas")
                for c in comps:
                    print(f"ID: {c.id} | {c.legal_name} | NIT: {c.tax_id}")
                input("\nPresione Enter para continuar...")
                
            elif choice == '2':
                print_header("Nueva Empresa")
                ln = input("Razón Social: ")
                tid = input("NIT: ")
                c = Company(legal_name=ln, tax_id=tid, status_id=1)
                try:
                    cid = self.service.c_repo.insert(c)
                    print(f"\n✅ Empresa creada con ID: {cid}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                input("\nPresione Enter...")

            elif choice == '3':
                # ... lógica de actualización ...
                cid = input("\nID de la empresa a actualizar: ")
                ln = input("Nueva Razón Social (blanco para omitir): ")
                data = {}
                if ln: data['legal_name'] = ln
                if data:
                    self.service.c_repo.update(int(cid), data)
                    print("\n✅ Empresa actualizada.")
                input("\nPresione Enter...")
                
            elif choice == '4':
                cid = input("\nID de la empresa a ELIMINAR (Papelera): ")
                confirm = input(f"¿Está seguro de enviar la empresa {cid} a la papelera? (s/n): ")
                if confirm.lower() == 's':
                    self.service.c_repo.delete(int(cid))
                    print("\n✅ Empresa movida a la papelera.")
                input("\nPresione Enter...")

            elif choice == '5':
                self.menu_merge_companies()

            elif choice == '0': break

    def menu_merge_companies(self):
        print_header("Combinar y Corregir Empresas")
        dups = self.hygiene.find_company_duplicates()
        if not dups:
            print("No se encontraron empresas duplicadas.")
        else:
            for d in dups:
                print(f"\n✨ SUGERENCIA DE FUSIÓN:")
                print(f"  Empresa: {d.get('legal_name', 'N/A')} (NIT: {d.get('tax_id', d.get('rut_nit', 'N/A'))})")
                print(f"  Razon: Coincidencia en datos base")
                print(f"  Registros involucrados (IDs): {d['ids']}")
                
                print("\n⚠️  ADVERTENCIA: Esta acción es IRREVERSIBLE.")
                print("   Se conservará el ID más antiguo y se eliminarán los demás.")
                confirm = input(f"¿Desea fusionar estos registros AHORA? (s/n): ")
                
                if confirm.lower() == 's':
                    ids = [int(x) for x in d['ids'].split(',')]
                    survivor = ids[0]
                    for other in ids[1:]:
                        self.hygiene.merge_companies(survivor, other)
                        print(f"  ✅ ID {other} fusionado en el ID {survivor}")
        input("\nEnter...")

    @safe_execute
    def menu_relations(self):
        while True:
            clear_screen()
            print_header("Vínculos Corporativos (B2B)")
            print(" 1. Listar Contactos por Empresa")
            print(" 2. Vincular Usuario a Empresa")
            print(" 3. Desvincular Usuario")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                cid = input("ID de la Empresa: ")
                contacts = self.service.get_company_contacts(int(cid))
                print_header(f"Contactos de la Empresa {cid}")
                for u in contacts:
                    print(f"  - {u.first_name} {u.last_name} (ID: {u.id})")
                input("\nEnter para continuar...")

            elif choice == '2':
                uid = int(input("ID del Usuario: "))
                cid = int(input("ID de la Empresa: "))
                
                print("\n--- Lista de DEPARTAMENTOS ---")
                depts = self.service.get_departments()
                for d in depts: print(f"  [{d['id']}] {d['nombre_departamento']}")
                did = int(input("Seleccione el ID del Departamento: "))

                print("\n--- Lista de CARGOS ---")
                cargos = self.service.get_cargos()
                for cg in cargos: print(f"  [{cg['id']}] {cg['nombre_cargo']}")
                cgid = int(input("Seleccione el ID del Cargo: "))
                
                self.service.link_user_to_company(uid, cid, position_id=cgid, department_id=did)
                print("\n✅ Vínculo B2B creado exitosamente.")
                input("\nEnter...")

            elif choice == '0': break

    @safe_execute
    def menu_hierarchy(self):
        while True:
            clear_screen()
            print_header("Jerarquía de Empresas (Holding)")
            print(" 1. Vincular Empresa (Matriz -> Subsidiaria)")
            print(" 2. Listar Jerarquías Actuales")
            print(" 0. Volver")
            choice = input("\nOpción: ")
            if choice == '1':
                comps = self.service.c_repo.list()
                print_header("Empresas")
                for c in comps: print(f"  [{c.id}] {c.legal_name}")
                
                oid = int(input("\nID Empresa ORIGEN (Matriz/Jefe): "))
                did = int(input("ID Empresa DESTINO (Subsidiaria/Empleado): "))
                
                print("\nTipos de Relación Corporativa (Recíprocos):")
                types = self.service.get_company_relation_types()
                for t in types: 
                    print(f"  [{t['id']}] {t['name']} <-> {t['inverse_name'] or t['name']}")
                
                tid = int(input("Seleccione el ID del Tipo: "))
                
                try:
                    self.service.link_companies(oid, did, tid)
                    print("\n✅ Relación de Holding establecida exitosamente.")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                input("\nEnter para continuar...")
            elif choice == '0': break

    @safe_execute
    def menu_user_user_relations(self):
        while True:
            clear_screen()
            print_header("Vínculos entre Usuarios")
            print(" 1. Vincular 2 Usuarios")
            print(" 2. Ver Vínculos de un Usuario")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                print_header("Nuevo Vínculo Personal")
                users = self.service.u_repo.list()
                for u in users: print(f"  [{u.id}] {u.first_name} {u.last_name}")
                
                u1 = input("\nID Usuario 1 (Origen): ")
                u2 = input("ID Usuario 2 (Destino): ")
                
                rels = self.service.get_user_relation_types()
                print("\nTipos de relación humana disponibles:")
                for r in rels:
                    print(f"  [{r['id']}] {r['name']} <-> {r['inverse_name'] or r['name']}")
                
                rid = input("\nID del tipo de relación: ")
                label = input("Etiqueta personalizada (opcional): ")
                
                try:
                    self.service.link_users(int(u1), int(u2), int(rid), label)
                    print("\n✅ Vínculo creado exitosamente.")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                input("\nPresione Enter...")
                
            elif choice == '0': break

    @safe_execute
    def menu_config(self):
        while True:
            clear_screen()
            print_header("Configuración de Sistema")
            print(" 1. 🧬 Gestionar Columnas (Añadir)")
            print(" 2. 🧬 Gestionar Columnas (Eliminar)")
            print(" 3. 👥 Gestionar Tipos de Relación (Humanos)")
            print(" 4. 🏷️ Gestionar Etiquetas (Tags)")
            print(" 5. 🗂️ Gestionar Catálogos (Cargos, Deptos, Estados, etc.)")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                print_header("Añadir Columna Personalizada")
                table = input("Tabla (users/companies): ")
                col = input("Nombre columna (ej: favorite_sport): ")
                dname = input("Nombre a mostrar (ej: Deporte Favorito): ")
                ctype = input("Tipo (VARCHAR(255), TEXT, INT, DATE): ")
                if self.schema_manager.add_column(table, col, ctype, dname):
                    print(f"\n✅ Columna `{col}` añadida.")
                else: print("\n❌ Error al añadir.")
                input("\nEnter...")

            elif choice == '2':
                print_header("Eliminar Columna Personalizada")
                table = input("Tabla (users/companies): ")
                cols = self.schema_manager.get_custom_columns(table)
                for c in cols: print(f" - {c['column_name']} ({c['display_name']})")
                col_to_del = input("\nNombre columna a borrar: ")
                if self.schema_manager.remove_column(table, col_to_del):
                    print("\n✅ Columna eliminada.")
                else: print("\n❌ Error.")
                input("\nEnter...")

            elif choice == '3':
                self.menu_master_relations()

            elif choice == '4':
                self.menu_master_tags()

            elif choice == '5':
                self.menu_catalogs()

            elif choice == '0': break

    def menu_master_relations(self):
        while True:
            clear_screen()
            print_header("Gestionar Tipos de Relación")
            rels = self.service.get_user_relation_types()
            for r in rels:
                print(f"  [{r['id']}] {r['name']} <-> {r['inverse_name']}")
            
            print("\n 1. Añadir Tipo de Relación")
            print(" 2. Eliminar Tipo de Relación")
            print(" 0. Volver")
            
            c = input("\nOpción: ")
            if c == '1':
                name = input("Nombre (ej: Padre): ")
                inv = input("Nombre Inverso (ej: Hijo): ")
                if name and inv:
                    self.service.add_user_relation_type(name, inv)
                    print("✅ Añadido.")
                input("\nEnter...")
            elif c == '2':
                rid = input("ID a eliminar: ")
                if rid:
                    self.service.delete_user_relation_type(int(rid))
                    print("✅ Eliminado.")
                input("\nEnter...")
            elif c == '0': break

    def menu_master_tags(self):
        while True:
            clear_screen()
            print_header("Gestionar Etiquetas (Tags)")
            tags = self.service.get_tags()
            for t in tags:
                print(f"  [{t['id']}] {t['name']} ({t['color']})")
            
            print("\n 1. Añadir Etiqueta")
            print(" 2. Eliminar Etiqueta")
            print(" 0. Volver")
            
            c = input("\nOpción: ")
            if c == '1':
                name = input("Nombre de etiqueta: ")
                color = input("Color (HEX, ej: #FF5733): ") or '#808080'
                if name:
                    self.service.add_tag(name, color)
                    print("✅ Añadida.")
                input("\nEnter...")
            elif c == '2':
                tid = input("ID a eliminar: ")
                if tid:
                    self.service.delete_tag(int(tid))
                    print("✅ Eliminada.")
                input("\nEnter...")
            elif c == '0': break

    @safe_execute
    def menu_catalogs(self):
        tables = {
            '1': ('cargos', 'nombre_cargo', 'Cargos'),
            '2': ('departamentos_empresa', 'nombre_departamento', 'Departamentos'),
            '3': ('status_types', 'name', 'Estados o Status'),
            '4': ('genders', 'name', 'Géneros')
        }
        while True:
            clear_screen()
            print_header("Gestión de Catálogos")
            for k, v in tables.items(): print(f" {k}. {v[2]}")
            print(" 0. Volver")
            
            sel = input("\nSeleccione el catálogo a gestionar: ")
            if sel == '0': break
            
            if sel in tables:
                table, field, title = tables[sel]
                self.submenu_generic_lookup(table, field, title)

    def submenu_generic_lookup(self, table, field, title):
        while True:
            clear_screen()
            print_header(f"Gestión de {title}")
            data = self.service.get_lookup_data(table)
            for item in data:
                print(f"  [{item['id']}] {item.get(field, 'N/A')}")
            
            print(f"\n 1. Añadir a {title}")
            print(f" 2. Eliminar de {title}")
            print(" 0. Volver")
            
            c = input("\nOpción: ")
            if c == '1':
                val = input(f"Nuevo valor para {title}: ")
                if val:
                    self.service.add_lookup_item(table, {field: val})
                    print("✅ Añadido.")
                input("\nEnter...")
            elif c == '2':
                iid = input("ID a eliminar: ")
                if iid:
                    self.service.delete_lookup_item(table, int(iid))
                    print("✅ Eliminado.")
                input("\nEnter...")
            elif c == '0': break

    @safe_execute
    def menu_trash(self):
        while True:
            clear_screen()
            print_header("Papelera de Reciclaje")
            print(" 1. Ver Usuarios en Papelera")
            print(" 2. Ver Empresas en Papelera")
            print(" 3. 💣 VACÍAR Papelera de Usuarios")
            print(" 4. 💣 VACÍAR Papelera de Empresas")
            print(" 0. Volver")
            
            c = input("\nSeleccione: ")
            if c == '1': self.submenu_trash_list('users')
            elif c == '2': self.submenu_trash_list('companies')
            elif c == '3':
                confirm = input("¿Está REALMENTE seguro de purgar TODOS los usuarios borrados? (s/n): ")
                if confirm.lower() == 's':
                    self.hygiene.purge_trash('users')
                    print("💥 Papelera de usuarios vaciada.")
                    input("\nEnter...")
            elif c == '4':
                confirm = input("¿Está REALMENTE seguro de purgar TODAS las empresas borradas? (s/n): ")
                if confirm.lower() == 's':
                    self.hygiene.purge_trash('companies')
                    print("💥 Papelera de empresas vaciada.")
                    input("\nEnter...")
            elif c == '0': break

    def submenu_trash_list(self, table):
        items = self.hygiene.list_trash(table)
        print_header(f"Borrados en {table}")
        for i in items:
            name = i.get('first_name', '') + ' ' + i.get('last_name', '') if table == 'users' else i.get('legal_name', '')
            print(f"  [{i['id']}] {name} - Borrado el: {i['deleted_at']}")
        
        print("\n 1. Restaurar")
        print(" 2. Eliminar Definitivamente (PUGAR)")
        print(" 0. Volver")
        o = input("\nOpción: ")
        if o == '1':
            iid = input("ID a restaurar: ")
            self.hygiene.restore_item(table, int(iid))
            print("✅ Restaurado.")
            input("\nEnter...")
        elif o == '2':
            iid = input("ID a PURGAR definitivamente: ")
            confirm = input(f"¿Está REALMENTE seguro de eliminar permanentemente el ID {iid}? No hay marcha atrás. (s/n): ")
            if confirm.lower() == 's':
                self.hygiene.permanent_delete_item(table, int(iid))
                print("🔥 Registro eliminado permanentemente.")
            input("\nEnter...")

    def menu_merge_users(self):
        print_header("Combinar y Corregir Usuarios")
        dups = self.hygiene.find_user_duplicates()
        if not dups:
            print("No se encontraron duplicados mediante inteligencia de datos.")
        else:
            for d in dups:
                print(f"\n✨ SUGERENCIA DE FUSIÓN:")
                print(f"  Motivo: {d['reason']}")
                if 'first_name' in d:
                    print(f"  Nombre: {d['first_name']} {d['last_name']}")
                print(f"  Registros involucrados (IDs): {d['ids']}")
                
                print("\n⚠️  ADVERTENCIA: Al combinar, se conservará un solo registro.")
                print("   Los datos de contacto de los duplicados se moverán al principal.")
                print("   Los registros duplicados serán enviados a la PAPELERA.")
                confirm = input(f"¿Desea proceder con la fusión? (s/n): ")
                
                if confirm.lower() == 's':
                    ids = [int(x) for x in d['ids'].split(',')]
                    survivor = ids[0]
                    for other in ids[1:]:
                        self.hygiene.merge_users(survivor, other)
                        print(f"  ✅ ID {other} fusionado con éxito en el ID {survivor}")
        input("\nEnter...")

    @safe_execute
    def menu_geography(self):
        while True:
            clear_screen()
            print_header("Expansión Geográfica")
            print(" 1. Listar Países")
            print(" 2. Añadir Nuevo País (+ Prefijo)")
            print(" 3. Añadir Departamento (Estado)")
            print(" 4. Añadir Municipio (Ciudad)")
            print(" 0. Volver")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '1':
                countries = self.service.list_countries()
                print_header("Catálogo de Países")
                for c in countries:
                    print(f"  [{c['id']}] {c['country_name']} (Prefijo: +{c['phone_code']})")
                input("\nEnter para continuar...")
                
            elif choice == '2':
                name = input("Nombre del País: ")
                code = input("Prefijo Telefónico (sin +): ")
                self.service.add_country(name, code)
                print(f"✅ País {name} registrado y normalizador actualizado.")
                input("\nEnter...")
                
            elif choice == '3':
                countries = self.service.list_countries()
                for c in countries: print(f"  [{c['id']}] {c['country_name']}")
                cid = input("ID del País al que pertenece: ")
                name = input("Nombre del Departamento: ")
                self.service.add_state(name, int(cid))
                print(f"✅ Departamento {name} registrado.")
                input("\nEnter...")
                
            elif choice == '4':
                # Quick lookup for country then state
                cid = input("ID del País: ")
                states = self.service.list_states(int(cid))
                for s in states: print(f"  [{s['id']}] {s['state_name']}")
                sid = input("ID del Departamento: ")
                name = input("Nombre del Municipio: ")
                self.service.add_city(name, int(sid))
                print(f"✅ Municipio {name} registrado.")
                input("\nEnter...")
                
            elif choice == '0': break

if __name__ == "__main__":
    app = CRMConsole()
    app.run()
