import asyncio
from fastapi import FastAPI
from logzero import logger

from app.config import settings
from app.db.session import Base, engine, SessionLocal
from app.providers.smartapi_provider import SmartAPIProvider
from app.services.levels_service import LevelsService
from app.services.scanner_service import ScannerService

from app.routers import (
    health,
    signals,
    market,
    ws,
    instruments,
    dashboard,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React dev
        "http://127.0.0.1:3000",
        "http://localhost:5173",     # Vite
        "http://127.0.0.1:5173",
        "http://localhost:5500",     # static server
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

    provider = SmartAPIProvider()
    levels = LevelsService(provider)
    scanner = ScannerService(provider, levels)

    app.state.scanner = scanner
    asyncio.create_task(scanner.run_intraday_loop(SessionLocal))

    logger.info("🚀 App initialized & scanner loop started")


# 🔥 ROUTERS (ORDER DOES NOT MATTER)
app.include_router(health.router)
app.include_router(signals.router)
app.include_router(market.router)
app.include_router(instruments.router)
app.include_router(dashboard.router)
app.include_router(signals.router)
app.include_router(ws.router)


