from fastapi import APIRouter
from .endpoints import health, query, tenants

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
