from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ALLOW_ORIGINS
from app.routers.health import router as health_router
from app.routers.stt import router as stt_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="opic-master-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(stt_router)
