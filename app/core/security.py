import hashlib
import hmac
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Tenant
from app.db.session import get_db


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    return hmac.compare_digest(hash_api_key(raw_key), hashed_key)


def get_current_tenant(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.api_key_hash == hash_api_key(x_api_key)).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
    return tenant