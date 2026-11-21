import hashlib
import secrets
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Tenant  # Assuming models exists
from app.database import get_db  # Assuming database dependency exists

def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()

def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    return hash_api_key(raw_key) == hashed_key

def get_current_tenant(x_api_key: str = Header(alias="X-API-Key"), db: Session = Depends(get_db)) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.api_key_hash == hash_api_key(x_api_key)).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
    return tenant
