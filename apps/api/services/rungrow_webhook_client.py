"""Signed lifecycle and revenue event delivery to RunGrow Workforce."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal
from typing import Any
import httpx

EVENTS = {
    "studio_tenant_onboarded", "trial_started", "lead_converted",
    "booking_confirmed", "invoice_recognised", "churn_risk_flagged",
}
REVENUE_EVENTS = {"invoice_recognised"}

class RunGrowWebhookClient:
    def __init__(self, *, base_url: str | None = None, secret: str | None = None,
                 product_id: str = "photo-studio-growth-os", timeout: float = 10.0,
                 transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = (base_url or os.getenv("RUNGROW_WORKFORCE_WEBHOOK_URL", "")).rstrip("/")
        self.secret = secret or os.getenv("RUNGROW_WORKFORCE_HMAC_SECRET", "")
        self.product_id = product_id
        self.timeout = timeout
        self.transport = transport
        if not self.base_url:
            raise RuntimeError("RUNGROW_WORKFORCE_WEBHOOK_URL is not configured")
        if len(self.secret.encode("utf-8")) < 32:
            raise RuntimeError("RUNGROW_WORKFORCE_HMAC_SECRET must contain at least 32 bytes")

    def _canonical(self, timestamp: str, internal_tenant_id: str,
                   external_tenant_id: str, body: bytes) -> bytes:
        body_hash = hashlib.sha256(body).hexdigest()
        return ".".join((timestamp, self.product_id, internal_tenant_id,
                         external_tenant_id, "", body_hash)).encode("utf-8")

    async def emit(self, *, event_type: str, event_id: str, external_tenant_id: str,
                   internal_tenant_id: str, correlation_id: str,
                   occurred_at: str, recognised_revenue_inr: int | float | str = 0,
                   source_ref: str | None = None, metadata: dict[str, Any] | None = None) -> dict:
        if event_type not in EVENTS:
            raise ValueError("Unsupported RunGrow lifecycle event")
        revenue = Decimal(str(recognised_revenue_inr or 0))
        if not revenue.is_finite() or revenue < 0:
            raise ValueError("recognised_revenue_inr must be a non-negative finite INR amount")
        if event_type not in REVENUE_EVENTS and revenue != 0:
            raise ValueError("recognised_revenue_inr must be zero for non-revenue events")
        if not event_id or not external_tenant_id or not internal_tenant_id or external_tenant_id == internal_tenant_id:
            raise ValueError("Distinct tenant IDs and a stable event_id are required")
        payload = {
            "tenant_id": external_tenant_id,
            "workforce_tenant_id": internal_tenant_id,
            "product_id": self.product_id,
            "event_id": event_id,
            "event_type": event_type,
            "recognised_revenue_inr": float(revenue),
            "occurred_at": occurred_at,
            "source_ref": source_ref,
            "metadata": metadata or {},
        }
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        timestamp = str(int(time.time()))
        binding = self._canonical(timestamp, internal_tenant_id, external_tenant_id, body)
        signature = "sha256=" + hmac.new(self.secret.encode("utf-8"), binding, hashlib.sha256).hexdigest()
        headers = {
            "X-RunGrow-Signature": signature,
            "X-RunGrow-Timestamp": timestamp,
            "X-RunGrow-Product-Id": self.product_id,
            "X-RunGrow-External-Tenant-Id": external_tenant_id,
            "X-RunGrow-Tenant-Id": internal_tenant_id,
            "X-Correlation-ID": correlation_id,
            "Idempotency-Key": f"{self.product_id}:{event_id}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(transport=self.transport, timeout=self.timeout) as client:
            response = await client.post(self.base_url, content=body, headers=headers)
        response.raise_for_status()
        return response.json() if response.content else {"status": "accepted"}
