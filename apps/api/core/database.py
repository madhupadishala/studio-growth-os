"""
Studio Growth OS - Database Connection
"""
from prisma import Prisma
from core.config import settings

prisma = Prisma(
    datasource={
        "url": settings.DATABASE_URL,
    },
    auto_register=True,
    log_queries=settings.DEBUG,
)


async def get_db() -> Prisma:
    if not prisma.is_connected():
        await prisma.connect()
    return prisma