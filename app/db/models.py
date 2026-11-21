import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

JSONType = JSON().with_variant(JSONB(), "postgresql")

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    api_key_hash: Mapped[str] = mapped_column(String(255))
    target_db_dialect: Mapped[str] = mapped_column(String(50))
    max_query_cost_limit: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    name: Mapped[str] = mapped_column(String(100))
    allowed_schema_map: Mapped[dict] = mapped_column(JSONType)
    allowed_statements: Mapped[dict] = mapped_column(JSONType)
    can_bypass_cost_limit: Mapped[bool] = mapped_column(default=False)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uix_tenant_role_name"),
    )

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    role_id: Mapped[uuid.UUID]
    email: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["role_id", "tenant_id"], 
            ["roles.id", "roles.tenant_id"], 
            ondelete="RESTRICT"
        ),
    )
