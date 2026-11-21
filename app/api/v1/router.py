from fastapi import APIRouter
from app.api.v1.endpoints import health, query, tenants

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(query.router, prefix="/query", tags=["Query & Security"])