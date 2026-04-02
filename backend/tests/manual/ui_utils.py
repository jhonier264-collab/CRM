
import os
import msvcrt

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("=" * 60)
    print(f" {title.center(58)}")
    print("=" * 60 + "\n")

def get_masked_input(prompt):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in [b'\r', b'\n']:
            print()
            break
        elif char == b'\x08': # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        else:
            password += char.decode('utf-8')
            print('*', end='', flush=True)
    return password

def safe_execute(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\n⚠️  ERROR: {str(e)}")
            input("\nPresione Enter para continuar...")
            return None
    return wrapper

def interactive_editor(title, current_data, fields_config, service=None):
    """
    Editor interactivo genérico.
    """
    temp_data = current_data.copy()
    while True:
        clear_screen()
        print_header(title)
        print("Seleccione el número del campo para editar:\n")
        
        for i, config in enumerate(fields_config, 1):
            key = config['key']
            val = temp_data.get(key, '')
            
            # Si es una etiqueta separadora, solo imprimir
            if config.get('type') == 'label':
                print(f"\n {config['label']}")
                continue

            # Mostrar valor basado en el tipo
            if config.get('type') == 'masked' and val:
                display_val = '*' * 8
            elif config.get('type') == 'location' and service:
                cid = temp_data.get('country_id')
                sid = temp_data.get('state_id')
                cityid = temp_data.get('city_id')
                display_val = f"País:{cid or '?'} Dept:{sid or '?'} Mun:{cityid or '?'}"
            elif isinstance(val, list):
                display_val = f"[{len(val)} ítems]"
            else:
                display_val = val

            # Lookups
            if config.get('lookup') and service and val:
                items = []
                ln = config['lookup']
                # Mapeo dinámico de métodos de lookup
                method_name = f"get_{ln}"
                if hasattr(service, method_name):
                    items = getattr(service, method_name)()
                
                name_key = 'country_name' if ln == 'countries' else 'name'
                match = next((x[name_key] for x in items if str(x['id']) == str(val)), val)
                display_val = f"[{val}] {match}"

            print(f" {i:2d}. {config['label']:.<40} {display_val}")
            
        print(f"\n s. 💾 GUARDAR CAMBIOS")
        print(f" c. ❌ CANCELAR")
        
        choice = input("\nSeleccione una opción: ").lower()
        if choice == 's': return temp_data
        elif choice == 'c': return None
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(fields_config):
                conf = fields_config[idx]
                if conf.get('type') == 'label': continue

                # Submenús
                if conf.get('type') == 'submenu' and service:
                    handler = conf.get('handler')
                    # Esto requiere que los handlers estén disponibles o se pasen
                    # Por ahora lo dejaremos para ser manejado afuera si es complejo, 
                    # o inyectaremos una función de despacho.
                    if 'submenu_dispatcher' in temp_data:
                        temp_data['submenu_dispatcher'](temp_data, conf, service)
                    continue

                # Lookups
                if conf.get('lookup') and service:
                    print(f"\n--- SELECCIONE {conf['label'].upper()} ---")
                    items = []
                    ln = conf['lookup']
                    method_name = f"get_{ln}"
                    if hasattr(service, method_name):
                        items = getattr(service, method_name)()
                    
                    name_key = 'country_name' if ln == 'countries' else 'name'
                    for item in items: print(f" [{item['id']}] {item[name_key]}")
                    
                    new_val_str = input(f"\nIngrese el ID (o Enter para omitir): ")
                    new_val = int(new_val_str) if new_val_str.strip() else None
                elif conf.get('type') == 'location' and service:
                    loc = select_location_flow(service)
                    if loc: temp_data.update(loc)
                    continue
                elif conf.get('type') == 'bool':
                    new_val = input(f"{conf['label']} (s/n): ").lower() == 's'
                elif conf.get('type') == 'masked':
                    new_val = get_masked_input(f"Nuevo {conf['label']}: ")
                else:
                    new_val = input(f"Nuevo {conf['label']}: ")
                
                temp_data[conf['key']] = new_val
    return None

def select_location_flow(service):
    """Flujo jerárquico de ubicación."""
    print("\n--- SELECCIÓN DE UBICACIÓN ---")
    countries = service.get_countries()
    for c in countries: print(f" [{c['id']}] {c['country_name']}")
    cid_str = input("\nID País (o Enter): ")
    if not cid_str.strip(): return None
    cid = int(cid_str)
    
    states = service.get_states(cid)
    for s in states: print(f" [{s['id']}] {s['state_name']}")
    sid_str = input("\nID Depto (o Enter): ")
    sid = int(sid_str) if sid_str.strip() else None
    
    city_id = None
    if sid:
        cities = service.get_cities(sid)
        for ci in cities: print(f" [{ci['id']}] {ci['city_name']}")
        city_str = input("\nID Ciudad (o Enter): ")
        city_id = int(city_str) if city_str.strip() else None
        
    return {'country_id': cid, 'state_id': sid, 'city_id': city_id}

def manage_list_flow(title, current_list, fields, service):
    """Gestor genérico de listas."""
    while True:
        clear_screen()
        print_header(f"GESTIÓN: {title}")
        for i, item in enumerate(current_list, 1):
            # Mostrar primer valor no ID como descripción
            desc = next((v for k, v in item.items() if k != 'id' and not k.endswith('_id')), "Item")
            print(f" {i}. {desc}")
            
        print("\n n. ➕ Añadir | d. 🗑️ Eliminar | v. ✅ Volver")
        opt = input("\nSeleccione: ").lower()
        if opt == 'v': return current_list
        elif opt == 'n':
            new_item = interactive_editor(f"NUEVO {title[:-1]}", {}, fields, service)
            if new_item: current_list.append(new_item)
        elif opt == 'd':
            idx = input("ID a eliminar: ")
            if idx.isdigit() and 1 <= int(idx) <= len(current_list): current_list.pop(int(idx)-1)
        elif opt.isdigit():
            idx = int(opt)-1
            if 0 <= idx < len(current_list):
                updated = interactive_editor(f"EDITAR {title[:-1]}", current_list[idx], fields, service)
                if updated: current_list[idx] = updated
