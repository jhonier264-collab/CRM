
# Centralización de configuraciones de campos para el editor interactivo

USER_FIELDS = [
    {'label': '--- DATOS BÁSICOS ---', 'key': '_sep1', 'type': 'label'},
    {'label': 'Prefijo', 'key': 'prefix', 'type': 'str'},
    {'label': 'Primer Nombre', 'key': 'first_name', 'type': 'str'},
    {'label': 'Segundo Nombre', 'key': 'middle_name', 'type': 'str'},
    {'label': 'Primer Apellido', 'key': 'last_name', 'type': 'str'},
    {'label': '--- CONTACTOS ---', 'key': '_sep2', 'type': 'label'},
    {'label': '📱 📧 🏠 GESTIONAR CONTACTOS', 'key': '_contacts', 'type': 'submenu', 'handler': 'manage_contacts'},
    {'label': '--- EMPRESA / CARGO ---', 'key': '_sep3', 'type': 'label'},
    {'label': '🏢 VÍNCULOS PROFESIONALES', 'key': 'user_companies', 'type': 'submenu', 'handler': 'manage_professional_links'},
    {'label': '--- OTROS DATOS ---', 'key': '_sep4', 'type': 'label'},
    {'label': 'RUT/NIT', 'key': 'rut_nit', 'type': 'str'},
    {'label': 'Género', 'key': 'gender_id', 'lookup': 'genders'},
    {'label': 'Rol del Sistema', 'key': 'role_id', 'lookup': 'roles'},
    {'label': 'Estado', 'key': 'status_id', 'lookup': 'statuses'},
    {'label': 'Username (Staff)', 'key': 'username', 'type': 'str'},
    {'label': 'Contraseña (Staff)', 'key': 'password', 'type': 'masked'},
    {'label': 'Confirmar Contraseña', 'key': 'password_confirm', 'type': 'masked'},
    {'label': 'Notas', 'key': 'notes', 'type': 'str'},
]

COMPANY_FIELDS = [
    {'label': 'Nombre Legal', 'key': 'legal_name', 'type': 'str'},
    {'label': 'Nombre Comercial', 'key': 'commercial_name', 'type': 'str'},
    {'label': 'RUT/NIT', 'key': 'rut_nit', 'type': 'str'},
    {'label': '--- CONTACTOS ---', 'key': '_sep1', 'type': 'label'},
    {'label': '📱 📧 🏠 GESTIONAR CONTACTOS', 'key': '_contacts', 'type': 'submenu', 'handler': 'manage_contacts'},
    {'label': '--- OTROS ---', 'key': '_sep2', 'type': 'label'},
    {'label': 'Web/Dominio', 'key': 'domain', 'type': 'str'},
    {'label': 'Descripción', 'key': 'description', 'type': 'str'},
    {'label': 'Ingresos Anuales', 'key': 'revenue', 'type': 'str'},
    {'label': 'Estado', 'key': 'status_id', 'lookup': 'statuses'},
]

PHONE_FIELDS = [
    {'label': 'Número', 'key': 'local_number', 'type': 'str'},
    {'label': 'Etiqueta', 'key': 'label_id', 'lookup': 'labels'}
]

EMAIL_FIELDS = [
    {'label': 'Email', 'key': 'email_address', 'type': 'str'},
    {'label': 'Etiqueta', 'key': 'label_id', 'lookup': 'labels'}
]

ADDRESS_FIELDS = [
    {'label': 'Línea 1', 'key': 'address_line1', 'type': 'str'},
    {'label': 'Línea 2', 'key': 'address_line2', 'type': 'str'},
    {'label': 'Cód. Postal', 'key': 'postal_code', 'type': 'str'},
    {'label': 'Ubicación', 'key': 'country_id', 'type': 'location'}
]

PROFESSIONAL_LINK_FIELDS = [
    {'label': 'Empresa', 'key': 'company_id', 'lookup': 'companies'},
    {'label': 'Cargo/Posición', 'key': 'position_id', 'lookup': 'positions'},
    {'label': 'Departamento', 'key': 'company_department_id', 'lookup': 'departments'},
    {'label': 'Es Contacto Principal', 'key': 'is_main_contact', 'type': 'bool'}
]

COUNTRY_FIELDS = [
    {'label': 'Nombre del País', 'key': 'country_name', 'type': 'str'},
    {'label': 'Código de Llamada', 'key': 'phone_code', 'type': 'str'},
    {'label': 'Área (km2)', 'key': 'area_km2', 'type': 'str'},
    {'label': 'Población', 'key': 'population', 'type': 'str'},
]

COMPANY_RELATION_FIELDS = [
    {'label': 'Empresa Matriz', 'key': 'parent_company_id', 'lookup': 'companies'},
    {'label': 'Empresa Subsidiaria', 'key': 'child_company_id', 'lookup': 'companies'},
    {'label': 'Tipo de Relación', 'key': 'relation_type_id', 'lookup': 'company_relation_types'},
]

USER_RELATION_FIELDS = [
    {'label': 'Usuario Origen', 'key': 'from_user_id', 'lookup': 'users'},
    {'label': 'Usuario Destino', 'key': 'to_user_id', 'lookup': 'users'},
    {'label': 'Relación', 'key': 'relation_type_id', 'lookup': 'user_relation_types'},
    {'label': 'Etiqueta Personalizada', 'key': 'custom_label', 'type': 'str'},
]
