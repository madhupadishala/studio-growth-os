"""
Studio Growth OS - Webhook Endpoints
"""
import hmac
import hashlib
import json
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from prisma import Prisma

from core.config import settings
from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Instagram Webhook
@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Verify Instagram webhook subscription"""
    # In production, verify against stored verify token per tenant
    if hub_mode == "subscribe" and hub_verify_token:
        # For demo, accept any verify token
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/instagram")
async def instagram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Handle Instagram webhook events"""
    body = await request.body()

    # Verify signature (simplified)
    # In production: verify against each tenant's app secret

    payload = await request.json()

    # Store inbound event for processing
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") in ["comments", "messages"]:
                await db.inboundEvent.create(
                    data={
                        "tenantId": tenant_ctx["tenant_id"],
                        "provider": "instagram",
                        "providerEventId": change.get("value", {}).get("id", ""),
                        "eventType": change.get("field", ""),
                        "externalActorId": change.get("value", {}).get("from", {}).get("id"),
                        "occurredAt": datetime.utcnow(),
                        "sourceAssetId": change.get("value", {}).get("media", {}).get("id"),
                        "payloadRef": f"instagram_{entry.get('id')}_{change.get('value', {}).get('id')}",
                        "state": "received",
                    }
                )

    return {"status": "received"}

# WhatsApp Webhook
@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Verify WhatsApp webhook subscription"""
    # Verify against stored verify token
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Handle WhatsApp webhook events"""
    body = await request.body()

    # Verify signature
    expected_signature = "sha256=" + hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if x_hub_signature_256 != expected_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # Process messages, statuses, etc.
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "messages":
                value = change.get("value", {})
                for message in value.get("messages", []):
                    await db.inboundEvent.create(
                        data={
                            "tenantId": tenant_ctx["tenant_id"],
                            "provider": "whatsapp",
                            "providerEventId": message.get("id", ""),
                            "eventType": "message",
                            "externalActorId": message.get("from"),
                            "occurredAt": datetime.utcfromtimestamp(int(message.get("timestamp", 0))),
                            "payloadRef": f"whatsapp_{message.get('id')}",
                            "state": "received",
                        }
                    )

    return {"status": "received"}

# Razorpay Webhook
@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature"),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Handle Razorpay payment webhooks"""
    body = await request.body()

    # Verify signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if x_razorpay_signature != expected_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = payload.get("event")
    payment = payload.get("payload", {}).get("payment", {}).get("entity", {})

    if event == "payment.captured":
        payment_id = payment.get("id")
        order_id = payment.get("order_id")

        # Find and update payment record
        payment_record = await db.payment.find_first(
            where={"razorpayOrderId": order_id, "tenantId": tenant_ctx["tenant_id"]}
        )

        if payment_record:
            await db.payment.update(
                where={"id": payment_record.id},
                data={
                    "razorpayPaymentId": payment_id,
                    "status": "captured",
                    "capturedAt": datetime.utcnow(),
                    "feePaise": payment.get("fee", 0),
                    "netPaise": payment.get("amount", 0) - payment.get("fee", 0),
                    "ledgerSyncedAt": datetime.utcnow(),
                }
            )

            # If linked to booking, confirm booking
            if payment_record.bookingId:
                await db.booking.update(
                    where={"id": payment_record.bookingId},
                    data={"state": "confirmed", "confirmedAt": datetime.utcnow()}
                )

                # Convert slot holds
                await db.slotHold.update_many(
                    where={"leadId": payment_record.booking.leadId, "state": "active"},
                    data={"state": "converted"}
                )

    return {"status": "processed"}

# Generic webhook for other providers
@router.post("/{provider}")
async def generic_webhook(
    provider: str,
    request: Request,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Generic webhook handler for other providers"""
    body = await request.body()
    payload = await request.json()

    await db.inboundEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "provider": provider,
            "providerEventId": payload.get("id", str(hash(str(payload)))),
            "eventType": "webhook",
            "payloadRef": f"{provider}_{datetime.utcnow().timestamp()}",
            "state": "received",
        }
    )

    return {"status": "received"}