"""
Studio Growth OS - Leads Endpoints
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from prisma import Prisma
from prisma.enums import LeadStage

from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Schemas
class LeadBase(BaseModel):
    contact_id: str
    stage: LeadStage = LeadStage.new
    score: int = 0
    event_date: Optional[datetime] = None
    budget_band: Optional[str] = None
    source_first: Optional[str] = None
    source_last: Optional[str] = None
    utm_json: Optional[dict] = None
    campaign: Optional[str] = None
    owner_id: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    stage: Optional[LeadStage] = None
    score: Optional[int] = None
    event_date: Optional[datetime] = None
    budget_band: Optional[str] = None
    owner_id: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    tenant_id: str
    contact_id: str
    stage: str
    score: int
    event_date: Optional[datetime]
    budget_band: Optional[str]
    source_first: Optional[str]
    source_last: Optional[str]
    campaign: Optional[str]
    owner_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int

class LeadStageTransition(BaseModel):
    stage: LeadStage
    reason: Optional[str] = None

# Query parameters
class LeadFilterParams(BaseModel):
    stage: Optional[LeadStage] = None
    source: Optional[str] = None
    owner_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    search: Optional[str] = None

# Endpoints
@router.get("", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stage: Optional[LeadStage] = None,
    source: Optional[str] = None,
    owner_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|score|event_date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """List leads with filtering, pagination, and sorting"""
    where = {"tenantId": tenant_ctx["tenant_id"]}

    if stage:
        where["stage"] = stage
    if source:
        where["sourceFirst"] = source
    if owner_id:
        where["ownerId"] = owner_id
    if date_from or date_to:
        where["createdAt"] = {}
        if date_from:
            where["createdAt"]["gte"] = date_from
        if date_to:
            where["createdAt"]["lte"] = date_to
    if min_score is not None:
        where["score"] = where.get("score", {})
        where["score"]["gte"] = min_score
    if max_score is not None:
        where["score"] = where.get("score", {})
        where["score"]["lte"] = max_score
    if search:
        where["OR"] = [
            {"contact": {"displayName": {"contains": search, "mode": "insensitive"}}},
            {"contact": {"phoneE164": {"contains": search}}},
            {"contact": {"emailNormalized": {"contains": search, "mode": "insensitive"}}},
        ]

    order_by = {sort_by: sort_order}

    total = await db.lead.count(where=where)
    leads = await db.lead.find_many(
        where=where,
        order=order_by,
        skip=(page - 1) * page_size,
        take=page_size,
        include={
            "contact": True,
            "owner": True,
        },
    )

    return LeadListResponse(
        leads=[LeadResponse.model_validate(l) for l in leads],
        total=total,
        page=page,
        page_size=page_size,
    )

@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Create a new lead"""
    # Verify contact exists and belongs to tenant
    contact = await db.contact.find_first(
        where={"id": lead_data.contact_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    lead = await db.lead.create(
        data={
            **lead_data.model_dump(),
            "tenantId": tenant_ctx["tenant_id"],
        }
    )

    # Create audit event
    await db.auditEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "actorId": tenant_ctx["user_id"],
            "action": "lead_created",
            "entityType": "lead",
            "entityId": lead.id,
            "beforeAfterRef": {"after": {"stage": lead.stage, "source": lead.source_first}},
        }
    )

    logger.info("Lead created", lead_id=lead.id, tenant_id=tenant_ctx["tenant_id"])
    return LeadResponse.model_validate(lead)

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get a single lead by ID"""
    lead = await db.lead.find_first(
        where={"id": lead_id, "tenantId": tenant_ctx["tenant_id"]},
        include={"contact": True, "owner": True},
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)

@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Update a lead"""
    lead = await db.lead.find_first(
        where={"id": lead_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_data.model_dump(exclude_unset=True)
    old_stage = lead.stage

    lead = await db.lead.update(
        where={"id": lead_id},
        data=update_data,
    )

    # Audit stage change
    if "stage" in update_data and update_data["stage"] != old_stage:
        await db.auditEvent.create(
            data={
                "tenantId": tenant_ctx["tenant_id"],
                "actorId": tenant_ctx["user_id"],
                "action": "lead_stage_changed",
                "entityType": "lead",
                "entityId": lead_id,
                "beforeAfterRef": {"before": {"stage": old_stage}, "after": {"stage": update_data["stage"]}},
            }
        )

    return LeadResponse.model_validate(lead)

@router.post("/{lead_id}/stage", response_model=LeadResponse)
async def transition_lead_stage(
    lead_id: str,
    transition: LeadStageTransition,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Transition lead to a new stage with validation"""
    lead = await db.lead.find_first(
        where={"id": lead_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Validate stage transition
    valid_transitions = {
        "new": ["contacted", "spam"],
        "contacted": ["qualified", "spam", "lost"],
        "qualified": ["quote_requested", "lost"],
        "quote_requested": ["quoted", "lost"],
        "quoted": ["negotiating", "accepted", "declined", "expired", "lost"],
        "negotiating": ["quoted", "accepted", "declined", "lost"],
        "accepted": ["won"],
        "declined": ["lost"],
        "expired": ["lost"],
        "won": [],
        "lost": ["new"],  # allow restore
        "spam": [],
    }

    if transition.stage not in valid_transitions.get(lead.stage, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage transition from {lead.stage} to {transition.stage}",
        )

    old_stage = lead.stage
    lead = await db.lead.update(
        where={"id": lead_id},
        data={"stage": transition.stage},
    )

    # Audit
    await db.auditEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "actorId": tenant_ctx["user_id"],
            "action": "lead_stage_changed",
            "entityType": "lead",
            "entityId": lead_id,
            "beforeAfterRef": {
                "before": {"stage": old_stage},
                "after": {"stage": transition.stage, "reason": transition.reason},
            },
        }
    )

    logger.info("Lead stage transitioned", lead_id=lead_id, from_stage=old_stage, to_stage=transition.stage)
    return LeadResponse.model_validate(lead)

@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Delete a lead (soft delete by marking as spam)"""
    lead = await db.lead.find_first(
        where={"id": lead_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.lead.update(
        where={"id": lead_id},
        data={"stage": "spam"},
    )

    await db.auditEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "actorId": tenant_ctx["user_id"],
            "action": "lead_deleted",
            "entityType": "lead",
            "entityId": lead_id,
        }
    )