from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.session import engine
from .db.base import Base
from .api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="GuardSQL Enterprise", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
