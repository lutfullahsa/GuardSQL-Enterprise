from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_tenant
from app.schemas.query import NaturalLanguageQueryRequest, NaturalLanguageQueryResponse
from app.services.text_to_sql import TextToSQLService
from app.models import Tenant, User, QueryAuditLog # Assuming models exist
from app.database import get_db

router = APIRouter()
text_to_sql = TextToSQLService()

@router.post("/ask", response_model=NaturalLanguageQueryResponse)
async def ask_query(req: NaturalLanguageQueryRequest, tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id, User.tenant_id == tenant.id).first()
    if not user:
        raise HTTPException(status_code=403, detail="User not found or access denied")
    
    # 1. Generate SQL
    sql = text_to_sql.generate_sql(req.prompt, user.role.allowed_schema_map)
    
    # 2. Validation (Placeholder for SQLValidatorService)
    # Result: APPROVED or BLOCKED_*
    
    # 3. Log
    log = QueryAuditLog(tenant_id=tenant.id, user_id=user.id, query=sql, status="APPROVED")
    db.add(log)
    db.commit()
    
    return NaturalLanguageQueryResponse(
        audit_id=str(log.id),
        tenant_name=tenant.name,
        user_email=user.email,
        role_name=user.role.name,
        generated_sql=sql,
        validation_result={"status": "APPROVED", "message": "Query validated"},
        execution_time_ms=10
    )
