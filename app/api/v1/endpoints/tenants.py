from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Tenant # Assumed
from app.database import get_db
from app.core.security import hash_api_key

router = APIRouter()

@router.post("/seed-demo")
def seed_demo(db: Session = Depends(get_db)):
    # Create Acme Finans
    tenant = Tenant(name="Acme Finans A.Ş.", api_key_hash=hash_api_key("gsql_demo_secret_key_2026"), is_active=True)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return {"status": "success", "tenant_id": tenant.id}
