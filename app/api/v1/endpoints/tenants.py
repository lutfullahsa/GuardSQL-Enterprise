from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_api_key
from app.db.models import Role, Tenant, User
from app.db.session import get_db

router = APIRouter()


@router.post("/seed-demo")
def seed_demo(db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == "acme-finans").first()
    if not tenant:
        tenant = Tenant(
            name="Acme Finans A.Ş.",
            slug="acme-finans",
            api_key_hash=hash_api_key("gsql_demo_secret_key_2026"),
            target_db_dialect="sqlite",
            max_query_cost_limit=10000,
            is_active=True,
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    analyst_role = db.query(Role).filter(Role.tenant_id == tenant.id, Role.name == "Finance_Analyst").first()
    if not analyst_role:
        analyst_role = Role(
            tenant_id=tenant.id,
            name="Finance_Analyst",
            allowed_schema_map={
                "customers": ["id", "full_name", "city"],
                "orders": ["id", "customer_name", "total_amount", "status"],
            },
            allowed_statements=["SELECT"],
            can_bypass_cost_limit=False,
        )
        db.add(analyst_role)
        db.commit()
        db.refresh(analyst_role)

    admin_role = db.query(Role).filter(Role.tenant_id == tenant.id, Role.name == "Risk_Admin").first()
    if not admin_role:
        admin_role = Role(
            tenant_id=tenant.id,
            name="Risk_Admin",
            allowed_schema_map={
                "customers": ["id", "full_name", "city", "email"],
                "orders": ["id", "customer_name", "total_amount", "status"],
                "hr_salaries": ["id", "employee_name", "salary"],
            },
            allowed_statements=["SELECT"],
            can_bypass_cost_limit=True,
        )
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    analyst = db.query(User).filter(User.tenant_id == tenant.id, User.email == "analyst@acmefinans.com").first()
    if not analyst:
        analyst = User(
            tenant_id=tenant.id,
            role_id=analyst_role.id,
            email="analyst@acmefinans.com",
            full_name="Ahmet Yılmaz (Analyst)",
            preferred_language="tr",
        )
        db.add(analyst)
        db.commit()
        db.refresh(analyst)

    admin = db.query(User).filter(User.tenant_id == tenant.id, User.email == "admin@acmefinans.com").first()
    if not admin:
        admin = User(
            tenant_id=tenant.id,
            role_id=admin_role.id,
            email="admin@acmefinans.com",
            full_name="Zeynep Kaya (Risk Admin)",
            preferred_language="tr",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    db.execute(text("CREATE TABLE IF NOT EXISTS customers (id INT, full_name TEXT, city TEXT, email TEXT)"))
    db.execute(text("CREATE TABLE IF NOT EXISTS orders (id INT, customer_name TEXT, total_amount REAL, status TEXT)"))
    db.execute(text("CREATE TABLE IF NOT EXISTS hr_salaries (id INT, employee_name TEXT, salary REAL)"))

    if db.execute(text("SELECT COUNT(*) FROM orders")).scalar() == 0:
        db.execute(text("INSERT INTO customers VALUES (1, 'Mehmet Demir', 'İstanbul', 'mehmet@ornek.com'), (2, 'Ayşe Çelik', 'Bursa', 'ayse@ornek.com')"))
        db.execute(text("INSERT INTO orders VALUES (101, 'Mehmet Demir', 45000.0, 'COMPLETED'), (102, 'Ayşe Çelik', 18500.0, 'PENDING')"))
        db.execute(text("INSERT INTO hr_salaries VALUES (1, 'Ahmet Yılmaz', 85000.0), (2, 'Zeynep Kaya', 140000.0)"))
    db.commit()

    return {
        "status": "success",
        "tenant_id": tenant.id,
        "api_key": "gsql_demo_secret_key_2026",
        "analyst_id": analyst.id,
        "admin_id": admin.id,
    }