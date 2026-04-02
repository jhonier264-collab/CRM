from typing import List, Dict, Any, Optional
from src.core.database_interface import IDatabase
from .repositories import BusinessPipelineRepository
from .models import Deal, Quote

class BusinessPipelineService:
    def __init__(self, db: IDatabase):
        self.db = db
        self.repo = BusinessPipelineRepository(db)

    def register_deal(self, deal_data: Dict[str, Any]) -> int:
        deal = Deal(**deal_data)
        return self.repo.create_deal(deal)

    def get_pipeline_summary(self) -> List[Dict[str, Any]]:
        return self.repo.list_deals()

    def advance_deal(self, deal_id: int, next_stage_id: int):
        return self.repo.update_deal_stage(deal_id, next_stage_id)

    def generate_quote(self, quote_data: Dict[str, Any]) -> int:
        quote = Quote(**quote_data)
        return self.repo.create_quote(quote)
