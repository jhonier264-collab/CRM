"""
Encabezado Profesional: Servicio de Higiene y Deduplicación de Datos
Propósito: Gestiona la limpieza, recuperación y fusión de registros (Deduplicación).
Por qué: Mantener la integridad de la base de datos y optimizar la calidad de la información SaaS.
"""

import logging
from typing import List, Dict, Any
from src.core.database_interface import IDatabase
from src.models.models import User, Company

class DataHygieneService:
    def __init__(self, persistence: IDatabase):
        """
        Inyección de dependencia: Recibe el motor de persistencia.
        """
        self.persistence = persistence
        self.logger = logging.getLogger(__name__)

    # --- Soft Delete & Recovery ---

    def list_trash(self, table: str) -> List[Dict[str, Any]]:
        """Lista elementos en la papelera de reciclaje."""
        if table not in ['users', 'companies']: return []
        command = f"SELECT * FROM {table} WHERE deleted_at IS NOT NULL"
        return self.persistence.execute_command(command)

    def restore_item(self, table: str, item_id: int):
        """Restaura un elemento borrado de forma suave."""
        sql = f"UPDATE {table} SET deleted_at = NULL WHERE id = %s"
        return self.persistence.execute_command(sql, (item_id,), perform_commit=True, fetch_results=False)

    def soft_delete_item(self, table: str, item_id: int):
        """Mueve un elemento a la papelera (Soft Delete)."""
        sql = f"UPDATE {table} SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.persistence.execute_command(sql, (item_id,), perform_commit=True, fetch_results=False)

    def permanent_delete_item(self, table: str, item_id: int):
        """Elimina PERMANENTEMENTE un registro y sus relaciones."""
        if table not in ['users', 'companies']: return False
        
        with self.persistence.start_transaction() as cursor:
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
        name_dups = self.persistence.execute_command("""
            SELECT first_name, last_name, COUNT(*) as count, GROUP_CONCAT(DISTINCT id) as ids, 'Nombre/Apellido' as reason
            FROM users WHERE deleted_at IS NULL GROUP BY first_name, last_name HAVING count > 1
        """)

        # 2. Shared Emails (SQL is fine)
        email_dups = self.persistence.execute_command("""
            SELECT e.email_address, COUNT(*) as count, GROUP_CONCAT(DISTINCT u.id) as ids, 'Correo Electrónico' as reason
            FROM emails e
            JOIN users u ON e.user_id = u.id
            WHERE u.deleted_at IS NULL
            GROUP BY e.email_address HAVING count > 1
        """)

        # 3. Shared Phones (Intelligent Python Normalization)
        all_phones = self.persistence.execute_command("""
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
        Fusiona un usuario duplicado en un sobreviviente con deduplicación de contactos.
        """
        with self.persistence.start_transaction() as cursor:
            # 1. Deduplicar Emails
            cursor.execute("SELECT email_address FROM emails WHERE user_id = %s", (survivor_id,))
            survivor_emails = {row['email_address'].lower() for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, email_address FROM emails WHERE user_id = %s", (duplicate_id,))
            dup_emails = cursor.fetchall()
            
            for e in dup_emails:
                if e['email_address'].lower() in survivor_emails:
                    cursor.execute("DELETE FROM emails WHERE id = %s", (e['id'],))
                else:
                    cursor.execute("UPDATE emails SET user_id = %s WHERE id = %s", (survivor_id, e['id']))
            
            # 2. Deduplicar Teléfonos (Normalización Inteligente)
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

            # 3. Transferir Direcciones
            cursor.execute("UPDATE IGNORE addresses SET user_id = %s WHERE user_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM addresses WHERE user_id = %s", (duplicate_id,))
            
            # 4. Transferir Vínculos con Empresas
            cursor.execute("UPDATE IGNORE user_companies SET user_id = %s WHERE user_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM user_companies WHERE user_id = %s", (duplicate_id,))

            # 5. Soft-delete del registro duplicado
            cursor.execute("UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s", (duplicate_id,))
            
        return True

    def find_company_duplicates(self) -> List[Dict[str, Any]]:
        """Busca posibles empresas duplicadas."""
        sql = """
        SELECT legal_name, tax_id, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM companies
        WHERE deleted_at IS NULL
        GROUP BY legal_name, tax_id
        HAVING count > 1
        """
        return self.persistence.execute_command(sql)

    def merge_companies(self, survivor_id: int, duplicate_id: int):
        """
        Fusiona una empresa duplicada en una sobreviviente.
        """
        with self.persistence.start_transaction() as cursor:
            # 1. Deduplicar Emails
            cursor.execute("SELECT email_address FROM emails WHERE company_id = %s", (survivor_id,))
            survivor_emails = {row['email_address'].lower() for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, email_address FROM emails WHERE company_id = %s", (duplicate_id,))
            for e in cursor.fetchall():
                if e['email_address'].lower() in survivor_emails:
                    cursor.execute("DELETE FROM emails WHERE id = %s", (e['id'],))
                else:
                    cursor.execute("UPDATE emails SET company_id = %s WHERE id = %s", (survivor_id, e['id']))
            
            # 2. Deduplicar Teléfonos
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
            
            # 3. Transferir Direcciones
            cursor.execute("UPDATE IGNORE addresses SET company_id = %s WHERE company_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM addresses WHERE company_id = %s", (duplicate_id,))
            
            # 4. Transferir Vínculos con Usuarios
            cursor.execute("UPDATE IGNORE user_companies SET company_id = %s WHERE company_id = %s", (survivor_id, duplicate_id))
            cursor.execute("DELETE FROM user_companies WHERE company_id = %s", (duplicate_id,))

            # 5. Soft-delete de la empresa duplicada
            cursor.execute("UPDATE companies SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s", (duplicate_id,))
            
        return True
