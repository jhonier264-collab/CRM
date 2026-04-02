import os
import sys
from dotenv import load_dotenv # Carga de variables de entorno

# Carga de configuración desde archivo .env en la raíz del proyecto
# Se hace lo más pronto posible para que las variables estén disponibles para los módulos importados
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Forzar que el directorio 'backend' esté en el path para encontrar 'src'
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import logging  # Gestión de logs
from typing import List, Optional, Dict, Any # Tipado estático
from fastapi import FastAPI, HTTPException, Depends, Security, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware # Política de CORS
from pydantic import BaseModel # Validación de esquemas de datos
import jwt # PyJWT

# Importación de componentes del núcleo
from src.core.database_manager import DatabaseManager
from src.core.responses import ApiResponse
from src.services.services import CRMService
from src.services.data_hygiene_service import DataHygieneService
from src.models.models import User, Company, Phone, Email, Address
# Auth & Provisioning Imports
from src.lib.shared_auth.services import AuthCore, validar_rut_colombia
from src.lib.shared_auth.interfaces import IAuthRepository
from src.lib.shared_auth.security import SessionManager # Import Token Logic
from src.repositories.auth_repository import AuthRepository
from src.services.provisioning_service import ProvisioningService
from src.core.mysql_repository import MySQLRepository
from src.core.exceptions import DuplicateError, ValidationError, CRMError

# Configuración centralizada de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancia de la aplicación FastAPI
app = FastAPI(
    title="CRM Industrial API - Pro Edition", 
    version="2.0.0",
    description="API Refactorizada con estándares profesionales de respuesta y serialización.",
    strict_slashes=False
)

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- INYECCIÓN DE DEPENDENCIAS ---

def get_db():
    """Generador de conexiones a la base de datos por petición."""
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decodifica el token JWT y extrae la información del usuario."""
    try:
        payload = SessionManager.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciales de autenticación inválidas")

def get_service(db: DatabaseManager = Depends(get_db), token: str = Security(oauth2_scheme, scopes=[])):
    """
    Inyecta el servicio orquestador CRM con CONTEXTO DE TENANT.
    Extrae el tenant_db del token y configura la conexión.
    """
    user_payload = get_current_user(token)
    tenant_db = user_payload.get('tenant_db')
    
    if not tenant_db:
        config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('MASTER_DB_NAME') or 'master_db',
            'port': int(os.getenv('DB_PORT', 3306))
        }
        repo_auth = AuthRepository(MySQLRepository(config))
        user_data = None
        username = user_payload.get('sub')
        if username:
            user_data = repo_auth.get_user_by_identifier(username)
        
        if user_data:
            tenant_db = user_data.get('tenant_db')

    if tenant_db:
        db.switch_database(tenant_db)
    
    return CRMService(db)

def get_service_public(db: DatabaseManager = Depends(get_db)):
    """Para endpoints que no requieren auth o tenant específico."""
    return CRMService(db)

def get_hygiene(db: DatabaseManager = Depends(get_db)):
    """Inyecta el servicio de higiene y recuperación de datos."""
    return DataHygieneService(db)

def get_auth_service():
    """Inyecta el servicio de autenticación."""
    # Nota: En un entorno real, la config vendría de Environment o ConfigProvider
    # Por ahora reconstruimos el repo con la config del .env
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('MASTER_DB_NAME') or 'master_db',
        'port': int(os.getenv('DB_PORT', 3306))
    }
    db_repo = MySQLRepository(config)
    auth_repo = AuthRepository(db_repo)
    return AuthCore(auth_repo)

def get_provisioning_service():
    """Inyecta el servicio de aprovisionamiento de tenants."""
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('MASTER_DB_NAME') or 'master_db',
        'port': int(os.getenv('DB_PORT', 3306))
    }
    db_repo = MySQLRepository(config)
    return ProvisioningService(db_repo)

# --- MODELOS DE ENTRADA (ESQUEMAS PYDANTIC) ---

class PhoneInput(BaseModel):
    """Esquema para entrada de números telefónicos."""
    local_number: str
    label_id: int = 1
    country_id: Optional[int] = 1

class EmailInput(BaseModel):
    """Esquema para entrada de correos electrónicos."""
    email_address: str
    label_id: int = 1

class AddressInput(BaseModel):
    """Esquema para entrada de direcciones."""
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    country_id: Optional[int] = None
    label_id: int = 1
    postal_code: Optional[str] = None

class UserCreate(BaseModel):
    """Esquema para creación de usuario completo."""
    first_name: str
    last_name: str
    tax_id: Optional[str] = None
    status_id: int = 1
    is_natural_person: bool = True
    phones: List[PhoneInput] = []
    emails: List[EmailInput] = []
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    prefix: Optional[str] = None
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    nickname: Optional[str] = None
    phonetic_first_name: Optional[str] = None
    phonetic_middle_name: Optional[str] = None
    phonetic_last_name: Optional[str] = None
    file_as: Optional[str] = None
    birthday: Optional[str] = None # ISO format date
    gender_id: Optional[int] = None
    notes: Optional[str] = None
    tags: List[Dict[str, Any]] = []
    companies: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []

class TagCreate(BaseModel):
    name: str
    color: Optional[str] = '#808080'

class CompanyCreate(BaseModel):
    """Esquema para creación de empresa completa."""
    legal_name: str
    commercial_name: Optional[str] = None
    rut_nit: Optional[str] = None
    verification_digit: Optional[int] = None
    domain: Optional[str] = None
    status_id: int = 1
    agent_id: Optional[int] = None
    company_department_id: Optional[int] = None
    revenue: float = 0.0
    employee_count: Optional[int] = 0
    description: Optional[str] = None
    phones: List[PhoneInput] = []
    emails: List[EmailInput] = []
    economic_activity_code: Optional[int] = None
    addresses: List[AddressInput] = []
    tags: List[Dict[str, Any]] = []
    employees: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []

# Auth Schemas
class LoginInput(BaseModel):
    identifier: Optional[str] = None
    username: Optional[str] = None
    password: str

class RegisterInput(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    account_type: str = 'INDIVIDUAL'
    rut: Optional[str] = None

class RutValidationInput(BaseModel):
    rut: str

class RecoveryInput(BaseModel):
    email: str

# --- ENDPOINTS DE LA API ---

@app.get("/health")
def health_check(db: DatabaseManager = Depends(get_db)):
    """Verifica la salud de la API y la conexión a la base de datos."""
    try:
        # Intento de consulta simple para validar conectividad real
        db.execute_query("SELECT 1")
        return {
            "status": "ok",
            "db_connected": True,
            "message": "Servidor y Base de Datos operativos."
        }
    except Exception as e:
        logger.error(f"Fallo en Health Check de BD: {e}")
        return {
            "status": "degraded",
            "db_connected": False,
            "error": str(e)
        }

@app.get("/")
def welcome():
    """Ruta raíz para verificar que el API está funcionando."""
    return {
        "status": "online",
        "message": "Bienvenido al CRM API Industrial",
        "version": "2.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }

# --- MÓDULO DE AUTENTICACIÓN Y APROVISIONAMIENTO ---

@app.post("/auth/login")
def login(data: LoginInput, auth: AuthCore = Depends(get_auth_service)):
    identity = data.identifier or data.username
    if not identity:
        return ApiResponse.error(message="Se requiere usuario o email", status_code=422)
        
    result = auth.authenticate(identity, data.password)
    if result.get('authenticated'):
        return ApiResponse.success(data=result, message="Inicio de sesión exitoso.")
    return ApiResponse.error(message=result.get('error'), status_code=401)

@app.post("/auth/register")
def register(data: RegisterInput, provisioning: ProvisioningService = Depends(get_provisioning_service)):
    """Registro público que dispara el aprovisionamiento de tenant."""
    try:
        # Adaptar el input al formato que espera provisioning_service
        tenant_data = {
            "username": data.username,
            "email": data.email,
            "password": data.password,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "account_type": data.account_type,
            "rut": data.rut
        }
        
        # Validar RUT si es empresa (Doble check backend)
        if data.account_type == 'COMPANY' and data.rut:
             if not validar_rut_colombia(data.rut):
                 return ApiResponse.error(message="RUT inválido (Validación Backend).")

        result = provisioning.create_tenant(tenant_data)
        if result:
             # Auto-login simulation logic could go here, for now just success
             return ApiResponse.success(message="Cuenta creada y entorno aprovisionado exitosamente.")
        return ApiResponse.error(message="Error desconocido durante el aprovisionamiento.")
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return ApiResponse.error(message=str(e))

@app.post("/auth/validate-rut")
def validate_rut_endpoint(data: RutValidationInput):
    is_valid = validar_rut_colombia(data.rut)
    return ApiResponse.success(data={"isValid": is_valid})

@app.post("/auth/recovery/request")
def recovery_request(data: RecoveryInput, auth: AuthCore = Depends(get_auth_service)):
    success, msg = auth.request_password_recovery(data.email)
    if success:
        return ApiResponse.success(message=msg)
    return ApiResponse.error(message=msg)

class PasswordResetInput(BaseModel):
    identifier: str
    token: str
    new_password: str

@app.post("/auth/recovery/reset")
def password_reset(data: PasswordResetInput, auth: AuthCore = Depends(get_auth_service)):
    success, msg = auth.reset_password(data.identifier, data.token, data.new_password)
    if success:
        return ApiResponse.success(message=msg)
    return ApiResponse.error(message=msg)

# --- MÓDULO DE USUARIOS ---

@app.get("/users")
def list_users(service: CRMService = Depends(get_service)):
    """Lista todos los usuarios activos con resumen de contacto."""
    try:
        data = service.get_users_summary()
        return ApiResponse.success(data=data)
    except Exception as e:
        return ApiResponse.error(message="Error al listar usuarios", data=str(e))

    # Removed duplicate get_user_detail route, using the one at line 321

@app.post("/users")
def create_user(user_data: UserCreate, service: CRMService = Depends(get_service), auth_service: AuthCore = Depends(get_auth_service)):
    """Crea un usuario completo (maestro + contactos) en una transacción."""
    try:
        # 1. Crear Usuario Global (Master DB)
        # Necesitamos el tenant_db actual para vincularlo? 
        # Si es un empleado, el tenant_db es el del contexto actual.
        # Pero AuthRepository register_user lo pide.
        # Por ahora asumimos que los empleados pertenecen al tenant donde se crean.
        # Sin embargo, el tenant_db en global_users a veces es para el "dueño" del tenant.
        # Para empleados, tenant_db puede ser NULL si soportamos multi-tenant real (un user en varios tenants).
        # Pero bajo el modelo actual (siloed), asignamos el tenant actual.
        # Obtenemos nombre de DB actual desde el servicio
        current_db = service.db.connection.database if service.db.connection else None
        
        # Derive username and email if not provided
        uname = user_data.username
        if not uname:
            if user_data.emails:
                uname = user_data.emails[0].email_address.split('@')[0]
            else:
                uname = f"{user_data.first_name.lower()}.{user_data.last_name.lower()}"
        
        primary_email = user_data.emails[0].email_address if user_data.emails else f"{uname}@placeholder.com"

        global_data = {
            "username": uname,
            "email": primary_email,
            "password": user_data.password or "123456",
            "tenant_db": current_db,
            "account_type": "INDIVIDUAL", # Empleado
            "rut": user_data.tax_id
        }
        
        success, result_id = auth_service.create_global_user(global_data)
        if not success:
             return ApiResponse.error(message=f"Error creando usuario global: {result_id}")
             
        global_user_id = int(result_id)

        # 2. Crear Usuario Local vinculándolo
        u = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            rut_nit=user_data.tax_id,
            status_id=user_data.status_id,
            is_natural_person=user_data.is_natural_person,
            role_id=user_data.role_id,
            prefix=user_data.prefix,
            middle_name=user_data.middle_name,
            suffix=user_data.suffix,
            nickname=user_data.nickname,
            phonetic_first_name=user_data.phonetic_first_name,
            phonetic_middle_name=user_data.phonetic_middle_name,
            phonetic_last_name=user_data.phonetic_last_name,
            file_as=user_data.file_as,
            gender_id=user_data.gender_id,
            notes=user_data.notes
        )
        if user_data.birthday:
            from datetime import datetime
            try:
                u.birthday = datetime.fromisoformat(user_data.birthday)
            except: pass

        phones = [Phone(local_number=p.local_number, label_id=p.label_id) for p in user_data.phones]
        emails = [Email(email_address=e.email_address, label_id=e.label_id) for e in user_data.emails]
        
        # Convert tags payload to tag_ids since create_user_complete expects it
        tag_ids = [t['id'] for t in user_data.tags if 'id' in t]
        
        user_id = service.create_user_complete(u, phones=phones, emails=emails, global_user_id=global_user_id, tag_ids=tag_ids)
        
        # 3. Guardar vínculos en 1-paso reutilizando update_user_complete
        update_data = {}
        if user_data.tags: update_data['tags'] = user_data.tags
        if user_data.companies: update_data['companies'] = user_data.companies
        if user_data.relationships: update_data['relationships'] = user_data.relationships
        if update_data:
             service.update_user_complete(user_id, update_data)
             
        return ApiResponse.success(data={"id": user_id, "global_id": global_user_id}, message="Usuario creado satisfactoriamente.")
    except DuplicateError as de:
        return ApiResponse.error(message=str(de), status_code=409)
    except CRMError as ce:
        return ApiResponse.error(message=str(ce), status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado creando usuario: {e}")
        return ApiResponse.error(message=f"Error inesperado al crear el usuario: {str(e)}")


@app.post("/companies/parse-rut")
async def parse_rut_endpoint(file: UploadFile = File(...), service: CRMService = Depends(get_service)):
    """Procesa un PDF de RUT y extrae los datos refinados."""
    try:
        filename = file.filename
        logger.info(f"Procesando RUT: {filename}")
        content = await file.read()
        
        if not content:
            return ApiResponse.error(message="El archivo está vacío o no es un PDF válido.", status_code=400)
            
        data = service.parse_rut(content)
        
        # Validación de campos mínimos para evitar falsos positivos
        if not data.get('rut_nit') and not data.get('legal_name'):
             logger.warning(f"RUT {filename} procesado pero no se detectaron campos clave (NIT/Razón Social).")
             return ApiResponse.error(message="No se pudieron identificar datos en este RUT. Verifique que el archivo sea un PDF legible del RUT.", status_code=422)

        return ApiResponse.success(data=data, message="RUT procesado exitosamente.")
    except Exception as e:
        logger.error(f"Error crítico parsing RUT ({file.filename}): {e}", exc_info=True)
        return ApiResponse.error(message=f"Error técnico al procesar el RUT: {str(e)}", status_code=500)

@app.delete("/users/{user_id}/companies/{company_id}")
def unlink_user_company(user_id: int, company_id: int, service: CRMService = Depends(get_service)):
    """Remueve el vínculo entre un usuario y una empresa."""
    try:
        service.unlink_user_from_company(user_id, company_id)
        return ApiResponse.success(message="Vínculo eliminado correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

class UserRelationInput(BaseModel):
    target_user_id: int
    relation_type_id: int
    custom_label: Optional[str] = None

@app.post("/users/{user_id}/relate")
def link_users_rel(user_id: int, data: UserRelationInput, service: CRMService = Depends(get_service)):
    """Crea una relación entre dos usuarios."""
    try:
        service.link_users(user_id, data.target_user_id, data.relation_type_id, data.custom_label)
        return ApiResponse.success(message="Usuarios vinculados correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.delete("/users/{user_id}/relate/{target_id}")
def unlink_users_rel(user_id: int, target_id: int, service: CRMService = Depends(get_service)):
    """Elimina una relación entre dos usuarios."""
    try:
        service.unlink_users(user_id, target_id)
        return ApiResponse.success(message="Vínculo eliminado correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.get("/users/{user_id}")
def get_user_detail(user_id: int, service: CRMService = Depends(get_service)):
    """Obtiene el detalle profundo de un usuario (direcciones, empresas vinculadas, etc)."""
    detail = service.get_user_detail_full(user_id)
    if not detail:
        return ApiResponse.not_found(message="El usuario solicitado no existe.")
    return ApiResponse.success(data=detail)

@app.put("/users/{user_id}")
def update_user_complete(user_id: int, data: Dict[str, Any], service: CRMService = Depends(get_service), auth_service: AuthCore = Depends(get_auth_service)):
    """Actualiza y sincroniza el perfil completo del usuario."""
    try:
        # Handle Password Update separately via Auth Service (Master DB)
        if 'plain_password' in data and data['plain_password']:
             # Need to find the global_user_id. The user_id passed here is the tenant-local ID.
             # We need to look up the local user to get their global_user_id.
             user_local = service.u_repo.get_by_id(user_id)
             if user_local and user_local.get('global_user_id'):
                 success = auth_service.update_password(user_local['global_user_id'], data['plain_password'])
                 if not success:
                     return ApiResponse.error(message="No se pudo actualizar la contraseña global.")
             else:
                 logger.warning(f"Intento de cambio de clave para usuario local {user_id} sin global_user_id vinculado.")

        # Sync Profile Data & Access Control (Master DB)
        # We need the user's global_user_id
        user_local = service.u_repo.get_by_id(user_id)
        if user_local and user_local.get('global_user_id'):
            gid = user_local['global_user_id']
            
            # 1. Sync Email/Username
            updates = {}
            if 'username' in data: # Usually immutable, but if allowed:
                updates['username'] = data['username']
            if 'emails' in data and len(data['emails']) > 0:
                 # Assume primary email is the first one
                 updates['email'] = data['emails'][0]['email_address']
            
            if updates:
                auth_service.sync_global_user(gid, updates)

            # 2. Check Role Downgrade (Revoke Access)
            if 'role_id' in data:
                new_role = int(data['role_id'])
                # Roles with Access: 1=Admin, 2=Agent, 3=Special (Example IDs, adjust as per DB)
                # Roles without Access: 4=Client, 5=Visitor, etc.
                PRIVILEGED_ROLES = {1, 2, 3}
                
                # Check previous role to see if they HAD access? 
                # Or just ensure: If New Role is NOT privileged, revoke access.
                # If New Role IS privileged, ensure access (maybe they were blocked?) -> Optional: Reactivate
                
                if new_role not in PRIVILEGED_ROLES:
                    logger.info(f"Revoking global access for user {user_id} (Global: {gid}) due to role change to {new_role}")
                    auth_service.revoke_access(gid)
                else:
                    # Optional: Re-enable if they are promoted back? 
                    # auth_service.repository.set_user_active_status(gid, True)
                    pass

        # Remove password from payload before passing to local service update
        data.pop('plain_password', None)
        
        service.update_user_complete(user_id, data)
        return ApiResponse.success(message="Perfil y contactos actualizados correctamente.")
    except Exception as e:
        return ApiResponse.error(message=f"Error durante la actualización: {str(e)}")

@app.delete("/users/{user_id}")
def delete_user(user_id: int, service: CRMService = Depends(get_service)):
    """Borrado suave de un usuario (envío a papelera)."""
    try:
        service.delete_user_complete(user_id)
        return ApiResponse.success(message="Usuario movido a la papelera de reciclaje.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.post("/users/{user_id}/restore")
def restore_user(user_id: int, hygiene: DataHygieneService = Depends(get_hygiene)):
    """Restaura un usuario que fue borrado previamente."""
    if hygiene.restore_item('users', user_id):
        return ApiResponse.success(message="Usuario restaurado con éxito.")
    return ApiResponse.error(message="No se pudo restaurar el usuario.")

# --- MÓDULO DE EMPRESAS ---

@app.get("/companies")
def list_companies(service: CRMService = Depends(get_service)):
    """Lista el resumen de todas las empresas activas."""
    try:
        data = service.get_companies_summary()
        return ApiResponse.success(data=data)
    except Exception as e:
        logger.error(f"Error listing companies: {str(e)}")
        return ApiResponse.error(message="Error al listar empresas", data=str(e))

    # Removed duplicate get_company_detail route, using the one at line 392

@app.post("/companies")
def create_company(data: CompanyCreate, service: CRMService = Depends(get_service)):
    """Crea una empresa completa con sus contactos iniciales."""
    try:
        # Limpieza proactiva de nulos para campos opcionales con restricciones
        c = Company(
            legal_name=data.legal_name,
            commercial_name=data.commercial_name if data.commercial_name and data.commercial_name.strip() else None,
            rut_nit=data.rut_nit or '',
            verification_digit=data.verification_digit,
            domain=data.domain if data.domain and data.domain.strip() else None,
            status_id=data.status_id,
            agent_id=data.agent_id,
            revenue=data.revenue,
            employee_count=data.employee_count,
            description=data.description if data.description and data.description.strip() else None
        )
        if hasattr(data, 'company_department_id'):
            setattr(c, 'company_department_id', data.company_department_id)
        phones = [Phone(local_number=p.local_number, label_id=p.label_id) for p in data.phones]
        emails = [Email(email_address=e.email_address, label_id=e.label_id) for e in data.emails]
        addresses = [Address(
            address_line1=a.address_line1,
            address_line2=a.address_line2,
            city_id=a.city_id,
            state_id=a.state_id,
            country_id=a.country_id,
            postal_code=a.postal_code
        ) for a in data.addresses]
        
        # Convert tags payload to tag_ids since create_company_complete expects it
        tag_ids = [t['id'] for t in data.tags if 'id' in t]
        
        company_id = service.create_company_complete(c, phones=phones, emails=emails, addresses=addresses, tag_ids=tag_ids)
        
        # 3. Guardar vínculos corporativos en 1-paso reutilizando update_company_complete
        update_data = {}
        if data.tags: update_data['tags'] = data.tags
        if data.employees: update_data['employees'] = data.employees
        if data.relationships: update_data['relationships'] = data.relationships
        if update_data:
             service.update_company_complete(company_id, update_data)
             
        return ApiResponse.success(data={"id": company_id}, message="Empresa registrada correctamente.")
    except DuplicateError as de:
        return ApiResponse.error(message=str(de), status_code=409)
    except CRMError as ce:
        return ApiResponse.error(message=str(ce), status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado creando empresa: {e}")
        return ApiResponse.error(message=f"Error inesperado al procesar la solicitud: {str(e)}")

@app.put("/companies/{company_id}")
def update_company(company_id: int, data: Dict[str, Any], service: CRMService = Depends(get_service)):
    """Actualiza y sincroniza el perfil completo de la empresa."""
    try:
        service.update_company_complete(company_id, data)
        return ApiResponse.success(message="Empresa y contactos actualizados correctamente.")
    except Exception as e:
        return ApiResponse.error(message=f"Error durante la actualización: {str(e)}")

@app.get("/companies/{company_id}")
def get_company_detail(company_id: int, service: CRMService = Depends(get_service)):
    """Detalle completo de la empresa incluyendo su listado de empleados vinculados."""
    detail = service.get_company_detail_full(company_id)
    if not detail:
        return ApiResponse.not_found(message="Empresa no encontrada.")
    return ApiResponse.success(data=detail)

@app.delete("/companies/{company_id}")
def delete_company(company_id: int, service: CRMService = Depends(get_service)):
    """Borrado suave de una empresa (envío a papelera)."""
    try:
        service.delete_company_complete(company_id)
        return ApiResponse.success(message="Empresa movida a la papelera de reciclaje.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

# --- MÓDULO PROFESIONAL (VÍNCULOS USUARIO-EMPRESA) ---

@app.post("/professional/link")
def link_professional(data: Dict[str, Any], service: CRMService = Depends(get_service)):
    """Establece una relación laboral entre un Usuario y una Empresa."""
    try:
        service.link_user_to_company(
            user_id=data['user_id'],
            company_id=data['company_id'],
            position_id=data.get('position_id', 1),
            department_id=data.get('department_id', 1)
        )
        return ApiResponse.success(message="Vínculo profesional establecido exitosamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))


# --- MÓDULO DE RELACIONES ENTRE EMPRESAS (B2B) ---

class CompanyRelationInput(BaseModel):
    target_company_id: int
    relation_type_id: int
    notes: Optional[str] = None
    is_inverse: Optional[bool] = False

@app.post("/hygiene/consolidate-types")
@app.post("/companies/{company_id}/relate")
def link_companies(company_id: int, data: CompanyRelationInput, service: CRMService = Depends(get_service)):
    """Crea una relación entre dos empresas."""
    try:
        service.link_companies(company_id, data.target_company_id, data.relation_type_id, data.notes, data.is_inverse)
        return ApiResponse.success(message="Relación corporativa establecida correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.put("/companies/{company_id}/relate/{target_company_id}")
def update_company_links(company_id: int, target_company_id: int, data: CompanyRelationInput, service: CRMService = Depends(get_service)):
    """Actualiza una relación existente."""
    try:
        service.update_company_relation(company_id, target_company_id, data.relation_type_id, data.notes, data.is_inverse)
        return ApiResponse.success(message="Relación corporativa actualizada correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.delete("/companies/{company_id}/relate/{target_company_id}")
def unlink_companies(company_id: int, target_company_id: int, service: CRMService = Depends(get_service)):
    """Elimina una relación entre dos empresas."""
    try:
        service.unlink_companies(company_id, target_company_id)
        return ApiResponse.success(message="Relación corporativa eliminada correctamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.get("/catalog/company-relation-types")
def list_company_relation_types(service: CRMService = Depends(get_service)):
    """Retorna los tipos de relación entre empresas (Proveedor, Cliente, Filial, etc)."""
    return ApiResponse.success(data=service.get_company_relation_types())

class RelationTypeInput(BaseModel):
    name: str
    inverse_name: Optional[str] = None
    is_symmetric: Optional[bool] = False

@app.post("/catalog/company-relation-types")
def create_company_relation_type(data: RelationTypeInput, service: CRMService = Depends(get_service)):
    try:
        new_id = service.create_company_relation_type(data.name, data.inverse_name, data.is_symmetric)
        return ApiResponse.success(data={"id": new_id}, message="Tipo de relación corporativa creado.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.delete("/catalog/company-relation-types/{type_id}")
def delete_company_relation_type(type_id: int, service: CRMService = Depends(get_service)):
    try:
        service.delete_company_relation_type(type_id)
        return ApiResponse.success(message="Tipo de relación eliminado correctamente.")
    except ValueError as ve:
        return ApiResponse.error(message=str(ve)) # Protected types
    except Exception as e:
        return ApiResponse.error(message=str(e))

# --- MÓDULO DE CATÁLOGOS Y GEOGRAFÍA ---

@app.get("/catalog/positions")
def list_positions(service: CRMService = Depends(get_service)):
    """Retorna el listado maestro de cargos configurados."""
    return ApiResponse.success(data=service.get_positions())

@app.get("/catalog/departments")
def list_departments(service: CRMService = Depends(get_service)):
    """Retorna el listado maestro de departamentos de empresa."""
    return ApiResponse.success(data=service.get_departments())

@app.get("/catalog/labels")
def list_labels(service: CRMService = Depends(get_service)):
    """Retorna el listado maestro de etiquetas de contacto."""
    return ApiResponse.success(data=service.get_labels())

@app.get("/catalog/genders")
def list_genders(service: CRMService = Depends(get_service)):
    """Retorna el listado maestro de géneros."""
    return ApiResponse.success(data=service.get_genders())

@app.get("/catalog/roles")
def list_roles(service: CRMService = Depends(get_service)):
    """Lista todos los roles de usuario."""
    return ApiResponse.success(data=service.get_roles())

@app.get("/catalog/user-relation-types")
def list_user_relation_types(service: CRMService = Depends(get_service)):
    """Lista los tipos de relación entre personas (Cónyuge, Socio, etc)."""
    return ApiResponse.success(data=service.get_user_relation_types())

@app.get("/catalog/statuses")
def list_statuses(service: CRMService = Depends(get_service)):
    """Lista todos los estados de usuario."""
    return ApiResponse.success(data=service.get_statuses())

@app.get("/catalog/tags")
def list_tags(service: CRMService = Depends(get_service)):
    """Lista todas las etiquetas globales disponibles."""
    return ApiResponse.success(data=service.get_tags())

@app.get("/catalog/economic-activities")
def list_economic_activities(q: Optional[str] = None, service: CRMService = Depends(get_service)):
    """Lista o busca actividades económicas (CIIU)."""
    return ApiResponse.success(data=service.get_economic_activities(q))

@app.post("/catalog/tags")
def create_tag(tag: TagCreate, service: CRMService = Depends(get_service)):
    """Crea una nueva etiqueta."""
    try:
        tag_id = service.create_tag(tag.name, tag.color)
        return ApiResponse.success(data={"id": tag_id, "name": tag.name, "color": tag.color}, message="Etiqueta creada.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.get("/catalog/agents")
def list_agents(service: CRMService = Depends(get_service)):
    """Lista usuarios con roles de gestión (Admin, Agente, Vendedor)."""
    # En un sistema real filtraríamos por role_id. Aquí pedimos el lookup de agentes al servicio.
    return ApiResponse.success(data=service.get_agents())

@app.get("/geography/countries")
def list_countries(service: CRMService = Depends(get_service)):
    """Lista todos los países registrados."""
    return ApiResponse.success(data=service.list_countries())

@app.get("/geography/states/{country_id}")
def list_states(country_id: int, service: CRMService = Depends(get_service)):
    """Lista departamentos/estados por país."""
    return ApiResponse.success(data=service.get_states(country_id))

@app.get("/geography/cities/{state_id}")
def list_cities(state_id: int, service: CRMService = Depends(get_service)):
    """Lista ciudades/municipios por departamento."""
    return ApiResponse.success(data=service.get_cities(state_id))

# --- MÓDULO DE PRODUCTIVIDAD E HIGIENE (PAPELERA) ---

@app.get("/hygiene/trash/{table}")
def list_trash(table: str, hygiene: DataHygieneService = Depends(get_hygiene)):
    """Lista los elementos borrados (soft-deleted) para una tabla permitida."""
    if table not in ['users', 'companies']:
        return ApiResponse.error(message="Tabla no permitida para inspección de papelera.")
    return ApiResponse.success(data=hygiene.list_trash(table))

@app.post("/hygiene/purge/{table}")
def purge_trash(table: str, hygiene: DataHygieneService = Depends(get_hygiene)):
    """Borrado definitivo de todos los elementos en la papelera de una tabla."""
    success = hygiene.purge_trash(table)
    if success:
        return ApiResponse.success(message=f"La papelera de {table} ha sido vaciada definitivamente.")
    return ApiResponse.error(message="Hubo un error al intentar vaciar la papelera.")

# --- CATALOGO DINAMICO DE TIPOS DE RELACION ---

class RelationTypeInput(BaseModel):
    name: str
    inverse_name: Optional[str] = None

@app.post("/catalog/user-relation-types")
def create_user_relation_type(data: RelationTypeInput, service: CRMService = Depends(get_service)):
    """Crea un nuevo tipo de relación usuario-usuario (ej. Entrenador)."""
    try:
        if not data.inverse_name:
            return ApiResponse.error(message="Debe especificar el nombre inverso (ej. Deportista).")
        
        new_id = service.create_user_relation_type(data.name, data.inverse_name)
        return ApiResponse.success(data={'id': new_id}, message="Tipo de relación creado exitosamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

@app.post("/catalog/company-relation-types")
def create_company_relation_type(data: RelationTypeInput, service: CRMService = Depends(get_service)):
    """Crea un nuevo tipo de relación empresa-empresa (ej. Partner)."""
    try:
        new_id = service.create_company_relation_type(data.name, data.inverse_name)
        return ApiResponse.success(data={'id': new_id}, message="Tipo de relación creado exitosamente.")
    except Exception as e:
        return ApiResponse.error(message=str(e))

# --- INICIO DEL SERVIDOR ---

if __name__ == "__main__":
    import uvicorn
    # Carga el puerto configurado en el .env raíz (Default: 8000)
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
