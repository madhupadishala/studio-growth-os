"""Tenant-scoped booking API backed by the product database."""
from fastapi import APIRouter, Depends, Query
from prisma import Prisma
from core.database import get_db
from api.v1.endpoints.auth import get_tenant_context

router = APIRouter()

@router.get("")
async def list_bookings(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        state: str | None = None,
                        tenant_ctx: dict = Depends(get_tenant_context),
                        db: Prisma = Depends(get_db)):
    where = {"tenantId": tenant_ctx["tenant_id"]}
    if state:
        where["state"] = state
    rows = await db.booking.find_many(where=where, skip=(page - 1) * page_size,
                                      take=page_size, order={"createdAt": "desc"})
    total = await db.booking.count(where=where)
    return {"bookings": rows, "total": total, "page": page, "page_size": page_size}
