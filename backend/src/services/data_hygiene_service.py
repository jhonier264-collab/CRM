import logging
from typing import List, Dict, Any
from src.core.database_manager import DatabaseManager
from src.models.models import User, Company

class DataHygieneService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.logger = logging.getLogger(__name__)

    # --- Soft Delete & Recovery ---

    def list_trash(self, table: str) -> List[Dict[str, Any]]:
        """Lists items in the recycling bin."""
        if table not in ['users', 'companies']: return []
        return self.db.execute_query(f"SELECT * FROM {table} WHERE deleted_at IS NOT NULL")

    def restore_item(self, table: str, item_id: int):
        """Restores a soft-deleted item."""
        sql = f"UPDATE {table} SET deleted_at = NULL WHERE id = %s"
        return self.db.execute_query(sql, (item_id,), commit=True, is_select=False)

    def soft_delete_item(self, table: str, item_id: int):
        """Moves an item to the recycling bin."""
        sql = f"UPDATE {table} SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db.execute_query(sql, (item_id,), commit=True, is_select=False)

    def permanent_delete_item(self, table: str, item_id: int):
        """PERMANENTLY deletes an item from the database (No Undo)."""
        if table not in ['users', 'companies']: return False
        
        with self.db.transaction() as cursor:
            if table == 'users':
                cursor.execute("DELETE FROM user_companies WHERE user_id = %s", (item_id,))
                cursor.execute("DELETE FROM phones WHERE user_id = %s", (item_id,))
                cursor.execute("DELETE FROM emails WHERE user_id = %s", (item_id,))
                cursor.execute("DELETE FROM addresses WHERE user_id = %s", (item_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (item_id,))
            else:
                cursor.execute("DELETE FROM user_companies WHERE company_id = %s", (item_id,))
                cursor.execute("DELETE FROM companies WHERE id = %s", (item_id,))
        return True

    def purge_trash(self, table: str):
        """Permanently deletes ALL items currently in the trash for a table."""
        if table not in ['users', 'companies']: return False
        
        items = self.list_trash(table)
        for item in items:
            self.permanent_delete_item(table, item['id'])
        return True

    # --- Deduplication (Merge & Fix) ---

    def _normalize_phone(self, phone: str) -> str:
        """Removes spaces, dashes, and country prefixes for comparison."""
        import re
        if not phone: return ""
        # Keep only digits
        digits = re.sub(r'\D', '', phone)
        # If it's too long (country code), take the last 10 (common for many LATAM formats)
        # or just keep it as is for exact matching of normalized string.
        return digits[-10:] if len(digits) > 10 else digits

    def find_user_duplicates(self) -> List[Dict[str, Any]]:
        """
        Intelligent duplicate search using Python normalization for phones.
        """
        # 1. Duplicate Names (SQL is fine for this as they are unique_key bound otherwise)
        name_dups = self.db.execute_query("""
            SELECT first_name, last_name, COUNT(*) as count, GROUP_CONCAT(DISTINCT id) as ids, 'Nombre/Apellido' as reason
            FROM users WHERE deleted_at IS NULL GROUP BY first_name, last_name HAVING count > 1
        """)

        # 2. Shared Emails (SQL is fine)
        email_dups = self.db.execute_query("""
            SELECT e.email_address, COUNT(*) as count, GROUP_CONCAT(DISTINCT u.id) as ids, 'Correo Electrónico' as reason
            FROM emails e
            JOIN users u ON e.user_id = u.id
            WHERE u.deleted_at IS NULL
            GROUP BY e.email_address HAVING count > 1
        """)

        # 3. Shared Phones (Intelligent Python Normalization)
        all_phones = self.db.execute_query("""
            SELECT p.local_number, u.id
            FROM phones p
            JOIN users u ON p.user_id = u.id
            WHERE u.deleted_at IS NULL
        """)

        normalized_map = {} # {normal_phone: [user_ids]}
        for p in all_phones:
            norm = self._normalize_phone(p['local_number'])
            if len(norm) < 7: continue # Ignore too short
            if norm not in normalized_map: normalized_map[norm] = set()
            normalized_map[norm].add(p['id'])

        phone_dups = []
        for norm, user_ids in normalized_map.items():
            if len(user_ids) > 1:
                phone_dups.append({
                    'reason': f'Número Telefónico (Símil: {norm})',
                    'count': len(user_ids),
                    'ids': ",".join(map(str, sorted(list(user_ids))))
                })

        # Consolidate and deduplicate result pairs
        results = []
        seen_pairs = set()

        for dup in (name_dups + email_dups + phone_dups):
            ids_list = sorted([int(x) for x in str(dup['ids']).split(',')])
            pair_key = tuple(ids_list)
            if pair_key not in seen_pairs:
                results.append(dup)
                seen_pairs.add(pair_key)

        return results

    def merge_users(self, survivor_id: int, duplicate_id: int):
        """
        Merges duplicate user into survivor with contact deduplication.
        """
        with self.db.transaction() as cursor:
            # 1. Deduplicate Emails
            # Get existing emails for survivor
            cursor.execute("SELECT email_address FROM emails WHERE user_id = %s", (survivor_id,))
            survivor_emails = {row['email_address'].lower() for row in cursor.fetchall()}
            
            # Get emails for duplicate
            cursor.execute("SELECT id, email_address FROM emails WHERE user_id = %s", (duplicate_id,))
            dup_emails = cursor.fetchall()
            
            for e in dup_emails:
                if e['email_address'].lower() in survivor_emails:
                    cursor.execute("DELETE FROM emails WHERE id = %s", (e['id'],))
                else:
                    cursor.execute("UPDATE emails SET user_id = %s WHERE id = %s", (survivor_id, e['id']))
            
            # 2. Deduplicate Phones (Intelligent Normalization)
            cursor.execute("SELECT local_number FROM phones WHERE user_id = %s", (survivor_id,))
            survivor_phones = {self._normalize_phone(row['local_number']) for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, local_number FROM phones WHERE user_id = %s", (duplicate_id,))
            dup_phones = cursor.fetchall()
            
            for p in dup_phones:
                norm_p = self._normalize_phone(p['local_number'])
                if norm_p in survivor_phones:
                    cursor.execute("DELETE FROM phones WHERE id = %s", (p['id'],))
                else:
                    cursor.execute("UPDATE phones SET user_id = %s WHERE id = %s", (survivor_id, p['id']))
                    survivor_phones.add(norm_p)

            # 3. Transfer Addresses (Simple transfer for now)
            cursor.execute("UPDATE IGNORE addresses SET user_id = %s WHERE user_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM addresses WHERE user_id = %s", (duplicate_id,))
            
            # 4. Transfer Company Links
            cursor.execute("UPDATE IGNORE user_companies SET user_id = %s WHERE user_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM user_companies WHERE user_id = %s", (duplicate_id,))

            # 5. Soft-delete the duplicate user record
            cursor.execute("UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s", (duplicate_id,))
            
        return True

    def find_company_duplicates(self) -> List[Dict[str, Any]]:
        """Finds potential duplicate companies."""
        sql = """
        SELECT legal_name, tax_id, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM companies
        WHERE deleted_at IS NULL
        GROUP BY legal_name, tax_id
        HAVING count > 1
        """
        return self.db.execute_query(sql)

    def merge_companies(self, survivor_id: int, duplicate_id: int):
        """
        Merges duplicate company into survivor with contact deduplication.
        """
        with self.db.transaction() as cursor:
            # 1. Deduplicate Emails
            cursor.execute("SELECT email_address FROM emails WHERE company_id = %s", (survivor_id,))
            survivor_emails = {row['email_address'].lower() for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, email_address FROM emails WHERE company_id = %s", (duplicate_id,))
            for e in cursor.fetchall():
                if e['email_address'].lower() in survivor_emails:
                    cursor.execute("DELETE FROM emails WHERE id = %s", (e['id'],))
                else:
                    cursor.execute("UPDATE emails SET company_id = %s WHERE id = %s", (survivor_id, e['id']))
            
            # 2. Deduplicate Phones
            cursor.execute("SELECT local_number FROM phones WHERE company_id = %s", (survivor_id,))
            survivor_phones = {self._normalize_phone(row['local_number']) for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, local_number FROM phones WHERE company_id = %s", (duplicate_id,))
            for p in cursor.fetchall():
                norm_p = self._normalize_phone(p['local_number'])
                if norm_p in survivor_phones:
                    cursor.execute("DELETE FROM phones WHERE id = %s", (p['id'],))
                else:
                    cursor.execute("UPDATE phones SET company_id = %s WHERE id = %s", (survivor_id, p['id']))
                    survivor_phones.add(norm_p)
            
            # 3. Transfer Addresses
            cursor.execute("UPDATE IGNORE addresses SET company_id = %s WHERE company_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM addresses WHERE company_id = %s", (duplicate_id,))
            
            # 4. Transfer User links
            cursor.execute("UPDATE IGNORE user_companies SET company_id = %s WHERE company_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM user_companies WHERE company_id = %s", (duplicate_id,))

            # 5. Soft-delete the duplicate company
            cursor.execute("UPDATE companies SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s", (duplicate_id,))
            
        return True
