"""
Studio Growth OS - shared native Prisma database connection.
All API persistence, including workforce idempotency, uses this client.
"""
from prisma import Prisma
from core.config import settings

db = Prisma(
    datasource={"url": settings.DATABASE_URL},
    auto_register=True,
    log_queries=settings.DEBUG,
)

# Backwards-compatible alias for existing routers and services.
prisma = db


async def get_db() -> Prisma:
    if not db.is_connected():
        await db.connect()
    return db
