"""RunGrow Workforce contract: tenant-scoped reads and governed idempotent writes."""
from __future__ import annotations
import os
from typing import Any
import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prisma import Prisma
from core.database import get_db
from core.rungrow_auth import require_workforce_scope
from core.workforce_idempotency import claim, complete

router = APIRouter()
READ = "photo-studio-growth-os:read"
WRITE = "photo-studio-growth-os:write"
AI_IDENTITY_DISCLOSURE = ("I am an AI assistant acting on behalf of RunGrow. I can help explain the product and "
                         "arrange a human follow-up; I am not a human representative.")

def _tenant(request: Request) -> str:
    context = request.scope.get("state", {}).get("rungrow_service")
    if not context or not context.get("external_tenant_id"):
        raise HTTPException(status_code=403, detail="Authenticated external tenant context is required")
    return context["external_tenant_id"]

def _correlation(request: Request) -> str:
    return request.scope.get("state", {}).get("rungrow_service", {}).get("correlation_id", "rungrow-service")

@router.get("/tenant-summary", dependencies=[Depends(require_workforce_scope(READ))])
async def tenant_summary(request: Request, db: Prisma = Depends(get_db)):
    tenant = _tenant(request)
    where = {"tenantId": tenant}
    lead_count = await db.lead.count(where=where)
    quote_count = await db.quote.count(where=where)
    booking_count = await db.booking.count(where=where)
    conversation_count = await db.conversation.count(where=where)
    return {"external_tenant_id": tenant, "lead_count": lead_count, "quote_count": quote_count,
            "booking_count": booking_count, "conversation_count": conversation_count}

@router.get("/leads", dependencies=[Depends(require_workforce_scope(READ))])
async def workforce_leads(request: Request, page: int = 1, page_size: int = 50,
                          stage: str | None = None, db: Prisma = Depends(get_db)):
    tenant = _tenant(request)
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    where: dict[str, Any] = {"tenantId": tenant}
    if stage:
        where["stage"] = stage
    rows = await db.lead.find_many(where=where, skip=(page - 1) * page_size,
                                   take=page_size, order={"createdAt": "desc"})
    total = await db.lead.count(where=where)
    return {"leads": rows, "total": total, "page": page, "page_size": page_size}

@router.get("/quotes", dependencies=[Depends(require_workforce_scope(READ))])
async def workforce_quotes(request: Request, page: int = 1, page_size: int = 50,
                           status: str | None = None, db: Prisma = Depends(get_db)):
    tenant = _tenant(request)
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    where: dict[str, Any] = {"tenantId": tenant}
    if status:
        where["status"] = status
    rows = await db.quote.find_many(where=where, skip=(page - 1) * page_size,
                                    take=page_size, order={"createdAt": "desc"})
    return rows

@router.get("/bookings", dependencies=[Depends(require_workforce_scope(READ))])
async def workforce_bookings(request: Request, page: int = 1, page_size: int = 50,
                             state: str | None = None, db: Prisma = Depends(get_db)):
    tenant = _tenant(request)
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    where: dict[str, Any] = {"tenantId": tenant}
    if state:
        where["state"] = state
    rows = await db.booking.find_many(where=where, skip=(page - 1) * page_size,
                                      take=page_size, order={"createdAt": "desc"})
    return rows

@router.get("/conversations/{lead_id}", dependencies=[Depends(require_workforce_scope(READ))])
async def workforce_conversation(lead_id: str, request: Request, db: Prisma = Depends(get_db)):
    tenant = _tenant(request)
    lead = await db.lead.find_first(where={"id": lead_id, "tenantId": tenant})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    rows = await db.conversation.find_many(
        where={"leadId": lead_id, "tenantId": tenant}, order={"createdAt": "asc"})
    return {"lead_id": lead_id, "external_tenant_id": tenant, "messages": rows}

class FollowupRequest(BaseModel):
    channel: str = "whatsapp"
    message: str | None = None
    quote_id: str | None = None
    template_vars: dict[str, Any] = Field(default_factory=dict)
    ai_identity_disclosure: str = Field(min_length=1)
    dry_run: bool = True

@router.post("/leads/{lead_id}/followup", dependencies=[Depends(require_workforce_scope(WRITE))])
async def lead_followup(lead_id: str, payload: FollowupRequest, request: Request,
                        idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
                        db: Prisma = Depends(get_db)):
    tenant, correlation = _tenant(request), _correlation(request)
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    if payload.ai_identity_disclosure != AI_IDENTITY_DISCLOSURE:
        raise HTTPException(status_code=422, detail="The approved RunGrow AI identity disclosure is mandatory")
    lead = await db.lead.find_first(where={"id": lead_id, "tenantId": tenant})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    body = payload.model_dump()
    endpoint = f"POST:/api/v1/workforce/leads/{lead_id}/followup"
    claim_result = await claim(tenant, endpoint, idempotency_key, body, correlation)
    if not claim_result["created"]:
        return JSONResponse(status_code=claim_result["status_code"], content=claim_result["body"])
    if payload.dry_run:
        response = {"status": "dry_run", "lead_id": lead_id, "channel": payload.channel,
                    "disclosure_included": True, "correlation_id": correlation}
    elif payload.channel == "whatsapp":
        token, phone_id = os.getenv("WHATSAPP_ACCESS_TOKEN", ""), os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        if not token or not phone_id:
            raise HTTPException(status_code=503, detail="WhatsApp provider is not configured")
        text = payload.message or (f"Your requested quote is ready. {payload.ai_identity_disclosure}")
        async with httpx.AsyncClient(timeout=15) as client:
            result = await client.post(f"https://graph.facebook.com/v21.0/{phone_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"messaging_product":"whatsapp","to":getattr(lead, "phone_e164", None),
                      "type":"text","text":{"body":text}})
        if result.is_error:
            raise HTTPException(status_code=502, detail="WhatsApp provider rejected the follow-up")
        response = {"status":"sent","lead_id":lead_id,"provider_response":result.json(),
                    "correlation_id":correlation}
    else:
        raise HTTPException(status_code=503, detail=f"{payload.channel} provider is not configured")
    await complete(tenant, endpoint, idempotency_key, 200, response)
    return response

class ProspectHandoffRequest(BaseModel):
    contact_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    approval_id: str = Field(min_length=1)
    correlation_id: str | None = None
    campaign: str | None = None
    event_date: str | None = None
    budget_band: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

@router.post("/prospects/handoff", dependencies=[Depends(require_workforce_scope(WRITE))])
async def prospect_handoff(payload: ProspectHandoffRequest, request: Request,
                           idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
                           db: Prisma = Depends(get_db)):
    tenant, correlation = _tenant(request), payload.correlation_id or _correlation(request)
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    body = payload.model_dump()
    endpoint = "POST:/api/v1/workforce/prospects/handoff"
    claim_result = await claim(tenant, endpoint, idempotency_key, body, correlation)
    if not claim_result["created"]:
        return JSONResponse(status_code=claim_result["status_code"], content=claim_result["body"])
    lead = await db.lead.find_first(where={"tenantId": tenant, "contactId": payload.contact_id})
    provenance = {**payload.metadata, "source_url": payload.source_url,
                  "correlation_id": correlation, "approval_id": payload.approval_id}
    data: dict[str, Any] = {"stage": "qualified", "sourceFirst": "rungrow",
                            "sourceLast": "rungrow", "campaign": payload.campaign,
                            "utmJson": provenance}
    if payload.event_date:
        data["eventDate"] = payload.event_date
    if payload.budget_band:
        data["budgetBand"] = payload.budget_band
    if lead:
        saved = await db.lead.update(where={"id": lead.id}, data=data)
    else:
        saved = await db.lead.create(data={"tenantId": tenant, "contactId": payload.contact_id, **data})
    response = {"status":"accepted","lead_id":saved.id,"external_tenant_id":tenant,
                "source_url":payload.source_url,"correlation_id":correlation,"approval_id":payload.approval_id}
    await complete(tenant, endpoint, idempotency_key, 200, response)
    return response
