# backend/app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import init_db
from app.seed import seed_demo_conversations, seed_demo_provider_data, seed_character_bots
from app.services import init_providers, ProviderRegistry
from app.routes import chat_router, orders_router, export_router, character_router

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클"""
    # Startup
    logger.info("🚀 Starting ChatBook API...")
    init_db()
    seed_demo_conversations()
    seed_demo_provider_data()
    seed_character_bots()
    init_providers(settings)
    logger.info(f"[OK] Providers registered: {ProviderRegistry.list_providers()}")
    yield
    # Shutdown
    logger.info("👋 Shutting down...")


app = FastAPI(
    title="ChatBook API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

# 라우터 등록
app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(export_router)
app.include_router(character_router)


# ==================== 공통 예외 핸들러 ====================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Provider 선택 오류 등 비즈니스 로직 예외"""
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "BAD_REQUEST", "message": str(exc)},
    )


@app.exception_handler(ConnectionError)
async def connection_error_handler(request: Request, exc: ConnectionError):
    """AI Provider 연결 오류"""
    logger.error(f"ConnectionError: {exc}")
    return JSONResponse(
        status_code=502,
        content={"error": "AI_PROVIDER_ERROR", "message": f"AI 서비스 연결 실패: {str(exc)}"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """처리되지 않은 모든 예외"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "message": "서버 내부 오류가 발생했습니다."},
    )


# 헬스체크
@app.get("/api/health")
async def health_check():
    db_status = "ok"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")
        db_status = "unavailable"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": "chatbook-backend",
        "demo_mode": settings.USE_DEMO_MODE,
        "database": db_status,
    }
