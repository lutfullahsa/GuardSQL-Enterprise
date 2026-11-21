from enum import Enum
from pydantic import BaseModel


class ValidationStatus(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED_SYNTAX = "BLOCKED_SYNTAX"
    BLOCKED_DDL_DML = "BLOCKED_DDL_DML"
    BLOCKED_HALLUCINATION = "BLOCKED_HALLUCINATION"
    BLOCKED_RBAC = "BLOCKED_RBAC"
    BLOCKED_COST = "BLOCKED_COST"


class SQLValidationRequest(BaseModel):
    sql: str
    dialect: str = "postgres"
    allowed_schema_map: dict[str, list[str]]
    allowed_statements: list[str] = ["SELECT"]
    max_cost_limit: int = 10000
    can_bypass_cost_limit: bool = False
    language: str = "tr"


class SQLValidationResult(BaseModel):
    is_valid: bool
    status: ValidationStatus
    sanitized_sql: str | None = None
    block_reason: str | None = None
    detected_tables: list[str] = []
    detected_columns: list[str] = []
    estimated_cost: int = 0