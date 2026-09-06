from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, items, users
from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.core.redis import get_redis

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI + PostgreSQL + AWS Cognito + Floci Demo",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok", "environment": settings.APP_ENV}


@app.get("/health/db", tags=["Health"])
async def health_db() -> dict:
    try:
        from sqlalchemy import text

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "database": str(exc)}


@app.get("/health/redis", tags=["Health"])
async def health_redis() -> dict:
    try:
        redis = await get_redis()
        await redis.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as exc:
        return {"status": "error", "redis": str(exc)}


@app.get("/health/aws", tags=["Health"])
async def health_aws() -> dict:
    try:
        from app.integrations.aws.clients import AWSClientFactory

        client = AWSClientFactory.create_client("sts")
        client.get_caller_identity()
        return {"status": "ok", "aws": "connected"}
    except Exception as exc:
        return {"status": "error", "aws": str(exc)}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
