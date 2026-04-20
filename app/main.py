from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.api.routers.mock_tests import router as mock_test_router
from app.api.routers.practice import router as practice_router
from app.api.routers.records import router as records_router
from app.api.routers.saved import router as saved_router
from app.api.routers.stt import router as stt_router
from app.api.routers.users import router as users_router
from app.config import CORS_ALLOW_ORIGINS
from app.db.base import Base
from app.db import models as _models
from app.db.session import engine

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="opic-master-backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(stt_router)
app.include_router(practice_router)
app.include_router(mock_test_router)
app.include_router(saved_router)
app.include_router(records_router)
