# Importación de librerías necesarias para el registro de eventos, variables de entorno y conexión MySQL
import logging  # Para el registro de logs
import os  # Para interactuar con el sistema de archivos y variables de entorno
from typing import Optional, Any  # Para tipado opcional y genérico
import mysql.connector  # Driver de conexión a MySQL
from mysql.connector import Error, errorcode  # Excepciones estándar de MySQL
from contextlib import contextmanager  # Para manejar contextos de transacciones
from dotenv import load_dotenv  # Para cargar el archivo .env

# Importación de interfaces propias y excepciones personalizadas
from .database_interface import IDatabase
from .exceptions import DatabaseError

# Cargamos las variables de entorno definidas en el archivo .env del proyecto
load_dotenv() 

# Configuramos el logger para este módulo específico
logger = logging.getLogger(__name__)

class DatabaseManager(IDatabase):
    """
    Gestor de conexiones a bases de datos MySQL.
    Implementa la interfaz IDatabase para permitir el desacoplamiento de la persistencia.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Inicializa la configuración de la base de datos.
        Si no se provee un 'config', los toma directamente del archivo .env.
        """
        if config:
            self.config = config
        else:
            self.config = {
                'host': os.getenv('DB_HOST'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_NAME'),
                'port': int(os.getenv('DB_PORT', 3306))
            }
        
        # Validación preventiva: verificamos que las variables críticas existan
        if not all([self.config['host'], self.config['user'], self.config['database']]):
             logger.warning("Faltan variables de entorno críticas para la conexión a la base de datos.")
             
        # La conexión se inicializa como None (lazy loading)
        self.connection = None

    def get_connection(self, db_name: Optional[str] = None):
        """
        Establece o retorna una conexión activa.
        - Si se provee db_name, crea una NUEVA conexión a esa base de datos (para multitenancy).
        - Si db_name es None, retorna la conexión compartida/maestra.
        """
        try:
            # Conexión dinámica (Cambio de tenant en caliente)
            if db_name:
                dynamic_config = self.config.copy()
                dynamic_config['database'] = db_name
                conn = mysql.connector.connect(**dynamic_config)
                conn.autocommit = False  # Obligamos a transacciones manuales por seguridad
                return conn

            # Conexión por defecto (Carga perezosa/reutilización)
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                self.connection.autocommit = False
            return self.connection
        except Error as err:
            # Captura y mapeo de errores comunes de conexión MySQL
            logger.error(f"Error crítico de conexión: {err}")
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise DatabaseError("Usuario o contraseña de base de datos incorrectos.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise DatabaseError(f"La base de datos '{db_name or self.config['database']}' no existe.")
            else:
                raise DatabaseError(f"Fallo en la conexión MySQL: {err}")

    def connect(self):
        """Alias para get_connection() que cumple con la interfaz IDatabase."""
        return self.get_connection()

    def start_transaction(self):
        """Implementación de IDatabase.start_transaction."""
        return self.transaction()
        
    def dispose(self):
        """Implementación de IDatabase.dispose."""
        self.close()

    def switch_database(self, db_name: Optional[str]):
        """
        Cambia el contexto de la base de datos activa para la conexión actual.
        Si db_name es None, revierte a la base de datos original (Master).
        """
        target_db = db_name if db_name else self.config.get('database') # o master default
        
        # Si ya estamos conectados a esa DB, no hacer nada
        if self.connection and self.connection.is_connected() and self.connection.database == target_db:
             return

        # Si hay conexión abierta a otra DB, cerrarla
        if self.connection and self.connection.is_connected():
            self.connection.close()
        
        # Actualizar config temporal
        self.config['database'] = target_db
        # Forzar reconexión en la próxima llamada a get_connection
        self.connection = None
        self.get_connection()

    def execute_query(self, query, params=None, commit=False, is_select=True):
        """
        Ejecuta una consulta SQL parametrizada.
        - query: La sentencia SQL con marcadores %s.
        - params: Tupla de valores para los marcadores.
        - commit: Si es True, realiza commit inmediatamente (para inserts simples).
        - is_select: Si es True, retorna todos los resultados (fetchall).
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True) # Usamos diccionarios para facilitar serialización JSON
        try:
            cursor.execute(query, params or ())
            if is_select:
                result = cursor.fetchall()
            else:
                if commit:
                    conn.commit()
                result = cursor.lastrowid # Retorna el ID generado en inserciones
            return result
        except Error as e:
            # Si algo falla y no hemos enviado commit, realizamos rollback
            if not commit:
                 conn.rollback()
            # Mapeo de errores específicos de ejecución
            error_msg = self._map_mysql_error(e)
            logger.error(f"Error ejecutando query: {query} | Error: {error_msg}")
            raise DatabaseError(error_msg)
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """
        Ejecuta una consulta y retorna un único resultado.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except Error as e:
            error_msg = self._map_mysql_error(e)
            logger.error(f"Error en fetch_one: {query} | Error: {error_msg}")
            raise DatabaseError(error_msg)
        finally:
            cursor.close()

    def execute_command(self, command: str, parameters: Optional[tuple] = None, perform_commit: bool = False, fetch_results: bool = True) -> Any:
        """Implementación de IDatabase.execute_command."""
        return self.execute_query(query=command, params=parameters, commit=perform_commit, is_select=fetch_results)

    @contextmanager
    def transaction(self):
        """
        Administrador de contexto para asegurar operaciones atómicas.
        Garantiza que toda la lógica dentro del bloque se guarde o se revierta en conjunto.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit() # Si no hay excepciones, guardamos cambios
            logger.debug("Transacción completada satisfactoriamente.")
        except Error as e:
            conn.rollback() # Ante cualquier error de MySQL, revertimos todo el bloque
            error_msg = self._map_mysql_error(e)
            logger.error(f"Error en transacción, se realizó rollback: {error_msg}")
            raise DatabaseError(error_msg)
        except Exception as e:
            conn.rollback() # Captura de errores inesperados (no solo de MySQL)
            logger.error(f"Error inesperado en transacción: {e}")
            raise
        finally:
            cursor.close()

    def _map_mysql_error(self, err: Error) -> str:
        """
        Mapea códigos de error de MySQL a mensajes claros y en español para el usuario/API.
        """
        code = err.errno
        msg = err.msg
        
        # Errores de restricción (Check Constraints) - Código MySQL 3819
        if code == 3819:
            return f"Violación de restricción (Check Constraint): {msg}"
        
        # Errores de llave foránea (Foreign Key) - Código MySQL 1451 o 1452
        if code in [1451, 1452]:
            return "No se pudo realizar la operación debido a una restricción de relación (Llave Foránea)."
        
        # Registros duplicados - Código MySQL 1062
        if code == 1062:
            return "Ya existe un registro con estos datos únicos (Entrada Duplicada)."
            
        # Error de 'Group By' estricto - Código MySQL 1055
        if code == 1055:
            return "Error de sintaxis SQL (ONLY_FULL_GROUP_BY). Por favor, contacte a soporte técnico."
            
        # Error genérico pero con mensaje de MySQL
        return f"Error de base de datos ({code}): {msg}"

    def close(self):
        """Cierra la conexión activa a la base de datos."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            logger.info("Conexión a la base de datos cerrada.")
