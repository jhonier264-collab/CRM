"""
Encabezado Profesional: Servicio de Aprovisionamiento y Mantenimiento de Tenants
Propósito: Gestiona el ciclo de vida de los clientes (Tenants), desde su creación física
hasta el mantenimiento masivo de sus estructuras de datos.
Por qué: Centralizar la lógica multi-base de datos para asegurar escalabilidad SaaS.
"""

import logging
import os
import re
from typing import Dict, Any, List
from src.core.database_interface import IDatabase
from src.lib.shared_auth.security import PasswordHasher, validar_rut_colombia

logger = logging.getLogger(__name__)

class ProvisioningService:
    def __init__(self, persistence: IDatabase):
        """
        Inyección de dependencia: Recibe el motor de persistencia global.
        """
        self.persistence = persistence

    def create_tenant(self, admin_data: Dict[str, Any]):
        """
        Crea un nuevo cliente (Tenant) y su infraestructura de datos.
        """
        username = admin_data['username']
        account_type = admin_data.get('account_type', 'INDIVIDUAL')
        rut = admin_data.get('rut')

        if account_type == 'COMPANY' and not validar_rut_colombia(rut):
            raise ValueError("El RUT/NIT ingresado es inválido según el algoritmo de la DIAN.")

        # Nombre de DB único basado en el usuario
        safe_username = "".join(c for c in username if c.isalnum())
        db_name = f"crm_user_{safe_username}"
        
        try:
            # 1. Verificar existencia global
            check_cmd = "SELECT id FROM global_users WHERE username = %s OR email = %s"
            exists = self.persistence.execute_command(check_cmd, (username, admin_data['email']))
            if exists:
                raise ValueError("El nombre de usuario o email ya está en uso.")

            # 2. Registrar Usuario Global
            hashed_pw = PasswordHasher.hash(admin_data['password'])
            reg_cmd = """
                INSERT INTO global_users (username, email, password_hash, tenant_db, account_type, rut) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            global_user_id = self.persistence.execute_command(reg_cmd, (username, admin_data['email'], hashed_pw, db_name, account_type, rut), perform_commit=True, fetch_results=False)
            
            # 3. Crear Persistencia Física (Database)
            self.persistence.execute_command(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            
            # 4. Cambiar contexto al nuevo Tenant para inicializarlo
            self.persistence.switch_database(db_name)
            
            # 5. Inicializar Esquema Local y Admin
            self._init_tenant_schema()
            self._create_local_admin(admin_data, global_user_id)
            
            # 6. Volver al contexto maestro
            self.persistence.switch_database(None)

            # 7. Registrar mapeo de Tenant en Master
            mapping_cmd = "INSERT INTO tenants (owner_user_id, db_name) SELECT id, %s FROM global_users WHERE username = %s"
            self.persistence.execute_command(mapping_cmd, (db_name, username), perform_commit=True, fetch_results=False)
            
            logger.info(f"Instancia {db_name} aprovisionada exitosamente para {username}.")
            return True

        except Exception as e:
            logger.error(f"Fallo crítico en aprovisionamiento: {e}")
            raise e

    def maintenance_broadcast(self, command_string: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        SISTEMA DE MANTENIMIENTO MASIVO:
        Ejecuta una instrucción en todas las bases de datos de clientes registradas.
        """
        logger.info(">>> INICIANDO MANTENIMIENTO MASIVO (BROADCAST) <<<")
        
        # 1. Obtener todos los tenants activos desde la Master DB
        tenants = self.persistence.execute_command("SELECT db_name FROM tenants WHERE status = 'ACTIVE'")
        report = []

        for tenant in tenants:
            db_name = tenant['db_name']
            status = {'database': db_name, 'success': False, 'message': ''}
            try:
                # Cambiar contexto al tenant
                self.persistence.switch_database(db_name)
                
                # Ejecutar comando
                self.persistence.execute_command(command_string, params, perform_commit=True, fetch_results=False)
                
                status['success'] = True
                status['message'] = "Comando aplicado exitosamente."
            except Exception as e:
                status['message'] = f"Error: {str(e)}"
                logger.warning(f"Fallo en mantenimiento para {db_name}: {e}")
            
            report.append(status)
        
        # Volver al contexto maestro
        self.persistence.switch_database(None)
        
        logger.info(f"Broadcast finalizado. Procesados {len(report)} tenants.")
        return report

    def install_module(self, tenant_id: int, module_name: str) -> bool:
        """
        Instala un módulo adicional (on-demand) en la base de datos de un tenant.
        Garantiza atomicidad y registro en la Master DB.
        """
        try:
            # 1. Obtener datos del tenant
            tenant = self.persistence.execute_command(
                "SELECT db_name FROM tenants WHERE id = %s", (tenant_id,)
            )
            if not tenant:
                raise ValueError(f"Tenant con ID {tenant_id} no encontrado.")
            
            db_name = tenant[0]['db_name']
            
            # 2. Localizar script SQL del módulo
            module_path = os.path.join(os.path.dirname(__file__), f"../../../database/modules/{module_name}.sql")
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"El script del módulo '{module_name}' no existe en {module_path}")

            with open(module_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # 3. Ejecutar instalación en el contexto del tenant
            logger.info(f"Instalando módulo '{module_name}' en tenant {db_name}...")
            self.persistence.switch_database(db_name)
            
            with self.persistence.start_transaction() as cursor:
                # Separar por ';' que estén al final de línea para evitar romper strings internos
                statements = re.split(r';\s*(?=\n|$)', sql_script)
                for statement in statements:
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
            
            # 4. Registrar activación en Master DB
            self.persistence.switch_database(None) # Volver a master
            reg_mod_cmd = """
                INSERT INTO tenant_modules (tenant_id, module_name, status) 
                VALUES (%s, %s, 'active')
                ON DUPLICATE KEY UPDATE status = 'active'
            """
            self.persistence.execute_command(reg_mod_cmd, (tenant_id, module_name), perform_commit=True, fetch_results=False)
            
            logger.info(f"Módulo '{module_name}' instalado exitosamente en {db_name}.")
            return True

        except Exception as e:
            logger.error(f"Error instalando módulo '{module_name}': {e}")
            # El rollback del cursor en start_transaction maneja la atomicidad SQL
            self.persistence.switch_database(None) # Asegurar retorno a master
            raise e

    # ... _init_tenant_schema remains similar ...

    def _create_local_admin(self, db_name: str, admin_data: Dict[str, Any], hashed_pw: str):
        """Inserts the admin user into the new tenant's users table."""

    def _init_tenant_schema(self):
        """Ejecuta el script SQL de plantilla core en la base de datos actual."""
        try:
            # Nuevo paradigma: core_template.sql es el ADN mínimo
            template_path = os.path.join(os.path.dirname(__file__), '../../../database/core_template.sql')
            template_path = os.path.abspath(template_path)
            logger.info(f"Cargando esquema core desde: {template_path}")
            with open(template_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            with self.persistence.start_transaction() as cursor:
                statements = re.split(r';\s*(?=\n|$)', sql_script)
                for statement in statements:
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
            
            # INSPECCIÓN QA: Confirmar que la tabla users esté limpia
            users_check = self.persistence.execute_command("SELECT COUNT(*) as count FROM users")
            logger.debug(f"Usuarios iniciales en tenant: {users_check[0]['count']}")
            
            logger.info("Esquema core inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando esquema core: {e}")
            raise

    def _create_local_admin(self, admin_data: Dict[str, Any], global_user_id: int):
        """Crea el usuario administrador inicial dentro del tenant."""
        try:
            with self.persistence.start_transaction() as cursor:
                sql_user = """
                INSERT INTO users (first_name, last_name, global_user_id, role_id, status_id) 
                VALUES (%s, %s, %s, 1, 1)
                """
                logger.debug(f"Ejecutando inserción de admin local: {admin_data['username']} ({admin_data['first_name']} {admin_data['last_name']})")
                cursor.execute(sql_user, (admin_data['first_name'], admin_data['last_name'], global_user_id))
                user_id = cursor.lastrowid
                
                sql_email = "INSERT INTO emails (user_id, email_address, label_id) VALUES (%s, %s, 1)"
                cursor.execute(sql_email, (user_id, admin_data['email']))
            logger.info(f"Admin local {admin_data['username']} (ID: {user_id}) creado exitosamente.")
        except Exception as e:
            logger.error(f"Error creando administrador local: {e}")
            raise
