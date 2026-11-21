from pydantic import BaseModel
from typing import Optional, List

class NaturalLanguageQueryRequest(BaseModel):
    user_id: str
    prompt: str
    execute_query: bool = False
    language: Optional[str] = None

class SQLValidationResult(BaseModel):
    status: str
    message: str

class NaturalLanguageQueryResponse(BaseModel):
    audit_id: str
    tenant_name: str
    user_email: str
    role_name: str
    generated_sql: str
    validation_result: SQLValidationResult
    execution_preview: Optional[List[dict]] = None
    execution_time_ms: int

class AuditLogOut(BaseModel):
    id: int
    tenant_id: int
    user_id: str
    query: str
    status: str
    timestamp: str
