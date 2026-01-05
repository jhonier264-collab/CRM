
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class User:
    id: Optional[int] = None
    agent_id: Optional[int] = None
    role_id: Optional[int] = None
    status_id: int = 1
    prefix: Optional[str] = None
    first_name: str = ""
    middle_name: Optional[str] = None
    last_name: str = ""
    username: Optional[str] = None
    password_hash: Optional[str] = None
    suffix: Optional[str] = None
    nickname: Optional[str] = None
    phonetic_first_name: Optional[str] = None
    phonetic_middle_name: Optional[str] = None
    phonetic_last_name: Optional[str] = None
    file_as: Optional[str] = None
    rut_nit: Optional[str] = None
    verification_digit: Optional[int] = None
    birthday: Optional[datetime] = None
    gender_id: Optional[int] = None
    notes: Optional[str] = None
    is_natural_person: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in User.__dataclass_fields__.values()}})

@dataclass
class Company:
    id: Optional[int] = None
    agent_id: Optional[int] = None
    status_id: int = 1
    rut_nit: str = ""
    verification_digit: Optional[int] = None
    legal_name: str = ""
    commercial_name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    revenue: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in Company.__dataclass_fields__.values()}})

@dataclass
class Address:
    id: Optional[int] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    postal_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in Address.__dataclass_fields__.values()}})

@dataclass
class Phone:
    id: Optional[int] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    country_id: int = 1
    local_number: str = ""
    label_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in Phone.__dataclass_fields__.values()}})

@dataclass
class Email:
    id: Optional[int] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    email_address: str = ""
    label_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in Email.__dataclass_fields__.values()}})
