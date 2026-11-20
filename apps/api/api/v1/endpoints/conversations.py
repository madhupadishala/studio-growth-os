"""Tenant-scoped conversation reads backed by the product database."""
from fastapi import APIRouter, Depends, HTTPException, Query
from prisma import Prisma
from core.database import get_db
from api.v1.endpoints.auth import get_tenant_context

router = APIRouter()

@router.get("")
async def list_conversations(lead_id: str = Query(...), include_messages: bool = True,
                             tenant_ctx: dict = Depends(get_tenant_context),
                             db: Prisma = Depends(get_db)):
    lead = await db.lead.find_first(where={"id": lead_id, "tenantId": tenant_ctx["tenant_id"]})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    rows = await db.conversation.find_many(
        where={"leadId": lead_id, "tenantId": tenant_ctx["tenant_id"]},
        order={"createdAt": "asc"},
    )
    return {"lead_id": lead_id, "tenant_id": tenant_ctx["tenant_id"],
            "messages": rows if include_messages else []}
