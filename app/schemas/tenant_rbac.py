from pydantic import BaseModel, ConfigDict
import uuid

class TenantBase(BaseModel):
    name: str
    slug: str

class UserCreate(BaseModel):
    tenant_id: uuid.UUID
    role_id: uuid.UUID
    email: str
    full_name: str
