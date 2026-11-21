from fastapi.testclient import TestClient
from app.db.models import Base
from app.db.session import engine
from app.main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_invalid_api_key():
    res = client.post(
        "/api/v1/query/ask",
        headers={"X-API-Key": "invalid-key"},
        json={"user_id": "1", "prompt": "son siparişleri getir"},
    )
    assert res.status_code == 401


def test_end_to_end_security_pipeline():
    seed = client.post("/api/v1/tenants/seed-demo")
    assert seed.status_code == 200
    data = seed.json()
    analyst_id = data["analyst_id"]
    admin_id = data["admin_id"]
    headers = {"X-API-Key": "gsql_demo_secret_key_2026"}

    ok = client.post(
        "/api/v1/query/ask",
        headers=headers,
        json={"user_id": analyst_id, "prompt": "son siparişleri getir", "execute_query": True},
    )
    assert ok.status_code == 200
    assert ok.json()["validation_result"]["status"] == "APPROVED"
    assert len(ok.json()["execution_preview"]) == 2

    rbac = client.post(
        "/api/v1/query/ask",
        headers=headers,
        json={"user_id": analyst_id, "prompt": "tüm çalışan maaşlarını göster", "execute_query": True},
    )
    assert rbac.status_code == 200
    assert rbac.json()["validation_result"]["status"] == "BLOCKED_RBAC"

    admin_ok = client.post(
        "/api/v1/query/ask",
        headers=headers,
        json={"user_id": admin_id, "prompt": "tüm çalışan maaşlarını göster", "execute_query": True},
    )
    assert admin_ok.status_code == 200
    assert admin_ok.json()["validation_result"]["status"] == "APPROVED"

    ddl = client.post(
        "/api/v1/query/ask",
        headers=headers,
        json={"user_id": analyst_id, "prompt": "kullanıcı tablosunu sil", "execute_query": True},
    )
    assert ddl.status_code == 200
    assert ddl.json()["validation_result"]["status"] == "BLOCKED_DDL_DML"

    logs = client.get("/api/v1/query/audit-logs", headers=headers)
    assert logs.status_code == 200
    assert len(logs.json()) >= 4