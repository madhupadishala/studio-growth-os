"""
Studio Growth OS - Quotes Endpoints
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from prisma import Prisma

from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Schemas
class QuoteItemCreate(BaseModel):
    package_id: Optional[str] = None
    addon_id: Optional[str] = None
    name: str
    base_price_paise: int
    quantity: int = 1

class QuoteItemResponse(BaseModel):
    id: str
    package_id: Optional[str]
    addon_id: Optional[str]
    name: str
    base_price_paise: int
    quantity: int
    line_total_paise: int

class QuoteCalculateRequest(BaseModel):
    lead_id: str
    package_id: str
    addon_ids: List[str] = []
    event_date: datetime
    location: str
    discount_code: Optional[str] = None

class QuoteCalculateResponse(BaseModel):
    quote_id: str
    items: List[QuoteItemResponse]
    totals: dict
    policy_flags: dict
    snapshot_ref: str
    expires_at: datetime

class QuoteResponse(BaseModel):
    id: str
    tenant_id: str
    lead_id: str
    revision: int
    status: str
    pricebook_version: int
    totals_json: dict
    expires_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class QuoteApproveRequest(BaseModel):
    revision: int

class QuoteSendRequest(BaseModel):
    channel: str = "whatsapp"
    template_vars: dict = {}

# Endpoints
@router.post("/calculate", response_model=QuoteCalculateResponse)
async def calculate_quote(
    request: QuoteCalculateRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Calculate a quote using the pricing engine"""
    # Verify lead exists and belongs to tenant
    lead = await db.lead.find_first(
        where={"id": request.lead_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Verify package exists and is active
    package = await db.servicePackage.find_first(
        where={"id": request.package_id, "tenantId": tenant_ctx["tenant_id"], "isActive": True}
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Get active pricing rules
    pricing_rule = await db.pricingRule.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "isActive": True},
        order={"version": "desc"},
    )
    if not pricing_rule:
        raise HTTPException(status_code=500, detail="No active pricing rules configured")

    # Calculate pricing (simplified - in production use pricing engine service)
    items = []
    subtotal = 0

    # Base package
    package_price = package.basePricePaise
    items.append({
        "package_id": package.id,
        "name": package.name,
        "base_price_paise": package_price,
        "quantity": 1,
        "line_total_paise": package_price,
    })
    subtotal += package_price

    # Add-ons
    for addon_id in request.addon_ids:
        # Find addon in package addOns JSON
        for addon in package.addOns:
            if addon["id"] == addon_id:
                addon_price = addon["price_paise"]
                items.append({
                    "addon_id": addon_id,
                    "name": addon["name"],
                    "base_price_paise": addon_price,
                    "quantity": 1,
                    "line_total_paise": addon_price,
                })
                subtotal += addon_price
                break

    # Travel calculation (simplified)
    travel_paise = 0
    if request.location:
        # In production, calculate actual distance and apply travel policy
        travel_paise = 26000  # placeholder

    if travel_paise > 0:
        items.append({
            "name": f"Travel ({request.location})",
            "base_price_paise": travel_paise,
            "quantity": 1,
            "line_total_paise": travel_paise,
        })
        subtotal += travel_paise

    # Discount
    discount_paise = 0
    if request.discount_code:
        # Validate discount code against pricing rules
        discount_paise = 0  # placeholder

    total = subtotal - discount_paise

    # Create quote
    quote = await db.quote.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "leadId": request.lead_id,
            "revision": 1,
            "status": "draft",
            "pricebookVersion": pricing_rule.version,
            "totalsJson": {
                "items": items,
                "subtotal_paise": subtotal,
                "discount_paise": discount_paise,
                "tax_paise": 0,
                "total_paise": total,
                "currency": "INR",
            },
            "expiresAt": datetime.utcnow() + timedelta(days=7),
        }
    )

    # Create quote items
    for item in items:
        await db.quoteItem.create(
            data={
                "quoteId": quote.id,
                "packageId": item.get("package_id"),
                "addonId": item.get("addon_id"),
                "name": item["name"],
                "basePricePaise": item["base_price_paise"],
                "quantity": item.get("quantity", 1),
                "lineTotalPaise": item["line_total_paise"],
            }
        )

    # Policy flags
    policy_flags = {
        "requires_approval": total > 5000000,  # 50k INR
        "discount_approval_needed": discount_paise > 0,
        "travel_approval_needed": travel_paise > 0,
    }

    return QuoteCalculateResponse(
        quote_id=quote.id,
        items=[QuoteItemResponse(**i) for i in items],
        totals={
            "subtotal_paise": subtotal,
            "discount_paise": discount_paise,
            "tax_paise": 0,
            "total_paise": total,
            "currency": "INR",
        },
        policy_flags=policy_flags,
        snapshot_ref=f"pricing_v{pricing_rule.version}",
        expires_at=quote.expiresAt,
    )

@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get a quote by ID"""
    quote = await db.quote.find_first(
        where={"id": quote_id, "tenantId": tenant_ctx["tenant_id"]},
        include={"items": True, "lead": {"include": {"contact": True}}},
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return QuoteResponse.model_validate(quote)

@router.post("/{quote_id}/approve", response_model=QuoteResponse)
async def approve_quote(
    quote_id: str,
    request: QuoteApproveRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Approve a quote (requires owner/manager role)"""
    quote = await db.quote.find_first(
        where={"id": quote_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    if quote.revision != request.revision:
        raise HTTPException(status_code=409, detail="Quote revision mismatch")

    if quote.status not in ["draft", "pending_approval"]:
        raise HTTPException(status_code=400, detail="Quote cannot be approved in current state")

    # Check approval permissions
    if tenant_ctx["role"] not in ["studio.owner", "studio.manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to approve quotes")

    quote = await db.quote.update(
        where={"id": quote_id},
        data={
            "status": "approved",
            "approvedBy": tenant_ctx["user_id"],
            "approvedAt": datetime.utcnow(),
        }
    )

    # Audit
    await db.auditEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "actorId": tenant_ctx["user_id"],
            "action": "quote_approved",
            "entityType": "quote",
            "entityId": quote_id,
            "beforeAfterRef": {"before": {"status": "pending_approval"}, "after": {"status": "approved"}},
        }
    )

    logger.info("Quote approved", quote_id=quote_id, by=tenant_ctx["user_id"])
    return QuoteResponse.model_validate(quote)

@router.post("/{quote_id}/send")
async def send_quote(
    quote_id: str,
    request: QuoteSendRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Send quote to customer via specified channel"""
    quote = await db.quote.find_first(
        where={"id": quote_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    if quote.status != "approved":
        raise HTTPException(status_code=400, detail="Quote must be approved before sending")

    # Update quote status
    quote = await db.quote.update(
        where={"id": quote_id},
        data={"status": "sent"}
    )

    # In production: send via WhatsApp/email/etc.
    # For now, just log
    logger.info("Quote sent", quote_id=quote_id, channel=request.channel)

    return {"message": "Quote sent successfully", "quote_id": quote_id}

@router.get("", response_model=List[QuoteResponse])
async def list_quotes(
    status: Optional[str] = None,
    lead_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """List quotes with filtering"""
    where = {"tenantId": tenant_ctx["tenant_id"]}
    if status:
        where["status"] = status
    if lead_id:
        where["leadId"] = lead_id

    quotes = await db.quote.find_many(
        where=where,
        order={"createdAt": "desc"},
        skip=(page - 1) * page_size,
        take=page_size,
    )
    return [QuoteResponse.model_validate(q) for q in quotes]