from typing import List, Dict, Any, Optional
from src.core.database_interface import IDatabase
from .models import Deal, Quote

class BusinessPipelineRepository:
    def __init__(self, db: IDatabase):
        self.db = db

    def create_deal(self, deal: Deal) -> int:
        sql = """
            INSERT INTO deals (title, company_id, contact_id, value, stage_id, expected_closing_date, agent_id, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (deal.title, deal.company_id, deal.contact_id, deal.value, deal.stage_id, deal.expected_closing_date, deal.agent_id, deal.description)
        return self.db.execute_command(sql, params, perform_commit=True, fetch_results=False)

    def get_deal(self, deal_id: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM deals WHERE id = %s AND deleted_at IS NULL"
        res = self.db.execute_command(sql, (deal_id,))
        return res[0] if res else None

    def list_deals(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM deals WHERE deleted_at IS NULL"
        return self.db.execute_command(sql)

    def update_deal_stage(self, deal_id: int, stage_id: int):
        sql = "UPDATE deals SET stage_id = %s WHERE id = %s"
        return self.db.execute_command(sql, (stage_id, deal_id), perform_commit=True, fetch_results=False)

    def create_quote(self, quote: Quote) -> int:
        sql = """
            INSERT INTO quotes (deal_id, quote_number, total_amount, status, valid_until)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (quote.deal_id, quote.quote_number, quote.total_amount, quote.status, quote.valid_until)
        return self.db.execute_command(sql, params, perform_commit=True, fetch_results=False)
