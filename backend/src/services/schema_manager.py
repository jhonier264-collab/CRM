
import logging
from typing import List, Dict, Any
from src.core.database_interface import IDatabase

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages dynamic schema changes (ADD/DROP columns) safely."""
    
    # Critical columns that must never be deleted
    PROTECTED_COLUMNS = {
        'users': ['id', 'agent_id', 'role_id', 'status_id', 'first_name', 'last_name', 'username', 'password_hash', 'rut_nit', 'is_natural_person', 'created_at', 'updated_at'],
        'companies': ['id', 'agent_id', 'status_id', 'rut_nit', 'legal_name', 'created_at'],
        'company_relation_types': ['id', 'name', 'inverse_type_id'],
        'user_relation_types': ['id', 'name', 'inverse_type_id']
    }

    def __init__(self, db: IDatabase):
        self.db = db

    def add_column(self, table: str, column_name: str, data_type: str, display_name: str) -> bool:
        """Adds a new column to a table and records it in metadata."""
        if table not in self.PROTECTED_COLUMNS:
            logger.warning(f"Table {table} is not managed by SchemaManager.")
            return False
            
        try:
            # 1. Alter the physical table
            sql_alter = f"ALTER TABLE `{table}` ADD COLUMN `{column_name}` {data_type} NULL"
            self.db.execute_command(sql_alter, perform_commit=True, fetch_results=False)
            
            # 2. Record in metadata
            sql_meta = """
            INSERT INTO custom_columns_metadata (table_name, column_name, display_name, data_type, is_protected)
            VALUES (%s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE display_name = VALUES(display_name)
            """
            self.db.execute_command(sql_meta, (table, column_name, display_name, data_type), perform_commit=True, fetch_results=False)
            return True
        except Exception as e:
            logger.error(f"Error adding column {column_name} to {table}: {e}")
            return False

    def remove_column(self, table: str, column_name: str) -> bool:
        """Removes a column if it is NOT protected."""
        if column_name in self.PROTECTED_COLUMNS.get(table, []):
            logger.error(f"Attempted to remove protected column: {column_name}")
            return False
            
        try:
            # 1. Check if it's in metadata (to ensure it's a custom column)
            res = self.db.execute_command("SELECT id FROM custom_columns_metadata WHERE table_name = %s AND column_name = %s", (table, column_name))
            if not res:
                logger.error(f"Column {column_name} is not a registered custom column.")
                return False
                
            # 2. Alter the table
            sql_alter = f"ALTER TABLE `{table}` DROP COLUMN `{column_name}`"
            self.db.execute_command(sql_alter, perform_commit=True, fetch_results=False)
            
            # 3. Remove from metadata
            self.db.execute_command("DELETE FROM custom_columns_metadata WHERE table_name = %s AND column_name = %s", (table, column_name), perform_commit=True, fetch_results=False)
            return True
        except Exception as e:
            logger.error(f"Error removing column {column_name} from {table}: {e}")
            return False

    def get_custom_columns(self, table: str) -> List[Dict[str, Any]]:
        """Returns list of custom columns for a table."""
        return self.db.execute_command("SELECT column_name, display_name, data_type FROM custom_columns_metadata WHERE table_name = %s", (table,))
