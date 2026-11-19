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
