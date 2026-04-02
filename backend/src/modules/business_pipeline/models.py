from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Deal:
    id: Optional[int] = None
    title: str = ""
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    value: float = 0.0
    stage_id: int = 1
    expected_closing_date: Optional[datetime] = None
    agent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Quote:
    id: Optional[int] = None
    deal_id: int = 0
    quote_number: str = ""
    total_amount: float = 0.0
    status: str = "Draft"
    valid_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
