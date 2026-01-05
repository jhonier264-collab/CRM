
import logging
import os
from typing import Optional
import mysql.connector
from mysql.connector import Error, errorcode
from contextlib import contextmanager
from dotenv import load_dotenv

from .database_interface import IDatabase
from .exceptions import DatabaseError

# Load environment variables
load_dotenv() 

logger = logging.getLogger(__name__)

class DatabaseManager(IDatabase):
    """MySQL connection manager and utilities.
    
    Implements IDatabase to allow decoupling.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initializes configuration. If not provided, loads from .env."""
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
        
        if not all([self.config['host'], self.config['user'], self.config['database']]):
             logger.warning("Critical environment variables for database connection are missing.")
             
        self.connection = None

    def connect(self):
        """Establishes or returns the current connection."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                self.connection.autocommit = False  # Mandatory manual transactions
            return self.connection
        except Error as err:
            logger.error(f"Critical connection error: {err}")
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise DatabaseError("Incorrect username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise DatabaseError("Database does not exist")
            else:
                raise DatabaseError(f"MySQL connection error: {err}")

    def execute_query(self, query, params=None, commit=False, is_select=True):
        """Executes a SQL query with parameters.
        
        Args:
            query (str): SQL query with %s placeholders.
            params (tuple): Parameters for the query.
            commit (bool): If True, commits immediately (for simple updates).
            is_select (bool): If True, returns fetchall().
        """
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if is_select:
                result = cursor.fetchall()
            else:
                if commit:
                    conn.commit()
                result = cursor.lastrowid
            return result
        except Error as e:
            if not commit:
                 conn.rollback()
            logger.error(f"Error executing query: {query} | Error: {e}")
            raise DatabaseError(f"Database error: {e}")
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """Context manager to ensure atomic operations (Commit/Rollback)."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
            logger.debug("Transaction completed successfully")
        except Error as e:
            conn.rollback()
            logger.error(f"Error in transaction, rollback performed: {e}")
            if e.errno == 3819:
                 raise DatabaseError(f"Constraint violation (Check Constraint): {e.msg}")
            raise DatabaseError(f"Transactional error: {e}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error in transaction: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
