"""
Encabezado Profesional: Repositorio MySQL Concreto
Propósito: Implementa la interfaz IDatabase específicamente para motores MySQL.
Por qué: Encapsular todo el conocimiento de MySQL (librerías, errores, sintaxis) en una sola clase 
para que el resto de la aplicación no dependa de él.
"""

import logging
import mysql.connector
import os
from mysql.connector import Error, errorcode
from contextlib import contextmanager
from typing import Any, Optional
from .database_interface import IDatabase
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)

class MySQLRepository(IDatabase):
    """
    Implementación concreta de persistencia para MySQL.
    Encapsula el uso de mysql.connector y el manejo de errores SQL.
    """

    def __init__(self, config: dict):
        """
        Recibe la configuración necesaria para la conexión.
        Por qué: Inyección de configuración para facilitar pruebas y cambios de entorno.
        """
        self.config = config
        self.connection = None

    def connect(self, database_name: Optional[str] = None):
        """
        Establece la conexión física.
        - database_name: Permite cambiar dinámicamente de base de datos (Multitenancy).
        """
        try:
            config = self.config.copy()
            if database_name:
                config['database'] = database_name
            
            # Conexión dinámica para soportar múltiples clientes (Tenants)
            conn = mysql.connector.connect(**config)
            conn.autocommit = False # Forzamos control manual de integridad
            return conn
        except Error as err:
            logger.error(f"Error de conexión MySQL: {err}")
            raise DatabaseError(f"Fallo en la conexión MySQL: {err}")

    def execute_command(self, command: str, parameters: Optional[tuple] = None, perform_commit: bool = False, fetch_results: bool = True) -> Any:
        """
        Ejecuta sentencias SQL de forma segura y parametrizada.
        """
        # Obtenemos conexión activa o maestra
        if not self.connection or not self.connection.is_connected():
            self.connection = self.connect()
            
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(command, parameters or ())
            
            if fetch_results:
                result = cursor.fetchall()
            else:
                if perform_commit:
                    self.connection.commit()
                result = cursor.lastrowid # Retorna el ID generado en inserciones
            return result
        except Error as e:
            if not perform_commit:
                self.connection.rollback()
            logger.error(f"Error MySQL ejecutando comando: {e}")
            raise DatabaseError(str(e))
        finally:
            cursor.close()

    @contextmanager
    def start_transaction(self):
        """
        Gestor de contexto para transacciones atómicas.
        Asegura que todas las operaciones dentro del bloque 'with' se guarden o se descarten juntas.
        """
        if not self.connection or not self.connection.is_connected():
            self.connection = self.connect()
            
        cursor = self.connection.cursor(dictionary=True)
        try:
            yield cursor
            self.connection.commit()
            logger.debug("Transacción MySQL completada exitosamente.")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error en transacción MySQL, se realizó rollback: {e}")
            raise
        finally:
            cursor.close()

    def switch_database(self, database_name: str):
        """
        Cambia el esquema activo en la conexión actual.
        Útil para operaciones multitenant (Broadcast).
        """
        if database_name is None:
            database_name = self.config.get('master_database', os.getenv('MASTER_DB_NAME'))
            
        self.config['database'] = database_name
        
        if not self.connection or not self.connection.is_connected():
            self.connection = self.connect(database_name)
        else:
            self.connection.database = database_name
            logger.debug(f"Cambiado contexto de base de datos a: {database_name}")

    def dispose(self):
        """Libera los recursos de conexión."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            logger.info("Conexión MySQL cerrada profesionalmente.")
