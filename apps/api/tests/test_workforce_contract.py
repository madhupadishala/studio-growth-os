import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock

import pytest
import httpx
from fastapi import HTTPException
from starlette.requests import Request

from core.rungrow_auth import verify_rungrow_request, require_workforce_scope
from services.rungrow_webhook_client import RunGrowWebhookClient

SECRET = "test-rungrow-workforce-secret-32-bytes-minimum"
TENANT_MAP = {"studio-external-001": "workforce-internal-001"}

def _signed_headers(body: bytes, scopes: str):
    timestamp = str(int(time.time()))
    external, internal, product = "studio-external-001", "workforce-internal-001", "photo-studio-growth-os"
    canonical = ".".join((timestamp, product, internal, external, scopes, hashlib.sha256(body).hexdigest())).encode()
    signature = "sha256=" + hmac.new(SECRET.encode(), canonical, hashlib.sha256).hexdigest()
    return {"x-rungrow-signature": signature, "x-rungrow-timestamp": timestamp,
            "x-rungrow-product-id": product, "x-rungrow-external-tenant-id": external,
            "x-rungrow-tenant-id": internal, "x-rungrow-scopes": scopes,
            "x-correlation-id": "corr-test-001"}

def test_scope_bound_hmac_verification_and_tenant_binding():
    body = b'{"page":1}'
    headers = _signed_headers(body, "photo-studio-growth-os:read")
    result = verify_rungrow_request(headers, body, SECRET, TENANT_MAP)
    assert result["external_tenant_id"] == "studio-external-001"
    assert result["workforce_tenant_id"] == "workforce-internal-001"
    assert result["scopes"] == ["photo-studio-growth-os:read"]
    tampered = dict(headers, **{"x-rungrow-scopes": "photo-studio-growth-os:write"})
    with pytest.raises(HTTPException) as exc:
        verify_rungrow_request(tampered, body, SECRET, TENANT_MAP)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_scope_dependency_denies_missing_scope():
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": [],
                       "query_string": b"", "server": ("test", 80), "scheme": "http",
                       "client": ("test", 1), "root_path": "",
                       "state": {"rungrow_service": {"scopes": ["photo-studio-growth-os:read"]}}})
    dependency = require_workforce_scope("photo-studio-growth-os:write")
    with pytest.raises(HTTPException) as exc:
        await dependency(request)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_outbound_webhook_uses_shared_hmac_and_zeroes_non_revenue_events():
    captured = {}
    def handler(request):
        captured["request"] = request
        return httpx.Response(200, json={"status": "accepted"})
    transport = httpx.MockTransport(handler)
    client = RunGrowWebhookClient(base_url="https://workforce.test/hooks", secret=SECRET,
                                  transport=transport)
    await client.emit(event_type="trial_started", event_id="trial-001",
        external_tenant_id="studio-external-001", internal_tenant_id="workforce-internal-001",
        correlation_id="corr-test-001", occurred_at="2026-11-19T10:00:00+05:30",
        recognised_revenue_inr=0)
    request = captured["request"]
    payload = json.loads(request.content)
    assert payload["recognised_revenue_inr"] == 0
    assert request.headers["X-RunGrow-External-Tenant-Id"] == "studio-external-001"
    assert request.headers["X-RunGrow-Tenant-Id"] == "workforce-internal-001"
    assert request.headers["X-RunGrow-Scopes"] == "photo-studio-growth-os:write"
    assert request.headers["Idempotency-Key"] == "photo-studio-growth-os:trial-001"

    timestamp = request.headers["X-RunGrow-Timestamp"]
    canonical = ".".join((
        timestamp,
        "photo-studio-growth-os",
        "workforce-internal-001",
        "studio-external-001",
        "photo-studio-growth-os:write",
        hashlib.sha256(request.content).hexdigest(),
    )).encode()
    expected = "sha256=" + hmac.new(SECRET.encode(), canonical, hashlib.sha256).hexdigest()
    assert hmac.compare_digest(request.headers["X-RunGrow-Signature"], expected)
    verified = verify_rungrow_request(
        {key.lower(): value for key, value in request.headers.items()},
        request.content,
        SECRET,
        TENANT_MAP,
    )
    assert verified["scopes"] == ["photo-studio-growth-os:write"]


@pytest.mark.asyncio
async def test_fastapi_lifespan_connects_to_generated_prisma_client():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import importlib.util
    api_root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("studio_api_main", api_root / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    app = module.app
    from core.database import db

    async with app.router.lifespan_context(app):
        assert db.is_connected()
        assert await db.query_raw("SELECT 1 AS ready") == [{"ready": 1}]
    assert not db.is_connected()


@pytest.mark.asyncio
async def test_prisma_idempotency_persists_replay_and_payload_conflict():
    from uuid import uuid4
    from core.database import db
    from core.workforce_idempotency import claim, complete

    await db.connect()
    tenant = "workforce-internal-001"
    endpoint = "POST:/api/v1/workforce/test-idempotency"
    key = f"ci-{uuid4()}"
    payload = {"lead_id": "lead-ci-001", "action": "followup"}
    first = await claim(tenant, endpoint, key, payload, "corr-ci-001")
    assert first["created"] is True
    response_body = {"status": "accepted", "lead_id": "lead-ci-001"}
    await complete(tenant, endpoint, key, 200, response_body)

    replay = await claim(tenant, endpoint, key, payload, "corr-ci-replay")
    assert replay["created"] is False
    assert replay["status_code"] == 200
    assert replay["body"] == response_body

    count = await db.workforceadapteridempotency.count(where={
        "externalTenantId": tenant, "endpoint": endpoint, "idempotencyKey": key
    })
    assert count == 1

    with pytest.raises(HTTPException) as exc:
        await claim(tenant, endpoint, key, {"lead_id": "different"}, "corr-ci-conflict")
    assert exc.value.status_code == 409
    await db.disconnect()


@pytest.mark.asyncio
async def test_workforce_routes_use_real_postgres_and_enforce_tenant_and_write_idempotency():
    import importlib.util
    import sys
    from datetime import datetime, timedelta, timezone
    from pathlib import Path
    from uuid import uuid4

    from httpx import ASGITransport, AsyncClient
    from core.database import db

    api_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(api_root))
    spec = importlib.util.spec_from_file_location("studio_api_workforce_integration", api_root / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from api.v1.endpoints.workforce import AI_IDENTITY_DISCLOSURE

    internal_tenant = "workforce-internal-001"
    external_tenant = "studio-external-001"
    suffix = str(uuid4())
    await db.connect()

    tenant = await db.tenant.create(data={
        "id": internal_tenant, "slug": f"ci-workforce-{suffix}",
        "name": "Workforce CI Tenant", "planId": "test",
        "brandConfig": {"theme": "test"},
    })
    other_tenant = await db.tenant.create(data={
        "id": f"workforce-other-{suffix}", "slug": f"ci-other-{suffix}",
        "name": "Other Tenant", "planId": "test", "brandConfig": {},
    })
    contact = await db.contact.create(data={
        "tenantId": tenant.id, "displayName": "Primary Contact",
        "sourceFirst": "test", "sourceLast": "test",
    })
    other_contact = await db.contact.create(data={
        "tenantId": other_tenant.id, "displayName": "Other Contact",
        "sourceFirst": "test", "sourceLast": "test",
    })
    lead = await db.lead.create(data={
        "tenantId": tenant.id, "contactId": contact.id, "stage": "new",
        "score": 10, "reasonsJson": {}, "sourceFirst": "test", "sourceLast": "test",
    })
    other_lead = await db.lead.create(data={
        "tenantId": other_tenant.id, "contactId": other_contact.id, "stage": "new",
        "score": 5, "reasonsJson": {}, "sourceFirst": "test", "sourceLast": "test",
    })
    quote = await db.quote.create(data={
        "tenantId": tenant.id, "leadId": lead.id, "pricebookVersion": 1,
        "totalsJson": {"total": 1000},
        "expiresAt": datetime.now(timezone.utc) + timedelta(days=7),
    })
    resource = await db.resource.create(data={
        "tenantId": tenant.id, "name": "CI Photographer", "type": "photographer",
    })
    await db.booking.create(data={
        "tenantId": tenant.id, "resourceId": resource.id, "customerId": contact.id,
        "quoteId": quote.id, "startsAt": datetime.now(timezone.utc) + timedelta(days=2),
        "endsAt": datetime.now(timezone.utc) + timedelta(days=2, hours=2),
    })
    await db.conversation.create(data={
        "tenantId": tenant.id, "leadId": lead.id, "channel": "whatsapp",
    })

    async with module.app.router.lifespan_context(module.app):
        async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
            read_headers = _signed_headers(b"", "photo-studio-growth-os:read")
            summary = await client.get("/api/v1/workforce/tenant-summary", headers=read_headers)
            assert summary.status_code == 200
            assert summary.json()["external_tenant_id"] == external_tenant
            assert summary.json()["lead_count"] == 1
            assert summary.json()["quote_count"] == 1
            assert summary.json()["booking_count"] == 1
            assert summary.json()["conversation_count"] == 1

            leads = await client.get("/api/v1/workforce/leads", headers=read_headers)
            assert leads.status_code == 200
            assert [row["id"] for row in leads.json()["leads"]] == [lead.id]

            quotes = await client.get("/api/v1/workforce/quotes", headers=read_headers)
            assert quotes.status_code == 200
            assert [row["id"] for row in quotes.json()] == [quote.id]

            bookings = await client.get("/api/v1/workforce/bookings", headers=read_headers)
            assert bookings.status_code == 200
            assert len(bookings.json()) == 1

            conversations = await client.get(
                f"/api/v1/workforce/conversations/{lead.id}", headers=read_headers
            )
            assert conversations.status_code == 200
            assert conversations.json()["external_tenant_id"] == external_tenant

            followup_payload = {
                "channel": "whatsapp", "message": "Your studio follow-up",
                "quote_id": quote.id, "template_vars": {},
                "ai_identity_disclosure": AI_IDENTITY_DISCLOSURE, "dry_run": True,
            }
            followup_body = json.dumps(
                followup_payload, separators=(",", ":"), ensure_ascii=False
            ).encode()
            followup_headers = _signed_headers(
                followup_body, "photo-studio-growth-os:write"
            )
            followup_headers["Idempotency-Key"] = f"followup-{suffix}"
            first_followup = await client.post(
                f"/api/v1/workforce/leads/{lead.id}/followup",
                content=followup_body, headers=followup_headers,
            )
            replay_followup = await client.post(
                f"/api/v1/workforce/leads/{lead.id}/followup",
                content=followup_body, headers=followup_headers,
            )
            assert first_followup.status_code == replay_followup.status_code == 200
            assert first_followup.json() == replay_followup.json()
            changed_followup = dict(followup_payload, message="altered payload")
            changed_body = json.dumps(
                changed_followup, separators=(",", ":"), ensure_ascii=False
            ).encode()
            changed_headers = _signed_headers(
                changed_body, "photo-studio-growth-os:write"
            )
            changed_headers["Idempotency-Key"] = f"followup-{suffix}"
            conflict_followup = await client.post(
                f"/api/v1/workforce/leads/{lead.id}/followup",
                content=changed_body, headers=changed_headers,
            )
            assert conflict_followup.status_code == 409

            new_contact = await db.contact.create(data={
                "tenantId": tenant.id, "displayName": "RunGrow Prospect",
                "sourceFirst": "rungrow", "sourceLast": "rungrow",
            })
            handoff_payload = {
                "contact_id": new_contact.id, "source_url": "https://rungrow.test/prospect/1",
                "approval_id": "approval-ci-001", "campaign": "ci-campaign",
                "metadata": {"source": "ci"},
            }
            handoff_body = json.dumps(
                handoff_payload, separators=(",", ":"), ensure_ascii=False
            ).encode()
            handoff_headers = _signed_headers(
                handoff_body, "photo-studio-growth-os:write"
            )
            handoff_headers["Idempotency-Key"] = f"handoff-{suffix}"
            before = await db.lead.count(where={"tenantId": tenant.id})
            first_handoff = await client.post(
                "/api/v1/workforce/prospects/handoff",
                content=handoff_body, headers=handoff_headers,
            )
            replay_handoff = await client.post(
                "/api/v1/workforce/prospects/handoff",
                content=handoff_body, headers=handoff_headers,
            )
            assert first_handoff.status_code == replay_handoff.status_code == 200
            assert first_handoff.json() == replay_handoff.json()
            after = await db.lead.count(where={"tenantId": tenant.id})
            assert after == before + 1

            changed_handoff = dict(handoff_payload, campaign="changed")
            changed_handoff_body = json.dumps(
                changed_handoff, separators=(",", ":"), ensure_ascii=False
            ).encode()
            changed_handoff_headers = _signed_headers(
                changed_handoff_body, "photo-studio-growth-os:write"
            )
            changed_handoff_headers["Idempotency-Key"] = f"handoff-{suffix}"
            conflict_handoff = await client.post(
                "/api/v1/workforce/prospects/handoff",
                content=changed_handoff_body, headers=changed_handoff_headers,
            )
            assert conflict_handoff.status_code == 409

            assert await db.workforceadapteridempotency.count(where={
                "externalTenantId": external_tenant,
                "idempotencyKey": f"followup-{suffix}",
            }) == 1
            assert await db.workforceadapteridempotency.count(where={
                "externalTenantId": external_tenant,
                "idempotencyKey": f"handoff-{suffix}",
            }) == 1

    await db.tenant.delete(where={"id": tenant.id})
    await db.tenant.delete(where={"id": other_tenant.id})
    await db.disconnect()
