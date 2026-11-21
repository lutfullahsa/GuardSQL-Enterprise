import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import get_current_tenant
from app.db.models import QueryAuditLog, Tenant, User
from app.db.session import get_db
from app.schemas.query import AuditLogOut, NaturalLanguageQueryRequest, NaturalLanguageQueryResponse
from app.schemas.validation import SQLValidationRequest
from app.services.sql_validator import SQLValidatorService
from app.services.text_to_sql import TextToSQLService

router = APIRouter()
text_to_sql = TextToSQLService()
validator = SQLValidatorService()


@router.post("/validate")
def validate_sql_endpoint(req: SQLValidationRequest):
    return validator.validate(
        sql=req.sql,
        dialect=req.dialect,
        allowed_schema_map=req.allowed_schema_map,
        allowed_statements=req.allowed_statements,
        max_cost_limit=req.max_cost_limit,
        can_bypass_cost_limit=req.can_bypass_cost_limit,
        language=req.language,
    )


@router.post("/ask", response_model=NaturalLanguageQueryResponse)
def ask_query(
    req: NaturalLanguageQueryRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    start_time = time.perf_counter()
    user = db.query(User).filter(User.id == req.user_id, User.tenant_id == tenant.id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=403, detail="User not found or access denied")

    lang = req.language or user.preferred_language
    generated_sql = text_to_sql.generate_sql(req.prompt, user.role.allowed_schema_map, dialect=tenant.target_db_dialect)

    val_res = validator.validate(
        sql=generated_sql,
        dialect=tenant.target_db_dialect,
        allowed_schema_map=user.role.allowed_schema_map,
        allowed_statements=user.role.allowed_statements,
        max_cost_limit=tenant.max_query_cost_limit,
        can_bypass_cost_limit=user.role.can_bypass_cost_limit,
        language=lang,
    )

    preview = None
    if val_res.is_valid and req.execute_query and val_res.sanitized_sql:
        rows = db.execute(text(val_res.sanitized_sql)).mappings().fetchmany(50)
        preview = [dict(r) for r in rows]

    elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

    audit = QueryAuditLog(
        tenant_id=tenant.id,
        user_id=user.id,
        target_dialect=tenant.target_db_dialect,
        natural_language_prompt=req.prompt,
        generated_sql=generated_sql,
        status=val_res.status.value,
        block_reason=val_res.block_reason,
        estimated_cost=val_res.estimated_cost,
        execution_time_ms=elapsed_ms,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    return NaturalLanguageQueryResponse(
        audit_id=audit.id,
        tenant_name=tenant.name,
        user_email=user.email,
        role_name=user.role.name,
        generated_sql=generated_sql,
        validation_result=val_res,
        execution_preview=preview,
        execution_time_ms=elapsed_ms,
    )


@router.get("/audit-logs", response_model=list[AuditLogOut])
def get_audit_logs(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return (
        db.query(QueryAuditLog)
        .filter(QueryAuditLog.tenant_id == tenant.id)
        .order_by(QueryAuditLog.created_at.desc())
        .limit(50)
        .all()
    )