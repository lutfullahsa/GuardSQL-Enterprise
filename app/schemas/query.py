from datetime import datetime
from pydantic import BaseModel
from app.schemas.validation import SQLValidationResult


class NaturalLanguageQueryRequest(BaseModel):
    user_id: str
    prompt: str
    execute_query: bool = False
    language: str | None = None


class NaturalLanguageQueryResponse(BaseModel):
    audit_id: str
    tenant_name: str
    user_email: str
    role_name: str
    generated_sql: str
    validation_result: SQLValidationResult
    execution_preview: list[dict] | None = None
    execution_time_ms: int


class AuditLogOut(BaseModel):
    id: str
    user_id: str | None
    target_dialect: str
    natural_language_prompt: str
    generated_sql: str | None
    status: str
    block_reason: str | None
    estimated_cost: int | None
    execution_time_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}