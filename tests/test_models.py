import pytest
from sqlalchemy.exc import IntegrityError
from app.db.models import Tenant, Role, User
import uuid

def test_tenant_role_integrity(db_session):
    t1 = Tenant(id=uuid.uuid4(), name="T1", slug="t1", api_key_hash="x", target_db_dialect="pg", max_query_cost_limit=10)
    t2 = Tenant(id=uuid.uuid4(), name="T2", slug="t2", api_key_hash="y", target_db_dialect="pg", max_query_cost_limit=10)
    db_session.add_all([t1, t2])
    db_session.commit()

    r1 = Role(id=uuid.uuid4(), tenant_id=t1.id, name="Admin", allowed_schema_map={}, allowed_statements={})
    db_session.add(r1)
    db_session.commit()

    # Should fail because role r1 belongs to t1, but user belongs to t2
    u1 = User(id=uuid.uuid4(), tenant_id=t2.id, role_id=r1.id, email="a@b.com", full_name="User")
    db_session.add(u1)
    with pytest.raises(IntegrityError):
        db_session.commit()
