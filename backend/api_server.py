
import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.services.data_hygiene_service import DataHygieneService
from src.models.models import User, Company, Phone, Email, Address

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CRM Industrial API", version="1.0.0")

# CORS Setup for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection
def get_db():
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()

def get_service(db: DatabaseManager = Depends(get_db)):
    return CRMService(db)

def get_hygiene(db: DatabaseManager = Depends(get_db)):
    return DataHygieneService(db)

# --- MODELS FOR API ---
class PhoneInput(BaseModel):
    local_number: str
    label_id: int = 1
    country_id: Optional[int] = 1

class EmailInput(BaseModel):
    email_address: str
    label_id: int = 1

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    tax_id: Optional[str] = None
    status_id: int = 1
    is_natural_person: bool = True
    phones: List[PhoneInput] = []
    emails: List[EmailInput] = []
    # Authentication fields
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None

class CompanyCreate(BaseModel):
    legal_name: str
    rut_nit: Optional[str] = None
    verification_digit: Optional[int] = None
    domain: Optional[str] = None
    status_id: int = 1
    phones: List[PhoneInput] = []
    emails: List[EmailInput] = []

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "online", "message": "CRM API is running"}

# USERS
@app.get("/users")
def list_users(service: CRMService = Depends(get_service)):
    return service.get_users_summary()

@app.post("/users")
def create_user(user_data: UserCreate, service: CRMService = Depends(get_service)):
    try:
        u = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            rut_nit=user_data.tax_id,
            status_id=user_data.status_id,
            is_natural_person=user_data.is_natural_person,
            username=user_data.username,
            role_id=user_data.role_id
        )
        phones = [Phone(local_number=p.local_number, label_id=p.label_id) for p in user_data.phones]
        emails = [Email(email_address=e.email_address, label_id=e.label_id) for e in user_data.emails]
        
        user_id = service.create_user_complete(u, phones=phones, emails=emails, password=user_data.password)
        return {"id": user_id, "message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}")
def get_user_detail(user_id: int, service: CRMService = Depends(get_service)):
    detail = service.get_user_detail_full(user_id)
    if not detail:
        raise HTTPException(status_code=404, detail="User not found")
    return detail

@app.put("/users/{user_id}")
def update_user_complete(user_id: int, data: Dict[str, Any], service: CRMService = Depends(get_service)):
    try:
        service.update_user_complete(user_id, data)
        return {"message": "User and relations updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/users/{user_id}")
def delete_user(user_id: int, service: CRMService = Depends(get_service)):
    service.delete_user_complete(user_id)
    return {"message": "User moved to trash"}

@app.post("/users/{user_id}/restore")
def restore_user(user_id: int, hygiene: DataHygieneService = Depends(get_hygiene)):
    success = hygiene.restore_item('users', user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error restoring user")
    return {"message": "User restored"}

# COMPANIES
@app.get("/companies")
def list_companies(service: CRMService = Depends(get_service)):
    return service.get_companies_summary()

@app.post("/companies")
def create_company(data: CompanyCreate, service: CRMService = Depends(get_service)):
    try:
        c = Company(
            legal_name=data.legal_name,
            rut_nit=data.rut_nit,
            verification_digit=data.verification_digit,
            domain=data.domain,
            status_id=data.status_id
        )
        phones = [Phone(local_number=p.local_number, label_id=p.label_id) for p in data.phones]
        emails = [Email(email_address=e.email_address, label_id=e.label_id) for e in data.emails]
        
        company_id = service.create_company_complete(c, phones=phones, emails=emails)
        return {"id": company_id, "message": "Company created successfully"}
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/companies/{company_id}")
def get_company_detail(company_id: int, service: CRMService = Depends(get_service)):
    detail = service.get_company_detail_full(company_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Company not found")
    return detail

@app.put("/companies/{company_id}")
def update_company_complete(company_id: int, data: Dict[str, Any], service: CRMService = Depends(get_service)):
    try:
        service.update_company_complete(company_id, data)
        return {"message": "Company and relations updated successfully"}
    except Exception as e:
        logger.error(f"Error updating company: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/companies/{company_id}")
def delete_company(company_id: int, service: CRMService = Depends(get_service)):
    service.delete_company_complete(company_id)
    return {"message": "Company moved to trash"}

@app.get("/geography/countries")
def list_countries(service: CRMService = Depends(get_service)):
    return service.list_countries()

@app.get("/catalog/genders")
def list_genders(service: CRMService = Depends(get_service)):
    return service.get_genders()

@app.get("/catalog/labels")
def list_labels(service: CRMService = Depends(get_service)):
    return service.get_labels()

@app.get("/catalog/positions")
def list_positions(service: CRMService = Depends(get_service)):
    return service.get_cargos()

@app.get("/catalog/departments")
def list_departments(service: CRMService = Depends(get_service)):
    return service.get_departments()

@app.post("/professional/link")
def link_professional(data: Dict[str, Any], service: CRMService = Depends(get_service)):
    try:
        service.link_user_to_company(
            user_id=data['user_id'],
            company_id=data['company_id'],
            position_id=data.get('position_id', 1),
            department_id=data.get('department_id', 1)
        )
        return {"message": "Professional link established"}
    except Exception as e:
        logger.error(f"Error linking professional: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/professional/unlink")
def unlink_professional(user_id: int, company_id: int, service: CRMService = Depends(get_service)):
    try:
        service.unlink_user_from_company(user_id, company_id)
        return {"message": "Professional link removed"}
    except Exception as e:
        logger.error(f"Error unlinking professional: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# HYGIENE
@app.get("/hygiene/trash/{table}")
def list_trash(table: str, hygiene: DataHygieneService = Depends(get_hygiene)):
    if table not in ['users', 'companies']:
        raise HTTPException(status_code=400, detail="Invalid table")
    return hygiene.list_trash(table)

@app.post("/hygiene/purge/{table}")
def purge_trash(table: str, hygiene: DataHygieneService = Depends(get_hygiene)):
    success = hygiene.purge_trash(table)
    return {"success": success, "message": f"Trash for {table} purged"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
